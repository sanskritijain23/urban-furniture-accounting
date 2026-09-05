import secrets
import uuid

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.password import hash_password
from app.models.contact import Contact
from app.models.enums import UserRole
from app.models.user import User
from app.services.auth_service import get_user_by_login_id, get_user_by_email


class DuplicateContactEmailError(Exception):
    pass


class ContactNotFoundError(Exception):
    pass


def _generate_unique_login_id(db: Session, max_attempts: int = 5) -> str:
    for _ in range(max_attempts):
        candidate = "c" + uuid.uuid4().hex[:9]
        if get_user_by_login_id(db, candidate) is None:
            return candidate
    raise RuntimeError("Could not generate a unique login_id")


def _generate_temp_password() -> str:
    return "Aa1!" + secrets.token_urlsafe(8)


def list_contacts(db: Session) -> list[Contact]:
    return db.query(Contact).order_by(Contact.id).all()


def get_contact(db: Session, contact_id: int) -> Contact:
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if contact is None:
        raise ContactNotFoundError(f"Contact {contact_id} not found")
    return contact


def create_contact(db: Session, data: dict) -> tuple[Contact, str | None, str | None]:
    """
    Returns (contact, provisioned_login_id, temporary_password).
    provisioned_login_id/temporary_password are None if auto-provisioning
    was skipped (e.g. the contact's email is already tied to an existing
    login).
    """
    existing = db.query(Contact).filter(Contact.email == data["email"]).first()
    if existing is not None:
        raise DuplicateContactEmailError(f"email '{data['email']}' is already registered")

    contact = Contact(**data)
    db.add(contact)
    db.flush()  # get contact.id without committing yet

    provisioned_login_id: str | None = None
    temp_password: str | None = None

    if get_user_by_email(db, contact.email) is None:
        provisioned_login_id = _generate_unique_login_id(db)
        temp_password = _generate_temp_password()
        contact_user = User(
            login_id=provisioned_login_id,
            email=contact.email,
            password_hash=hash_password(temp_password),
            name=contact.name,
            role=UserRole.CONTACT,
            contact_id=contact.id,
        )
        db.add(contact_user)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateContactEmailError(f"email '{data['email']}' is already registered") from exc

    db.refresh(contact)
    return contact, provisioned_login_id, temp_password


def update_contact(db: Session, contact_id: int, data: dict) -> Contact:
    contact = get_contact(db, contact_id)

    new_email = data.get("email")
    if new_email and new_email != contact.email:
        existing = db.query(Contact).filter(Contact.email == new_email).first()
        if existing is not None:
            raise DuplicateContactEmailError(f"email '{new_email}' is already registered")

    for field, value in data.items():
        if value is not None:
            setattr(contact, field, value)

    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateContactEmailError("email is already registered") from exc

    db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int) -> None:
    contact = get_contact(db, contact_id)

    linked_user = db.query(User).filter(User.contact_id == contact.id).first()
    if linked_user is not None:
        db.delete(linked_user)

    db.delete(contact)
    db.commit()
