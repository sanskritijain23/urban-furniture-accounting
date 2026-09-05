"""
Standalone Payment routes (for cases not reached via the
/vendor-bills/{id}/pay or /customer-invoices/{id}/pay convenience
routes). Payment is modeled as a reusable component/modal on the
frontend, not necessarily its own page.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.payment import PaymentCreate, PaymentResponse
from app.services import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.get("/", response_model=list[PaymentResponse])
def list_payments(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
def confirm_payment(payment_id: int, db: Session = Depends(get_db)):
    """Creates a SEPARATE Journal Entry via accounting_engine — see payment_service."""
    raise NotImplementedError
