from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Float, Boolean, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class StockMovementType(str, enum.Enum):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"
    RETURN = "return"

class Category(Base):
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    

    products = relationship("Product", back_populates="category")
    children = relationship("Category", backref="parent", remote_side=[id])

class Product(Base):
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category_id = Column(Integer, ForeignKey("category.id"), nullable=True)
    unit_price = Column(Float, nullable=False)
    cost_price = Column(Float, nullable=True)
    current_stock = Column(Integer, default=0)
    min_stock_level = Column(Integer, default=0)
    max_stock_level = Column(Integer, nullable=True)
    reorder_level = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    

    category = relationship("Category", back_populates="products")
    movements = relationship("StockMovement", back_populates="product")
    alerts = relationship("LowStockAlert", back_populates="product")

class StockMovement(Base):
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    movement_type = Column(SQLEnum(StockMovementType), nullable=False)
    reference_type = Column(String(50), nullable=True)  # invoice, purchase_order, etc.
    reference_id = Column(Integer, nullable=True)
    notes = Column(Text, nullable=True)
    performed_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    

    product = relationship("Product", back_populates="movements")
    performed_by = relationship("User")

class LowStockAlert(Base):
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    current_stock = Column(Integer, nullable=False)
    reorder_level = Column(Integer, nullable=False)
    status = Column(String(20), default="pending")  # pending, sent, resolved
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime, nullable=True)
    

    product = relationship("Product", back_populates="alerts")