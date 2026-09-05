"""
Journal master routes (Sales / Purchase / Bank / Cash), each carrying
a Default Account used by the accounting engine.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.journal import JournalCreate, JournalResponse

router = APIRouter(prefix="/journals", tags=["journals"])


@router.get("/", response_model=list[JournalResponse])
def list_journals(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/", response_model=JournalResponse)
def create_journal(payload: JournalCreate, db: Session = Depends(get_db)):
    raise NotImplementedError
