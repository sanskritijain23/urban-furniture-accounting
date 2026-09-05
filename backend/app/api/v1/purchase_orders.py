"""
Purchase Order routes. Confirming a PO does NOT create a Journal
Entry -- see app.services.purchase_service and accounting_engine.py
for the audited rule. Purchase Orders are an internal procurement
document -- never exposed to Contact-role users (they only see Bills).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, require_role
from app.core.database import get_db
from app.schemas.purchase_order import (
    PurchaseOrderCreate, PurchaseOrderResponse, PurchaseOrderConfirmResponse,
)
from app.schemas.vendor_bill import VendorBillCreate, VendorBillResponse
from app.services import purchase_service

router = APIRouter(
    prefix="/purchase-orders",
    tags=["purchase-orders"],
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)


@router.get("/", response_model=list[PurchaseOrderResponse])
def list_purchase_orders(db: Session = Depends(get_db)):
    return purchase_service.list_purchase_orders(db)


@router.post("/", response_model=PurchaseOrderResponse, status_code=status.HTTP_201_CREATED)
def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db)):
    try:
        return purchase_service.create_purchase_order(db, payload)
    except (purchase_service.InvalidVendorError, purchase_service.ProductNotFoundError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{po_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    try:
        return purchase_service.get_purchase_order(db, po_id)
    except purchase_service.PurchaseOrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase Order not found")


@router.post("/{po_id}/confirm", response_model=PurchaseOrderConfirmResponse)
def confirm_purchase_order(po_id: int, db: Session = Depends(get_db)):
    """No accounting entry created here -- see purchase_service.confirm_purchase_order.
    Budget warnings (if any) are informational only and never block confirmation."""
    try:
        po, warnings = purchase_service.confirm_purchase_order(db, po_id)
    except purchase_service.PurchaseOrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase Order not found")
    except purchase_service.InvalidTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    return PurchaseOrderConfirmResponse(
        **PurchaseOrderResponse.model_validate(po).model_dump(),
        budget_warnings=warnings,
    )


@router.post("/{po_id}/create-bill", response_model=VendorBillResponse, status_code=status.HTTP_201_CREATED)
def create_bill_from_po(po_id: int, payload: VendorBillCreate, db: Session = Depends(get_db)):
    try:
        return purchase_service.create_vendor_bill_from_po(db, po_id, payload)
    except purchase_service.PurchaseOrderNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Purchase Order not found")
    except (
        purchase_service.InvalidTransitionError,
        purchase_service.DuplicateBillError,
        purchase_service.InvalidVendorError,
        purchase_service.ProductNotFoundError,
    ) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
