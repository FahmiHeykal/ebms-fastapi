from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import func
from app.core.database import get_db
from app.modules.auth.service import AuthService
from app.modules.auth.schemas import LoginRequest, RegisterRequest, TokenResponse, RefreshTokenRequest
from app.modules.audit.service import AuditService

router = APIRouter()

@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    user_data: RegisterRequest,
    db: AsyncSession = Depends(get_db)
):
    """Register new user"""
    # Check if user exists
    existing_user = await AuthService.get_user_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists"
        )
    
    # Create user
    user = await AuthService.create_user(db, user_data.dict())
    
    # Log audit
    await AuditService.log_action(
        db, user.id, user.email, "register", "auth",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    # Create tokens
    tokens = await AuthService.create_tokens(db, user)
    return tokens

@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login user"""
    user = await AuthService.authenticate_user(db, login_data.email, login_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Update last login
    user.last_login = func.now()
    await db.commit()
    
    # Log audit
    await AuditService.log_action(
        db, user.id, user.email, "login", "auth",
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent")
    )
    
    # Create tokens
    tokens = await AuthService.create_tokens(db, user)
    return tokens

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token"""
    tokens = await AuthService.refresh_access_token(db, refresh_data.refresh_token)
    if not tokens:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    return tokens

@router.post("/logout")
async def logout(
    refresh_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Logout user"""
    await AuthService.revoke_refresh_token(db, refresh_data.refresh_token)
    return {"message": "Successfully logged out"}