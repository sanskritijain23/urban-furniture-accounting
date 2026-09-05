"""
Shared pytest fixtures for the whole `tests/` package.

Uses a throwaway SQLite file (not the Postgres `DATABASE_URL` from
app.core.config) so tests run anywhere with zero external services --
important since Database/Backend/Frontend devs may not all have
Postgres running locally, and CI shouldn't need it either.

This only overrides the `get_db` FastAPI dependency for the duration
of the test session; it does not modify app/core/database.py, which
is owned by the Database developer.
"""
import uuid
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Importing app.models (not just app.core.database) ensures every table
# -- User, Contact, Product, etc. -- is registered on Base.metadata
# before create_all runs, even though this checkpoint only exercises
# the `users` table.
import app.models  # noqa: F401
from app.core.database import Base, get_db
from app.main import app

TEST_DB_PATH = Path(__file__).resolve().parent / "urban_furniture_test.db"
TEST_DB_PATH.unlink(missing_ok=True)

test_engine = create_engine(
    f"sqlite:///{TEST_DB_PATH}",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

Base.metadata.create_all(bind=test_engine)


def _override_get_db():
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def db_session():
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def unique_login_id() -> str:
    """6-12 char alnum login_id, unique per test call."""
    return "u" + uuid.uuid4().hex[:8]


@pytest.fixture()
def unique_email(unique_login_id) -> str:
    return f"{unique_login_id}@example.com"


VALID_PASSWORD = "Str0ng!Pass"


def _random_login_id() -> str:
    return "u" + uuid.uuid4().hex[:8]


@pytest.fixture()
def accountant_token(client) -> str:
    login_id = _random_login_id()
    email = f"{login_id}@example.com"
    signup = client.post(
        "/api/v1/auth/signup",
        json={"login_id": login_id, "email": email, "password": VALID_PASSWORD},
    )
    assert signup.status_code == 201, signup.text
    resp = client.post(
        "/api/v1/auth/login", json={"login_id": login_id, "password": VALID_PASSWORD}
    )
    return resp.json()["access_token"]


@pytest.fixture()
def admin_token(client, db_session) -> str:
    from app.auth.password import hash_password
    from app.models.enums import UserRole
    from app.models.user import User

    login_id = _random_login_id()
    email = f"{login_id}@example.com"
    admin = User(
        login_id=login_id,
        email=email,
        password_hash=hash_password(VALID_PASSWORD),
        role=UserRole.ADMIN,
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post(
        "/api/v1/auth/login", json={"login_id": login_id, "password": VALID_PASSWORD}
    )
    return resp.json()["access_token"]


@pytest.fixture(scope="session")
def seeded_accounting():
    """
    Session-scoped: creates the Chart of Accounts + Journals that
    accounting_engine.py looks up by name/type (Debtors A/c,
    Creditors A/c, Purchase Expense A/c, Sales Income A/c, Bank, Cash)
    plus the demo vendor/customer/product from the Problem Statement's
    worked example, exactly once for the whole test run (idempotent --
    checks existence first, mirroring database/seed/seed_data.py).
    Returns a dict of the created/found IDs for tests to build on.
    """
    from app.models.account import Account
    from app.models.journal import Journal
    from app.models.contact import Contact
    from app.models.product import Product, ProductCategory
    from app.models.enums import AccountType, AccountStatus, JournalType, ContactType, ProductType

    db = TestSessionLocal()
    try:
        accounts = {}
        for name, acc_type in [
            ("Cash", AccountType.CASH),
            ("Bank", AccountType.BANK),
            ("Debtors A/c", AccountType.ASSET),
            ("Creditors A/c", AccountType.LIABILITY),
            ("Capital A/c", AccountType.CAPITAL),
            ("Sales Income A/c", AccountType.INCOME),
            ("Purchase Expense A/c", AccountType.EXPENSES),
            ("Other Expenses A/c", AccountType.OTHER_EXPENSES),
        ]:
            existing = db.query(Account).filter_by(name=name).first()
            if existing is None:
                existing = Account(name=name, type=acc_type, status=AccountStatus.CONFIRMED)
                db.add(existing)
                db.flush()
            accounts[name] = existing.id

        journal_defs = [
            ("Sales", JournalType.SALES, accounts["Sales Income A/c"]),
            ("Purchase", JournalType.PURCHASE, accounts["Purchase Expense A/c"]),
            ("Bank", JournalType.BANK, accounts["Bank"]),
            ("Cash", JournalType.CASH, accounts["Cash"]),
        ]
        journals = {}
        for name, j_type, default_account_id in journal_defs:
            existing = db.query(Journal).filter_by(name=name).first()
            if existing is None:
                existing = Journal(name=name, type=j_type, default_account_id=default_account_id)
                db.add(existing)
                db.flush()
            journals[name] = existing.id

        vendor = db.query(Contact).filter_by(email="azure.furniture@example.com").first()
        if vendor is None:
            vendor = Contact(
                name="Azure Furniture", type=ContactType.VENDOR,
                email="azure.furniture@example.com",
            )
            db.add(vendor)
            db.flush()

        customer = db.query(Contact).filter_by(email="nimesh.pathak@example.com").first()
        if customer is None:
            customer = Contact(
                name="Nimesh Pathak", type=ContactType.CUSTOMER,
                email="nimesh.pathak@example.com",
            )
            db.add(customer)
            db.flush()

        category = db.query(ProductCategory).filter_by(name="Furniture").first()
        if category is None:
            category = ProductCategory(name="Furniture")
            db.add(category)
            db.flush()

        product = db.query(Product).filter_by(name="Office Chair").first()
        if product is None:
            product = Product(
                name="Office Chair", type=ProductType.GOODS,
                sales_price=2500, cost=1500, category_id=category.id,
            )
            db.add(product)
            db.flush()

        db.commit()

        return {
            "accounts": accounts,
            "journals": journals,
            "vendor_id": vendor.id,
            "customer_id": customer.id,
            "product_id": product.id,
        }
    finally:
        db.close()
