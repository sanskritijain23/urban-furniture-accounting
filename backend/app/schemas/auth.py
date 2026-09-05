"""
Auth-related schemas: login, token, signup, admin user creation.

TODO (business logic, not yet implemented):
  - login_id: unique, 6-12 characters
  - email: unique
  - password: must contain uppercase, lowercase, special char, 8+ chars
These validators should be added with `field_validator` before this
schema is used in a real endpoint.
"""
from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.enums import UserRole


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


class AdminCreateUserRequest(BaseModel):
    """Admin-only 'Create User' form. Role is restricted to admin or
    accountant (never 'contact' — contact logins are only ever
    auto-created via Contact Master)."""
    login_id: str
    email: EmailStr
    password: str
    name: Optional[str] = None
    role: UserRole  # TODO: validate role in {ADMIN, ACCOUNTANT} only


class UserResponse(BaseModel):
    id: int
    login_id: str
    email: EmailStr
    name: Optional[str] = None
    role: UserRole

    class Config:
        from_attributes = True
