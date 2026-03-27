from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, declared_attr
from typing import AsyncGenerator
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)


async_database_url = settings.DATABASE_URL
if "postgresql://" in async_database_url and "asyncpg" not in async_database_url:
    async_database_url = async_database_url.replace("postgresql://", "postgresql+asyncpg://")

logger.info(f"Database URL: {async_database_url.replace(settings.DATABASE_URL.split('@')[0].split(':')[0], '***')}")

engine = create_async_engine(
    async_database_url,
    pool_size=settings.DATABASE_POOL_SIZE,
    max_overflow=settings.DATABASE_MAX_OVERFLOW,
    echo=settings.DEBUG,
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

class Base:
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()
    
    def dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

Base = declarative_base(cls=Base)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()