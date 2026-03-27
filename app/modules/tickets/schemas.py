from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from typing import Optional, List
from enum import Enum

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TicketBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    priority: TicketPriority = TicketPriority.MEDIUM

class TicketCreate(TicketBase):
    assigned_to_id: Optional[int] = None

class TicketUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[TicketStatus] = None
    priority: Optional[TicketPriority] = None
    assigned_to_id: Optional[int] = None

class TicketResponse(TicketBase):
    id: int
    status: TicketStatus
    created_by_id: int
    created_by_name: Optional[str] = None  # Make optional with default
    assigned_to_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class TicketListResponse(BaseModel):
    items: List[TicketResponse]
    total: int
    page: int
    size: int
    pages: int

class TicketCommentCreate(BaseModel):
    content: str = Field(..., min_length=1)

class TicketCommentResponse(BaseModel):
    id: int
    ticket_id: int
    user_id: int
    user_name: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True