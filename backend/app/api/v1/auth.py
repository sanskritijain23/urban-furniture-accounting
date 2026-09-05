"""
Auth routes: login, public signup, admin-only user creation.

Three user-creation paths (audited requirement):
    POST /auth/signup           -> always creates role=accountant
    POST /users (admin only)    -> creates role=admin or accountant
    (Contact creation auto-creates role=contact — see contacts.py)
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, SignupRequest, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """TODO: verify login_id + password (app.auth.password), issue JWT (app.auth.jwt_handler)."""
    raise NotImplementedError


@router.post("/signup", response_model=UserResponse)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """TODO: create a User with role=accountant. Validate login_id/email
    uniqueness and password complexity before persisting."""
    raise NotImplementedError
