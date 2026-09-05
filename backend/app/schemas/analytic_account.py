from typing import Optional
from pydantic import BaseModel

from app.models.enums import AnalyticAccountType
from app.schemas.common import ORMBase


class AnalyticAccountCreate(BaseModel):
    name: str
    type: AnalyticAccountType


class AnalyticAccountUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[AnalyticAccountType] = None


class AnalyticAccountResponse(AnalyticAccountCreate, ORMBase):
    id: int
