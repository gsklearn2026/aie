import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from ..main import app
from ..database import async_session
from ..models import QuizAttempt, AnalyticsEvent

@pytest.fixture
async def test_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def db_session():
    async with async_session() as session:
        yield session

@pytest.mark.asyncio
async def test_create_analytics_event(test_client: AsyncClient):
    event_data = {
        "event_type": "quiz_completed",
        "user_id": "test-user",
        "quiz_id": "quiz-1",
        "topic_id": "mathematics",
        "data": {"score": 85, "max_score": 100}
    }
    
    response = await test_client.post("/api/v1/analytics/events", json=event_data)
    assert response.status_code == 200
    assert "event_id" in response.json()

@pytest.mark.asyncio
async def test_dashboard_metrics(test_client: AsyncClient):
    response = await test_client.get("/api/v1/analytics/dashboard?days=7")
    assert response.status_code == 200
    
    data = response.json()
    assert "overview" in data
    assert "daily_activity" in data
    assert "topic_performance" in data

@pytest.mark.asyncio
async def test_user_performance(test_client: AsyncClient):
    response = await test_client.get("/api/v1/analytics/user/test-user/performance?days=30")
    assert response.status_code == 200
    
    data = response.json()
    assert "user_id" in data
    assert "summary" in data
    assert "topic_performance" in data

@pytest.mark.asyncio
async def test_analytics_processor():
    from ..services.analytics_processor import AnalyticsProcessor
    
    processor = AnalyticsProcessor()
    # Test processing without errors
    await processor.process_events()
    
    assert True  # If no exception, test passes

if __name__ == "__main__":
    pytest.main([__file__])
