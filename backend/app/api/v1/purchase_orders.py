"""
Purchase Order routes. Confirming a PO does NOT create a Journal
Entry — see app.services.purchase_service and accounting_engine.py
for the audited rule.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.purchase_order import PurchaseOrderCreate, PurchaseOrderResponse
from app.schemas.vendor_bill import VendorBillCreate, VendorBillResponse
from app.services import purchase_service

router = APIRouter(prefix="/purchase-orders", tags=["purchase-orders"])


@router.get("/", response_model=list[PurchaseOrderResponse])
def list_purchase_orders(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/", response_model=PurchaseOrderResponse)
def create_purchase_order(payload: PurchaseOrderCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{po_id}", response_model=PurchaseOrderResponse)
def get_purchase_order(po_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/{po_id}/confirm", response_model=PurchaseOrderResponse)
def confirm_purchase_order(po_id: int, db: Session = Depends(get_db)):
    """No accounting entry created here — see purchase_service.confirm_purchase_order."""
    raise NotImplementedError


@router.post("/{po_id}/create-bill", response_model=VendorBillResponse)
def create_bill_from_po(po_id: int, payload: VendorBillCreate, db: Session = Depends(get_db)):
    raise NotImplementedError
