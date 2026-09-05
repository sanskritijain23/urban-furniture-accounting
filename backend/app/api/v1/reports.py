"""
Financial report routes: Balance Sheet, Profit & Loss, Budget Report.
All figures are read-only aggregations delegated to
app.services.report_service, which itself reads via ledger_service.
No accounting/debit-credit logic lives in this route module.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.report import BalanceSheetResponse, ProfitAndLossResponse, BudgetReportResponse
from app.services import report_service

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/balance-sheet", response_model=BalanceSheetResponse)
def balance_sheet(year: int = Query(...), db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/profit-loss", response_model=ProfitAndLossResponse)
def profit_and_loss(year: int = Query(...), db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/budget", response_model=BudgetReportResponse)
def budget_report(year: int = Query(...), db: Session = Depends(get_db)):
    raise NotImplementedError
