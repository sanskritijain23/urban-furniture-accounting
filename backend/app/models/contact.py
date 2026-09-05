from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import ContactType


class Contact(Base):
    __tablename__ = "contacts"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    type = Column(Enum(ContactType), nullable=False)

    email = Column(String(255), unique=True, nullable=False)
    mobile = Column(String(20), nullable=True)

    address_city = Column(String(100), nullable=True)
    address_state = Column(String(100), nullable=True)
    address_pincode = Column(String(20), nullable=True)

    # Simplified per hackathon scope: URL/placeholder, not a real
    # file-upload pipeline.
    profile_image_url = Column(String(500), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="contact", uselist=False)

    def __repr__(self) -> str:
        return f"<Contact id={self.id} name={self.name} type={self.type}>"
