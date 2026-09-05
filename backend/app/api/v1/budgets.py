"""
Budget routes. Lifecycle: Draft -> Confirmed -> Revised -> Cancelled.
Achieved amount/percentage/amount-to-achieve are computed fields
(never stored), populated via app.services.budget_service.
Budget-exceeded warnings surfaced elsewhere (PO/Bill confirm) are
NON-BLOCKING and do not live in this route module.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.budget import BudgetCreate, BudgetReviseRequest, BudgetResponse
from app.services import budget_service

router = APIRouter(prefix="/budgets", tags=["budgets"])


@router.get("/", response_model=list[BudgetResponse])
def list_budgets(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/", response_model=BudgetResponse)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    """TODO: merge in computed achieved_amount/percentage/amount_to_achieve
    via budget_service.compute_achieved when status == CONFIRMED."""
    raise NotImplementedError


@router.post("/{budget_id}/confirm", response_model=BudgetResponse)
def confirm_budget(budget_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/{budget_id}/revise", response_model=BudgetResponse)
def revise_budget(budget_id: int, payload: BudgetReviseRequest, db: Session = Depends(get_db)):
    """Creates a NEW linked Budget record — see budget_service.revise_budget."""
    raise NotImplementedError


@router.post("/{budget_id}/cancel", response_model=BudgetResponse)
def cancel_budget(budget_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError
