from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from app.modules.audit.models import AuditLog
import json
import logging

logger = logging.getLogger(__name__)

def json_serializer(obj):
    """Custom JSON serializer for objects not serializable by default json code"""
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

class AuditService:
    @staticmethod
    async def create_audit_table():
        """Ensure audit table exists (handled by Alembic)"""
        pass
    
    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: int,
        username: str,
        action: str,
        module: str,
        record_id: str = None,
        old_data: dict = None,
        new_data: dict = None,
        ip_address: str = None,
        user_agent: str = None
    ) -> AuditLog:
        """Log audit action"""

        if old_data:
            old_data = json.loads(json.dumps(old_data, default=json_serializer))
        if new_data:
            new_data = json.loads(json.dumps(new_data, default=json_serializer))
        
        audit_log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            module=module,
            record_id=record_id,
            old_data=old_data,
            new_data=new_data,
            ip_address=ip_address,
            user_agent=user_agent
        )
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        return audit_log
    
    @staticmethod
    async def get_audit_logs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[int] = None,
        module: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[AuditLog], int]:
        """Get audit logs with filters"""
        query = select(AuditLog)
        
        if user_id:
            query = query.where(AuditLog.user_id == user_id)
        if module:
            query = query.where(AuditLog.module == module)
        if action:
            query = query.where(AuditLog.action == action)
        if start_date:
            query = query.where(AuditLog.created_at >= start_date)
        if end_date:
            query = query.where(AuditLog.created_at <= end_date)
        

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        

        query = query.offset(skip).limit(limit).order_by(AuditLog.created_at.desc())
        result = await db.execute(query)
        logs = result.scalars().all()
        
        return list(logs), total