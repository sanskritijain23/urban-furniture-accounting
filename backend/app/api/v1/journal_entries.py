"""
Journal Entries routes — includes the MUST HAVE manual Journal Entry
creation screen, plus the read-only list of all entries (manual +
auto-generated from Vendor Bills / Customer Invoices / Payments).

IMPORTANT: this route module must NOT construct JournalEntry/Line
objects itself — it delegates entirely to
app.services.accounting_engine.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.journal_entry import ManualJournalEntryCreate, JournalEntryResponse
from app.services import accounting_engine

router = APIRouter(prefix="/journal-entries", tags=["journal-entries"])


@router.get("/", response_model=list[JournalEntryResponse])
def list_journal_entries(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{entry_id}", response_model=JournalEntryResponse)
def get_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/", response_model=JournalEntryResponse)
def create_manual_journal_entry(payload: ManualJournalEntryCreate, db: Session = Depends(get_db)):
    """Delegates to accounting_engine.create_manual_journal_entry."""
    raise NotImplementedError


@router.post("/{entry_id}/post", response_model=JournalEntryResponse)
def post_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delegates to accounting_engine.post_journal_entry. Blocks
    (raises) if debit != credit — see accounting_engine.UnbalancedEntryError."""
    raise NotImplementedError
