"""
Contact master routes. Creating a Contact may auto-create a linked
User with role=contact (see docs/workflows.md) so that person can log
into the restricted Contact Portal.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, require_role
from app.core.database import get_db
from app.schemas.contact import ContactCreate, ContactUpdate, ContactResponse, ContactCreateResponse
from app.services import contact_service

router = APIRouter(
    prefix="/contacts",
    tags=["contacts"],
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)


@router.get("/", response_model=list[ContactResponse])
def list_contacts(db: Session = Depends(get_db)):
    """Supports both List and Kanban views on the frontend from the same data."""
    return contact_service.list_contacts(db)


@router.post("/", response_model=ContactCreateResponse, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, db: Session = Depends(get_db)):
    """Persists the Contact, then auto-creates a linked User(role=contact)
    unless a user with that email already exists."""
    try:
        contact, login_id, temp_password = contact_service.create_contact(db, payload.model_dump())
    except contact_service.DuplicateContactEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))

    return ContactCreateResponse(
        **ContactResponse.model_validate(contact).model_dump(),
        provisioned_login_id=login_id,
        temporary_password=temp_password,
    )


@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    try:
        return contact_service.get_contact(db, contact_id)
    except contact_service.ContactNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")


@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, payload: ContactUpdate, db: Session = Depends(get_db)):
    try:
        return contact_service.update_contact(
            db, contact_id, payload.model_dump(exclude_unset=True)
        )
    except contact_service.ContactNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
    except contact_service.DuplicateContactEmailError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    try:
        contact_service.delete_contact(db, contact_id)
    except contact_service.ContactNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contact not found")
