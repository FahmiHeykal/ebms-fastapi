import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

class EmailService:
    @staticmethod
    async def send_email(
        to_emails: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ):
        """Send email using SMTP"""
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.EMAIL_FROM
            msg["To"] = ", ".join(to_emails)
            
            # Attach plain text body
            msg.attach(MIMEText(body, "plain"))
            
            # Attach HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, "html"))
            
            # Send email
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
                
            logger.info(f"Email sent to {to_emails}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False