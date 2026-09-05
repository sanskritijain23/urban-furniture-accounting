"""
Sales Order routes. Confirming an SO does NOT create a Journal Entry
— see app.services.sales_service and accounting_engine.py.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.sales_order import SalesOrderCreate, SalesOrderResponse
from app.schemas.customer_invoice import CustomerInvoiceCreate, CustomerInvoiceResponse
from app.services import sales_service

router = APIRouter(prefix="/sales-orders", tags=["sales-orders"])


@router.get("/", response_model=list[SalesOrderResponse])
def list_sales_orders(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/", response_model=SalesOrderResponse)
def create_sales_order(payload: SalesOrderCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{so_id}", response_model=SalesOrderResponse)
def get_sales_order(so_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/{so_id}/confirm", response_model=SalesOrderResponse)
def confirm_sales_order(so_id: int, db: Session = Depends(get_db)):
    """No accounting entry created here — see sales_service.confirm_sales_order."""
    raise NotImplementedError


@router.post("/{so_id}/create-invoice", response_model=CustomerInvoiceResponse)
def create_invoice_from_so(so_id: int, payload: CustomerInvoiceCreate, db: Session = Depends(get_db)):
    raise NotImplementedError
