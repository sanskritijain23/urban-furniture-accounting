"""
Journal Entries routes -- includes the MUST HAVE manual Journal Entry
creation screen, plus the read-only list of all entries (manual +
auto-generated from Vendor Bills / Customer Invoices / Payments).

IMPORTANT: this route module must NOT construct JournalEntry/Line
objects itself -- it delegates entirely to
app.services.accounting_engine.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, require_role
from app.core.database import get_db
from app.models.journal_entry import JournalEntry
from app.schemas.journal_entry import ManualJournalEntryCreate, JournalEntryResponse
from app.services import accounting_engine

router = APIRouter(
    prefix="/journal-entries",
    tags=["journal-entries"],
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)


@router.get("/", response_model=list[JournalEntryResponse])
def list_journal_entries(db: Session = Depends(get_db)):
    return db.query(JournalEntry).order_by(JournalEntry.id).all()


@router.get("/{entry_id}", response_model=JournalEntryResponse)
def get_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(JournalEntry).filter(JournalEntry.id == entry_id).first()
    if entry is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal Entry not found")
    return entry


@router.post("/", response_model=JournalEntryResponse, status_code=status.HTTP_201_CREATED)
def create_manual_journal_entry(payload: ManualJournalEntryCreate, db: Session = Depends(get_db)):
    """Delegates to accounting_engine.create_manual_journal_entry.
    Persisted as DRAFT -- use POST /{id}/post to actually post it."""
    try:
        return accounting_engine.create_manual_journal_entry(db, payload)
    except (accounting_engine.MissingJournalError, accounting_engine.InvalidLineError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/{entry_id}/post", response_model=JournalEntryResponse)
def post_journal_entry(entry_id: int, db: Session = Depends(get_db)):
    """Delegates to accounting_engine.post_journal_entry. Blocks
    (raises) if debit != credit -- see accounting_engine.UnbalancedEntryError."""
    try:
        return accounting_engine.post_journal_entry(db, entry_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    except (accounting_engine.UnbalancedEntryError, accounting_engine.InvalidLineError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
