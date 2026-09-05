"""
Shared FastAPI dependencies used across route modules
(e.g. get_current_user, drawn from the Authorization header).

Implements get_current_user: decodes the bearer token via
app.auth.jwt_handler, loads the corresponding User from the DB, and
raises 401 for any invalid/expired token or missing/inactive user.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.auth.jwt_handler import TokenError, decode_access_token
from app.core.database import get_db
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = decode_access_token(token)
    except TokenError:
        raise CREDENTIALS_EXCEPTION

    login_id: str | None = payload.get("sub")
    if login_id is None:
        raise CREDENTIALS_EXCEPTION

    user = db.query(User).filter(User.login_id == login_id).first()
    if user is None:
        raise CREDENTIALS_EXCEPTION
    if not getattr(user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Account is inactive"
        )

    return user
