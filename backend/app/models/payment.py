"""
Payment — settles a VendorBill or CustomerInvoice.

IMPORTANT (audited rule): every confirmed Payment creates its OWN
Journal Entry via app/services/accounting_engine.py, SEPARATE from the
Journal Entry created when the Bill/Invoice was confirmed:

    Bill Payment (Send):
        Debit  Creditors / Accounts Payable
        Credit Bank or Cash (per payment_via)

    Invoice Payment (Receive):
        Debit  Bank or Cash (per payment_via)
        Credit Debtors / Accounts Receivable

`source_type` + `source_id` is a lightweight polymorphic reference
back to the VendorBill or CustomerInvoice being paid (mirrors the
pattern used on JournalEntry).

amount defaults to the bill/invoice's remaining Amount Due but is
user-editable (partial payments allowed -> payment_status = PARTIAL).

Owned by: Database Developer.
"""
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
