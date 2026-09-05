"""
=======================================================================
ACCOUNTING ENGINE — the single centralized source of truth for all
double-entry bookkeeping in the Urban Furniture Accounting System.
=======================================================================

CRITICAL RULE (approved architecture — non-negotiable):

    This module is the ONLY place in the entire codebase permitted to
    create, modify, or post JournalEntry / JournalEntryLine rows.

    purchase_service.py, sales_service.py, payment_service.py, and
    report_service.py must NEVER construct a JournalEntry or
    JournalEntryLine directly. They call into the functions below
    instead. This prevents divergent/duplicated accounting logic
    living in multiple modules.

Overall flow:

    Business Transaction (Vendor Bill / Customer Invoice / Payment /
    Manual Entry)
            |
            v
    Accounting Service  (this module)
            |
            v
    Journal Entry
            |
            v
    Journal Entry Lines   <-- SUM(debit) must equal SUM(credit)
            |
            v
    Ledger  (see ledger_service.py, read-side aggregation)
            |
            v
    Financial Reports  (see report_service.py)

-----------------------------------------------------------------------
AUDITED ACCOUNTING RULES (from the approved Problem Statement + MVP):
-----------------------------------------------------------------------

1. Purchase Order confirmation  -> NO Journal Entry.
   (A PO is a commitment only; it has no accounting impact.)

2. Sales Order confirmation     -> NO Journal Entry.
   (Same reasoning as above.)

3. Vendor Bill confirmation     -> Creates ONE Journal Entry:
       Debit  : Purchase Expense (per line's account, default
                "Purchase Expense")
       Credit : Creditors / Accounts Payable (the vendor)
   Reference: source_type=VENDOR_BILL, source_id=<vendor_bill.id>

4. Customer Invoice confirmation -> Creates ONE Journal Entry:
       Debit  : Debtors / Accounts Receivable (the customer)
       Credit : Sales Income (per line's account, default
                "Sales Income")
   Reference: source_type=CUSTOMER_INVOICE, source_id=<invoice.id>

5. Vendor Bill Payment (payment_type=SEND) -> Creates ONE Journal
   Entry, SEPARATE from the Bill's own entry:
       Debit  : Creditors / Accounts Payable
       Credit : Bank or Cash (per payment_via)
   Reference: source_type=PAYMENT, source_id=<payment.id>

6. Customer Invoice Payment (payment_type=RECEIVE) -> Creates ONE
   Journal Entry, SEPARATE from the Invoice's own entry:
       Debit  : Bank or Cash (per payment_via)
       Credit : Debtors / Accounts Receivable
   Reference: source_type=PAYMENT, source_id=<payment.id>

7. Manual Journal Entry -> User selects Journal, Accounting Date, and
   enters Account/Partner/Debit/Credit lines directly. Cannot be
   POSTED unless SUM(debit) == SUM(credit) (see
   validate_entry_is_balanced below).

Every payment ALWAYS creates a journal entry distinct from the one
created by the bill/invoice it settles — never merge the two.

-----------------------------------------------------------------------
IMPLEMENTATION STATUS: STRUCTURE / INTERFACE ONLY.
No transaction logic is implemented yet. Function bodies raise
NotImplementedError as placeholders until business logic is built.
-----------------------------------------------------------------------
"""
from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.journal_entry import JournalEntry, JournalEntryLine
from app.models.enums import JournalEntryStatus, JournalEntrySourceType


class UnbalancedEntryError(Exception):
    """Raised when a Journal Entry's debit and credit totals do not match."""
    pass


def validate_entry_is_balanced(lines: List[JournalEntryLine]) -> bool:
    """
    Returns True if SUM(debit) == SUM(credit) across the given lines.

    This is the single blocking validation rule referenced everywhere
    in the approved architecture (manual JE screen, Bill/Invoice
    confirmation, Payment confirmation). Must be called before any
    JournalEntry transitions to POSTED.
    """
    total_debit = sum((line.debit or Decimal("0")) for line in lines)
    total_credit = sum((line.credit or Decimal("0")) for line in lines)
    return total_debit == total_credit


def create_journal_entry(
    db: Session,
    journal_id: int,
    accounting_date,
    lines: List[dict],
    source_type: JournalEntrySourceType = JournalEntrySourceType.MANUAL,
    source_id: Optional[int] = None,
    reference_no: Optional[str] = None,
) -> JournalEntry:
    """
    Create (and validate) a Journal Entry with its lines.

    `lines` is a list of dicts shaped like:
        {"account_id": int, "partner_id": Optional[int],
         "debit": Decimal, "credit": Decimal}

    TODO:
      1. Build JournalEntry + JournalEntryLine ORM objects.
      2. Call validate_entry_is_balanced(); raise UnbalancedEntryError
         if it fails.
      3. Persist and return the entry with status=POSTED (or DRAFT if
         the caller wants to review before posting — see
         post_journal_entry below).
    """
    raise NotImplementedError("create_journal_entry: business logic not yet implemented")


def post_journal_entry(db: Session, journal_entry_id: int) -> JournalEntry:
    """
    Transition a DRAFT Journal Entry to POSTED.

    TODO:
      1. Load the entry + its lines.
      2. Call validate_entry_is_balanced(); raise
         UnbalancedEntryError (blocking) if not balanced.
      3. Set status = JournalEntryStatus.POSTED and commit.
    """
    raise NotImplementedError("post_journal_entry: business logic not yet implemented")


def create_entry_for_vendor_bill_confirmation(db: Session, vendor_bill_id: int) -> JournalEntry:
    """
    Rule 3 above: Debit Purchase Expense / Credit Creditors.
    Called by purchase_service.py when a Vendor Bill is confirmed.
    Must NOT be called from anywhere else.
    """
    raise NotImplementedError("create_entry_for_vendor_bill_confirmation: not yet implemented")


def create_entry_for_customer_invoice_confirmation(db: Session, invoice_id: int) -> JournalEntry:
    """
    Rule 4 above: Debit Debtors / Credit Sales Income.
    Called by sales_service.py when a Customer Invoice is confirmed.
    Must NOT be called from anywhere else.
    """
    raise NotImplementedError("create_entry_for_customer_invoice_confirmation: not yet implemented")


def create_entry_for_payment(db: Session, payment_id: int) -> JournalEntry:
    """
    Rules 5 & 6 above. Branches on payment.payment_type (SEND vs
    RECEIVE) and payment.payment_via (CASH vs BANK) to pick the
    correct debit/credit accounts. Always creates a NEW entry,
    separate from the one created for the underlying Bill/Invoice.
    Called by payment_service.py. Must NOT be called from anywhere else.
    """
    raise NotImplementedError("create_entry_for_payment: not yet implemented")


def create_manual_journal_entry(db: Session, payload) -> JournalEntry:
    """
    Rule 7 above — backs the manual Journal Entry screen
    (MUST HAVE requirement). `payload` is expected to be a
    ManualJournalEntryCreate schema instance (see
    app/schemas/journal_entry.py).

    TODO: build lines from payload.lines, validate balance, persist
    with status=DRAFT, and only allow a subsequent explicit "Post"
    action (post_journal_entry) to move it to POSTED — mirrors the
    Draft/Confirm/Post buttons shown in the MVP mockup.
    """
    raise NotImplementedError("create_manual_journal_entry: not yet implemented")
