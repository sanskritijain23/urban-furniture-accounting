"""
Auto-numbering sequence service.

Approved formats (audited from MVP mockups):
    Purchase Order    -> PO0001
    Vendor Bill       -> Bill/2026/0001
    Sales Order       -> SO00001
    Customer Invoice  -> INV/2026/0001

These numbers are generated server-side and are NEVER accepted from
the client. They are distinct from the free-text `reference` field on
Bill/Invoice, which the user can type manually.

Concurrency note: numbering is COUNT-based (per the original TODO),
with a collision-retry loop as a defensive backstop. This is adequate
for a single-presenter hackathon demo but is not a fully
concurrency-safe allocator (no SELECT ... FOR UPDATE / DB sequence) --
under genuinely simultaneous requests from multiple users, a race is
still theoretically possible. Flagged here rather than silently
assumed away.
"""
from sqlalchemy.orm import Session

from app.models.purchase_order import PurchaseOrder
from app.models.vendor_bill import VendorBill
from app.models.sales_order import SalesOrder
from app.models.customer_invoice import CustomerInvoice


def next_po_number(db: Session) -> str:
    count = db.query(PurchaseOrder).count()
    candidate = f"PO{count + 1:04d}"
    while db.query(PurchaseOrder).filter_by(po_no=candidate).first() is not None:
        count += 1
        candidate = f"PO{count + 1:04d}"
    return candidate


def next_bill_number(db: Session, year: int) -> str:
    prefix = f"Bill/{year}/"
    count = db.query(VendorBill).filter(VendorBill.bill_no.like(f"{prefix}%")).count()
    candidate = f"{prefix}{count + 1:04d}"
    while db.query(VendorBill).filter_by(bill_no=candidate).first() is not None:
        count += 1
        candidate = f"{prefix}{count + 1:04d}"
    return candidate


def next_so_number(db: Session) -> str:
    count = db.query(SalesOrder).count()
    candidate = f"SO{count + 1:05d}"
    while db.query(SalesOrder).filter_by(so_no=candidate).first() is not None:
        count += 1
        candidate = f"SO{count + 1:05d}"
    return candidate


def next_invoice_number(db: Session, year: int) -> str:
    prefix = f"INV/{year}/"
    count = db.query(CustomerInvoice).filter(CustomerInvoice.invoice_no.like(f"{prefix}%")).count()
    candidate = f"{prefix}{count + 1:04d}"
    while db.query(CustomerInvoice).filter_by(invoice_no=candidate).first() is not None:
        count += 1
        candidate = f"{prefix}{count + 1:04d}"
    return candidate
