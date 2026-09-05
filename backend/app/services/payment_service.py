"""
Payment business logic — settles a VendorBill (payment_type=SEND) or
a CustomerInvoice (payment_type=RECEIVE).

IMPORTANT: this module must NOT create or modify JournalEntry /
JournalEntryLine rows directly. Call
app.services.accounting_engine.create_entry_for_payment instead.

Every confirmed Payment creates its OWN Journal Entry, separate from
the entry created when the underlying Bill/Invoice was confirmed.
"""
from sqlalchemy.orm import Session

from app.services import accounting_engine


def create_payment(db: Session, payload):
    """
    TODO:
      1. amount should default to the bill/invoice's remaining amount
         due (computed, see ledger_service) but the frontend/schema
         allows it to be overridden for partial payments.
      2. Persist Payment (status=DRAFT).
    """
    raise NotImplementedError


def confirm_payment(db: Session, payment_id: int):
    """
    TODO:
      1. Set Payment.status -> CONFIRMED.
      2. Call accounting_engine.create_entry_for_payment(db, payment_id)
         <-- the ONLY accounting call this function is allowed to make.
      3. Update the related VendorBill/CustomerInvoice.payment_status
         to PARTIAL or PAID based on cumulative payments vs line total.
    """
    raise NotImplementedError
