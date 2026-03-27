from app.core.config import settings

print("=" * 50)
print("Testing Configuration")
print("=" * 50)

print(f"DATABASE_URL: {settings.DATABASE_URL}")
print(f"SECRET_KEY: {settings.SECRET_KEY[:10]}...")
print(f"DEBUG: {settings.DEBUG}")
print(f"ALLOWED_ORIGINS: {settings.ALLOWED_ORIGINS}")
print(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
print(f"ALLOWED_EXTENSIONS: {settings.ALLOWED_EXTENSIONS}")
print(f"UPLOAD_DIR: {settings.UPLOAD_DIR}")
print(f"MAX_UPLOAD_SIZE: {settings.MAX_UPLOAD_SIZE}")
print("=" * 50)
print("Configuration loaded successfully!")