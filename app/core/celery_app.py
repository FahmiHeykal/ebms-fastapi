from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "ebms",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,
    task_soft_time_limit=25 * 60,
)

@celery_app.task(name="send_notification_email")
def send_notification_email(to_email: str, subject: str, content: str):
    """Async task to send notification email"""
    from app.utils.email import EmailService
    import asyncio
    
    asyncio.run(EmailService.send_email([to_email], subject, content))