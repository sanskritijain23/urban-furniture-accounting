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
    # Exactly-one-of-debit/credit-per-line is enforced in
    # accounting_engine.create_journal_entry.


class JournalEntryLineResponse(ORMBase):
    id: int
    account_id: int
    partner_id: Optional[int] = None
    debit: Decimal
    credit: Decimal


class ManualJournalEntryCreate(BaseModel):
    """Used by the manual Journal Entry screen (MUST HAVE).
    Rejected by accounting_engine.create_journal_entry if SUM(debit) !=
    SUM(credit) when status is being set to POSTED."""
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
