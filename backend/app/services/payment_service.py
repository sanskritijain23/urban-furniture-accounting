"""
Payment business logic -- settles a VendorBill (payment_type=SEND) or
a CustomerInvoice (payment_type=RECEIVE).

IMPORTANT: this module must NOT create or modify JournalEntry /
JournalEntryLine rows directly. Call
app.services.accounting_engine.create_entry_for_payment instead.

Every confirmed Payment creates its OWN Journal Entry, separate from
the entry created when the underlying Bill/Invoice was confirmed.
"""
from decimal import Decimal
from typing import List

from sqlalchemy.orm import Session

from app.models.customer_invoice import CustomerInvoice
from app.models.enums import (
    DocumentStatus, JournalEntrySourceType, PaymentStatus, PaymentType,
)
from app.models.payment import Payment
from app.models.vendor_bill import VendorBill
from app.services import accounting_engine


class PaymentNotFoundError(Exception):
    pass


class InvalidPaymentSourceError(Exception):
    pass


class InvalidPaymentAmountError(Exception):
    pass


class InvalidTransitionError(Exception):
    pass


ALLOWED_SOURCE_TYPES = (JournalEntrySourceType.VENDOR_BILL, JournalEntrySourceType.CUSTOMER_INVOICE)


def list_payments(db: Session) -> List[Payment]:
    return db.query(Payment).order_by(Payment.id).all()


def get_payment(db: Session, payment_id: int) -> Payment:
    payment = db.query(Payment).filter(Payment.id == payment_id).first()
    if payment is None:
        raise PaymentNotFoundError(f"Payment {payment_id} not found")
    return payment


def _get_source_document(db: Session, source_type: JournalEntrySourceType, source_id: int):
    if source_type == JournalEntrySourceType.VENDOR_BILL:
        doc = db.query(VendorBill).filter(VendorBill.id == source_id).first()
    else:
        doc = db.query(CustomerInvoice).filter(CustomerInvoice.id == source_id).first()
    if doc is None:
        raise InvalidPaymentSourceError(
            f"{source_type.value} {source_id} not found"
        )
    return doc


def get_amount_due(db: Session, source_type: JournalEntrySourceType, source_id: int) -> Decimal:
    doc = _get_source_document(db, source_type, source_id)
    total = sum((line.total or Decimal("0")) for line in doc.lines)

    confirmed_payments = (
        db.query(Payment)
        .filter(
            Payment.source_type == source_type,
            Payment.source_id == source_id,
            Payment.status == DocumentStatus.CONFIRMED,
        )
        .all()
    )
    paid = sum((p.amount or Decimal("0")) for p in confirmed_payments)
    return total - paid


def create_payment(db: Session, payload) -> Payment:
    if payload.source_type not in ALLOWED_SOURCE_TYPES:
        raise InvalidPaymentSourceError(
            "source_type must be VENDOR_BILL or CUSTOMER_INVOICE"
        )
    if payload.amount <= 0:
        raise InvalidPaymentAmountError("Payment amount must be greater than zero")

    doc = _get_source_document(db, payload.source_type, payload.source_id)
    if doc.status != DocumentStatus.CONFIRMED:
        raise InvalidPaymentSourceError(
            f"{payload.source_type.value} {payload.source_id} must be CONFIRMED before payment"
        )

    # Sanity-check payment direction matches source type.
    if payload.source_type == JournalEntrySourceType.VENDOR_BILL and payload.payment_type != PaymentType.SEND:
        raise InvalidPaymentSourceError("Vendor Bill payments must be payment_type=SEND")
    if payload.source_type == JournalEntrySourceType.CUSTOMER_INVOICE and payload.payment_type != PaymentType.RECEIVE:
        raise InvalidPaymentSourceError("Customer Invoice payments must be payment_type=RECEIVE")

    amount_due = get_amount_due(db, payload.source_type, payload.source_id)
    if payload.amount > amount_due:
        raise InvalidPaymentAmountError(
            f"Payment amount {payload.amount} exceeds amount due {amount_due}"
        )

    payment = Payment(
        payment_type=payload.payment_type,
        payment_via=payload.payment_via,
        date=payload.date,
        partner_id=payload.partner_id,
        amount=payload.amount,
        note=payload.note,
        status=DocumentStatus.DRAFT,
        source_type=payload.source_type,
        source_id=payload.source_id,
    )
    db.add(payment)
    db.commit()
    db.refresh(payment)
    return payment


def confirm_payment(db: Session, payment_id: int) -> Payment:
    """
    Sets Payment.status -> CONFIRMED, then calls accounting_engine to
    create a Journal Entry SEPARATE from the Bill/Invoice's own entry
    -- the ONLY accounting call this function makes. Updates the
    related document's payment_status to PARTIAL or PAID based on
    cumulative confirmed payments vs line total.

    Atomicity: status change staged before the accounting_engine call;
    its commit persists both, or neither if it raises.
    """
    payment = get_payment(db, payment_id)
    if payment.status != DocumentStatus.DRAFT:
        raise InvalidTransitionError(
            f"Only DRAFT payments can be confirmed (current status: {payment.status.value})"
        )

    payment.status = DocumentStatus.CONFIRMED
    try:
        accounting_engine.create_entry_for_payment(db, payment.id)
    except Exception:
        db.rollback()
        raise

    doc = _get_source_document(db, payment.source_type, payment.source_id)
    total = sum((line.total or Decimal("0")) for line in doc.lines)
    confirmed_payments = (
        db.query(Payment)
        .filter(
            Payment.source_type == payment.source_type,
            Payment.source_id == payment.source_id,
            Payment.status == DocumentStatus.CONFIRMED,
        )
        .all()
    )
    paid = sum((p.amount or Decimal("0")) for p in confirmed_payments)

    if paid >= total:
        doc.payment_status = PaymentStatus.PAID
    elif paid > 0:
        doc.payment_status = PaymentStatus.PARTIAL
    else:
        doc.payment_status = PaymentStatus.NOT_PAID
    db.commit()
    db.refresh(payment)

    return payment
