from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional, List, Dict, Any
from app.modules.users.models import User, UserRole
from app.core.security import get_password_hash
import logging

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
        """Get user by ID"""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email"""
        result = await db.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create(db: AsyncSession, user_data: Dict[str, Any]) -> User:
        """Create new user"""
        user = User(**user_data)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def update(db: AsyncSession, user_id: int, update_data: Dict[str, Any]) -> Optional[User]:
        """Update user"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(user, key, value)
        
        await db.commit()
        await db.refresh(user)
        return user
    
    @staticmethod
    async def delete(db: AsyncSession, user_id: int) -> bool:
        """Soft delete user"""
        user = await UserService.get_by_id(db, user_id)
        if not user:
            return False
        
        user.is_active = False
        await db.commit()
        return True
    
    @staticmethod
    async def list_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> tuple[List[User], int]:
        """List users with filters"""
        query = select(User)
        
        if role:
            query = query.where(User.role == role)
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        if search:
            query = query.where(
                User.full_name.ilike(f"%{search}%") | User.email.ilike(f"%{search}%")
            )
        

        count_query = select(func.count()).select_from(query.subquery())
        total_result = await db.execute(count_query)
        total = total_result.scalar_one()
        

        query = query.offset(skip).limit(limit)
        result = await db.execute(query)
        users = result.scalars().all()
        
        return list(users), total