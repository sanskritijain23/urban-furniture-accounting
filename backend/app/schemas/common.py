"""
Shared Pydantic base classes/config for all schemas.

IMPORTANT (approved correction): Pydantic schemas are owned by the
BACKEND developer, not the Database developer. They are API request/
response contracts and may legitimately diverge from the exact
SQLAlchemy column layout (e.g. nested objects, computed fields).
"""
from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ORMBase(BaseModel):
    """Base class for response schemas that read from SQLAlchemy objects."""
    model_config = ConfigDict(from_attributes=True)


class TimestampMixin(BaseModel):
    created_at: Optional[datetime] = None
