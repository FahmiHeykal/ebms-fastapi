from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any, List

class NotificationBase(BaseModel):
    title: str
    content: str
    type: str = "system"
    priority: str = "normal"
    data: Optional[Dict[str, Any]] = None

class NotificationCreate(NotificationBase):
    user_id: int

class NotificationResponse(NotificationBase):
    id: int
    user_id: int
    is_read: bool
    read_at: Optional[datetime]
    sent_at: Optional[datetime]
    delivered_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True

class NotificationListResponse(BaseModel):
    items: List[NotificationResponse]
    total: int
    page: int
    size: int
    pages: int