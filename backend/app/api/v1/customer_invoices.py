"""
Customer Invoice routes. Confirming an Invoice DOES create a Journal
Entry (Debit Debtors / Credit Sales Income) -- delegated entirely to
app.services.sales_service.confirm_customer_invoice, which in turn
calls accounting_engine. This route module contains no accounting logic.

Contact Portal: a role=contact user may view and pay only invoices
belonging to their own customer contact record.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, ANY_AUTHENTICATED, require_role
from app.core.database import get_db
from app.models.enums import JournalEntrySourceType, PaymentType, UserRole
from app.models.user import User
from app.schemas.customer_invoice import CustomerInvoiceResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services import sales_service, payment_service

router = APIRouter(prefix="/customer-invoices", tags=["customer-invoices"])


def _to_response(db: Session, invoice) -> CustomerInvoiceResponse:
    response = CustomerInvoiceResponse.model_validate(invoice)
    response.amount_due = payment_service.get_amount_due(
        db, JournalEntrySourceType.CUSTOMER_INVOICE, invoice.id
    )
    return response


def _assert_contact_owns_invoice(current_user: User, invoice) -> None:
    if current_user.role == UserRole.CONTACT and invoice.customer_id != current_user.contact_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer Invoice not found")


@router.get("/", response_model=list[CustomerInvoiceResponse])
def list_customer_invoices(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ANY_AUTHENTICATED)),
):
    invoices = sales_service.list_customer_invoices(db)
    if current_user.role == UserRole.CONTACT:
        invoices = [i for i in invoices if i.customer_id == current_user.contact_id]
    return [_to_response(db, i) for i in invoices]


@router.get("/{invoice_id}", response_model=CustomerInvoiceResponse)
def get_customer_invoice(
    invoice_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ANY_AUTHENTICATED)),
):
    try:
        invoice = sales_service.get_customer_invoice(db, invoice_id)
    except sales_service.CustomerInvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer Invoice not found")

    _assert_contact_owns_invoice(current_user, invoice)
    return _to_response(db, invoice)


@router.post(
    "/{invoice_id}/confirm",
    response_model=CustomerInvoiceResponse,
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)
def confirm_customer_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Creates a Journal Entry via accounting_engine -- see sales_service."""
    try:
        invoice = sales_service.confirm_customer_invoice(db, invoice_id)
    except sales_service.CustomerInvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer Invoice not found")
    except sales_service.InvalidTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return _to_response(db, invoice)


@router.post("/{invoice_id}/pay", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def pay_customer_invoice(
    invoice_id: int,
    payload: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(*ANY_AUTHENTICATED)),
):
    """
    Amount defaults to Amount Due on the frontend; editable for
    partial payments. Creates a DRAFT Payment (source forced to this
    invoice server-side) -- POST /payments/{id}/confirm actually posts
    the Journal Entry. A contact user may only pay their own invoice.
    """
    try:
        invoice = sales_service.get_customer_invoice(db, invoice_id)
    except sales_service.CustomerInvoiceNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer Invoice not found")

    _assert_contact_owns_invoice(current_user, invoice)

    payload.source_type = JournalEntrySourceType.CUSTOMER_INVOICE
    payload.source_id = invoice_id
    payload.payment_type = PaymentType.RECEIVE
    payload.partner_id = invoice.customer_id

    try:
        return payment_service.create_payment(db, payload)
    except (payment_service.InvalidPaymentSourceError, payment_service.InvalidPaymentAmountError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
