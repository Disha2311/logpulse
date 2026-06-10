import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from app.config import settings

logger = logging.getLogger("app.email_service")

class EmailService:
    @staticmethod
    def send_alert_email(to_email: str, service: str, error_count: int, threshold: int) -> bool:
        """
        Send an alert email using smtplib.
        Falls back to local logger printing if credentials are default.
        """
        subject = f"[ALERT] Service '{service}' error rate breached threshold"
        body = (
            f"Alert triggered for service: {service}\n"
            f"Current error count: {error_count}\n"
            f"Configured threshold: {threshold}\n"
            f"Time of alert: {smtp_time_str()}"
        )
        
        # Check if dummy/default config
        is_dummy = (
            settings.SMTP_USER == "test@gmail.com" or 
            settings.SMTP_PASSWORD == "testpassword" or 
            not settings.SMTP_USER or 
            not settings.SMTP_PASSWORD
        )
        
        if is_dummy:
            logger.warning(
                f"[DEVELOPMENT/MOCK EMAIL ALERT]\n"
                f"To: {to_email}\n"
                f"Subject: {subject}\n"
                f"Body:\n{body}\n"
            )
            return True
            
        # Real SMTP sending
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))
        
        try:
            # Connect to SMTP
            server = smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT)
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_USER, to_email, msg.as_string())
            server.quit()
            logger.info(f"Successfully sent alert email to {to_email} for service {service}")
            return True
        except Exception as e:
            logger.error(f"Failed to send alert email to {to_email} for service {service}: {str(e)}")
            return False

def smtp_time_str() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
