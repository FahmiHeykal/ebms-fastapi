from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.modules.auth.models import RefreshToken
from app.modules.users.models import User
from app.modules.users.service import UserService
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.config import settings
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AuthService:
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> User:
        logger.debug(f"🔍 Looking for user with email: {email}")
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalar_one_or_none()
        logger.debug(f"✅ Found: {user is not None}")
        return user

    @staticmethod
    async def authenticate_user(db: AsyncSession, email: str, password: str) -> User:
        user = await AuthService.get_user_by_email(db, email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        if not user.is_active:
            return None
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user_data: dict) -> User:
        logger.debug(f"📝 Creating user: {user_data.get('email')}")
        try:
            password = user_data.pop("password")
            user_data["hashed_password"] = get_password_hash(password)
            logger.debug("✅ Password hashed")

            user = User(**user_data)
            logger.debug(f"✅ User object created: {user.email}")

            db.add(user)
            await db.commit()
            await db.refresh(user)
            logger.debug(f"✅ User saved to DB with ID: {user.id}")
            return user

        except Exception as e:
            logger.error(f"❌ Error creating user: {type(e).__name__}: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    @staticmethod
    async def create_tokens(db: AsyncSession, user: User) -> dict:
        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role.value}
        )
        refresh_token = create_refresh_token(data={"sub": str(user.id)})

        refresh_token_obj = RefreshToken(
            user_id=user.id,
            token=refresh_token,
            expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        db.add(refresh_token_obj)
        await db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        }

    @staticmethod
    async def refresh_access_token(db: AsyncSession, refresh_token: str) -> dict:
        payload = decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            return None

        result = await db.execute(
            select(RefreshToken).where(
                and_(
                    RefreshToken.token == refresh_token,
                    RefreshToken.revoked == False,
                    RefreshToken.expires_at > datetime.utcnow()
                )
            )
        )
        token_record = result.scalar_one_or_none()

        if not token_record:
            return None

        user_id = payload.get("sub")
        user = await db.get(User, int(user_id))
        if not user or not user.is_active:
            return None

        return await AuthService.create_tokens(db, user)

    @staticmethod
    async def revoke_refresh_token(db: AsyncSession, refresh_token: str):
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == refresh_token)
        )
        token_record = result.scalar_one_or_none()
        if token_record:
            token_record.revoked = True
            await db.commit()