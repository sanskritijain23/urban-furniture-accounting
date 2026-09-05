"""
Shared enums for SQLAlchemy models.

These enums are the approved, audited values from the Urban Furniture
Problem Statement + MVP mockups. Do NOT add/remove values without
re-checking the source-of-truth mockups (see docs/database-design.md).

Owned by: Database Developer.
"""
import enum


class UserRole(str, enum.Enum):
    ADMIN = "admin"
    ACCOUNTANT = "accountant"
    CONTACT = "contact"


class ContactType(str, enum.Enum):
    CUSTOMER = "customer"
    VENDOR = "vendor"
    BOTH = "both"


class ProductType(str, enum.Enum):
    GOODS = "goods"
    SERVICE = "service"
    COMBO = "combo"


class AccountType(str, enum.Enum):
    """Chart of Accounts type — matches the approved mockup dropdown exactly."""
    ASSET = "asset"
    LIABILITY = "liability"
    BANK = "bank"
    CASH = "cash"
    CAPITAL = "capital"
    INCOME = "income"
    EXPENSES = "expenses"
    OTHER_EXPENSES = "other_expenses"


class AccountStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    ARCHIVED = "archived"


class JournalType(str, enum.Enum):
    SALES = "sales"
    PURCHASE = "purchase"
    BANK = "bank"
    CASH = "cash"


class JournalEntryStatus(str, enum.Enum):
    DRAFT = "draft"
    POSTED = "posted"
    CANCELLED = "cancelled"


class JournalEntrySourceType(str, enum.Enum):
    """What business transaction (if any) originated this Journal Entry."""
    MANUAL = "manual"
    VENDOR_BILL = "vendor_bill"
    CUSTOMER_INVOICE = "customer_invoice"
    PAYMENT = "payment"


class DocumentStatus(str, enum.Enum):
    """Generic Draft/Confirmed/Cancelled lifecycle for PO, SO, Bill, Invoice."""
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"


class PaymentStatus(str, enum.Enum):
    NOT_PAID = "not_paid"
    PARTIAL = "partial"
    PAID = "paid"


class PaymentType(str, enum.Enum):
    SEND = "send"
    RECEIVE = "receive"


class PaymentVia(str, enum.Enum):
    CASH = "cash"
    BANK = "bank"


class AnalyticAccountType(str, enum.Enum):
    INCOME = "income"
    EXPENSE = "expense"


class BudgetStatus(str, enum.Enum):
    DRAFT = "draft"
    CONFIRMED = "confirmed"
    REVISED = "revised"
    CANCELLED = "cancelled"
