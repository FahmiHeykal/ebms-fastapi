from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum

class DocumentVisibility(str, enum.Enum):
    PRIVATE = "private"
    PUBLIC = "public"
    ROLE_BASED = "role_based"

class Document(Base):
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    version = Column(Integer, default=1)
    

    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    

    visibility = Column(SQLEnum(DocumentVisibility), default=DocumentVisibility.PRIVATE)
    allowed_roles = Column(JSON, default=list)  # For role-based visibility
    allowed_users = Column(JSON, default=list)  # For private sharing
    

    owner_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("document.id"), nullable=True)  # For versioning
    

    is_deleted = Column(Boolean, default=False)
    deleted_at = Column(DateTime, nullable=True)
    

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    

    owner = relationship("User", foreign_keys=[owner_id])
    versions = relationship("Document", backref="parent", remote_side=[id])
    audit_logs = relationship("DocumentAudit", back_populates="document")

class DocumentAudit(Base):
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("document.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    action = Column(String(50), nullable=False)  # upload, download, delete, update, view
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    

    document = relationship("Document", back_populates="audit_logs")
    user = relationship("User")