
from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import DocumentStatus, PaymentType, PaymentVia, JournalEntrySourceType


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)

    payment_type = Column(Enum(PaymentType), nullable=False)  # send / receive
    payment_via = Column(Enum(PaymentVia), nullable=False)    # cash / bank

    date = Column(Date, nullable=False)
    partner_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)

    amount = Column(Numeric(12, 2), nullable=False)
    note = Column(String(500), nullable=True)

    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.DRAFT)

    # Polymorphic reference: which Bill or Invoice this payment settles.
    source_type = Column(Enum(JournalEntrySourceType), nullable=False)  # VENDOR_BILL or CUSTOMER_INVOICE
    source_id = Column(Integer, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    partner = relationship("Contact")

    def __repr__(self) -> str:
        return f"<Payment id={self.id} type={self.payment_type} amount={self.amount}>"
