from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.core.database import get_db
from app.core.dependencies import get_current_active_user, require_roles
from app.modules.users.models import User, UserRole
from app.modules.users.service import UserService
from app.modules.users.schemas import (
    UserResponse, UserUpdate, UserListResponse
)
from app.modules.audit.service import AuditService

router = APIRouter()

@router.get("/", response_model=UserListResponse)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = None,
    is_active: Optional[bool] = None,
    search: Optional[str] = None,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    """List users (admin/manager only)"""
    users, total = await UserService.list_users(
        db, skip, limit, role, is_active, search
    )
    
    return UserListResponse(
        items=users,
        total=total,
        page=skip // limit + 1,
        size=limit,
        pages=(total + limit - 1) // limit
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """Get current user info"""
    return current_user

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.MANAGER)),
    db: AsyncSession = Depends(get_db)
):
    """Get user by ID (admin/manager only)"""
    user = await UserService.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Update user (admin only)"""
    user = await UserService.update(db, user_id, user_data.dict(exclude_unset=True))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    await AuditService.log_action(
        db, current_user.id, current_user.email, "update", "users",
        record_id=str(user_id), new_data=user_data.dict(exclude_unset=True)
    )
    
    return user

@router.put("/me/update", response_model=UserResponse)
async def update_current_user(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user profile"""
    # Only allow updating certain fields
    allowed_fields = ["full_name"]
    update_dict = {k: v for k, v in user_data.dict(exclude_unset=True).items() if k in allowed_fields}
    
    user = await UserService.update(db, current_user.id, update_dict)
    
    await AuditService.log_action(
        db, current_user.id, current_user.email, "update_profile", "users",
        record_id=str(current_user.id), new_data=update_dict
    )
    
    return user

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db)
):
    """Delete user (soft delete) (admin only)"""
    deleted = await UserService.delete(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    
    await AuditService.log_action(
        db, current_user.id, current_user.email, "delete", "users",
        record_id=str(user_id)
    )