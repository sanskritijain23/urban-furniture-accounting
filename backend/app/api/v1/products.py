"""
Product master routes. Supports List + Kanban views (same data, two
frontend layouts). ProductCategory can be created inline/on-the-fly.

NOTE: the /categories routes are declared before /{product_id} so
FastAPI doesn't try to parse "categories" as an int product_id.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth.permissions import ADMIN_OR_ACCOUNTANT, require_role
from app.core.database import get_db
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse,
    ProductCategoryCreate, ProductCategoryResponse,
)
from app.services import product_service

router = APIRouter(
    prefix="/products",
    tags=["products"],
    dependencies=[Depends(require_role(*ADMIN_OR_ACCOUNTANT))],
)


@router.get("/categories", response_model=list[ProductCategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    return product_service.list_categories(db)


@router.post("/categories", response_model=ProductCategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(payload: ProductCategoryCreate, db: Session = Depends(get_db)):
    """Inline/on-the-fly category creation, as shown in the MVP mockup."""
    try:
        return product_service.create_category(db, payload.name)
    except product_service.DuplicateCategoryNameError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.get("/", response_model=list[ProductResponse])
def list_products(db: Session = Depends(get_db)):
    return product_service.list_products(db)


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(payload: ProductCreate, db: Session = Depends(get_db)):
    try:
        return product_service.create_product(db, payload.model_dump())
    except product_service.CategoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    try:
        return product_service.get_product(db, product_id)
    except product_service.ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, payload: ProductUpdate, db: Session = Depends(get_db)):
    try:
        return product_service.update_product(
            db, product_id, payload.model_dump(exclude_unset=True)
        )
    except product_service.ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
    except product_service.CategoryNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    try:
        product_service.delete_product(db, product_id)
    except product_service.ProductNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")
