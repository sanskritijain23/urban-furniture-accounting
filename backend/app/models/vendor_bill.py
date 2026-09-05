from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, Date, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import DocumentStatus, PaymentStatus


class VendorBill(Base):
    __tablename__ = "vendor_bills"

    id = Column(Integer, primary_key=True, index=True)

    bill_no = Column(String(50), unique=True, nullable=False)
    reference = Column(String(150), nullable=True)  # free-text, separate from bill_no

    vendor_id = Column(Integer, ForeignKey("contacts.id"), nullable=False)
    purchase_order_id = Column(Integer, ForeignKey("purchase_orders.id"), nullable=True)

    bill_date = Column(Date, nullable=False)
    due_date = Column(Date, nullable=True)

    status = Column(Enum(DocumentStatus), nullable=False, default=DocumentStatus.DRAFT)
    payment_status = Column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.NOT_PAID)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    vendor = relationship("Contact")
    purchase_order = relationship("PurchaseOrder", back_populates="vendor_bill")
    lines = relationship("VendorBillLine", back_populates="vendor_bill",
                          cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<VendorBill id={self.id} bill_no={self.bill_no} status={self.status}>"


class VendorBillLine(Base):
    __tablename__ = "vendor_bill_lines"

    id = Column(Integer, primary_key=True, index=True)

    vendor_bill_id = Column(Integer, ForeignKey("vendor_bills.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)

    account_id = Column(Integer, ForeignKey("accounts.id"), nullable=False)
    analytic_account_id = Column(Integer, ForeignKey("analytic_accounts.id"), nullable=True)

    qty = Column(Numeric(12, 2), nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    total = Column(Numeric(12, 2), nullable=False)

    vendor_bill = relationship("VendorBill", back_populates="lines")
    product = relationship("Product")
    account = relationship("Account")
    analytic_account = relationship("AnalyticAccount")
