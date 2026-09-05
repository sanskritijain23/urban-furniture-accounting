from decimal import Decimal
from typing import List
from pydantic import BaseModel


class ReportLineItem(BaseModel):
    account_name: str
    amount: Decimal


class BalanceSheetResponse(BaseModel):
    """TODO (report_service.py): populate from posted JournalEntryLines
    grouped by Account.type, filtered by the requested year."""
    year: int
    assets: List[ReportLineItem] = []
    liabilities: List[ReportLineItem] = []
    total_assets: Decimal = Decimal("0")
    total_liabilities: Decimal = Decimal("0")


class ProfitAndLossResponse(BaseModel):
    """TODO (report_service.py): Income - Expenses = Net Income."""
    year: int
    income: List[ReportLineItem] = []
    expenses: List[ReportLineItem] = []
    net_income: Decimal = Decimal("0")


class BudgetReportRow(BaseModel):
    budget_id: int
    budget_name: str
    committed_amount: Decimal
    achieved_amount: Decimal
    achieved_percentage: Decimal


class BudgetReportResponse(BaseModel):
    """TODO (budget_service.py / report_service.py): aggregate all
    Confirmed budgets for the requested period."""
    rows: List[BudgetReportRow] = []
