from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime
from app.core.database import get_db
from app.core.dependencies import require_roles
from app.modules.users.models import UserRole
from app.modules.audit.service import AuditService
from app.modules.audit.schemas import AuditLogResponse, AuditLogListResponse

router = APIRouter()

@router.get("/logs", response_model=AuditLogListResponse)
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[int] = None,
    module: Optional[str] = None,
    action: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db),
    _: UserRole = Depends(require_roles(UserRole.ADMIN))
):
    """Get audit logs (admin only)"""
    logs, total = await AuditService.get_audit_logs(
        db, skip, limit, user_id, module, action, start_date, end_date
    )
    
    return AuditLogListResponse(
        items=logs,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )