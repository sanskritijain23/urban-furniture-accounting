from sqlalchemy import Column, Integer, String, Enum, DateTime, func

from app.core.database import Base
from app.models.enums import AccountType, AccountStatus


class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), unique=True, nullable=False)
    type = Column(Enum(AccountType), nullable=False)
    status = Column(Enum(AccountStatus), nullable=False, default=AccountStatus.CONFIRMED)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self) -> str:
        return f"<Account id={self.id} name={self.name} type={self.type}>"
