"""
Sales Order + SalesOrderLine.

IMPORTANT (audited rule): confirming a Sales Order does NOT create
any Journal Entry. An SO is a commitment only; accounting impact only
begins at Customer Invoice confirmation.

so_no is auto-generated (format: SO00001) by
app/services/sequence_service.py.

Owned by: Database Developer.
"""
from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import DocumentStatus


class SalesOrder(Base):
    __tablename__ = "sales_orders"

    id = Column(Integer, primary_key=True, index=True)

    so_no = Column(String(50), unique=True, nullable=False)
    customer_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    so_date = Column(Date, nullable=False)

    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.DRAFT)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    customer = relationship("Contact")
    lines = relationship("SalesOrderLine", back_populates="sales_order",
                          cascade="all, delete-orphan")
    customer_invoice = relationship("CustomerInvoice", back_populates="sales_order", uselist=False)

    def __repr__(self) -> str:
        return f"<SalesOrder id={self.id} so_no={self.so_no} status={self.status}>"


class SalesOrderLine(Base):
    __tablename__ = "sales_order_lines"

    id = Column(Integer, primary_key=True, index=True)

    sales_order_id = Column(Integer, ForeignKey("sales_orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    analytic_account_id = Column(Integer, ForeignKey("analytic_accounts.id"), nullable=True)

    qty = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)

    sales_order = relationship("SalesOrder", back_populates="lines")
    product = relationship("Product")
    analytic_account = relationship("AnalyticAccount")
