import pytest
from fastapi.testclient import TestClient
from main import app, get_db
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base

# Setup an in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database dependency to use the test database
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test tables
Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    
def test_analytics_empty():
    response = client.get("/analytics")
    assert response.status_code == 200
    data = response.json()
    assert data["total_messages"] >= 0
    assert "intent_distribution" in data

# Note: Testing /chat endpoint requires the DL model to be trained and loaded. 
# We'll skip predicting in the test unless mocking is added, or assume model is available.
# In a real environment, we'd mock the `model.predict` and `nlp` calls.
