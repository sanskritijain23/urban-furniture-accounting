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
    role=contact — handled in the service layer, not here. TODO."""
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
