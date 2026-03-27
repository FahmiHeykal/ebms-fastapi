from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.modules.users.models import User, UserRole
from app.modules.notifications.service import NotificationService
from app.modules.notifications.schemas import (
    NotificationCreate, NotificationResponse, NotificationListResponse
)

router = APIRouter()

@router.get("/", response_model=NotificationListResponse)
async def get_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user notifications"""
    notifications, total = await NotificationService.get_user_notifications(
        db, current_user.id, skip, limit, unread_only
    )
    
    return NotificationListResponse(
        items=notifications,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.post("/mark-read/{notification_id}")
async def mark_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark notification as read"""
    notification = await NotificationService.mark_as_read(db, notification_id, current_user.id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}

@router.post("/mark-all-read")
async def mark_all_as_read(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark all notifications as read"""
    await NotificationService.mark_all_as_read(db, current_user.id)
    return {"message": "All notifications marked as read"}