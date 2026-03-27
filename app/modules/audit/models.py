from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Index
from sqlalchemy.sql import func
from app.core.database import Base

class AuditLog(Base):
    __tablename__ = "audit_log"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)  # Can be null for system actions
    username = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)
    module = Column(String(100), nullable=False)
    record_id = Column(String(100), nullable=True)
    old_data = Column(JSON, nullable=True)
    new_data = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        Index('idx_audit_user', 'user_id'),
        Index('idx_audit_module', 'module'),
        Index('idx_audit_action', 'action'),
        Index('idx_audit_created', 'created_at'),
    )