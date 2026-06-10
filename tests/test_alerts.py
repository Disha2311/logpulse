import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from unittest.mock import patch

from app.models import AlertRule, AlertHistory
from app.workers.celery_worker import check_alerts_async

@pytest.mark.asyncio
async def test_alert_rule_crud(client: AsyncClient, auth_headers: dict, db: AsyncSession):
    """Test creating, listing, and deleting alert rules."""
    # 1. Create Rule
    response = await client.post(
        "/alert-rules",
        json={
            "service": "checkout-service",
            "threshold": 10,
            "window_minutes": 5,
            "notify_email": "alerts@example.com",
            "notify_webhook_url": "https://example.com/webhook"
        },
        headers=auth_headers
    )
    assert response.status_code == 201
    rule_data = response.json()
    assert rule_data["service"] == "checkout-service"
    assert rule_data["threshold"] == 10
    
    # Verify in DB
    result = await db.execute(select(AlertRule).where(AlertRule.service == "checkout-service"))
    rule = result.scalars().first()
    assert rule is not None
    assert rule.threshold == 10
    
    # 2. List Rules
    response = await client.get("/alert-rules", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
    
    # 3. Delete Rule
    response = await client.delete(f"/alert-rules/{rule.id}", headers=auth_headers)
    assert response.status_code == 204
    
    # Verify deleted in DB
    result = await db.execute(select(AlertRule).where(AlertRule.id == rule.id))
    assert result.scalars().first() is None

@pytest.mark.asyncio
async def test_celery_check_alerts_no_breach(
    db: AsyncSession,
    mock_redis
):
    """Test celery check_alerts task when error counts are below threshold."""
    _, mock_sync_redis = mock_redis
    
    # Insert Alert Rule
    rule = AlertRule(
        service="gateway",
        threshold=5,
        window_minutes=5,
        notify_email="ops@example.com"
    )
    db.add(rule)
    await db.commit()
    
    # Mock Redis error count to 3 (threshold is 5)
    with patch("app.services.alert_service.AlertService.get_error_count_sync", return_value=3) as mock_get_count, \
         patch("app.services.email_service.EmailService.send_alert_email") as mock_email:
         
        await check_alerts_async(db)
        
        mock_get_count.assert_called_once_with("gateway", 5)
        # Email should not be sent
        mock_email.assert_not_called()
        
        # Verify no AlertHistory rows created
        result = await db.execute(select(AlertHistory).where(AlertHistory.service == "gateway"))
        assert len(result.scalars().all()) == 0

@pytest.mark.asyncio
async def test_celery_check_alerts_breach_and_cooldown(
    db: AsyncSession,
    mock_redis
):
    """Test celery check_alerts triggers alerts on breach and sets cooldown."""
    _, mock_sync_redis = mock_redis
    
    # Insert Alert Rule
    rule = AlertRule(
        service="auth-service",
        threshold=5,
        window_minutes=10,
        notify_email="sec@example.com",
        notify_webhook_url="https://sec.example.com/alert"
    )
    db.add(rule)
    await db.commit()
    
    # Mock Redis returns 8 errors (breaches threshold 5)
    with patch("app.services.alert_service.AlertService.get_error_count_sync", return_value=8) as mock_get_count, \
         patch("app.services.email_service.EmailService.send_alert_email", return_value=True) as mock_email, \
         patch("app.services.webhook_service.WebhookService.send_webhook_alert", return_value=True) as mock_webhook:
         
        # Run alert checker
        await check_alerts_async(db)
        
        # Check alerts sent
        mock_email.assert_called_once_with(
            to_email="sec@example.com",
            service="auth-service",
            error_count=8,
            threshold=5
        )
        mock_webhook.assert_called_once_with(
            url="https://sec.example.com/alert",
            service="auth-service",
            error_count=8,
            threshold=5
        )
        
        # Check cooldown is set
        mock_sync_redis.setex.assert_called_once_with(
            "alerts:auth-service:cooldown",
            300,  # 5 minutes
            "active"
        )
        
        # Verify AlertHistory log exists in DB
        result = await db.execute(select(AlertHistory).where(AlertHistory.service == "auth-service"))
        history = result.scalars().all()
        assert len(history) == 1
        assert history[0].error_count == 8
        assert history[0].threshold == 5
        assert history[0].notified_email == "sec@example.com"
