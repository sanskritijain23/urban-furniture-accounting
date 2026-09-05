"""
Chart of Accounts routes. Accounts are pre-configured/seeded and
generally managed via New -> Confirm -> Archived lifecycle, per the
MVP mockup.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, require_role
from app.core.database import get_db
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse
from app.services import account_service

router = APIRouter(
    prefix="/accounts",
    tags=["chart-of-accounts"],
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)


@router.get("/", response_model=list[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    return account_service.list_accounts(db)


@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    try:
        return account_service.create_account(db, payload.model_dump())
    except account_service.DuplicateAccountNameError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: int, db: Session = Depends(get_db)):
    try:
        return account_service.get_account(db, account_id)
    except account_service.AccountNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)):
    """Supports Confirm / Archive status transitions via the same PUT
    endpoint (send just {"status": "archived"})."""
    try:
        return account_service.update_account(
            db, account_id, payload.model_dump(exclude_unset=True)
        )
    except account_service.AccountNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    except account_service.DuplicateAccountNameError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
