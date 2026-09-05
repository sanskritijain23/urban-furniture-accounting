from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

from app.models.enums import BudgetStatus
from app.schemas.common import ORMBase


class BudgetCreate(BaseModel):
    name: str
    period_start: date
    period_end: date
    responsible_id: Optional[int] = None
    analytic_account_id: int
    committed_amount: Decimal


class BudgetReviseRequest(BaseModel):
    """Creates a NEW Budget record linked via revision_of_id, per the
    audited Draft -> Confirmed -> Revised -> Cancelled lifecycle.
    See app.services.budget_service.revise_budget for the implementation."""
    new_committed_amount: Decimal


class BudgetResponse(ORMBase):
    id: int
    name: str
    period_start: date
    period_end: date
    responsible_id: Optional[int] = None
    analytic_account_id: int
    committed_amount: Decimal
    status: BudgetStatus
    revision_of_id: Optional[int] = None

    # Computed fields (NOT stored columns) — populated by
    # budget_service.py, only meaningful once status == CONFIRMED.
    achieved_amount: Optional[Decimal] = None
    achieved_percentage: Optional[Decimal] = None
    amount_to_achieve: Optional[Decimal] = None
