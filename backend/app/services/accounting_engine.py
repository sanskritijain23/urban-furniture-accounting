"""
=======================================================================
ACCOUNTING ENGINE -- the single centralized source of truth for all
double-entry bookkeeping in the Urban Furniture Accounting System.
=======================================================================

CRITICAL RULE (approved architecture -- non-negotiable):

    This module is the ONLY place in the entire codebase permitted to
    create, modify, or post JournalEntry / JournalEntryLine rows.

    purchase_service.py, sales_service.py, payment_service.py, and
    report_service.py must NEVER construct a JournalEntry or
    JournalEntryLine directly. They call into the functions below
    instead.

-----------------------------------------------------------------------
AUDITED ACCOUNTING RULES:
-----------------------------------------------------------------------

1. Purchase Order confirmation  -> NO Journal Entry.
2. Sales Order confirmation     -> NO Journal Entry.
3. Vendor Bill confirmation     -> Debit Purchase Expense / Credit Creditors.
4. Customer Invoice confirmation -> Debit Debtors / Credit Sales Income.
5. Vendor Bill Payment (SEND)    -> Debit Creditors / Credit Bank or Cash.
6. Customer Invoice Payment (RECEIVE) -> Debit Bank or Cash / Credit Debtors.
7. Manual Journal Entry -> user-entered lines; cannot be POSTED unless
   SUM(debit) == SUM(credit).

Every payment ALWAYS creates a journal entry distinct from the one
created by the bill/invoice it settles -- never merge the two.

-----------------------------------------------------------------------
ACCOUNT RESOLUTION CONVENTION
-----------------------------------------------------------------------
The Chart of Accounts is pre-configured (see database/seed/seed_data.py)
with control accounts named "Debtors A/c" and "Creditors A/c". Since
there is no dedicated FK from Contact to a specific receivable/payable
account, this engine resolves them by a case-insensitive name lookup
("debtors" / "creditors" substring match). Bank/Cash accounts are
resolved by Account.type instead, since that's a controlled enum and
therefore reliable regardless of exact naming.

If the expected control account doesn't exist, a clear
MissingControlAccountError is raised (not a silent skip) so the admin
knows exactly which Chart of Accounts entry to create.
"""
from datetime import date
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.enums import (
    AccountType, JournalEntryStatus, JournalEntrySourceType,
    JournalType, PaymentType, PaymentVia,
)
from app.models.journal import Journal
from app.models.journal_entry import JournalEntry, JournalEntryLine


class UnbalancedEntryError(Exception):
    """Raised when a Journal Entry's debit and credit totals do not match."""
    pass


class InvalidLineError(Exception):
    """Raised when a line has both debit and credit non-zero, or both zero."""
    pass


class MissingControlAccountError(Exception):
    """Raised when a required control account (Debtors/Creditors/Bank/Cash/
    Purchase Expense/Sales Income) cannot be found in the Chart of Accounts."""
    pass


class MissingJournalError(Exception):
    """Raised when the expected default Journal (Sales/Purchase/Bank/Cash)
    cannot be found."""
    pass


def validate_entry_is_balanced(lines: List) -> bool:
    """
    Returns True if SUM(debit) == SUM(credit) across the given lines.
    `lines` may be JournalEntryLine ORM objects or plain dicts with
    "debit"/"credit" keys.
    """
    def _get(line, field):
        return line[field] if isinstance(line, dict) else getattr(line, field)

    total_debit = sum((_get(line, "debit") or Decimal("0")) for line in lines)
    total_credit = sum((_get(line, "credit") or Decimal("0")) for line in lines)
    return total_debit == total_credit


def _find_account_by_name_fragment(db: Session, fragment: str) -> Account:
    account = (
        db.query(Account)
        .filter(Account.name.ilike(f"%{fragment}%"))
        .order_by(Account.id)
        .first()
    )
    if account is None:
        raise MissingControlAccountError(
            f"No Chart of Accounts entry found matching '{fragment}'. "
            f"Please create one (e.g. seed data uses '{fragment.title()} A/c')."
        )
    return account


def get_debtors_account(db: Session) -> Account:
    return _find_account_by_name_fragment(db, "debtors")


def get_creditors_account(db: Session) -> Account:
    return _find_account_by_name_fragment(db, "creditors")


def get_default_purchase_expense_account(db: Session) -> Account:
    return _find_account_by_name_fragment(db, "purchase expense")


def get_default_sales_income_account(db: Session) -> Account:
    return _find_account_by_name_fragment(db, "sales income")


def get_bank_or_cash_account(db: Session, payment_via: PaymentVia) -> Account:
    account_type = AccountType.BANK if payment_via == PaymentVia.BANK else AccountType.CASH
    account = db.query(Account).filter(Account.type == account_type).order_by(Account.id).first()
    if account is None:
        raise MissingControlAccountError(
            f"No Chart of Accounts entry with type={account_type.value} found."
        )
    return account


def _get_journal_by_type(db: Session, journal_type: JournalType) -> Journal:
    journal = db.query(Journal).filter(Journal.type == journal_type).order_by(Journal.id).first()
    if journal is None:
        raise MissingJournalError(f"No Journal of type={journal_type.value} found.")
    return journal


def validate_lines_are_well_formed(lines: List[dict]) -> None:
    """
    Each line must have exactly one of debit/credit non-zero (never
    both, never neither). Raises InvalidLineError with a clear message
    identifying the offending line; never silently coerces.
    """
    for idx, line in enumerate(lines):
        debit = line.get("debit") or Decimal("0")
        credit = line.get("credit") or Decimal("0")
        if debit > 0 and credit > 0:
            raise InvalidLineError(f"Line {idx}: cannot have both debit and credit non-zero")
        if debit == 0 and credit == 0:
            raise InvalidLineError(f"Line {idx}: must have either a debit or a credit amount")


def create_journal_entry(
    db: Session,
    journal_id: int,
    accounting_date: date,
    lines: List[dict],
    source_type: JournalEntrySourceType = JournalEntrySourceType.MANUAL,
    source_id: Optional[int] = None,
    reference_no: Optional[str] = None,
    status: JournalEntryStatus = JournalEntryStatus.POSTED,
) -> JournalEntry:
    """
    Create a Journal Entry with its lines. Validates line shape and
    overall balance BEFORE persisting anything if status is being set
    to POSTED -- an invalid or unbalanced entry is rejected outright,
    never partially written. DRAFT entries (e.g. a manual JE still
    being edited) are not required to be well-formed yet.
    """
    if status == JournalEntryStatus.POSTED:
        validate_lines_are_well_formed(lines)
        if not validate_entry_is_balanced(lines):
            total_debit = sum((l.get("debit") or Decimal("0")) for l in lines)
            total_credit = sum((l.get("credit") or Decimal("0")) for l in lines)
            raise UnbalancedEntryError(
                f"Journal entry is not balanced: total debit={total_debit}, "
                f"total credit={total_credit}"
            )

    entry = JournalEntry(
        journal_id=journal_id,
        accounting_date=accounting_date,
        status=status,
        source_type=source_type,
        source_id=source_id,
        reference_no=reference_no,
    )
    db.add(entry)
    db.flush()  # get entry.id for the lines' FK

    for line in lines:
        db.add(JournalEntryLine(
            journal_entry_id=entry.id,
            account_id=line["account_id"],
            partner_id=line.get("partner_id"),
            debit=line.get("debit") or Decimal("0"),
            credit=line.get("credit") or Decimal("0"),
        ))

    db.commit()
    db.refresh(entry)
    return entry


def post_journal_entry(db: Session, journal_entry_id: int) -> JournalEntry:
    """Transition a DRAFT Journal Entry to POSTED, validating line shape
    and balance first."""
    entry = db.query(JournalEntry).filter(JournalEntry.id == journal_entry_id).first()
    if entry is None:
        raise ValueError(f"JournalEntry {journal_entry_id} not found")

    line_dicts = [{"debit": l.debit, "credit": l.credit} for l in entry.lines]
    validate_lines_are_well_formed(line_dicts)

    if not validate_entry_is_balanced(entry.lines):
        total_debit = sum((l.debit or Decimal("0")) for l in entry.lines)
        total_credit = sum((l.credit or Decimal("0")) for l in entry.lines)
        raise UnbalancedEntryError(
            f"Journal entry {journal_entry_id} is not balanced: "
            f"total debit={total_debit}, total credit={total_credit}"
        )

    entry.status = JournalEntryStatus.POSTED
    db.commit()
    db.refresh(entry)
    return entry


def create_entry_for_vendor_bill_confirmation(db: Session, vendor_bill_id: int) -> JournalEntry:
    """Debit Purchase Expense (per line's account) / Credit Creditors (total)."""
    from app.models.vendor_bill import VendorBill

    bill = db.query(VendorBill).filter(VendorBill.id == vendor_bill_id).first()
    if bill is None:
        raise ValueError(f"VendorBill {vendor_bill_id} not found")

    creditors_account = get_creditors_account(db)
    purchase_journal = _get_journal_by_type(db, JournalType.PURCHASE)

    lines = []
    total = Decimal("0")
    for line in bill.lines:
        lines.append({
            "account_id": line.account_id,
            "partner_id": bill.vendor_id,
            "debit": line.total,
            "credit": Decimal("0"),
        })
        total += line.total

    lines.append({
        "account_id": creditors_account.id,
        "partner_id": bill.vendor_id,
        "debit": Decimal("0"),
        "credit": total,
    })

    return create_journal_entry(
        db,
        journal_id=purchase_journal.id,
        accounting_date=bill.bill_date,
        lines=lines,
        source_type=JournalEntrySourceType.VENDOR_BILL,
        source_id=bill.id,
        reference_no=bill.bill_no,
    )


def create_entry_for_customer_invoice_confirmation(db: Session, invoice_id: int) -> JournalEntry:
    """Debit Debtors (total) / Credit Sales Income (per line's account)."""
    from app.models.customer_invoice import CustomerInvoice

    invoice = db.query(CustomerInvoice).filter(CustomerInvoice.id == invoice_id).first()
    if invoice is None:
        raise ValueError(f"CustomerInvoice {invoice_id} not found")

    debtors_account = get_debtors_account(db)
    sales_journal = _get_journal_by_type(db, JournalType.SALES)

    lines = []
    total = Decimal("0")
    for line in invoice.lines:
        lines.append({
            "account_id": line.account_id,
            "partner_id": invoice.customer_id,
            "debit": Decimal("0"),
            "credit": line.total,
        })
        total += line.total

    lines.append({
        "account_id": debtors_account.id,
        "partner_id": invoice.customer_id,
        "debit": total,
        "credit": Decimal("0"),
    })

    return create_journal_entry(
        db,
        journal_id=sales_journal.id,
        accounting_date=invoice.invoice_date,
        lines=lines,
        source_type=JournalEntrySourceType.CUSTOMER_INVOICE,
        source_id=invoice.id,
        reference_no=invoice.invoice_no,
    )


def create_entry_for_payment(db: Session, payment_id: int) -> JournalEntry:
    """
    Branches on payment_type (SEND vs RECEIVE) to pick Creditors vs
    Debtors, and on payment_via (CASH vs BANK) to pick the cash/bank
    account. Always a NEW entry, separate from the Bill/Invoice entry.
    """
    from app.models.payment import Payment

    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise ValueError(f"Payment {payment_id} not found")

    bank_or_cash_account = get_bank_or_cash_account(db, payment.payment_via)
    journal_type = JournalType.BANK if payment.payment_via == PaymentVia.BANK else JournalType.CASH
    journal = _get_journal_by_type(db, journal_type)

    if payment.payment_type == PaymentType.SEND:
        # Vendor payment: Dr Creditors / Cr Bank or Cash
        control_account = get_creditors_account(db)
        lines = [
            {"account_id": control_account.id, "partner_id": payment.partner_id,
             "debit": payment.amount, "credit": Decimal("0")},
            {"account_id": bank_or_cash_account.id, "partner_id": payment.partner_id,
             "debit": Decimal("0"), "credit": payment.amount},
        ]
    else:
        # Customer receipt: Dr Bank or Cash / Cr Debtors
        control_account = get_debtors_account(db)
        lines = [
            {"account_id": bank_or_cash_account.id, "partner_id": payment.partner_id,
             "debit": payment.amount, "credit": Decimal("0")},
            {"account_id": control_account.id, "partner_id": payment.partner_id,
             "debit": Decimal("0"), "credit": payment.amount},
        ]

    return create_journal_entry(
        db,
        journal_id=journal.id,
        accounting_date=payment.date,
        lines=lines,
        source_type=JournalEntrySourceType.PAYMENT,
        source_id=payment.id,
    )


def create_manual_journal_entry(db: Session, payload) -> JournalEntry:
    """
    Backs the manual Journal Entry screen. Persists as DRAFT first (per
    the mockup's Draft -> Confirm/Post buttons) -- posting to POSTED is
    a separate explicit action via post_journal_entry, which is where
    the balance check actually blocks.
    """
    lines = [
        {
            "account_id": line.account_id,
            "partner_id": line.partner_id,
            "debit": line.debit,
            "credit": line.credit,
        }
        for line in payload.lines
    ]

    return create_journal_entry(
        db,
        journal_id=payload.journal_id,
        accounting_date=payload.accounting_date,
        lines=lines,
        source_type=JournalEntrySourceType.MANUAL,
        source_id=None,
        reference_no=payload.reference_no,
        status=JournalEntryStatus.DRAFT,
    )
