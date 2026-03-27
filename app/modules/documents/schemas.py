from pydantic import BaseModel, Field, HttpUrl
from datetime import datetime
from typing import Optional, List, Any
from enum import Enum

class DocumentVisibility(str, Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    ROLE_BASED = "role_based"

class DocumentBase(BaseModel):
    title: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    visibility: DocumentVisibility = DocumentVisibility.PRIVATE
    allowed_roles: Optional[List[str]] = []
    allowed_users: Optional[List[int]] = []

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(DocumentBase):
    pass

class DocumentResponse(DocumentBase):
    id: int
    filename: str
    original_name: str
    file_size: int
    mime_type: str
    version: int
    owner_id: int
    owner_name: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    download_url: Optional[str] = None
    
    class Config:
        from_attributes = True

class DocumentVersionResponse(BaseModel):
    id: int
    version: int
    filename: str
    file_size: int
    created_at: datetime
    download_url: str

class DocumentListResponse(BaseModel):
    items: List[DocumentResponse]
    total: int
    page: int
    size: int
    pages: int