"""
Chart of Accounts routes. Accounts are pre-configured/seeded and
generally managed via New -> Confirm -> Archived lifecycle, per the
MVP mockup.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.account import AccountCreate, AccountUpdate, AccountResponse

router = APIRouter(prefix="/accounts", tags=["chart-of-accounts"])


@router.get("/", response_model=list[AccountResponse])
def list_accounts(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/", response_model=AccountResponse)
def create_account(payload: AccountCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.put("/{account_id}", response_model=AccountResponse)
def update_account(account_id: int, payload: AccountUpdate, db: Session = Depends(get_db)):
    """TODO: supports Confirm / Archive status transitions."""
    raise NotImplementedError
