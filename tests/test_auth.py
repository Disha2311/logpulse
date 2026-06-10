import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import User

@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient, db: AsyncSession):
    """Test successful user registration."""
    response = await client.post(
        "/auth/register",
        json={"email": "newuser@example.com", "password": "securepassword123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["email"] == "newuser@example.com"
    
    # Check it actually exists in database
    result = await db.execute(select(User).where(User.email == "newuser@example.com"))
    user = result.scalars().first()
    assert user is not None
    assert user.email == "newuser@example.com"

@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient, test_user: User):
    """Test registration fails when email already exists."""
    response = await client.post(
        "/auth/register",
        json={"email": test_user.email, "password": "anotherpassword"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Email is already registered"

@pytest.mark.asyncio
async def test_register_user_invalid_password_length(client: AsyncClient):
    """Test password length constraint validation (Pydantic schema)."""
    response = await client.post(
        "/auth/register",
        json={"email": "invalidpass@example.com", "password": "123"}
    )
    assert response.status_code == 422  # Validation Error

@pytest.mark.asyncio
async def test_login_user_success(client: AsyncClient, test_user: User):
    """Test successful login returns a JWT token."""
    response = await client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_login_user_invalid_credentials(client: AsyncClient, test_user: User):
    """Test login fails with incorrect password."""
    response = await client.post(
        "/auth/login",
        json={"email": test_user.email, "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert "detail" in response.json()
