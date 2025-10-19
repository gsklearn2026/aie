import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add the app directory to the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.main import app
from app.core.database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as c:
        yield c
    Base.metadata.drop_all(bind=engine)

def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "full_name": "Test User",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "testuser"

def test_login_user(client):
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "username": "logintest",
            "email": "login@example.com",
            "full_name": "Login Test",
            "password": "testpass123"
        }
    )
    
    # Then login
    response = client.post(
        "/api/auth/login",
        json={
            "username": "logintest",
            "password": "testpass123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "logintest"

def test_get_current_user(client):
    # Register and get token
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "currentuser",
            "email": "current@example.com",
            "full_name": "Current User",
            "password": "testpass123"
        }
    )
    token = register_response.json()["access_token"]
    
    # Get current user
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "currentuser"

def test_protected_endpoint(client):
    # Register and get token
    register_response = client.post(
        "/api/auth/register",
        json={
            "username": "protecteduser",
            "email": "protected@example.com",
            "full_name": "Protected User",
            "password": "testpass123"
        }
    )
    token = register_response.json()["access_token"]
    
    # Access protected endpoint
    response = client.get(
        "/api/quiz/protected-test",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["username"] == "protecteduser"
