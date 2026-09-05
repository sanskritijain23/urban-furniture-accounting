from typing import Optional
from decimal import Decimal
from pydantic import BaseModel

from app.models.enums import ProductType
from app.schemas.common import ORMBase


class ProductCategoryCreate(BaseModel):
    """Categories can be created inline/on-the-fly from the Product
    form — this schema supports that lightweight creation path."""
    name: str


class ProductCategoryResponse(ORMBase):
    id: int
    name: str


class ProductBase(BaseModel):
    name: str
    type: ProductType
    sales_price: Decimal
    cost: Decimal
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[ProductType] = None
    sales_price: Optional[Decimal] = None
    cost: Optional[Decimal] = None
    category_id: Optional[int] = None


class ProductResponse(ProductBase, ORMBase):
    id: int
