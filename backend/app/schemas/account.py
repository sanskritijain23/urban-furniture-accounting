from typing import Optional
from pydantic import BaseModel

from app.models.enums import AccountType, AccountStatus
from app.schemas.common import ORMBase


class AccountBase(BaseModel):
    name: str
    type: AccountType


class AccountCreate(AccountBase):
    pass


class AccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AccountType] = None
    status: Optional[AccountStatus] = None


class AccountResponse(AccountBase, ORMBase):
    id: int
    status: AccountStatus
