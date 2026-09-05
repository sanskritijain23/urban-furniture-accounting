"""
Ledger service -- the READ-SIDE aggregation layer over posted Journal
Entries. This is where account balances are computed for use by
report_service.py and budget_service.py.

IMPORTANT: this module only ever READS JournalEntry/JournalEntryLine
rows (status=POSTED). It never writes to them -- writing is the
exclusive responsibility of accounting_engine.py.

Balance sign convention: debit-normal accounts (Asset, Bank, Cash,
Expenses, Other Expenses) report balance = debit - credit.
Credit-normal accounts (Liability, Capital, Income) report
balance = credit - debit. This gives a "natural positive" balance for
every account type directly usable by report_service.py without it
having to know sign conventions itself.
"""
from decimal import Decimal
from typing import Optional
from datetime import date

from sqlalchemy.orm import Session

from app.models.account import Account
from app.models.analytic_account import AnalyticAccount
from app.models.customer_invoice import CustomerInvoiceLine, CustomerInvoice
from app.models.enums import AccountType, AnalyticAccountType, DocumentStatus, JournalEntryStatus
from app.models.journal_entry import JournalEntry, JournalEntryLine
from app.models.vendor_bill import VendorBillLine, VendorBill

DEBIT_NORMAL_TYPES = {
    AccountType.ASSET, AccountType.BANK, AccountType.CASH,
    AccountType.EXPENSES, AccountType.OTHER_EXPENSES,
}
CREDIT_NORMAL_TYPES = {
    AccountType.LIABILITY, AccountType.CAPITAL, AccountType.INCOME,
}


def _posted_lines_query(db: Session, account_id: int, as_of: Optional[date] = None):
    q = (
        db.query(JournalEntryLine)
        .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
        .filter(
            JournalEntryLine.account_id == account_id,
            JournalEntry.status == JournalEntryStatus.POSTED,
        )
    )
    if as_of is not None:
        q = q.filter(JournalEntry.accounting_date <= as_of)
    return q


def get_account_balance(db: Session, account_id: int, as_of: Optional[date] = None) -> Decimal:
    account = db.query(Account).filter(Account.id == account_id).first()
    if account is None:
        return Decimal("0")

    lines = _posted_lines_query(db, account_id, as_of).all()
    total_debit = sum((l.debit or Decimal("0")) for l in lines)
    total_credit = sum((l.credit or Decimal("0")) for l in lines)

    if account.type in DEBIT_NORMAL_TYPES:
        return total_debit - total_credit
    return total_credit - total_debit


def get_balances_by_account_type(db: Session, account_type: AccountType, as_of: Optional[date] = None):
    """
    Returns a list of (Account, balance) tuples for every account of
    the given type, using posted entries with accounting_date <= as_of
    (cumulative snapshot -- correct for a Balance Sheet's "as of" a
    given date, since balances carry forward across periods).
    """
    accounts = db.query(Account).filter(Account.type == account_type).order_by(Account.id).all()
    return [(account, get_account_balance(db, account.id, as_of)) for account in accounts]


def get_balances_by_account_type_for_period(
    db: Session, account_type: AccountType, period_start: date, period_end: date,
):
    """
    Like get_balances_by_account_type, but scoped strictly to
    [period_start, period_end] rather than cumulative-to-date --
    correct for a Profit & Loss statement, which resets each period
    (income/expenses within the year only, not carried forward).
    """
    accounts = db.query(Account).filter(Account.type == account_type).order_by(Account.id).all()
    results = []
    for account in accounts:
        lines = (
            db.query(JournalEntryLine)
            .join(JournalEntry, JournalEntryLine.journal_entry_id == JournalEntry.id)
            .filter(
                JournalEntryLine.account_id == account.id,
                JournalEntry.status == JournalEntryStatus.POSTED,
                JournalEntry.accounting_date >= period_start,
                JournalEntry.accounting_date <= period_end,
            )
            .all()
        )
        total_debit = sum((l.debit or Decimal("0")) for l in lines)
        total_credit = sum((l.credit or Decimal("0")) for l in lines)
        balance = (
            total_debit - total_credit
            if account.type in DEBIT_NORMAL_TYPES
            else total_credit - total_debit
        )
        results.append((account, balance))
    return results


def get_actuals_for_analytic_account(
    db: Session, analytic_account_id: int, period_start: date, period_end: date,
) -> Decimal:
    """
    Sums CONFIRMED transaction lines sharing this analytic account
    within the period. Per the approved analytic-tagging convention:
    Income-type analytic accounts are tracked via Customer Invoice
    lines; Expense-type analytic accounts are tracked via Vendor Bill
    lines (each line is tagged with an analytic account matching its
    document's economic direction).
    """
    analytic_account = (
        db.query(AnalyticAccount).filter(AnalyticAccount.id == analytic_account_id).first()
    )
    if analytic_account is None:
        return Decimal("0")

    if analytic_account.type == AnalyticAccountType.INCOME:
        lines = (
            db.query(CustomerInvoiceLine)
            .join(CustomerInvoice, CustomerInvoiceLine.customer_invoice_id == CustomerInvoice.id)
            .filter(
                CustomerInvoiceLine.analytic_account_id == analytic_account_id,
                CustomerInvoice.status == DocumentStatus.CONFIRMED,
                CustomerInvoice.invoice_date >= period_start,
                CustomerInvoice.invoice_date <= period_end,
            )
            .all()
        )
    else:
        lines = (
            db.query(VendorBillLine)
            .join(VendorBill, VendorBillLine.vendor_bill_id == VendorBill.id)
            .filter(
                VendorBillLine.analytic_account_id == analytic_account_id,
                VendorBill.status == DocumentStatus.CONFIRMED,
                VendorBill.bill_date >= period_start,
                VendorBill.bill_date <= period_end,
            )
            .all()
        )

    return sum((l.total or Decimal("0")) for l in lines) or Decimal("0")
