from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel

from app.models.enums import JournalEntryStatus, JournalEntrySourceType
from app.schemas.common import ORMBase


class JournalEntryLineCreate(BaseModel):
    account_id: int
    partner_id: Optional[int] = None
    debit: Decimal = Decimal("0")
    credit: Decimal = Decimal("0")
    # TODO (accounting_engine.py): validate exactly one of debit/credit
    # is non-zero per line.


class JournalEntryLineResponse(ORMBase):
    id: int
    account_id: int
    partner_id: Optional[int] = None
    debit: Decimal
    credit: Decimal


class ManualJournalEntryCreate(BaseModel):
    """Used by the manual Journal Entry screen (MUST HAVE).
    TODO (accounting_engine.py): reject if SUM(debit) != SUM(credit)
    when status is being set to POSTED."""
    journal_id: int
    accounting_date: date
    reference_no: Optional[str] = None
    lines: List[JournalEntryLineCreate]


class JournalEntryResponse(ORMBase):
    id: int
    journal_id: int
    accounting_date: date
    status: JournalEntryStatus
    source_type: JournalEntrySourceType
    source_id: Optional[int] = None
    reference_no: Optional[str] = None
    lines: List[JournalEntryLineResponse] = []
