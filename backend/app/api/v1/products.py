"""
Product master routes. Supports List + Kanban views (same data, two
frontend layouts). ProductCategory can be created inline/on-the-fly.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductCategoryCreate, ProductCategoryResponse,
)

router = APIRouter(prefix="/products", tags=["products"])


@router.get("/", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/", response_model=ProductResponse)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    raise NotImplementedError


@router.post("/categories", response_model=ProductCategoryResponse)
def create_category(payload: ProductCategoryCreate, db: Session = Depends(get_db)):
    """Inline/on-the-fly category creation, as shown in the MVP mockup."""
    raise NotImplementedError


@router.get("/categories", response_model=list[ProductCategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    raise NotImplementedError
