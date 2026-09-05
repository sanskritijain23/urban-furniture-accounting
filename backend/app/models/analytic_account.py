"""
Analytic Account — a financial marker used to group income/expense by
project, department, or business unit. Assigned per LINE ITEM on PO /
SO / Vendor Bill / Customer Invoice (audited requirement), and
referenced by Budget for planned-vs-actual tracking.

Owned by: Database Developer.
"""
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
