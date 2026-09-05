"""
Password hashing + complexity validation.

Requires `passlib[bcrypt]` — listed in requirements.txt.

Complexity rule (audited from MVP sign-up form):
  - 8+ characters
  - at least one uppercase, one lowercase, one special character
"""
import re

from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

PASSWORD_COMPLEXITY_REGEX = re.compile(
    r"^(?=.*[a-z])(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$"
)


def hash_password(plain_password: str) -> str:
    return pwd_context.hash(plain_password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def is_password_complex(plain_password: str) -> bool:
    """Returns True if the password meets the complexity rule above."""
    return bool(PASSWORD_COMPLEXITY_REGEX.match(plain_password))
