from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, require_role
from app.core.database import get_db
from app.schemas.journal import JournalCreate, JournalUpdate, JournalResponse
from app.services import journal_service

router = APIRouter(
    prefix="/journals",
    tags=["journals"],
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)


@router.get("/", response_model=list[JournalResponse])
def list_journals(db: Session = Depends(get_db)):
    return journal_service.list_journals(db)


@router.post("/", response_model=JournalResponse, status_code=status.HTTP_201_CREATED)
def create_journal(payload: JournalCreate, db: Session = Depends(get_db)):
    try:
        return journal_service.create_journal(db, payload.model_dump())
    except journal_service.InvalidDefaultAccountError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{journal_id}", response_model=JournalResponse)
def get_journal(journal_id: int, db: Session = Depends(get_db)):
    try:
        return journal_service.get_journal(db, journal_id)
    except journal_service.JournalNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")


@router.put("/{journal_id}", response_model=JournalResponse)
def update_journal(journal_id: int, payload: JournalUpdate, db: Session = Depends(get_db)):
    try:
        return journal_service.update_journal(
            db, journal_id, payload.model_dump(exclude_unset=True)
        )
    except journal_service.JournalNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Journal not found")
    except journal_service.InvalidDefaultAccountError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
