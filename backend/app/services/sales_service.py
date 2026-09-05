"""
Sales-side business logic: Sales Order -> Customer Invoice.

IMPORTANT: this module must NOT create or modify JournalEntry /
JournalEntryLine rows directly. When a Customer Invoice is confirmed,
call
app.services.accounting_engine.create_entry_for_customer_invoice_confirmation
instead of computing debits/credits here.

Confirming a Sales Order does NOT create any accounting entry -- only
Customer Invoice confirmation does.
"""
from typing import List

from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.customer_invoice import CustomerInvoice, CustomerInvoiceLine
from app.models.enums import ContactType, DocumentStatus
from app.models.product import Product
from app.models.sales_order import SalesOrder, SalesOrderLine
from app.services import accounting_engine, sequence_service


class SalesOrderNotFoundError(Exception):
    pass


class CustomerInvoiceNotFoundError(Exception):
    pass


class InvalidCustomerError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class InvalidTransitionError(Exception):
    pass


class DuplicateInvoiceError(Exception):
    pass


def _validate_customer(db: Session, customer_id: int) -> Contact:
    customer = db.query(Contact).filter(Contact.id == customer_id).first()
    if customer is None:
        raise InvalidCustomerError(f"Contact {customer_id} not found")
    if customer.type not in (ContactType.CUSTOMER, ContactType.BOTH):
        raise InvalidCustomerError(f"Contact {customer_id} is not a customer")
    return customer


def _validate_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise ProductNotFoundError(f"Product {product_id} not found")
    return product


def list_sales_orders(db: Session) -> List[SalesOrder]:
    return db.query(SalesOrder).order_by(SalesOrder.id).all()


def get_sales_order(db: Session, sales_order_id: int) -> SalesOrder:
    so = db.query(SalesOrder).filter(SalesOrder.id == sales_order_id).first()
    if so is None:
        raise SalesOrderNotFoundError(f"Sales Order {sales_order_id} not found")
    return so


def list_customer_invoices(db: Session) -> List[CustomerInvoice]:
    return db.query(CustomerInvoice).order_by(CustomerInvoice.id).all()


def get_customer_invoice(db: Session, invoice_id: int) -> CustomerInvoice:
    invoice = db.query(CustomerInvoice).filter(CustomerInvoice.id == invoice_id).first()
    if invoice is None:
        raise CustomerInvoiceNotFoundError(f"Customer Invoice {invoice_id} not found")
    return invoice


def create_sales_order(db: Session, payload) -> SalesOrder:
    _validate_customer(db, payload.customer_id)
    for line in payload.lines:
        _validate_product(db, line.product_id)

    so = SalesOrder(
        so_no=sequence_service.next_so_number(db),
        customer_id=payload.customer_id,
        so_date=payload.so_date,
        status=DocumentStatus.DRAFT,
    )
    db.add(so)
    db.flush()

    for line in payload.lines:
        total = line.qty * line.unit_price
        db.add(SalesOrderLine(
            sales_order_id=so.id,
            product_id=line.product_id,
            analytic_account_id=line.analytic_account_id,
            qty=line.qty,
            unit_price=line.unit_price,
            total=total,
        ))

    db.commit()
    db.refresh(so)
    return so


def confirm_sales_order(db: Session, sales_order_id: int) -> SalesOrder:
    """Sets status -> CONFIRMED. Does NOT call accounting_engine -- SOs
    never create entries."""
    so = get_sales_order(db, sales_order_id)
    if so.status != DocumentStatus.DRAFT:
        raise InvalidTransitionError(
            f"Only DRAFT sales orders can be confirmed (current status: {so.status.value})"
        )
    so.status = DocumentStatus.CONFIRMED
    db.commit()
    db.refresh(so)
    return so


def create_invoice_from_so(db: Session, sales_order_id: int, payload) -> CustomerInvoice:
    """
    Pre-fills CustomerInvoice fields from the linked SalesOrder. The
    frontend is expected to have populated `payload` from the SO's own
    data (customer, lines); this function additionally enforces the
    customer matches and forces the sales_order_id link server-side.
    """
    so = get_sales_order(db, sales_order_id)
    if so.status != DocumentStatus.CONFIRMED:
        raise InvalidTransitionError(
            f"Sales Order must be CONFIRMED before creating an invoice (current status: {so.status.value})"
        )
    if so.customer_invoice is not None:
        raise DuplicateInvoiceError(f"Sales Order {sales_order_id} already has a Customer Invoice")
    if payload.customer_id != so.customer_id:
        raise InvalidCustomerError("Customer Invoice customer must match the Sales Order's customer")

    for line in payload.lines:
        _validate_product(db, line.product_id)

    invoice = CustomerInvoice(
        invoice_no=sequence_service.next_invoice_number(db, year=payload.invoice_date.year),
        reference=payload.reference,
        customer_id=payload.customer_id,
        sales_order_id=so.id,
        invoice_date=payload.invoice_date,
        due_date=payload.due_date,
        status=DocumentStatus.DRAFT,
    )
    db.add(invoice)
    db.flush()

    default_income_account = None
    for line in payload.lines:
        account_id = line.account_id
        if account_id is None:
            if default_income_account is None:
                default_income_account = accounting_engine.get_default_sales_income_account(db)
            account_id = default_income_account.id

        total = line.qty * line.unit_price
        db.add(CustomerInvoiceLine(
            customer_invoice_id=invoice.id,
            product_id=line.product_id,
            account_id=account_id,
            analytic_account_id=line.analytic_account_id,
            qty=line.qty,
            unit_price=line.unit_price,
            total=total,
        ))

    db.commit()
    db.refresh(invoice)
    return invoice


def confirm_customer_invoice(db: Session, invoice_id: int) -> CustomerInvoice:
    """
    Sets status -> CONFIRMED, then calls accounting_engine to create
    exactly one Journal Entry (Debit Debtors / Credit Sales Income) --
    the ONLY accounting call this function makes.

    Atomicity: the status change is staged (not committed) before the
    accounting_engine call; accounting_engine's own commit persists
    both together, or neither if it raises.
    """
    invoice = get_customer_invoice(db, invoice_id)
    if invoice.status != DocumentStatus.DRAFT:
        raise InvalidTransitionError(
            f"Only DRAFT customer invoices can be confirmed (current status: {invoice.status.value})"
        )

    invoice.status = DocumentStatus.CONFIRMED
    try:
        accounting_engine.create_entry_for_customer_invoice_confirmation(db, invoice.id)
    except Exception:
        db.rollback()
        raise

    return invoice
