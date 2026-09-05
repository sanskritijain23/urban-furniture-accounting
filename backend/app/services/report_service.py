"""
Report generation service -- Balance Sheet, Profit & Loss, Budget
Report. All figures are derived by calling ledger_service.py (which
reads posted Journal Entries); this module must NOT recompute
debit/credit totals independently.
"""
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.enums import AccountType, BudgetStatus
from app.services import ledger_service, budget_service
from app.models.budget import Budget
from app.schemas.report import (
    BalanceSheetResponse, ProfitAndLossResponse, BudgetReportResponse,
    ReportLineItem, BudgetReportRow,
)


def generate_balance_sheet(db: Session, year: int) -> BalanceSheetResponse:
    """
    Cumulative snapshot as of Dec 31 of the given year (balances carry
    forward across periods, unlike P&L). Assets = Asset + Bank + Cash
    account types; Liabilities = Liability; Capital = Capital.
    """
    as_of = date(year, 12, 31)

    asset_types = [AccountType.ASSET, AccountType.BANK, AccountType.CASH]
    assets = []
    for acc_type in asset_types:
        for account, balance in ledger_service.get_balances_by_account_type(db, acc_type, as_of):
            if balance != 0:
                assets.append(ReportLineItem(account_name=account.name, amount=balance))

    liabilities = [
        ReportLineItem(account_name=account.name, amount=balance)
        for account, balance in ledger_service.get_balances_by_account_type(
            db, AccountType.LIABILITY, as_of
        )
        if balance != 0
    ]

    capital = [
        ReportLineItem(account_name=account.name, amount=balance)
        for account, balance in ledger_service.get_balances_by_account_type(
            db, AccountType.CAPITAL, as_of
        )
        if balance != 0
    ]

    total_assets = sum((item.amount for item in assets), Decimal("0"))
    total_liabilities = sum((item.amount for item in liabilities), Decimal("0"))
    total_capital = sum((item.amount for item in capital), Decimal("0"))

    return BalanceSheetResponse(
        year=year,
        assets=assets,
        liabilities=liabilities,
        capital=capital,
        total_assets=total_assets,
        total_liabilities=total_liabilities,
        total_capital=total_capital,
    )


def generate_profit_and_loss(db: Session, year: int) -> ProfitAndLossResponse:
    """
    Strictly within [Jan 1, Dec 31] of the given year (P&L resets each
    period, unlike the Balance Sheet). Net Income = Income - Expenses
    - Other Expenses.
    """
    period_start = date(year, 1, 1)
    period_end = date(year, 12, 31)

    income = [
        ReportLineItem(account_name=account.name, amount=balance)
        for account, balance in ledger_service.get_balances_by_account_type_for_period(
            db, AccountType.INCOME, period_start, period_end
        )
        if balance != 0
    ]
    expenses = [
        ReportLineItem(account_name=account.name, amount=balance)
        for account, balance in ledger_service.get_balances_by_account_type_for_period(
            db, AccountType.EXPENSES, period_start, period_end
        )
        if balance != 0
    ]
    other_expenses = [
        ReportLineItem(account_name=account.name, amount=balance)
        for account, balance in ledger_service.get_balances_by_account_type_for_period(
            db, AccountType.OTHER_EXPENSES, period_start, period_end
        )
        if balance != 0
    ]

    total_income = sum((item.amount for item in income), Decimal("0"))
    total_expenses = sum((item.amount for item in expenses), Decimal("0"))
    total_other_expenses = sum((item.amount for item in other_expenses), Decimal("0"))
    net_income = total_income - total_expenses - total_other_expenses

    return ProfitAndLossResponse(
        year=year,
        income=income,
        expenses=expenses,
        other_expenses=other_expenses,
        net_income=net_income,
    )


def generate_budget_report(db: Session, year: int) -> BudgetReportResponse:
    """
    For each CONFIRMED (or REVISED -- historically still relevant)
    Budget whose period overlaps the given year, compute achieved
    figures via budget_service.compute_achieved.
    """
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)

    budgets = (
        db.query(Budget)
        .filter(
            Budget.status.in_([BudgetStatus.CONFIRMED, BudgetStatus.REVISED]),
            Budget.period_start <= year_end,
            Budget.period_end >= year_start,
        )
        .order_by(Budget.id)
        .all()
    )

    rows = []
    for budget in budgets:
        achieved = budget_service.compute_achieved(db, budget.id)
        rows.append(BudgetReportRow(
            budget_id=budget.id,
            budget_name=budget.name,
            committed_amount=budget.committed_amount,
            achieved_amount=achieved["achieved_amount"],
            achieved_percentage=achieved["achieved_percentage"],
        ))

    return BudgetReportResponse(rows=rows)
