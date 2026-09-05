"""
Vendor Bill routes. Confirming a Vendor Bill DOES create a Journal
Entry (Debit Purchase Expense / Credit Creditors) — delegated entirely
to app.services.purchase_service.confirm_vendor_bill, which in turn
calls accounting_engine. This route module contains no accounting logic.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.vendor_bill import VendorBillResponse
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services import purchase_service, payment_service

router = APIRouter(prefix="/vendor-bills", tags=["vendor-bills"])


@router.get("/", response_model=list[VendorBillResponse])
def list_vendor_bills(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{bill_id}", response_model=VendorBillResponse)
def get_vendor_bill(bill_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/{bill_id}/confirm", response_model=VendorBillResponse)
def confirm_vendor_bill(bill_id: int, db: Session = Depends(get_db)):
    """Creates a Journal Entry via accounting_engine — see purchase_service."""
    raise NotImplementedError


@router.post("/{bill_id}/pay", response_model=PaymentResponse)
def pay_vendor_bill(bill_id: int, payload: PaymentCreate, db: Session = Depends(get_db)):
    """Amount defaults to Amount Due on the frontend; editable for
    partial payments. Creates a SEPARATE Journal Entry from the bill's own."""
    raise NotImplementedError
