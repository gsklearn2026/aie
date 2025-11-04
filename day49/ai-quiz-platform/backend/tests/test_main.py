import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "services" in data

def test_register_user():
    response = client.post("/api/auth/register", json={
        "email": "test@example.com",
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "user" in data

def test_create_quiz():
    # First register and login
    register_response = client.post("/api/auth/register", json={
        "email": "quiztest@example.com",
        "username": "quizuser",
        "password": "testpass123"
    })
    token = register_response.json()["token"]
    
    # Create quiz
    response = client.post(
        "/api/quizzes/generate",
        json={
            "title": "Test Quiz",
            "description": "A test quiz",
            "difficulty": "medium",
            "category": "general"
        },
        headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Quiz"
