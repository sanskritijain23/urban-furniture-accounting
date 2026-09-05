"""
JWT creation/verification.

Uses app.core.config.settings for SECRET_KEY / ALGORITHM /
ACCESS_TOKEN_EXPIRE_MINUTES — never hardcode secrets here.

Requires the `python-jose` (or `pyjwt`) package — listed in
requirements.txt.
"""
from datetime import datetime, timedelta
from typing import Optional

from app.core.config import settings


def create_access_token(subject: str, expires_delta: Optional[timedelta] = None) -> str:
    """
    TODO:
      1. Build payload: {"sub": subject, "exp": <expiry>}.
      2. Encode with jose.jwt.encode(payload, settings.SECRET_KEY,
         algorithm=settings.ALGORITHM).
    """
    raise NotImplementedError


def decode_access_token(token: str) -> dict:
    """
    TODO: jose.jwt.decode(token, settings.SECRET_KEY,
    algorithms=[settings.ALGORITHM]); raise on invalid/expired token.
    """
    raise NotImplementedError
