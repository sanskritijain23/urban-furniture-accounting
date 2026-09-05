"""
User model.

Three creation paths are supported by the approved architecture
(see docs/workflows.md):
  1. Admin-only "Create User" form -> role = admin or accountant
  2. Public Sign-Up page -> always creates role = accountant
  3. Adding a Contact in Contact Master -> auto-creates role = contact,
     linked via contact_id

Owned by: Database Developer (schema). Backend Developer owns the
Pydantic schemas and auth logic that populate this model.
"""
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    # Required, unique. Business rule (see docs/api-documentation.md):
    # 6-12 chars, unique across all users.
    login_id = Column(String(12), unique=True, nullable=False, index=True)

    # Required, unique.
    email = Column(String(255), unique=True, nullable=False, index=True)

    # Hashed password only — never store plaintext.
    # Complexity rule: upper + lower + special char, 8+ chars (enforced
    # in schemas/services, not at the DB layer).
    password_hash = Column(String(255), nullable=False)

    name = Column(String(255), nullable=True)

    role = Column(Enum(UserRole), nullable=False, default=UserRole.ACCOUNTANT)

    # Only populated when role == CONTACT. Links back to the Contact
    # record this login was auto-created for.
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contact = relationship("Contact", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} login_id={self.login_id} role={self.role}>"
