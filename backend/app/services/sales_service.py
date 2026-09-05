"""
Sales-side business logic: Sales Order -> Customer Invoice.

IMPORTANT: this module must NOT create or modify JournalEntry /
JournalEntryLine rows directly. When a Customer Invoice is confirmed,
call
app.services.accounting_engine.create_entry_for_customer_invoice_confirmation
instead of computing debits/credits here.

Confirming a Sales Order does NOT create any accounting entry — only
Customer Invoice confirmation does.
"""
from sqlalchemy.orm import Session

from app.services import accounting_engine, sequence_service


def create_sales_order(db: Session, payload):
    """
    TODO:
      1. Generate so_no via sequence_service.next_so_number().
      2. Persist SalesOrder + SalesOrderLine rows (status=DRAFT).
    """
    raise NotImplementedError


def confirm_sales_order(db: Session, sales_order_id: int):
    """
    TODO: set status -> CONFIRMED. Does NOT call accounting_engine —
    SOs never create entries.
    """
    raise NotImplementedError


def create_invoice_from_so(db: Session, sales_order_id: int, payload):
    """
    TODO: pre-fill CustomerInvoice fields (customer, product/price/qty
    lines) from the linked SalesOrder, per the mockup's invoice
    generation flow.
    """
    raise NotImplementedError


def confirm_customer_invoice(db: Session, invoice_id: int):
    """
    TODO:
      1. Set CustomerInvoice.status -> CONFIRMED.
      2. Generate invoice_no via sequence_service.next_invoice_number()
         if not already set.
      3. Call accounting_engine.create_entry_for_customer_invoice_confirmation(
             db, invoice_id
         )  <-- the ONLY accounting call this function is allowed to make.
    """
    raise NotImplementedError
