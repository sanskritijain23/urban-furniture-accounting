"""
Customer Invoice + CustomerInvoiceLine.

IMPORTANT (audited rule): confirming a Customer Invoice DOES create a
Journal Entry via app/services/accounting_engine.py:
    Debit  Debtors / Accounts Receivable (customer)
    Credit Sales Income (per line's account)

invoice_no is auto-generated (format: INV/2026/0001) by
app/services/sequence_service.py. `reference` is a separate free-text
field, distinct from invoice_no.

Owned by: Database Developer.
"""
from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import DocumentStatus, PaymentStatus


class CustomerInvoice(Base):
    __tablename__ = "customer_invoices"

    id = Column(Integer, primary_key=True, index=True)

    invoice_no = Column(String(50), unique=True, nullable=False)
    reference = Column(String(150), nullable=True)  # free-text, separate from invoice_no

    customer_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=True)

    invoice_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)

    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.DRAFT)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.NOT_PAID)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Contact")
    sales_order = relationship("SalesOrder", back_populates="customer_invoice")
    lines = relationship("CustomerInvoiceLine", back_populates="customer_invoice",
                          cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<CustomerInvoice id={self.id} invoice_no={self.invoice_no} status={self.status}>"


class CustomerInvoiceLine(Base):
    __tablename__ = "customer_invoice_lines"

    id = Column(Integer, primary_key=True, index=True)

    customer_invoice_id = Column(Integer, ForeignKey("customer_invoices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    # Defaults to the "Sales Income" Chart of Accounts entry; editable
    # per line.
    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    analytic_account_id = Column(Integer, ForeignKey("analytic_accounts.id"), nullable=True)

    qty = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)

    customer_invoice = relationship("CustomerInvoice", back_populates="lines")
    product = relationship("Product")
    account = relationship("Account")
    analytic_account = relationship("AnalyticAccount")
