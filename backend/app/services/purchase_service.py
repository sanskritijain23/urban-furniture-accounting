"""
Purchase-side business logic: Purchase Order -> Vendor Bill.

IMPORTANT: this module must NOT create or modify JournalEntry /
JournalEntryLine rows directly. When a Vendor Bill is confirmed, call
app.services.accounting_engine.create_entry_for_vendor_bill_confirmation
instead of computing debits/credits here.

Confirming a Purchase Order does NOT create any accounting entry —
only Vendor Bill confirmation does.
"""
from sqlalchemy.orm import Session

from app.services import accounting_engine, sequence_service


def create_purchase_order(db: Session, payload):
    """
    TODO:
      1. Generate po_no via sequence_service.next_po_number().
      2. Persist PurchaseOrder + PurchaseOrderLine rows (status=DRAFT).
      3. Return the created PurchaseOrder.
    """
    raise NotImplementedError


def confirm_purchase_order(db: Session, purchase_order_id: int):
    """
    TODO:
      1. Set status -> CONFIRMED.
      2. Check committed budget for each line's analytic_account_id
         (see budget_service.check_budget_warning) and surface a
         NON-BLOCKING warning if exceeded — do not raise/block here.
      3. Does NOT call accounting_engine — POs never create entries.
    """
    raise NotImplementedError


def create_vendor_bill_from_po(db: Session, purchase_order_id: int, payload):
    """
    TODO: pre-fill VendorBill fields (vendor, product/price/qty lines)
    from the linked PurchaseOrder, per the mockup's "Create Bill"
    button behaviour.
    """
    raise NotImplementedError


def confirm_vendor_bill(db: Session, vendor_bill_id: int):
    """
    TODO:
      1. Set VendorBill.status -> CONFIRMED.
      2. Generate bill_no via sequence_service.next_bill_number() if
         not already set.
      3. Call accounting_engine.create_entry_for_vendor_bill_confirmation(
             db, vendor_bill_id
         )  <-- the ONLY accounting call this function is allowed to make.
      4. Optionally check budget warning (non-blocking), same as POs.
    """
    raise NotImplementedError
