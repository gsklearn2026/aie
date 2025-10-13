import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "cpu_usage" in data
    assert "memory_usage" in data

@pytest.mark.asyncio
async def test_metrics_endpoint():
    """Test Prometheus metrics endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]

@pytest.mark.asyncio
async def test_dashboard_stats():
    """Test dashboard statistics endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "activeUsers" in data
    assert "questionsAnswered" in data
    assert "systemHealth" in data

@pytest.mark.asyncio
async def test_quiz_answer_submission():
    """Test quiz answer submission"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/quiz/answer", json={"answer": "A", "question_id": 1})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "score" in data

@pytest.mark.asyncio
async def test_user_login():
    """Test user login simulation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/users/login")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "user_id" in data

@pytest.mark.asyncio
async def test_load_simulation():
    """Test load simulation"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/simulate/load")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "new_active_users" in data
