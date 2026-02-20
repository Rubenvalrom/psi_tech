"""
conftest.py - Pytest configuration and fixtures for FastAPI testing
"""

import asyncio
import pytest
from typing import Generator
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db import get_db, Base


# Database configuration for testing
DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> Generator[AsyncSession, None, None]:
    """Create test database session"""
    
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async_session = AsyncSession(engine, expire_on_commit=False)
    
    yield async_session
    
    await async_session.close()
    await engine.dispose()


@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncClient:
    """FastAPI test client"""
    
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def auth_headers() -> dict:
    """Valid JWT auth headers"""
    # In real tests, use a valid JWT token
    return {
        "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
    }


@pytest.fixture
def mock_keycloak(mocker):
    """Mock Keycloak authentication"""
    
    async def mock_verify_token(token):
        return {
            "sub": "user-123",
            "preferred_username": "testuser",
            "email": "test@example.com",
            "roles": ["user", "admin"]
        }
    
    mocker.patch(
        "app.security.verify_jwt_token",
        side_effect=mock_verify_token
    )


@pytest.fixture
def mock_ollama(mocker):
    """Mock Ollama LLM service"""
    
    async def mock_generate(prompt: str, model: str = "mistral"):
        return {
            "response": "Mock LLM response",
            "done": True
        }
    
    mocker.patch(
        "ollama.AsyncClient.generate",
        side_effect=mock_generate
    )


@pytest.fixture
def mock_database(mocker):
    """Mock database operations"""
    
    mocker.patch(
        "app.db.async_session",
        return_value=AsyncSession()
    )


@pytest.fixture
async def sample_expediente():
    """Sample expediente (request) for testing"""
    return {
        "numero": "EXP-2024-001",
        "solicitante": "Juan Pérez García",
        "documento": "12345678A",
        "concepto": "Solicitud de licencia",
        "descripcion": "Solicitud de licencia de construcción",
        "presupuesto": 50000.00,
        "estado": "iniciado"
    }


@pytest.fixture
async def sample_user():
    """Sample user for testing"""
    return {
        "id": "user-123",
        "username": "testuser",
        "email": "test@example.com",
        "roles": ["user", "admin"]
    }


@pytest.fixture
def mock_httpx(mocker):
    """Mock HTTP requests"""
    
    async def mock_get(url: str, **kwargs):
        class MockResponse:
            status_code = 200
            async def json(self):
                return {"mock": "response"}
            def raise_for_status(self):
                pass
        
        return MockResponse()
    
    mocker.patch("httpx.AsyncClient.get", side_effect=mock_get)


@pytest.fixture
def caplog_async(caplog):
    """Async-compatible logging fixture"""
    return caplog
