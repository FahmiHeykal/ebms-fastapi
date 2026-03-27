import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Settings:
    """Application settings"""
    APP_NAME: str = os.getenv("APP_NAME", "EBMS")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "production")
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://ebms_user:strongpassword@localhost:5432/ebms_db")
    DATABASE_POOL_SIZE: int = int(os.getenv("DATABASE_POOL_SIZE", "20"))
    DATABASE_MAX_OVERFLOW: int = int(os.getenv("DATABASE_MAX_OVERFLOW", "10"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecretkeychangeinproduction")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    @property
    def ALLOWED_ORIGINS(self) -> List[str]:
        origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8000")
        return [origin.strip() for origin in origins.split(",") if origin.strip()]
    
    @property
    def ALLOWED_HOSTS(self) -> List[str]:
        hosts = os.getenv("ALLOWED_HOSTS", "localhost,127.0.0.1")
        return [host.strip() for host in hosts.split(",") if host.strip()]
    
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@ebms.com")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))
    
    @property
    def ALLOWED_EXTENSIONS(self) -> List[str]:
        extensions = os.getenv("ALLOWED_EXTENSIONS", ".jpg,.jpeg,.png,.pdf,.doc,.docx,.xls,.xlsx")
        return [ext.strip() for ext in extensions.split(",") if ext.strip()]

settings = Settings()

if not os.path.exists(settings.UPLOAD_DIR):
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)