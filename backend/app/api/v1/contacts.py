"""
Contact master routes. Creating a Contact may auto-create a linked
User with role=contact (see docs/workflows.md) so that person can log
into the restricted Contact Portal.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=list[ContactResponse])
def list_contacts(db: Session = Depends(get_db)):
    """TODO: supports both List and Kanban views on the frontend from the same data."""
    raise NotImplementedError


@router.post("/", response_model=ContactResponse)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    """TODO: persist Contact, then auto-create a linked User(role=contact)."""
    raise NotImplementedError


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, payload: ContactUpdate, db: Session = Depends(get_db)):
    raise NotImplementedError
