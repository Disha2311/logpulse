import asyncio
from typing import AsyncGenerator
import pytest
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.database import Base
from app.dependencies import get_db
from app.auth_utils import get_password_hash, create_access_token
from app.models import User

# In-memory SQLite for isolated testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(scope="session")
def event_loop():
    """Create a session-wide event loop."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    """Create database tables once for the test session."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a transactional test database session (rolled back after each test)."""
    async with test_engine.connect() as connection:
        transaction = await connection.begin()
        async with TestingSessionLocal(bind=connection) as session:
            
            # Override get_db inside this transaction scope
            async def _get_test_db():
                yield session
                
            app.dependency_overrides[get_db] = _get_test_db
            yield session
            
        await transaction.rollback()
    app.dependency_overrides.clear()

@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    """Mock Redis client instances globally for all tests."""
    mock_async = AsyncMock()
    mock_sync = MagicMock()
    
    # Defaults
    mock_async.incr.return_value = 1
    mock_async.expire.return_value = True
    mock_async.mget.return_value = []
    
    mock_sync.mget.return_value = []
    mock_sync.exists.return_value = False
    mock_sync.setex.return_value = True
    
    monkeypatch.setattr("app.services.alert_service.redis_async", mock_async)
    monkeypatch.setattr("app.services.alert_service.redis_sync", mock_sync)
    
    return mock_async, mock_sync

@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Provide an HTTPX AsyncClient bound to the FastAPI app."""
    # Use ASGITransport for httpx v0.27+
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver"
    ) as ac:
        yield ac

@pytest.fixture
async def test_user(db: AsyncSession) -> User:
    """Create a dummy user in the database for authentication tests."""
    hashed_pwd = get_password_hash("testpassword123")
    user = User(email="user@example.com", hashed_password=hashed_pwd)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user

@pytest.fixture
def auth_headers(test_user: User) -> dict:
    """Return headers containing a valid JWT token for the test user."""
    token = create_access_token(data={"sub": str(test_user.id)})
    return {"Authorization": f"Bearer {token}"}
