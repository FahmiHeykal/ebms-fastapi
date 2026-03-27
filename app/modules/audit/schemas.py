from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict, Any

class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int]
    username: Optional[str]
    action: str
    module: str
    record_id: Optional[str]
    old_data: Optional[Dict[str, Any]]
    new_data: Optional[Dict[str, Any]]
    ip_address: Optional[str]
    user_agent: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class AuditLogListResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    size: int
    pages: int