"""
Shared FastAPI dependencies used across route modules
(e.g. get_current_user, drawn from the Authorization header).

TODO: implement get_current_user using app.auth.jwt_handler to decode
the bearer token and load the corresponding User from the DB.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    """TODO: decode token via app.auth.jwt_handler.decode_access_token,
    load User by id/login_id, raise 401 if invalid/expired."""
    raise NotImplementedError
