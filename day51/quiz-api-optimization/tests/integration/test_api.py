import pytest
import httpx
import asyncio

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_health_check():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_get_quizzes():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/quizzes")
        assert response.status_code == 200
        data = response.json()
        assert "quizzes" in data
        assert len(data["quizzes"]) > 0

@pytest.mark.asyncio
async def test_compression_headers():
    async with httpx.AsyncClient() as client:
        headers = {"Accept-Encoding": "gzip, br"}
        response = await client.get(f"{BASE_URL}/api/quizzes", headers=headers)
        assert response.status_code == 200
        assert "X-Compression-Ratio" in response.headers

@pytest.mark.asyncio
async def test_field_filtering():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/quizzes?fields=id,title")
        data = response.json()
        if data["quizzes"]:
            quiz = data["quizzes"][0]
            assert "id" in quiz
            assert "title" in quiz
            assert "description" not in quiz

@pytest.mark.asyncio
async def test_metrics_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/api/metrics/performance")
        assert response.status_code == 200
        data = response.json()
        assert "performance_by_endpoint" in data
        assert "cache_statistics" in data
