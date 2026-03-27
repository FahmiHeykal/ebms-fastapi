from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class StockMovementType(str, Enum):
    IN = "in"
    OUT = "out"
    ADJUSTMENT = "adjustment"
    RETURN = "return"

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    parent_id: Optional[int] = None

class CategoryCreate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class ProductBase(BaseModel):
    sku: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_price: float = Field(..., gt=0)
    cost_price: Optional[float] = None
    current_stock: int = Field(0, ge=0)
    min_stock_level: int = Field(0, ge=0)
    max_stock_level: Optional[int] = None
    reorder_level: int = Field(10, ge=0)
    is_active: bool = True

class ProductCreate(ProductBase):
    pass

class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1)
    description: Optional[str] = None
    category_id: Optional[int] = None
    unit_price: Optional[float] = Field(None, gt=0)
    cost_price: Optional[float] = None
    current_stock: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    max_stock_level: Optional[int] = None
    reorder_level: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

class ProductResponse(ProductBase):
    id: int
    category_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    total: int
    page: int
    size: int
    pages: int

class StockMovementRequest(BaseModel):
    product_id: int
    quantity: int
    movement_type: StockMovementType
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    notes: Optional[str] = None

class StockMovementResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    quantity: int
    movement_type: StockMovementType
    reference_type: Optional[str]
    reference_id: Optional[int]
    notes: Optional[str]
    performed_by_id: int
    performed_by_name: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class LowStockAlertResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    current_stock: int
    reorder_level: int
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]
    
    class Config:
        from_attributes = True