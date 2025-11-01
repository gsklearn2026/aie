import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

@pytest.fixture
async def client():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.asyncio
async def test_generate_quiz_invalid_topic(client):
    response = await client.post("/api/generate-quiz", json={
        "topic": "",
        "difficulty": "medium"
    })
    assert response.status_code == 400
    assert "Topic must be at least 2 characters" in response.json()["message"]

@pytest.mark.asyncio
async def test_submit_answer_missing_fields(client):
    response = await client.post("/api/submit-answer", json={
        "quiz_id": "test_quiz"
        # Missing required fields
    })
    assert response.status_code == 400
    assert "Missing required field" in response.json()["message"]

@pytest.mark.asyncio
async def test_analytics_empty_quiz_id(client):
    response = await client.get("/api/analytics/")
    assert response.status_code == 404
