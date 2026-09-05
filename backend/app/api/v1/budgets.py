"""
Budget routes. Lifecycle: Draft -> Confirmed -> Revised -> Cancelled.
Achieved amount/percentage/amount-to-achieve are computed fields
(never stored), populated via app.services.budget_service.
Budget-exceeded warnings surfaced elsewhere (PO/Bill confirm) are
NON-BLOCKING and do not live in this route module.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, require_role
from app.core.database import get_db
from app.models.enums import BudgetStatus
from app.schemas.budget import BudgetCreate, BudgetReviseRequest, BudgetResponse
from app.services import budget_service

router = APIRouter(
    prefix="/budgets",
    tags=["budgets"],
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)


def _to_response(db: Session, budget) -> BudgetResponse:
    """Achieved fields are only meaningful (and only computed) once a
    budget has been confirmed at least once -- per the audited mockup
    rule that achieved fields become visible only once confirmed."""
    response = BudgetResponse.model_validate(budget)
    if budget.status in (BudgetStatus.CONFIRMED, BudgetStatus.REVISED):
        achieved = budget_service.compute_achieved(db, budget.id)
        response.achieved_amount = achieved["achieved_amount"]
        response.achieved_percentage = achieved["achieved_percentage"]
        response.amount_to_achieve = achieved["amount_to_achieve"]
    return response


@router.get("/", response_model=list[BudgetResponse])
def list_budgets(db: Session = Depends(get_db)):
    return [_to_response(db, b) for b in budget_service.list_budgets(db)]


@router.post("/", response_model=BudgetResponse, status_code=status.HTTP_201_CREATED)
def create_budget(payload: BudgetCreate, db: Session = Depends(get_db)):
    budget = budget_service.create_budget(db, payload)
    return _to_response(db, budget)


@router.get("/{budget_id}", response_model=BudgetResponse)
def get_budget(budget_id: int, db: Session = Depends(get_db)):
    try:
        budget = budget_service.get_budget(db, budget_id)
    except budget_service.BudgetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    return _to_response(db, budget)


@router.post("/{budget_id}/confirm", response_model=BudgetResponse)
def confirm_budget(budget_id: int, db: Session = Depends(get_db)):
    try:
        budget = budget_service.confirm_budget(db, budget_id)
    except budget_service.BudgetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    except budget_service.InvalidBudgetTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return _to_response(db, budget)


@router.post("/{budget_id}/revise", response_model=BudgetResponse)
def revise_budget(budget_id: int, payload: BudgetReviseRequest, db: Session = Depends(get_db)):
    """Creates a NEW linked Budget record -- see budget_service.revise_budget."""
    try:
        revised = budget_service.revise_budget(db, budget_id, payload.new_committed_amount)
    except budget_service.BudgetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    except budget_service.InvalidBudgetTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return _to_response(db, revised)


@router.post("/{budget_id}/cancel", response_model=BudgetResponse)
def cancel_budget(budget_id: int, db: Session = Depends(get_db)):
    try:
        budget = budget_service.cancel_budget(db, budget_id)
    except budget_service.BudgetNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Budget not found")
    except budget_service.InvalidBudgetTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return _to_response(db, budget)
