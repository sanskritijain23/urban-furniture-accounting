from sqlalchemy import Column, Integer, String, Numeric, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from app.core.database import Base
from app.models.enums import ProductType


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), unique=True, nullable=False)

    products = relationship("Product", back_populates="category")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(255), nullable=False)
    type = Column(Enum(ProductType), nullable=False)

    sales_price = Column(Numeric(12, 2), nullable=False)
    cost = Column(Numeric(12, 2), nullable=False)

    category_id = Column(Integer, ForeignKey("product_categories.id"), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    category = relationship("ProductCategory", back_populates="products")

    def __repr__(self) -> str:
        return f"<Product id={self.id} name={self.name}>"
