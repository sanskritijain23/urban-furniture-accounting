"""
Report generation service — Balance Sheet, Profit & Loss, Budget
Report. All figures are derived by calling ledger_service.py (which
reads posted Journal Entries); this module must NOT recompute
debit/credit totals independently.
"""
from sqlalchemy.orm import Session

from app.services import ledger_service, budget_service


def generate_balance_sheet(db: Session, year: int):
    """
    TODO: use ledger_service.get_balances_by_account_type() for
    Asset/Liability/Bank/Cash/Capital types, filtered to the given
    year, and assemble into schemas.report.BalanceSheetResponse.
    """
    raise NotImplementedError


def generate_profit_and_loss(db: Session, year: int):
    """
    TODO: use ledger_service.get_balances_by_account_type() for
    Income/Expenses/Other Expenses types, filtered to the given year,
    and assemble into schemas.report.ProfitAndLossResponse.
    Net Income = total Income - total Expenses.
    """
    raise NotImplementedError


def generate_budget_report(db: Session, year: int):
    """
    TODO: for each CONFIRMED Budget whose period overlaps the given
    year, call budget_service.compute_achieved(...) and assemble into
    schemas.report.BudgetReportResponse.
    """
    raise NotImplementedError
