"""
Purchase-side business logic: Purchase Order -> Vendor Bill.

IMPORTANT: this module must NOT create or modify JournalEntry /
JournalEntryLine rows directly. When a Vendor Bill is confirmed, call
app.services.accounting_engine.create_entry_for_vendor_bill_confirmation
instead of computing debits/credits here.

Confirming a Purchase Order does NOT create any accounting entry --
only Vendor Bill confirmation does.
"""
from decimal import Decimal
from typing import List, Tuple

from sqlalchemy.orm import Session

from app.models.contact import Contact
from app.models.enums import ContactType, DocumentStatus
from app.models.product import Product
from app.models.purchase_order import PurchaseOrder, PurchaseOrderLine
from app.models.vendor_bill import VendorBill, VendorBillLine
from app.services import accounting_engine, sequence_service, budget_service


class PurchaseOrderNotFoundError(Exception):
    pass


class VendorBillNotFoundError(Exception):
    pass


class InvalidVendorError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class InvalidTransitionError(Exception):
    pass


class DuplicateBillError(Exception):
    pass


def _validate_vendor(db: Session, vendor_id: int) -> Contact:
    vendor = db.query(Contact).filter(Contact.id == vendor_id).first()
    if vendor is None:
        raise InvalidVendorError(f"Contact {vendor_id} not found")
    if vendor.type not in (ContactType.VENDOR, ContactType.BOTH):
        raise InvalidVendorError(f"Contact {vendor_id} is not a vendor")
    return vendor


def _validate_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise ProductNotFoundError(f"Product {product_id} not found")
    return product


def list_purchase_orders(db: Session) -> List[PurchaseOrder]:
    return db.query(PurchaseOrder).order_by(PurchaseOrder.id).all()


def get_purchase_order(db: Session, purchase_order_id: int) -> PurchaseOrder:
    po = db.query(PurchaseOrder).filter(PurchaseOrder.id == purchase_order_id).first()
    if po is None:
        raise PurchaseOrderNotFoundError(f"Purchase Order {purchase_order_id} not found")
    return po


def list_vendor_bills(db: Session) -> List[VendorBill]:
    return db.query(VendorBill).order_by(VendorBill.id).all()


def get_vendor_bill(db: Session, vendor_bill_id: int) -> VendorBill:
    bill = db.query(VendorBill).filter(VendorBill.id == vendor_bill_id).first()
    if bill is None:
        raise VendorBillNotFoundError(f"Vendor Bill {vendor_bill_id} not found")
    return bill


def create_purchase_order(db: Session, payload) -> PurchaseOrder:
    _validate_vendor(db, payload.vendor_id)
    for line in payload.lines:
        _validate_product(db, line.product_id)

    po = PurchaseOrder(
        po_no=sequence_service.next_po_number(db),
        vendor_id=payload.vendor_id,
        po_date=payload.po_date,
        status=DocumentStatus.DRAFT,
    )
    db.add(po)
    db.flush()

    for line in payload.lines:
        total = line.qty * line.unit_price
        db.add(PurchaseOrderLine(
            purchase_order_id=po.id,
            product_id=line.product_id,
            analytic_account_id=line.analytic_account_id,
            qty=line.qty,
            unit_price=line.unit_price,
            total=total,
        ))

    db.commit()
    db.refresh(po)
    return po


def confirm_purchase_order(db: Session, purchase_order_id: int) -> Tuple[PurchaseOrder, List[str]]:
    """
    Sets status -> CONFIRMED. Checks budget for each line's analytic
    account (NON-BLOCKING -- warnings are collected and returned, never
    raised). Does NOT call accounting_engine: POs never create entries.
    """
    po = get_purchase_order(db, purchase_order_id)
    if po.status != DocumentStatus.DRAFT:
        raise InvalidTransitionError(
            f"Only DRAFT purchase orders can be confirmed (current status: {po.status.value})"
        )

    po.status = DocumentStatus.CONFIRMED
    db.commit()
    db.refresh(po)

    warnings = []
    for line in po.lines:
        if line.analytic_account_id:
            warning = budget_service.check_budget_warning(db, line.analytic_account_id, line.total)
            if warning:
                warnings.append(warning)

    return po, warnings


def create_vendor_bill_from_po(db: Session, purchase_order_id: int, payload) -> VendorBill:
    """
    Pre-fills VendorBill fields from the linked PurchaseOrder. The
    frontend is expected to have populated `payload` from the PO's own
    data (vendor, lines) before submitting; this function additionally
    enforces that the vendor matches and forces the purchase_order_id
    link server-side (never trusts the client for that association).
    """
    po = get_purchase_order(db, purchase_order_id)
    if po.status != DocumentStatus.CONFIRMED:
        raise InvalidTransitionError(
            f"Purchase Order must be CONFIRMED before creating a bill (current status: {po.status.value})"
        )
    if po.vendor_bill is not None:
        raise DuplicateBillError(f"Purchase Order {purchase_order_id} already has a Vendor Bill")
    if payload.vendor_id != po.vendor_id:
        raise InvalidVendorError("Vendor Bill vendor must match the Purchase Order's vendor")

    for line in payload.lines:
        _validate_product(db, line.product_id)

    bill = VendorBill(
        bill_no=sequence_service.next_bill_number(db, year=payload.bill_date.year),
        reference=payload.reference,
        vendor_id=payload.vendor_id,
        purchase_order_id=po.id,
        bill_date=payload.bill_date,
        due_date=payload.due_date,
        status=DocumentStatus.DRAFT,
    )
    db.add(bill)
    db.flush()

    default_expense_account = None
    for line in payload.lines:
        account_id = line.account_id
        if account_id is None:
            if default_expense_account is None:
                default_expense_account = accounting_engine.get_default_purchase_expense_account(db)
            account_id = default_expense_account.id

        total = line.qty * line.unit_price
        db.add(VendorBillLine(
            vendor_bill_id=bill.id,
            product_id=line.product_id,
            account_id=account_id,
            analytic_account_id=line.analytic_account_id,
            qty=line.qty,
            unit_price=line.unit_price,
            total=total,
        ))

    db.commit()
    db.refresh(bill)
    return bill


def confirm_vendor_bill(db: Session, vendor_bill_id: int) -> Tuple[VendorBill, List[str]]:
    """
    Sets status -> CONFIRMED, then calls accounting_engine to create
    exactly one Journal Entry (Debit Purchase Expense / Credit
    Creditors) -- the ONLY accounting call this function makes.

    Atomicity: the status change is staged (not committed) before the
    accounting_engine call; accounting_engine's own commit persists
    both together. If accounting_engine raises (unbalanced entry,
    missing control account, etc.), the pending status change is
    rolled back too -- no partial commit.
    """
    bill = get_vendor_bill(db, vendor_bill_id)
    if bill.status != DocumentStatus.DRAFT:
        raise InvalidTransitionError(
            f"Only DRAFT vendor bills can be confirmed (current status: {bill.status.value})"
        )

    bill.status = DocumentStatus.CONFIRMED
    try:
        accounting_engine.create_entry_for_vendor_bill_confirmation(db, bill.id)
    except Exception:
        db.rollback()
        raise

    warnings = []
    for line in bill.lines:
        if line.analytic_account_id:
            warning = budget_service.check_budget_warning(db, line.analytic_account_id, line.total)
            if warning:
                warnings.append(warning)

    return bill, warnings
