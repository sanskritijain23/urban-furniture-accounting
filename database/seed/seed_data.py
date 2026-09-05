"""
Seed script — harmless demo master data ONLY, matching the exact
names used in the official Problem Statement's worked example
(Section 7). Does NOT create any completed transactions (POs, Bills,
Invoices, Payments, or Journal Entries) — that would misrepresent the
system's actual state to the team.

Run with:
    python database/seed/seed_data.py

Owned by: Database Developer.
"""
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "backend")))

from app.core.database import SessionLocal  # noqa: E402
from app.models.contact import Contact  # noqa: E402
from app.models.product import Product, ProductCategory  # noqa: E402
from app.models.account import Account  # noqa: E402
from app.models.journal import Journal  # noqa: E402
from app.models.analytic_account import AnalyticAccount
from app.models.enums import (
    ContactType,
    ProductType,
    AccountType,
    AccountStatus,
    JournalType,
    AnalyticAccountType,
)


def seed_chart_of_accounts(db):
    """Pre-configured accounts, as required by the CoA mockup note
    ("all accounts are to be pre-configured")."""
    accounts = [
        ("Cash", AccountType.CASH),
        ("Bank", AccountType.BANK),
        ("Debtors A/c", AccountType.ASSET),
        ("Creditors A/c", AccountType.LIABILITY),
        ("Capital A/c", AccountType.CAPITAL),
        ("Sales Income A/c", AccountType.INCOME),
        ("Purchase Expense A/c", AccountType.EXPENSES),
        ("Other Expenses A/c", AccountType.OTHER_EXPENSES),
    ]
    created = {}
    for name, acc_type in accounts:
        existing = db.query(Account).filter_by(name=name).first()
        if existing:
            created[name] = existing
            continue
        acc = Account(name=name, type=acc_type, status=AccountStatus.CONFIRMED)
        db.add(acc)
        db.flush()
        created[name] = acc
    return created


def seed_journals(db, accounts):
    """Default journals, each wired to its default account."""
    journals = [
        ("Sales", JournalType.SALES, accounts["Sales Income A/c"]),
        ("Purchase", JournalType.PURCHASE, accounts["Purchase Expense A/c"]),
        ("Bank", JournalType.BANK, accounts["Bank"]),
        ("Cash", JournalType.CASH, accounts["Cash"]),
    ]
    for name, j_type, default_account in journals:
        existing = db.query(Journal).filter_by(name=name).first()
        if existing:
            continue
        db.add(Journal(name=name, type=j_type, default_account_id=default_account.id))


def seed_analytic_accounts(db):
    """Seed basic analytic accounts for income and expense tracking."""
    
    analytic_accounts = [
        ("Sales Analytics", AnalyticAccountType.INCOME),
        ("Purchase Analytics", AnalyticAccountType.EXPENSE),
    ]

    for name, account_type in analytic_accounts:
        existing = (
            db.query(AnalyticAccount)
            .filter_by(name=name)
            .first()
        )

        if existing:
            continue

        db.add(
            AnalyticAccount(
                name=name,
                type=account_type
            )
        )


def seed_contacts(db):
    """Demo contacts, matching the PS's worked example exactly."""
    contacts = [
        dict(name="Rahul Sharma", type=ContactType.VENDOR, email="rahul.sharma@example.com"),
        dict(name="Nimesh Pathak", type=ContactType.CUSTOMER, email="nimesh.pathak@example.com"),
        dict(name="Azure Furniture", type=ContactType.VENDOR, email="contact@azurefurniture.example.com"),
    ]
    for c in contacts:
        if db.query(Contact).filter_by(email=c["email"]).first():
            continue
        db.add(Contact(**c))


def seed_products(db):
    category = db.query(ProductCategory).filter_by(name="Furniture").first()
    if not category:
        category = ProductCategory(name="Furniture")
        db.add(category)
        db.flush()

    products = [
        dict(name="Office Chair", type=ProductType.GOODS, sales_price=2500, cost=1500),
        dict(name="Wooden Chair", type=ProductType.GOODS, sales_price=2000, cost=1200),
        dict(name="Wooden Table", type=ProductType.GOODS, sales_price=6000, cost=4000),
        dict(name="Sofa", type=ProductType.GOODS, sales_price=15000, cost=10000),
        dict(name="Dining Table", type=ProductType.GOODS, sales_price=12000, cost=8000),
    ]
    for p in products:
        if db.query(Product).filter_by(name=p["name"]).first():
            continue
        db.add(Product(category_id=category.id, **p))


def run():
    db = SessionLocal()

    try:
        accounts = seed_chart_of_accounts(db)

        seed_journals(db, accounts)
        seed_contacts(db)
        seed_products(db)
        seed_analytic_accounts(db)

        db.commit()

        print("Seed data inserted successfully.")

    except Exception as exc:
        db.rollback()
        print(f"Seed failed: {exc}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    run()
