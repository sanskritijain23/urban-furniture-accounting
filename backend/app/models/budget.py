"""
Budget.

Lifecycle (audited requirement, MUST HAVE):
    Draft -> Confirmed -> Revised -> Cancelled

Revising a Confirmed budget creates a NEW linked Budget record (does
not mutate the original in place) — `revision_of_id` is a
self-referential FK pointing back to the original/previous version.

The following are NOT stored columns — they are computed at read time
by app/services/budget_service.py from CustomerInvoiceLine /
VendorBillLine rows sharing the same analytic_account_id within the
budget's period:
    - achieved_amount
    - achieved_percentage  (= achieved_amount / committed_amount * 100)
    - amount_to_achieve    (= committed_amount - achieved_amount)

Exceeding committed_amount is a NON-BLOCKING warning surfaced at PO /
Vendor Bill confirmation time (see purchase_service.py), never a hard
validation error.

Owned by: Database Developer.
"""
from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import BudgetStatus


class Budget(Base):
    __tablename__ = "budgets"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(150), nullable=False)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)

    responsible_id = Column(Integer, ForeignKey("contacts.id"), nullable=True)
    analytic_account_id = Column(Integer, ForeignKey("analytic_accounts.id"), nullable=False)

    committed_amount = Column(Numeric(12, 2), nullable=False)

    status = Column(Enum(BudgetStatus), nullable=False, default=BudgetStatus.DRAFT)

    # Self-referential link for the Revise workflow.
    revision_of_id = Column(Integer, ForeignKey("budgets.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    responsible = relationship("Contact")
    analytic_account = relationship("AnalyticAccount", back_populates="budgets")
    revision_of = relationship("Budget", remote_side=[id])

    def __repr__(self) -> str:
        return f"<Budget id={self.id} name={self.name} status={self.status}>"
