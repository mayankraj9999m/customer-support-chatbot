import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from main import app
from database import get_db, Base
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# Setup an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(SQLALCHEMY_DATABASE_URL, echo=False)
TestingSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def override_get_db():
    async with TestingSessionLocal() as db:
        yield db

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def async_client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health_check(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    
@pytest.mark.asyncio
async def test_analytics_empty(async_client):
    response = await async_client.get("/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_messages"] >= 0
    assert "intent_distribution" in data

# Note: Testing /chat endpoint requires the DL model to be trained and loaded. 
# We'll skip predicting in the test unless mocking is added, or assume model is available.
# In a real environment, we'd mock the `ml_service` and `llm_service` calls.
