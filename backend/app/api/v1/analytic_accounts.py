"""
Analytic Account routes. Supports List + Kanban views on the frontend
(same data). Referenced per-line-item on PO/SO/Bill/Invoice, and by Budget.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, require_role
from app.core.database import get_db
from app.schemas.analytic_account import (
    AnalyticAccountCreate, AnalyticAccountUpdate, AnalyticAccountResponse,
)
from app.services import analytic_account_service

router = APIRouter(
    prefix="/analytic-accounts",
    tags=["analytic-accounts"],
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)


@router.get("/", response_model=list[AnalyticAccountResponse])
def list_analytic_accounts(db: Session = Depends(get_db)):
    return analytic_account_service.list_analytic_accounts(db)


@router.post("/", response_model=AnalyticAccountResponse, status_code=status.HTTP_201_CREATED)
def create_analytic_account(payload: AnalyticAccountCreate, db: Session = Depends(get_db)):
    try:
        return analytic_account_service.create_analytic_account(db, payload.model_dump())
    except analytic_account_service.DuplicateAnalyticAccountNameError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/{analytic_account_id}", response_model=AnalyticAccountResponse)
def get_analytic_account(analytic_account_id: int, db: Session = Depends(get_db)):
    try:
        return analytic_account_service.get_analytic_account(db, analytic_account_id)
    except analytic_account_service.AnalyticAccountNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analytic account not found")


@router.put("/{analytic_account_id}", response_model=AnalyticAccountResponse)
def update_analytic_account(
    analytic_account_id: int, payload: AnalyticAccountUpdate, db: Session = Depends(get_db)
):
    try:
        return analytic_account_service.update_analytic_account(
            db, analytic_account_id, payload.model_dump(exclude_unset=True)
        )
    except analytic_account_service.AnalyticAccountNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analytic account not found")
    except analytic_account_service.DuplicateAnalyticAccountNameError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete("/{analytic_account_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_analytic_account(analytic_account_id: int, db: Session = Depends(get_db)):
    try:
        analytic_account_service.delete_analytic_account(db, analytic_account_id)
    except analytic_account_service.AnalyticAccountNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Analytic account not found")
    except analytic_account_service.AnalyticAccountInUseError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
