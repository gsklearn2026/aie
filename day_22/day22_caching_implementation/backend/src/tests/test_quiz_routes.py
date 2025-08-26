import pytest
from httpx import AsyncClient
from fastapi import FastAPI
from unittest.mock import patch, AsyncMock

from src.main import app

@pytest.mark.asyncio
async def test_get_quiz_endpoint():
    """Test quiz endpoint returns data"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/quiz/test-quiz")
        
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-quiz"
    assert "title" in data
    assert "questions" in data

@pytest.mark.asyncio
async def test_cache_headers():
    """Test that cache headers are properly set"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/quiz/test-quiz")
        
    assert response.status_code == 200
    assert "X-Cache-Strategy" in response.headers
    assert response.headers["X-Cache-Strategy"] == "cache-aside"
    assert "X-Process-Time" in response.headers

@pytest.mark.asyncio
async def test_cache_invalidation_endpoint():
    """Test cache invalidation endpoint"""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/quiz/test-quiz/invalidate")
        
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "test-quiz" in data["message"]
