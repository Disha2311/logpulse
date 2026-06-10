import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import Log

@pytest.mark.asyncio
async def test_ingest_log_unauthorized(client: AsyncClient):
    """Test log ingestion fails without authorization header."""
    response = await client.post(
        "/logs",
        json={"service": "auth-service", "level": "INFO", "message": "User logged in"}
    )
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_ingest_log_success_info(
    client: AsyncClient,
    auth_headers: dict,
    db: AsyncSession,
    mock_redis
):
    """Test successful log ingestion (INFO level) - does not increment Redis."""
    mock_async_redis, _ = mock_redis
    
    response = await client.post(
        "/logs",
        json={"service": "payment-service", "level": "INFO", "message": "Payment successful"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["service"] == "payment-service"
    assert data["level"] == "INFO"
    
    # Verify saved in Postgres
    result = await db.execute(select(Log).where(Log.service == "payment-service"))
    log_entry = result.scalars().first()
    assert log_entry is not None
    assert log_entry.message == "Payment successful"
    
    # Verify Redis incr was NOT called
    mock_async_redis.incr.assert_not_called()

@pytest.mark.asyncio
async def test_ingest_log_success_error(
    client: AsyncClient,
    auth_headers: dict,
    mock_redis
):
    """Test successful log ingestion (ERROR level) - increments Redis."""
    mock_async_redis, _ = mock_redis
    
    response = await client.post(
        "/logs",
        json={"service": "payment-service", "level": "ERROR", "message": "Card declined"},
        headers=auth_headers
    )
    assert response.status_code == 201
    data = response.json()
    assert data["level"] == "ERROR"
    
    # Verify Redis incr was called
    mock_async_redis.incr.assert_called_once()

@pytest.mark.asyncio
async def test_query_logs_filtered(
    client: AsyncClient,
    auth_headers: dict,
    db: AsyncSession,
    test_user
):
    """Test log query filtering and pagination."""
    # Seed logs
    log1 = Log(service="web-service", level="INFO", message="Home loaded", user_id=test_user.id)
    log2 = Log(service="web-service", level="ERROR", message="Timeout", user_id=test_user.id)
    log3 = Log(service="db-service", level="INFO", message="Connected", user_id=test_user.id)
    db.add_all([log1, log2, log3])
    await db.commit()
    
    # Test level filter
    response = await client.get("/logs?level=ERROR", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["message"] == "Timeout"
    
    # Test service filter
    response = await client.get("/logs?service=db-service", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["level"] == "INFO"

@pytest.mark.asyncio
async def test_error_stats_24h(
    client: AsyncClient,
    auth_headers: dict,
    db: AsyncSession,
    test_user
):
    """Test error statistics aggregations."""
    # Seed 2 ERROR logs and 1 INFO log
    log1 = Log(service="web", level="ERROR", message="E1", user_id=test_user.id)
    log2 = Log(service="web", level="CRITICAL", message="C1", user_id=test_user.id)
    log3 = Log(service="web", level="INFO", message="I1", user_id=test_user.id)
    db.add_all([log1, log2, log3])
    await db.commit()
    
    response = await client.get("/logs/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["service"] == "web"
    assert data[0]["error_count"] == 2
