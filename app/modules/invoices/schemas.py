from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from enum import Enum


class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    PENDING = "pending"
    PAID = "paid"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class InvoiceItemBase(BaseModel):
    description: str = Field(..., max_length=500)
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    discount: float = Field(0, ge=0)


class InvoiceItemCreate(InvoiceItemBase):
    pass


class InvoiceItemResponse(InvoiceItemBase):
    id: int
    total: float

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    customer_name: str = Field(..., max_length=255)
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    tax_rate: float = Field(0, ge=0)
    discount: float = Field(0, ge=0)
    due_date: Optional[datetime] = None
    notes: Optional[str] = None
    terms: Optional[str] = None


class InvoiceCreate(InvoiceBase):
    items: List[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    customer_phone: Optional[str] = None
    customer_address: Optional[str] = None
    status: Optional[InvoiceStatus] = None
    notes: Optional[str] = None
    terms: Optional[str] = None


class InvoiceResponse(InvoiceBase):
    id: int
    invoice_number: str
    subtotal: float
    tax_amount: float
    total: float
    status: InvoiceStatus
    issue_date: datetime
    paid_at: Optional[datetime] = None
    created_by_id: int
    created_by_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    items: List[InvoiceItemResponse]

    class Config:
        from_attributes = True


class InvoiceListResponse(BaseModel):
    items: List[InvoiceResponse]
    total: int
    page: int
    size: int
    pages: int


class PaymentCreate(BaseModel):
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., max_length=50)
    reference_number: Optional[str] = None
    notes: Optional[str] = None


class PaymentResponse(BaseModel):
    id: int
    invoice_id: int
    amount: float
    payment_method: str
    reference_number: Optional[str]
    notes: Optional[str]
    paid_at: datetime
    received_by_id: int
    received_by_name: str

    class Config:
        from_attributes = True