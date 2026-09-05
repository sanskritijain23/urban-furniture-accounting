"""
Aggregates all SQLAlchemy models so that:
  - `Base.metadata` is aware of every table (required for Alembic
    autogenerate to detect them).
  - Other modules can `from app import models` and access anything.

Owned by: Database Developer. When adding a new model file, import it
here too, or Alembic will not see the new table.
"""
from app.core.database import Base  # noqa: F401

from app.models.enums import (  # noqa: F401
    UserRole, ContactType, ProductType, AccountType, AccountStatus,
    JournalType, JournalEntryStatus, JournalEntrySourceType, DocumentStatus,
    PaymentStatus, PaymentType, PaymentVia, AnalyticAccountType, BudgetStatus,
)

from app.models.user import User  # noqa: F401
from app.models.contact import Contact  # noqa: F401
from app.models.product import Product, ProductCategory  # noqa: F401
from app.models.account import Account  # noqa: F401
from app.models.journal import Journal  # noqa: F401
from app.models.journal_entry import JournalEntry, JournalEntryLine  # noqa: F401
from app.models.purchase_order import PurchaseOrder, PurchaseOrderLine  # noqa: F401
from app.models.vendor_bill import VendorBill, VendorBillLine  # noqa: F401
from app.models.sales_order import SalesOrder, SalesOrderLine  # noqa: F401
from app.models.customer_invoice import CustomerInvoice, CustomerInvoiceLine  # noqa: F401
from app.models.payment import Payment  # noqa: F401
from app.models.analytic_account import AnalyticAccount  # noqa: F401
from app.models.budget import Budget  # noqa: F401
