"""
Payment routes. Confirming a Payment creates a SEPARATE Journal Entry
via accounting_engine (never merged with the Bill/Invoice's own entry)
-- delegated entirely to app.services.payment_service. Payments
themselves are created via POST /vendor-bills/{id}/pay or
POST /customer-invoices/{id}/pay, which set the source correctly;
there is no bare POST / here by design (a payment always belongs to a
specific bill or invoice).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, ANY_AUTHENTICATED, require_role
from app.core.database import get_db
from app.models.enums import JournalEntrySourceType, UserRole
from app.models.user import User
from app.schemas.payment import PaymentResponse
from app.services import payment_service, purchase_service, sales_service

router = APIRouter(prefix="/payments", tags=["payments"])


def _assert_contact_owns_payment(db: Session, current_user: User, payment) -> None:
    if current_user.role != UserRole.CONTACT:
        return
    if payment.source_type == JournalEntrySourceType.VENDOR_BILL:
        bill = purchase_service.get_vendor_bill(db, payment.source_id)
        owner_contact_id = bill.vendor_id
    else:
        invoice = sales_service.get_customer_invoice(db, payment.source_id)
        owner_contact_id = invoice.customer_id
    if owner_contact_id != current_user.contact_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")


@router.get("/", response_model=list[PaymentResponse])
def list_payments(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ANY_AUTHENTICATED)),
):
    payments = payment_service.list_payments(db)
    if current_user.role == UserRole.CONTACT:
        visible = []
        for p in payments:
            try:
                _assert_contact_owns_payment(db, current_user, p)
                visible.append(p)
            except HTTPException:
                continue
        return visible
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ANY_AUTHENTICATED)),
):
    try:
        payment = payment_service.get_payment(db, payment_id)
    except payment_service.PaymentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    _assert_contact_owns_payment(db, current_user, payment)
    return payment


@router.post(
    "/{payment_id}/confirm",
    response_model=PaymentResponse,
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)
def confirm_payment(payment_id: int, db: Session = Depends(get_db)):
    """Creates a SEPARATE Journal Entry via accounting_engine -- see payment_service."""
    try:
        return payment_service.confirm_payment(db, payment_id)
    except payment_service.PaymentNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
    except payment_service.InvalidTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
