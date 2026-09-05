from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel

from app.models.enums import DocumentStatus, PaymentType, PaymentVia, JournalEntrySourceType
from app.schemas.common import ORMBase


class PaymentCreate(BaseModel):
    payment_type: PaymentType          # send / receive
    payment_via: PaymentVia            # cash / bank
    date: date
    partner_id: int
    amount: Decimal                    # defaults to Amount Due on the frontend, editable
    note: Optional[str] = None
    source_type: JournalEntrySourceType  # VENDOR_BILL or CUSTOMER_INVOICE
    source_id: int
    # TODO (payment_service.py): validate source_type is one of the
    # two allowed values, and that amount > 0.


class PaymentResponse(ORMBase):
    id: int
    payment_type: PaymentType
    payment_via: PaymentVia
    date: date
    partner_id: int
    amount: Decimal
    note: Optional[str] = None
    status: DocumentStatus
    source_type: JournalEntrySourceType
    source_id: int
