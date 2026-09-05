"""
Sales Order routes. Confirming an SO does NOT create a Journal Entry
-- see app.services.sales_service and accounting_engine.py for the
audited rule. Sales Orders are an internal document -- never exposed
to Contact-role users (they only see Invoices).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, require_role
from app.core.database import get_db
from app.schemas.sales_order import SalesOrderCreate, SalesOrderResponse
from app.schemas.customer_invoice import CustomerInvoiceCreate, CustomerInvoiceResponse
from app.services import sales_service

router = APIRouter(
    prefix="/sales-orders",
    tags=["sales-orders"],
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)


@router.get("/", response_model=list[SalesOrderResponse])
def list_sales_orders(db: Session = Depends(get_db)):
    return sales_service.list_sales_orders(db)


@router.post("/", response_model=SalesOrderResponse, status_code=status.HTTP_201_CREATED)
def create_sales_order(payload: SalesOrderCreate, db: Session = Depends(get_db)):
    try:
        return sales_service.create_sales_order(db, payload)
    except (sales_service.InvalidCustomerError, sales_service.ProductNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{so_id}", response_model=SalesOrderResponse)
def get_sales_order(so_id: int, db: Session = Depends(get_db)):
    try:
        return sales_service.get_sales_order(db, so_id)
    except sales_service.SalesOrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales Order not found")


@router.post("/{so_id}/confirm", response_model=SalesOrderResponse)
def confirm_sales_order(so_id: int, db: Session = Depends(get_db)):
    try:
        return sales_service.confirm_sales_order(db, so_id)
    except sales_service.SalesOrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales Order not found")
    except sales_service.InvalidTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/{so_id}/create-invoice", response_model=CustomerInvoiceResponse, status_code=status.HTTP_201_CREATED)
def create_invoice_from_so(so_id: int, payload: CustomerInvoiceCreate, db: Session = Depends(get_db)):
    try:
        return sales_service.create_invoice_from_so(db, so_id, payload)
    except sales_service.SalesOrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sales Order not found")
    except (
        sales_service.InvalidTransitionError,
        sales_service.DuplicateInvoiceError,
        sales_service.InvalidCustomerError,
        sales_service.ProductNotFoundError,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
