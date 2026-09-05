from decimal import Decimal
from typing import List
from pydantic import BaseModel


class ReportLineItem(BaseModel):
    account_name: str
    amount: Decimal


class BalanceSheetResponse(BaseModel):
    """Populated from posted JournalEntryLines grouped by Account.type,
    as a cumulative snapshot as of Dec 31 of the requested year."""
    year: int
    assets: List[ReportLineItem] = []
    liabilities: List[ReportLineItem] = []
    capital: List[ReportLineItem] = []
    total_assets: Decimal = Decimal("0")
    total_liabilities: Decimal = Decimal("0")
    total_capital: Decimal = Decimal("0")


class ProfitAndLossResponse(BaseModel):
    """Income - Expenses - Other Expenses = Net Income, strictly within
    the requested calendar year."""
    year: int
    income: List[ReportLineItem] = []
    expenses: List[ReportLineItem] = []
    other_expenses: List[ReportLineItem] = []
    net_income: Decimal = Decimal("0")


class BudgetReportRow(BaseModel):
    budget_id: int
    budget_name: str
    committed_amount: Decimal
    achieved_amount: Decimal
    achieved_percentage: Decimal


class BudgetReportResponse(BaseModel):
    """Aggregates all Confirmed/Revised budgets overlapping the
    requested year."""
    rows: List[BudgetReportRow] = []
