"""
Admin-only user management. This is the "Create User" screen path —
distinct from public signup (auth.py) and from the automatic contact
login creation (contacts.py).
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import AdminCreateUserRequest, UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserResponse)
def create_user(payload: AdminCreateUserRequest, db: Session = Depends(get_db)):
    """TODO: require role=admin (app.auth.permissions.ADMIN_ONLY).
    payload.role must be ADMIN or ACCOUNTANT only — reject CONTACT."""
    raise NotImplementedError


@router.get("/", response_model=list[UserResponse])
def list_users(db: Session = Depends(get_db)):
    """TODO: require role=admin."""
    raise NotImplementedError
