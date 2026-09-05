from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import UserRole


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    login_id = Column(String(12), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    name = Column(String(255), nullable=True)

    role = Column(Enum(UserRole), nullable=False, default=UserRole.ACCOUNTANT)
    contact_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    contact = relationship("Contact", back_populates="user", uselist=False)

    def __repr__(self) -> str:
        return f"<User id={self.id} login_id={self.login_id} role={self.role}>"
