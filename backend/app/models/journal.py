
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import JournalType


class Journal(Base):
    __tablename__ = "journals"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    type = Column(Enum(JournalType), nullable=False)

    default_account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    default_account = relationship("Account")
    journal_entries = relationship("JournalEntry", back_populates="journal")

    def __repr__(self) -> str:
        return f"<Journal id={self.id} name={self.name} type={self.type}>"
