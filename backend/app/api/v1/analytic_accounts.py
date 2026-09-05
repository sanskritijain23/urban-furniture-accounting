"""
Analytic Account routes. Supports List + Kanban views on the frontend
(same data). Referenced per-line-item on PO/SO/Bill/Invoice, and by Budget.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.analytic_account import AnalyticAccountCreate, AnalyticAccountResponse

router = APIRouter(prefix="/analytic-accounts", tags=["analytic-accounts"])


@router.get("/", response_model=list[AnalyticAccountResponse])
def list_analytic_accounts(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/", response_model=AnalyticAccountResponse)
def create_analytic_account(payload: AnalyticAccountCreate, db: Session = Depends(get_db)):
    raise NotImplementedError
