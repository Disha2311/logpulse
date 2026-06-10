import asyncio
import logging
from celery import Celery
from sqlalchemy.future import select

from app.config import settings
from app.database import AsyncSessionLocal
from app.models import AlertRule, AlertHistory
from app.services.alert_service import AlertService
from app.services.email_service import EmailService
from app.services.webhook_service import WebhookService

logger = logging.getLogger("celery_worker")

# Initialize Celery app
celery_app = Celery(
    "log_alerts",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

# Configuration
celery_app.conf.update(
    timezone="UTC",
    enable_utc=True,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json"
)

# Celery Beat schedule
celery_app.conf.beat_schedule = {
    "check-alerts-every-60-seconds": {
        "task": "app.workers.celery_worker.check_alerts",
        "schedule": 60.0,
    },
}

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

async def check_alerts_async(db: Optional[AsyncSession] = None):
    """Asynchronous alert check execution logic. Accepts optional db session override for testing."""
    if db is not None:
        await _check_alerts_impl(db)
    else:
        async with AsyncSessionLocal() as session:
            try:
                await _check_alerts_impl(session)
            except Exception as e:
                logger.error(f"Error checking alerts: {str(e)}")
                await session.rollback()

async def _check_alerts_impl(db: AsyncSession):
    # 1. Fetch all alert rules
    result = await db.execute(select(AlertRule))
    rules = result.scalars().all()
    
    for rule in rules:
        # 2. Check if service is currently on alert cooldown
        if AlertService.is_cooldown_active(rule.service):
            logger.info(f"Alert check skipped for service '{rule.service}' (cooldown active).")
            continue
        
        # 3. Fetch error counts in sliding window
        error_count = AlertService.get_error_count_sync(rule.service, rule.window_minutes)
        logger.info(f"Checking service '{rule.service}': {error_count} errors (threshold: {rule.threshold})")
        
        # 4. Trigger alert if threshold reached
        if error_count >= rule.threshold:
            logger.warning(
                f"THRESHOLD BREACHED for service '{rule.service}': "
                f"{error_count} errors in {rule.window_minutes} min (threshold: {rule.threshold})"
            )
            
            # Send Email
            EmailService.send_alert_email(
                to_email=rule.notify_email,
                service=rule.service,
                error_count=error_count,
                threshold=rule.threshold
            )
            
            # Send Webhook if configured
            if rule.notify_webhook_url:
                WebhookService.send_webhook_alert(
                    url=rule.notify_webhook_url,
                    service=rule.service,
                    error_count=error_count,
                    threshold=rule.threshold
                )
                
            # Save to alert history
            history_entry = AlertHistory(
                service=rule.service,
                error_count=error_count,
                threshold=rule.threshold,
                notified_email=rule.notify_email
            )
            db.add(history_entry)
            
            # Activate alert cooldown for 5 minutes
            AlertService.set_cooldown(rule.service, settings.DEFAULT_ALERT_COOLDOWN_MINUTES)
    
    await db.commit()

@celery_app.task
def check_alerts():
    """Periodic task executed by Celery Beat every 60s."""
    logger.info("Starting alert threshold checks...")
    # Run async function using event loop
    asyncio.run(check_alerts_async())
    logger.info("Finished alert threshold checks.")
