"""
Auth routes: login, public signup, admin-only user creation.

Three user-creation paths (audited requirement):
    POST /auth/signup           -> always creates role=accountant
    POST /users (admin only)    -> creates role=admin or accountant
    (Contact creation auto-creates role=contact — see contacts.py)
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.jwt_handler import create_access_token
from app.core.database import get_db
from app.schemas.auth import LoginRequest, TokenResponse, SignupRequest, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = auth_service.authenticate_user(db, payload.login_id, payload.password)
    except auth_service.InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login_id or password",
        )

    access_token = create_access_token(subject=user.login_id)
    return TokenResponse(access_token=access_token)


@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    """Public sign-up. Always creates role=accountant -- role is never
    accepted from the client (see SignupRequest, which has no role field)."""
    try:
        user = auth_service.create_signup_user(
            db, payload.login_id, payload.email, payload.password, payload.name
        )
    except auth_service.DuplicateLoginIdError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"login_id '{payload.login_id}' is already taken",
        )
    except auth_service.DuplicateEmailError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"email '{payload.email}' is already registered",
        )

    return user
