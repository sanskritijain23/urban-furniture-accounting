from typing import Optional
from pydantic import BaseModel

from app.models.enums import JournalType
from app.schemas.common import ORMBase


class JournalBase(BaseModel):
    name: str
    type: JournalType
    default_account_id: int


class JournalCreate(JournalBase):
    pass


class JournalUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[JournalType] = None
    default_account_id: Optional[int] = None


class JournalResponse(JournalBase, ORMBase):
    id: int
