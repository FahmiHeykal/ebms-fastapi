from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, update
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.modules.notifications.models import Notification
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    @staticmethod
    async def create_notification(
        db: AsyncSession,
        user_id: int,
        title: str,
        content: str,
        notification_type: str = "system",
        priority: str = "normal",
        data: Dict[str, Any] = None
    ) -> Notification:
        """Create a new notification"""
        notification = Notification(
            user_id=user_id,
            title=title,
            content=content,
            type=notification_type,
            priority=priority,
            data=data or {}
        )
        db.add(notification)
        await db.commit()
        await db.refresh(notification)
        return notification
    
    @staticmethod
    async def get_user_notifications(
        db: AsyncSession,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
        unread_only: bool = False
    ) -> tuple[List[Notification], int]:
        """Get user notifications"""
        query = select(Notification).where(Notification.user_id == user_id)
        
        if unread_only:
            query = query.where(Notification.is_read == False)
        

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        

        query = query.offset(skip).limit(limit).order_by(Notification.created_at.desc())
        result = await db.execute(query)
        notifications = result.scalars().all()
        
        return list(notifications), total
    
    @staticmethod
    async def mark_as_read(
        db: AsyncSession,
        notification_id: int,
        user_id: int
    ) -> Optional[Notification]:
        """Mark notification as read"""
        result = await db.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id
            )
        )
        notification = result.scalar_one_or_none()
        
        if notification and not notification.is_read:
            notification.is_read = True
            notification.read_at = datetime.utcnow()
            await db.commit()
            await db.refresh(notification)
        
        return notification
    
    @staticmethod
    async def mark_all_as_read(db: AsyncSession, user_id: int):
        """Mark all notifications as read"""
        await db.execute(
            update(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.is_read == False
            )
            .values(is_read=True, read_at=datetime.utcnow())
        )
        await db.commit()