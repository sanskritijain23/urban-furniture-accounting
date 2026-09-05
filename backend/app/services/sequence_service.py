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
"""
from sqlalchemy.orm import Session


def next_po_number(db: Session) -> str:
    """TODO: e.g. SELECT COUNT(*)+1 FROM purchase_orders, zero-padded to 4 digits -> 'PO0001'."""
    raise NotImplementedError


def next_bill_number(db: Session, year: int) -> str:
    """TODO: format 'Bill/{year}/{seq:04d}', sequence scoped per year."""
    raise NotImplementedError


def next_so_number(db: Session) -> str:
    """TODO: e.g. zero-padded to 5 digits -> 'SO00001'."""
    raise NotImplementedError


def next_invoice_number(db: Session, year: int) -> str:
    """TODO: format 'INV/{year}/{seq:04d}', sequence scoped per year."""
    raise NotImplementedError
