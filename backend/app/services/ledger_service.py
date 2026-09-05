"""
Ledger service — the READ-SIDE aggregation layer over posted Journal
Entries. This is where account balances are computed for use by
report_service.py and budget_service.py.

IMPORTANT: this module only ever READS JournalEntry/JournalEntryLine
rows (status=POSTED). It never writes to them — writing is the
exclusive responsibility of accounting_engine.py.
"""
from decimal import Decimal
from typing import Optional
from datetime import date

from sqlalchemy.orm import Session


def get_account_balance(db: Session, account_id: int, as_of: Optional[date] = None) -> Decimal:
    """
    TODO: sum(debit) - sum(credit) (or the reverse, depending on
    account type convention) across all POSTED JournalEntryLine rows
    for this account, optionally filtered to accounting_date <= as_of.
    """
    raise NotImplementedError


def get_balances_by_account_type(db: Session, account_type, year: Optional[int] = None):
    """
    TODO: group posted JournalEntryLines by Account.type
    (Asset/Liability/Bank/Cash/Capital/Income/Expenses/Other Expenses)
    for the Balance Sheet / P&L computations in report_service.py.
    """
    raise NotImplementedError


def get_actuals_for_analytic_account(db: Session, analytic_account_id: int,
                                      period_start: date, period_end: date) -> Decimal:
    """
    TODO: sum the totals of CustomerInvoiceLine / VendorBillLine rows
    (on CONFIRMED documents) sharing this analytic_account_id within
    the given period. Used by budget_service.py to compute
    achieved_amount for a Budget.
    """
    raise NotImplementedError
