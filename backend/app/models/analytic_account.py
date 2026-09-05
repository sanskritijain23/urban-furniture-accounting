from sqlalchemy import Column, Integer, String, Enum, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import AnalyticAccountType


class AnalyticAccount(Base):
    __tablename__ = "analytic_accounts"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), unique=True, nullable=False)
    type = Column(Enum(AnalyticAccountType), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    budgets = relationship("Budget", back_populates="analytic_account")

    def __repr__(self) -> str:
        return f"<AnalyticAccount id={self.id} name={self.name} type={self.type}>"
