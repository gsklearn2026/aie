import pytest
import httpx
from app.main import app
from app.config import get_settings

settings = get_settings()

@pytest.mark.asyncio
async def test_health_check():
    """Test basic health endpoint"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_readiness_check():
    """Test deep health check"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health/ready")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint"""
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "Quiz Platform API"
        assert data["environment"] == settings.environment
