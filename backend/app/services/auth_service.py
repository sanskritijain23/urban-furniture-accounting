"""
Auth service — DB-backed business logic behind the auth routes.

Kept separate from app/api/v1/auth.py and users.py so the HTTP layer
stays thin (parse request -> call service -> map result/errors to a
response) and so this logic is unit-testable without a running app.

Owned by: Backend Developer (see backend/app/services/ in
CONTRIBUTING.md ownership table).
"""
from sqlalchemy.orm import Session

from app.auth.password import hash_password, verify_password
from app.models.enums import UserRole
from app.models.user import User


class DuplicateLoginIdError(Exception):
    """Raised when login_id already exists for another user."""


class DuplicateEmailError(Exception):
    """Raised when email already exists for another user."""


class InvalidCredentialsError(Exception):
    """Raised when login_id/password do not match an active user."""


def get_user_by_login_id(db: Session, login_id: str) -> User | None:
    return db.query(User).filter(User.login_id == login_id).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def _ensure_unique(db: Session, login_id: str, email: str) -> None:
    if get_user_by_login_id(db, login_id) is not None:
        raise DuplicateLoginIdError(f"login_id '{login_id}' is already taken")
    if get_user_by_email(db, email) is not None:
        raise DuplicateEmailError(f"email '{email}' is already registered")


def create_signup_user(db: Session, login_id: str, email: str, password: str, name: str | None) -> User:
    """Public sign-up path. Always creates role=accountant regardless of
    any role value that might sneak in upstream -- role is hardcoded
    here, not read from the caller, as the last line of defense."""
    _ensure_unique(db, login_id, email)

    user = User(
        login_id=login_id,
        email=email,
        password_hash=hash_password(password),
        name=name,
        role=UserRole.ACCOUNTANT,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def create_admin_managed_user(
    db: Session, login_id: str, email: str, password: str, name: str | None, role: UserRole
) -> User:
    """Admin-only 'Create User' path. Caller (the route, guarded by
    require_role(ADMIN_ONLY)) has already confirmed the requester is an
    admin; the schema layer has already restricted `role` to
    admin/accountant."""
    _ensure_unique(db, login_id, email)

    user = User(
        login_id=login_id,
        email=email,
        password_hash=hash_password(password),
        name=name,
        role=role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, login_id: str, password: str) -> User:
    user = get_user_by_login_id(db, login_id)
    if user is None or not verify_password(password, user.password_hash):
        raise InvalidCredentialsError("Invalid login_id or password")
    return user
