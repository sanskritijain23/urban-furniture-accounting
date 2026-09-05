"""
Demo data seed script for the Urban Furniture Accounting System.

Creates connected dummy/demo data for:

MASTER DATA
- Contacts
- Product Categories
- Products
- Users

TRANSACTION DATA
- Sales Orders + Lines
- Purchase Orders + Lines
- Vendor Bills + Lines
- Customer Invoices + Lines
- Payments

IMPORTANT:
This script creates relational demo records directly in PostgreSQL.
It does NOT use the API/service layer to confirm transactions, so it
does not intentionally generate accounting journal entries.

The script is idempotent for its own predictable demo identifiers.

Run from project root:

    python3 database/seed/seed_demo_data.py
"""

import os
import sys
import random
from decimal import Decimal

from faker import Faker


# ============================================================
# BACKEND IMPORT PATH
# ============================================================

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "..",
            "backend",
        )
    ),
)


# ============================================================
# PROJECT IMPORTS
# ============================================================

from app.core.database import SessionLocal
from app.auth.password import hash_password

from app.models.contact import Contact
from app.models.product import Product, ProductCategory
from app.models.user import User
from app.models.sales_order import SalesOrder, SalesOrderLine
from app.models.purchase_order import PurchaseOrder, PurchaseOrderLine
from app.models.vendor_bill import VendorBill, VendorBillLine
from app.models.customer_invoice import (
    CustomerInvoice,
    CustomerInvoiceLine,
)
from app.models.payment import Payment
from app.models.analytic_account import AnalyticAccount
from app.models.account import Account

from app.models.enums import (
    ContactType,
    ProductType,
    UserRole,
    DocumentStatus,
    PaymentStatus,
    PaymentType,
    PaymentVia,
    JournalEntrySourceType,
)


fake = Faker()


# ============================================================
# HELPER
# ============================================================

def decimal(value):
    """Convert numeric values safely to Decimal."""
    return Decimal(str(value))


# ============================================================
# STEP 1 — DEMO CONTACTS
# ============================================================

def seed_extra_contacts(db, count=40):

    print(f"Creating/checking {count} demo contacts...")

    cities = [
        "Hyderabad",
        "Bengaluru",
        "Mumbai",
        "Delhi",
        "Chennai",
        "Pune",
        "Kolkata",
    ]

    states = [
        "Telangana",
        "Karnataka",
        "Maharashtra",
        "Delhi",
        "Tamil Nadu",
        "West Bengal",
    ]

    contacts = []

    for i in range(1, count + 1):

        email = f"demo.contact{i:03d}@example.com"

        existing = (
            db.query(Contact)
            .filter_by(email=email)
            .first()
        )

        if existing:
            contacts.append(existing)
            continue

        contact_type = random.choice([
            ContactType.CUSTOMER,
            ContactType.VENDOR,
            ContactType.BOTH,
        ])

        contact = Contact(
            name=fake.name(),
            type=contact_type,
            email=email,
            mobile=fake.msisdn()[:10],
            address_city=random.choice(cities),
            address_state=random.choice(states),
            address_pincode=fake.postcode(),
            profile_image_url=fake.image_url(),
        )

        db.add(contact)
        db.flush()

        contacts.append(contact)

    print(f"Demo contacts available: {len(contacts)}")

    return contacts


# ============================================================
# STEP 2 — PRODUCT CATEGORIES
# ============================================================

def seed_extra_categories(db):

    print("Creating/checking demo product categories...")

    category_names = [
        "Office Furniture",
        "Living Room Furniture",
        "Dining Furniture",
        "Bedroom Furniture",
        "Outdoor Furniture",
    ]

    categories = []

    for name in category_names:

        existing = (
            db.query(ProductCategory)
            .filter_by(name=name)
            .first()
        )

        if existing:
            categories.append(existing)
            continue

        category = ProductCategory(name=name)

        db.add(category)
        db.flush()

        categories.append(category)

    print(f"Demo categories available: {len(categories)}")

    return categories


# ============================================================
# STEP 3 — DEMO PRODUCTS
# ============================================================

def seed_extra_products(db, categories, count=30):

    print(f"Creating/checking {count} demo products...")

    furniture_names = [
        "Executive Office Chair",
        "Ergonomic Chair",
        "Wooden Coffee Table",
        "Modern Sofa",
        "Bookshelf",
        "Office Desk",
        "Dining Chair",
        "Dining Table",
        "Study Table",
        "TV Cabinet",
        "Wardrobe",
        "Bed Frame",
        "Side Table",
        "Recliner Chair",
        "Conference Table",
        "Computer Desk",
        "Storage Cabinet",
        "Reception Desk",
        "Wooden Bench",
        "Outdoor Chair",
        "Visitor Chair",
        "Wooden Stool",
        "Office Table",
        "Meeting Table",
        "Display Cabinet",
        "Shoe Rack",
        "Sideboard",
        "Study Chair",
        "Kitchen Table",
        "Lounge Chair",
    ]

    products = []

    for i in range(1, count + 1):

        product_name = f"{furniture_names[i - 1]} Demo"

        existing = (
            db.query(Product)
            .filter_by(name=product_name)
            .first()
        )

        if existing:
            products.append(existing)
            continue

        product_type = random.choice([
            ProductType.GOODS,
            ProductType.GOODS,
            ProductType.GOODS,
            ProductType.SERVICE,
        ])

        cost = random.randint(1000, 30000)

        sales_price = (
            cost +
            random.randint(500, 10000)
        )

        product = Product(
            name=product_name,
            type=product_type,
            sales_price=decimal(sales_price),
            cost=decimal(cost),
            category_id=random.choice(categories).id,
        )

        db.add(product)
        db.flush()

        products.append(product)

    print(f"Demo products available: {len(products)}")

    return products


# ============================================================
# STEP 4 — DEMO USERS
# ============================================================

def seed_extra_users(db, contacts, count=5):

    print(f"Creating/checking {count} demo users...")

    users = []

    demo_password = "Demo@123"

    password_hash = hash_password(
        demo_password
    )

    for i in range(1, count + 1):

        login_id = f"demo{i}"

        existing = (
            db.query(User)
            .filter_by(login_id=login_id)
            .first()
        )

        if existing:
            users.append(existing)
            continue

        role = random.choice([
            UserRole.ACCOUNTANT,
            UserRole.ACCOUNTANT,
            UserRole.CONTACT,
        ])

        contact = contacts[
            (i - 1) % len(contacts)
        ]

        user = User(
            login_id=login_id,
            email=f"demo{i}@example.com",
            password_hash=password_hash,
            name=fake.name(),
            role=role,
            contact_id=(
                contact.id
                if role == UserRole.CONTACT
                else None
            ),
        )

        db.add(user)
        db.flush()

        users.append(user)

    print(f"Demo users available: {len(users)}")

    return users


# ============================================================
# STEP 5 — SALES ORDERS
# ============================================================

def seed_sales_orders(db, count=15):

    print(
        f"Creating/checking {count} "
        "demo sales orders..."
    )

    customers = (
        db.query(Contact)
        .filter(
            Contact.type.in_([
                ContactType.CUSTOMER,
                ContactType.BOTH,
            ])
        )
        .all()
    )

    products = db.query(Product).all()

    analytic_accounts = (
        db.query(AnalyticAccount).all()
    )

    if not customers:
        raise ValueError(
            "No CUSTOMER/BOTH contacts available."
        )

    if not products:
        raise ValueError(
            "No products available."
        )

    sales_orders = []

    for i in range(1, count + 1):

        so_no = f"SO-DEMO-{i:03d}"

        existing = (
            db.query(SalesOrder)
            .filter_by(so_no=so_no)
            .first()
        )

        if existing:
            sales_orders.append(existing)
            continue

        sales_order = SalesOrder(
            so_no=so_no,
            customer_id=random.choice(customers).id,
            so_date=fake.date_between(
                start_date="-6M",
                end_date="today",
            ),
            status=DocumentStatus.DRAFT,
        )

        db.add(sales_order)
        db.flush()

        line_count = random.randint(2, 3)

        selected_products = random.sample(
            products,
            min(
                line_count,
                len(products),
            ),
        )

        for product in selected_products:

            qty = decimal(
                random.randint(1, 10)
            )

            unit_price = decimal(
                product.sales_price
            )

            total = qty * unit_price

            analytic_account_id = None

            if analytic_accounts:
                analytic_account_id = (
                    random.choice(
                        analytic_accounts
                    ).id
                )

            line = SalesOrderLine(
                sales_order_id=sales_order.id,
                product_id=product.id,
                analytic_account_id=analytic_account_id,
                qty=qty,
                unit_price=unit_price,
                total=total,
            )

            db.add(line)

        db.flush()

        sales_orders.append(
            sales_order
        )

    print(
        f"Demo sales orders available: "
        f"{len(sales_orders)}"
    )

    return sales_orders


# ============================================================
# STEP 6 — PURCHASE ORDERS
# ============================================================

def seed_purchase_orders(db, count=15):

    print(
        f"Creating/checking {count} "
        "demo purchase orders..."
    )

    vendors = (
        db.query(Contact)
        .filter(
            Contact.type.in_([
                ContactType.VENDOR,
                ContactType.BOTH,
            ])
        )
        .all()
    )

    products = db.query(Product).all()

    analytic_accounts = (
        db.query(AnalyticAccount).all()
    )

    if not vendors:
        raise ValueError(
            "No VENDOR/BOTH contacts available."
        )

    if not products:
        raise ValueError(
            "No products available."
        )

    purchase_orders = []

    for i in range(1, count + 1):

        po_no = f"PO-DEMO-{i:03d}"

        existing = (
            db.query(PurchaseOrder)
            .filter_by(po_no=po_no)
            .first()
        )

        if existing:
            purchase_orders.append(
                existing
            )
            continue

        purchase_order = PurchaseOrder(
            po_no=po_no,
            vendor_id=random.choice(vendors).id,
            po_date=fake.date_between(
                start_date="-6M",
                end_date="today",
            ),
            status=DocumentStatus.DRAFT,
        )

        db.add(purchase_order)
        db.flush()

        line_count = random.randint(2, 3)

        selected_products = random.sample(
            products,
            min(
                line_count,
                len(products),
            ),
        )

        for product in selected_products:

            qty = decimal(
                random.randint(1, 10)
            )

            unit_price = decimal(
                product.cost
            )

            total = qty * unit_price

            analytic_account_id = None

            if analytic_accounts:
                analytic_account_id = (
                    random.choice(
                        analytic_accounts
                    ).id
                )

            line = PurchaseOrderLine(
                purchase_order_id=(
                    purchase_order.id
                ),
                product_id=product.id,
                analytic_account_id=(
                    analytic_account_id
                ),
                qty=qty,
                unit_price=unit_price,
                total=total,
            )

            db.add(line)

        db.flush()

        purchase_orders.append(
            purchase_order
        )

    print(
        f"Demo purchase orders available: "
        f"{len(purchase_orders)}"
    )

    return purchase_orders


# ============================================================
# STEP 7 — VENDOR BILLS
# ============================================================

def seed_vendor_bills(
    db,
    purchase_orders,
    count=15,
):

    print(
        f"Creating/checking {count} "
        "demo vendor bills..."
    )

    purchase_expense_account = (
        db.query(Account)
        .filter_by(
            name="Purchase Expense A/c"
        )
        .first()
    )

    if not purchase_expense_account:

        raise ValueError(
            "Purchase Expense A/c "
            "was not found."
        )

    products = db.query(Product).all()

    analytic_accounts = (
        db.query(AnalyticAccount).all()
    )

    vendor_bills = []

    for i in range(1, count + 1):

        bill_no = f"VB-DEMO-{i:03d}"

        existing = (
            db.query(VendorBill)
            .filter_by(bill_no=bill_no)
            .first()
        )

        if existing:
            vendor_bills.append(
                existing
            )
            continue

        purchase_order = (
            purchase_orders[
                (i - 1) %
                len(purchase_orders)
            ]
        )

        bill_date = fake.date_between(
            start_date="-5M",
            end_date="today",
        )

        vendor_bill = VendorBill(
            bill_no=bill_no,
            reference=(
                f"Demo Vendor Bill {i}"
            ),
            vendor_id=(
                purchase_order.vendor_id
            ),
            purchase_order_id=(
                purchase_order.id
            ),
            bill_date=bill_date,
            due_date=fake.date_between(
                start_date="today",
                end_date="+60d",
            ),
            status=DocumentStatus.DRAFT,
            payment_status=(
                PaymentStatus.NOT_PAID
            ),
        )

        db.add(vendor_bill)
        db.flush()

        line_count = random.randint(2, 3)

        selected_products = random.sample(
            products,
            min(
                line_count,
                len(products),
            ),
        )

        for product in selected_products:

            qty = decimal(
                random.randint(1, 10)
            )

            unit_price = decimal(
                product.cost
            )

            total = qty * unit_price

            analytic_account_id = None

            if analytic_accounts:
                analytic_account_id = (
                    random.choice(
                        analytic_accounts
                    ).id
                )

            line = VendorBillLine(
                vendor_bill_id=(
                    vendor_bill.id
                ),
                product_id=product.id,
                account_id=(
                    purchase_expense_account.id
                ),
                analytic_account_id=(
                    analytic_account_id
                ),
                qty=qty,
                unit_price=unit_price,
                total=total,
            )

            db.add(line)

        db.flush()

        vendor_bills.append(
            vendor_bill
        )

    print(
        f"Demo vendor bills available: "
        f"{len(vendor_bills)}"
    )

    return vendor_bills


# ============================================================
# STEP 8 — CUSTOMER INVOICES
# ============================================================

def seed_customer_invoices(
    db,
    sales_orders,
    count=15,
):

    print(
        f"Creating/checking {count} "
        "demo customer invoices..."
    )

    sales_income_account = (
        db.query(Account)
        .filter_by(
            name="Sales Income A/c"
        )
        .first()
    )

    if not sales_income_account:

        raise ValueError(
            "Sales Income A/c "
            "was not found."
        )

    products = db.query(Product).all()

    analytic_accounts = (
        db.query(AnalyticAccount).all()
    )

    customer_invoices = []

    for i in range(1, count + 1):

        invoice_no = (
            f"INV-DEMO-{i:03d}"
        )

        existing = (
            db.query(CustomerInvoice)
            .filter_by(
                invoice_no=invoice_no
            )
            .first()
        )

        if existing:
            customer_invoices.append(
                existing
            )
            continue

        sales_order = (
            sales_orders[
                (i - 1) %
                len(sales_orders)
            ]
        )

        invoice_date = (
            fake.date_between(
                start_date="-5M",
                end_date="today",
            )
        )

        customer_invoice = (
            CustomerInvoice(
                invoice_no=invoice_no,
                reference=(
                    f"Demo Customer "
                    f"Invoice {i}"
                ),
                customer_id=(
                    sales_order.customer_id
                ),
                sales_order_id=(
                    sales_order.id
                ),
                invoice_date=invoice_date,
                due_date=(
                    fake.date_between(
                        start_date="today",
                        end_date="+60d",
                    )
                ),
                status=DocumentStatus.DRAFT,
                payment_status=(
                    PaymentStatus.NOT_PAID
                ),
            )
        )

        db.add(customer_invoice)
        db.flush()

        line_count = random.randint(2, 3)

        selected_products = random.sample(
            products,
            min(
                line_count,
                len(products),
            ),
        )

        for product in selected_products:

            qty = decimal(
                random.randint(1, 10)
            )

            unit_price = decimal(
                product.sales_price
            )

            total = qty * unit_price

            analytic_account_id = None

            if analytic_accounts:
                analytic_account_id = (
                    random.choice(
                        analytic_accounts
                    ).id
                )

            line = CustomerInvoiceLine(
                customer_invoice_id=(
                    customer_invoice.id
                ),
                product_id=product.id,
                account_id=(
                    sales_income_account.id
                ),
                analytic_account_id=(
                    analytic_account_id
                ),
                qty=qty,
                unit_price=unit_price,
                total=total,
            )

            db.add(line)

        db.flush()

        customer_invoices.append(
            customer_invoice
        )

    print(
        f"Demo customer invoices available: "
        f"{len(customer_invoices)}"
    )

    return customer_invoices


# ============================================================
# HELPER — CALCULATE DOCUMENT TOTAL
# ============================================================

def get_document_total(
    db,
    line_model,
    foreign_key_name,
    document_id,
):

    foreign_key = getattr(
        line_model,
        foreign_key_name,
    )

    lines = (
        db.query(line_model)
        .filter(
            foreign_key == document_id
        )
        .all()
    )

    return sum(
        (
            decimal(line.total)
            for line in lines
        ),
        Decimal("0"),
    )


# ============================================================
# STEP 9 — PAYMENTS
# ============================================================

def seed_payments(
    db,
    vendor_bills,
    customer_invoices,
):

    print(
        "Creating/checking demo payments..."
    )

    payments = []

    # --------------------------------------------------------
    # PAYMENTS TO VENDORS
    # --------------------------------------------------------

    for i, vendor_bill in enumerate(
        vendor_bills,
        start=1,
    ):

        note = (
            f"DEMO-VENDOR-PAYMENT-"
            f"{i:03d}"
        )

        existing = (
            db.query(Payment)
            .filter_by(note=note)
            .first()
        )

        if existing:
            payments.append(existing)
            continue

        total = get_document_total(
            db=db,
            line_model=VendorBillLine,
            foreign_key_name=(
                "vendor_bill_id"
            ),
            document_id=vendor_bill.id,
        )

        payment = Payment(
            payment_type=PaymentType.SEND,
            payment_via=random.choice([
                PaymentVia.CASH,
                PaymentVia.BANK,
            ]),
            date=fake.date_between(
                start_date="-3M",
                end_date="today",
            ),
            partner_id=vendor_bill.vendor_id,
            amount=total,
            note=note,
            status=DocumentStatus.DRAFT,
            source_type=(
                JournalEntrySourceType.VENDOR_BILL
            ),
            source_id=vendor_bill.id,
        )

        db.add(payment)
        db.flush()

        payments.append(payment)

    # --------------------------------------------------------
    # PAYMENTS FROM CUSTOMERS
    # --------------------------------------------------------

    for i, customer_invoice in enumerate(
        customer_invoices,
        start=1,
    ):

        note = (
            f"DEMO-CUSTOMER-PAYMENT-"
            f"{i:03d}"
        )

        existing = (
            db.query(Payment)
            .filter_by(note=note)
            .first()
        )

        if existing:
            payments.append(existing)
            continue

        total = get_document_total(
            db=db,
            line_model=CustomerInvoiceLine,
            foreign_key_name=(
                "customer_invoice_id"
            ),
            document_id=(
                customer_invoice.id
            ),
        )

        payment = Payment(
            payment_type=(
                PaymentType.RECEIVE
            ),
            payment_via=random.choice([
                PaymentVia.CASH,
                PaymentVia.BANK,
            ]),
            date=fake.date_between(
                start_date="-3M",
                end_date="today",
            ),
            partner_id=(
                customer_invoice.customer_id
            ),
            amount=total,
            note=note,
            status=DocumentStatus.DRAFT,
            source_type=(
                JournalEntrySourceType
                .CUSTOMER_INVOICE
            ),
            source_id=(
                customer_invoice.id
            ),
        )

        db.add(payment)
        db.flush()

        payments.append(payment)

    print(
        f"Demo payments available: "
        f"{len(payments)}"
    )

    return payments


# ============================================================
# MAIN
# ============================================================

def run():

    db = SessionLocal()

    try:

        print("\n===================================")
        print(
            "Starting demo data generation..."
        )
        print(
            "===================================\n"
        )

        # MASTER DATA

        contacts = seed_extra_contacts(
            db,
            count=40,
        )

        categories = (
            seed_extra_categories(db)
        )

        products = seed_extra_products(
            db,
            categories,
            count=30,
        )

        users = seed_extra_users(
            db,
            contacts,
            count=5,
        )

        # TRANSACTION DATA

        sales_orders = (
            seed_sales_orders(
                db,
                count=15,
            )
        )

        purchase_orders = (
            seed_purchase_orders(
                db,
                count=15,
            )
        )

        vendor_bills = (
            seed_vendor_bills(
                db,
                purchase_orders,
                count=15,
            )
        )

        customer_invoices = (
            seed_customer_invoices(
                db,
                sales_orders,
                count=15,
            )
        )

        payments = seed_payments(
            db,
            vendor_bills,
            customer_invoices,
        )

        # FINAL COMMIT

        db.commit()

        print(
            "\n==================================="
        )

        print(
            "Demo data inserted successfully."
        )

        print(
            "==================================="
        )

        print(
            f"Contacts processed: "
            f"{len(contacts)}"
        )

        print(
            f"Categories processed: "
            f"{len(categories)}"
        )

        print(
            f"Products processed: "
            f"{len(products)}"
        )

        print(
            f"Users processed: "
            f"{len(users)}"
        )

        print(
            f"Sales Orders processed: "
            f"{len(sales_orders)}"
        )

        print(
            f"Purchase Orders processed: "
            f"{len(purchase_orders)}"
        )

        print(
            f"Vendor Bills processed: "
            f"{len(vendor_bills)}"
        )

        print(
            f"Customer Invoices processed: "
            f"{len(customer_invoices)}"
        )

        print(
            f"Payments processed: "
            f"{len(payments)}"
        )

    except Exception as exc:

        db.rollback()

        print(
            f"\nDemo seed failed: {exc}"
        )

        raise

    finally:

        db.close()


if __name__ == "__main__":
    run()