"""
Vendor Bill routes. Confirming a Vendor Bill DOES create a Journal
Entry (Debit Purchase Expense / Credit Creditors) -- delegated entirely
to app.services.purchase_service.confirm_vendor_bill, which in turn
calls accounting_engine. This route module contains no accounting logic.

Contact Portal: a role=contact user may view (not list broadly) and
pay only bills belonging to their own vendor contact record.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.auth.permissions import ADMIN_OR_ACCOUNTANT, ANY_AUTHENTICATED, require_role
from app.core.database import get_db
from app.models.enums import JournalEntrySourceType, PaymentType, UserRole
from app.models.user import User
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.schemas.vendor_bill import VendorBillResponse, VendorBillConfirmResponse
from app.services import purchase_service, payment_service

router = APIRouter(prefix="/vendor-bills", tags=["vendor-bills"])


def _to_response(db: Session, bill) -> VendorBillResponse:
    response = VendorBillResponse.model_validate(bill)
    response.amount_due = payment_service.get_amount_due(
        db, JournalEntrySourceType.VENDOR_BILL, bill.id
    )
    return response


def _assert_contact_owns_bill(current_user: User, bill) -> None:
    if current_user.role == UserRole.CONTACT and bill.vendor_id != current_user.contact_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor Bill not found")


@router.get("/", response_model=list[VendorBillResponse])
def list_vendor_bills(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ANY_AUTHENTICATED)),
):
    bills = purchase_service.list_vendor_bills(db)
    if current_user.role == UserRole.CONTACT:
        bills = [b for b in bills if b.vendor_id == current_user.contact_id]
    return [_to_response(db, b) for b in bills]


@router.get("/{bill_id}", response_model=VendorBillResponse)
def get_vendor_bill(
    bill_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ANY_AUTHENTICATED)),
):
    try:
        bill = purchase_service.get_vendor_bill(db, bill_id)
    except purchase_service.VendorBillNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor Bill not found")

    _assert_contact_owns_bill(current_user, bill)
    return _to_response(db, bill)


@router.post(
    "/{bill_id}/confirm",
    response_model=VendorBillConfirmResponse,
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)
def confirm_vendor_bill(bill_id: int, db: Session = Depends(get_db)):
    """Creates a Journal Entry via accounting_engine -- see purchase_service."""
    try:
        bill, warnings = purchase_service.confirm_vendor_bill(db, bill_id)
    except purchase_service.VendorBillNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor Bill not found")
    except purchase_service.InvalidTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        # accounting_engine errors (UnbalancedEntryError, MissingControlAccountError,
        # MissingJournalError) -- always surfaced as a clear 400, never a raw 500.
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    response = VendorBillConfirmResponse.model_validate(bill)
    response.budget_warnings = warnings
    response.amount_due = payment_service.get_amount_due(
        db, JournalEntrySourceType.VENDOR_BILL, bill.id
    )
    return response


@router.post("/{bill_id}/pay", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def pay_vendor_bill(
    bill_id: int,
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ANY_AUTHENTICATED)),
):
    """
    Amount defaults to Amount Due on the frontend; editable for
    partial payments. Creates a DRAFT Payment (source forced to this
    bill server-side, never trusted from the client) -- a separate
    call to POST /payments/{id}/confirm actually posts the Journal
    Entry, mirroring the Draft/Confirm pattern used everywhere else.
    A contact user may only pay their own bill.
    """
    try:
        bill = purchase_service.get_vendor_bill(db, bill_id)
    except purchase_service.VendorBillNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vendor Bill not found")

    _assert_contact_owns_bill(current_user, bill)

    payload.source_type = JournalEntrySourceType.VENDOR_BILL
    payload.source_id = bill_id
    payload.payment_type = PaymentType.SEND
    payload.partner_id = bill.vendor_id

    try:
        return payment_service.create_payment(db, payload)
    except (payment_service.InvalidPaymentSourceError, payment_service.InvalidPaymentAmountError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
