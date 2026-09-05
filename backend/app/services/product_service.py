from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.product import Product, ProductCategory


class DuplicateCategoryNameError(Exception):
    pass


class ProductNotFoundError(Exception):
    pass


class CategoryNotFoundError(Exception):
    pass


def list_categories(db: Session) -> list[ProductCategory]:
    return db.query(ProductCategory).order_by(ProductCategory.id).all()


def create_category(db: Session, name: str) -> ProductCategory:
    existing = db.query(ProductCategory).filter(ProductCategory.name == name).first()
    if existing is not None:
        raise DuplicateCategoryNameError(f"category '{name}' already exists")

    category = ProductCategory(name=name)
    db.add(category)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise DuplicateCategoryNameError(f"category '{name}' already exists") from exc
    db.refresh(category)
    return category


def _validate_category_id(db: Session, category_id: int | None) -> None:
    if category_id is None:
        return
    if db.query(ProductCategory).filter(ProductCategory.id == category_id).first() is None:
        raise CategoryNotFoundError(f"category {category_id} not found")


def list_products(db: Session) -> list[Product]:
    return db.query(Product).order_by(Product.id).all()


def get_product(db: Session, product_id: int) -> Product:
    product = db.query(Product).filter(Product.id == product_id).first()
    if product is None:
        raise ProductNotFoundError(f"Product {product_id} not found")
    return product


def create_product(db: Session, data: dict) -> Product:
    _validate_category_id(db, data.get("category_id"))

    product = Product(**data)
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


def update_product(db: Session, product_id: int, data: dict) -> Product:
    product = get_product(db, product_id)

    if "category_id" in data:
        _validate_category_id(db, data["category_id"])

    for field, value in data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)
    return product


def delete_product(db: Session, product_id: int) -> None:
    product = get_product(db, product_id)
    db.delete(product)
    db.commit()
