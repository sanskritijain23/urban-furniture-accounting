from typing import Optional
from pydantic import BaseModel, EmailStr

from app.models.enums import ContactType
from app.schemas.common import ORMBase


class ContactBase(BaseModel):
    name: str
    type: ContactType
    email: EmailStr
    mobile: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_pincode: Optional[str] = None
    profile_image_url: Optional[str] = None


class ContactCreate(ContactBase):
    """Creating a Contact may trigger an auto-created User login with
    role=contact -- see app.services.contact_service.create_contact."""
    pass


class ContactUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ContactType] = None
    email: Optional[EmailStr] = None
    mobile: Optional[str] = None
    address_city: Optional[str] = None
    address_state: Optional[str] = None
    address_pincode: Optional[str] = None
    profile_image_url: Optional[str] = None


class ContactResponse(ContactBase, ORMBase):
    id: int


class ContactCreateResponse(ContactResponse):
    """Returned only from POST /contacts/. If a contact-role login was
    auto-provisioned, its one-time credentials are included here so an
    admin/accountant can relay them to the contact — they are never
    returned again from GET/list endpoints."""
    provisioned_login_id: Optional[str] = None
    temporary_password: Optional[str] = None
