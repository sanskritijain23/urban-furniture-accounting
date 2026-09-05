from pydantic import BaseModel

from app.models.enums import AnalyticAccountType
from app.schemas.common import ORMBase


class AnalyticAccountCreate(BaseModel):
    name: str
    type: AnalyticAccountType


class AnalyticAccountResponse(AnalyticAccountCreate, ORMBase):
    id: int
