"""
Financial report routes: Balance Sheet, Profit & Loss, Budget Report.
All figures are read-only aggregations delegated to
app.services.report_service, which itself reads via ledger_service.
No accounting/debit-credit logic lives in this route module.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, require_role
from app.core.database import get_db
from app.schemas.report import BalanceSheetResponse, ProfitAndLossResponse, BudgetReportResponse
from app.services import report_service

router = APIRouter(
    prefix="/reports",
    tags=["reports"],
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)


@router.get("/balance-sheet", response_model=BalanceSheetResponse)
def balance_sheet(year: int = Query(...), db: Session = Depends(get_db)):
    return report_service.generate_balance_sheet(db, year)


@router.get("/profit-loss", response_model=ProfitAndLossResponse)
def profit_and_loss(year: int = Query(...), db: Session = Depends(get_db)):
    return report_service.generate_profit_and_loss(db, year)


@router.get("/budget", response_model=BudgetReportResponse)
def budget_report(year: int = Query(...), db: Session = Depends(get_db)):
    return report_service.generate_budget_report(db, year)
