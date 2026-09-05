
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.auth.permissions import ADMIN_ONLY, require_role
from app.core.database import get_db
from app.models.user import User
from app.schemas.auth import AdminCreateUserRequest, UserResponse
from app.services import auth_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)):
    """Any authenticated user (admin/accountant/contact) can read their
    own profile. This is the minimal 'prove the JWT works' endpoint --
    it rejects unauthenticated requests but applies no role check."""
    return current_user


@router.post(
    "/",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role(*ADMIN_ONLY))],
)
def create_user(payload: AdminCreateUserRequest, db: Session = Depends(get_db)):
    """Admin-only 'Create User' form. payload.role is restricted to
    ADMIN or ACCOUNTANT at the schema layer (CONTACT is rejected with a
    422 before this handler ever runs)."""
    try:
        user = auth_service.create_admin_managed_user(
            db, payload.login_id, payload.email, payload.password, payload.name, payload.role
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


@router.get("/", response_model=list[UserResponse], dependencies=[Depends(require_role(*ADMIN_ONLY))])
def list_users(db: Session = Depends(get_db)):
    """Admin-only. Demonstrates role-based access control end to end:
    unauthenticated -> 401, authenticated non-admin -> 403, admin -> 200."""
    return db.query(User).all()
