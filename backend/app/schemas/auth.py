"""
Auth-related schemas: login, token, signup, admin user creation.

Business rules enforced here (DB-independent validation only —
login_id/email *uniqueness* can't be checked by Pydantic alone and is
enforced in app.services.auth_service against the database):
  - login_id: 6-12 characters
  - email: valid email format (EmailStr)
  - password: must contain uppercase, lowercase, special char, 8+ chars
"""
from typing import Optional

from pydantic import BaseModel, EmailStr, field_validator

from app.auth.password import is_password_complex
from app.models.enums import UserRole

LOGIN_ID_MIN_LEN = 6
LOGIN_ID_MAX_LEN = 12


def _validate_login_id(value: str) -> str:
    value = value.strip()
    if not (LOGIN_ID_MIN_LEN <= len(value) <= LOGIN_ID_MAX_LEN):
        raise ValueError(
            f"login_id must be between {LOGIN_ID_MIN_LEN} and "
            f"{LOGIN_ID_MAX_LEN} characters"
        )
    if not value.isalnum():
        raise ValueError("login_id may only contain letters and numbers")
    return value


def _validate_password(value: str) -> str:
    if not is_password_complex(value):
        raise ValueError(
            "password must be at least 8 characters and include an "
            "uppercase letter, a lowercase letter, and a special character"
        )
    return value


class LoginRequest(BaseModel):
    login_id: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class SignupRequest(BaseModel):
    """Public sign-up. Always results in role=accountant — enforced in
    the service layer, never accepted from the client."""
    login_id: str
    email: EmailStr
    password: str
    name: Optional[str] = None

    @field_validator("login_id")
    @classmethod
    def check_login_id(cls, v: str) -> str:
        return _validate_login_id(v)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return _validate_password(v)


class AdminCreateUserRequest(BaseModel):
    """Admin-only 'Create User' form. Role is restricted to admin or
    accountant (never 'contact' — contact logins are only ever
    auto-created via Contact Master)."""
    login_id: str
    email: EmailStr
    password: str
    name: Optional[str] = None
    role: UserRole

    @field_validator("login_id")
    @classmethod
    def check_login_id(cls, v: str) -> str:
        return _validate_login_id(v)

    @field_validator("password")
    @classmethod
    def check_password(cls, v: str) -> str:
        return _validate_password(v)

    @field_validator("role")
    @classmethod
    def check_role(cls, v: UserRole) -> UserRole:
        if v not in (UserRole.ADMIN, UserRole.ACCOUNTANT):
            raise ValueError("role must be 'admin' or 'accountant'")
        return v


class UserResponse(BaseModel):
    id: int
    login_id: str
    email: EmailStr
    name: Optional[str] = None
    role: UserRole

    class Config:
        from_attributes = True
