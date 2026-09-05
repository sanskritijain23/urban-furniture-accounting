"""
Customer Invoice routes. Confirming an Invoice DOES create a Journal
Entry (Debit Debtors / Credit Sales Income) — delegated entirely to
app.services.sales_service.confirm_customer_invoice, which in turn
calls accounting_engine. This route module contains no accounting logic.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.customer_invoice import CustomerInvoiceResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services import sales_service, payment_service

router = APIRouter(prefix="/customer-invoices", tags=["customer-invoices"])


@router.get("/", response_model=list[CustomerInvoiceResponse])
def list_customer_invoices(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{invoice_id}", response_model=CustomerInvoiceResponse)
def get_customer_invoice(invoice_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/{invoice_id}/confirm", response_model=CustomerInvoiceResponse)
def confirm_customer_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """Creates a Journal Entry via accounting_engine — see sales_service."""
    raise NotImplementedError


@router.post("/{invoice_id}/pay", response_model=PaymentResponse)
def pay_customer_invoice(invoice_id: int, payload: PaymentCreate, db: Session = Depends(get_db)):
    """Amount defaults to Amount Due on the frontend; editable for
    partial payments. Creates a SEPARATE Journal Entry from the invoice's own."""
    raise NotImplementedError
