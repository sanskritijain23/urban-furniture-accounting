from pydantic import BaseModel

from app.models.enums import JournalType
from app.schemas.common import ORMBase


class JournalBase(BaseModel):
    name: str
    type: JournalType
    default_account_id: int


class JournalCreate(JournalBase):
    pass


class JournalResponse(JournalBase, ORMBase):
    id: int
