import pytest
import asyncio
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_dashboard_overview():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/dashboard/overview")
        assert response.status_code == 200
        data = response.json()
        assert "success" in data
        assert "data" in data

@pytest.mark.asyncio
async def test_performance_trends():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/dashboard/charts/performance-trends")
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_realtime_dashboard():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/analytics/dashboard/realtime")
        assert response.status_code == 200

@pytest.mark.asyncio 
async def test_user_performance():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/analytics/user/1/performance")
        assert response.status_code == 200

if __name__ == "__main__":
    asyncio.run(test_dashboard_overview())
