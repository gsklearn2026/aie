import pytest
from app.services.metrics_service import MetricsService
from app.services.content_service import ContentService
from app.schemas.content import ContentCreate

@pytest.mark.asyncio
async def test_record_attempt(db_session):
    content_service = ContentService(db_session)
    metrics_service = MetricsService(db_session)
    
    content_data = ContentCreate(
        topic="Test",
        question="Test?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty="medium"
    )
    content = await content_service.create_content(content_data)
    
    # Record correct attempt
    metrics = await metrics_service.record_attempt(content.id, True, 45.0)
    
    assert metrics.total_attempts == 1
    assert metrics.correct_attempts == 1
    assert metrics.accuracy_rate == 100.0

@pytest.mark.asyncio
async def test_skip_recording(db_session):
    content_service = ContentService(db_session)
    metrics_service = MetricsService(db_session)
    
    content_data = ContentCreate(
        topic="Test",
        question="Test?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty="medium"
    )
    content = await content_service.create_content(content_data)
    
    # Record skip
    metrics = await metrics_service.record_attempt(content.id, False, 0, skipped=True)
    
    assert metrics.skip_count == 1
    assert metrics.skip_rate > 0
