import pytest
from datetime import datetime, timedelta
from app.services.refresh_service import RefreshService
from app.services.content_service import ContentService
from app.schemas.content import ContentCreate
from app.models.content import ContentLifecycle

@pytest.mark.asyncio
async def test_calculate_freshness_score(db_session):
    content_service = ContentService(db_session)
    refresh_service = RefreshService(db_session)
    
    content_data = ContentCreate(
        topic="Test",
        question="Test?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty="medium"
    )
    content = await content_service.create_content(content_data)
    
    score = await refresh_service.calculate_freshness_score(content)
    assert 0 <= score <= 100

@pytest.mark.asyncio
async def test_determine_lifecycle(db_session):
    refresh_service = RefreshService(db_session)
    
    # Fresh content
    lifecycle = refresh_service.determine_lifecycle(85.0, 3)
    assert lifecycle == ContentLifecycle.FRESH
    
    # Stale content
    lifecycle = refresh_service.determine_lifecycle(20.0, 100)
    assert lifecycle == ContentLifecycle.STALE

@pytest.mark.asyncio
async def test_create_refresh_job(db_session):
    content_service = ContentService(db_session)
    refresh_service = RefreshService(db_session)
    
    content_data = ContentCreate(
        topic="Test",
        question="Test?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty="medium"
    )
    content = await content_service.create_content(content_data)
    
    job = await refresh_service.create_refresh_job(content.id, "test_refresh")
    
    assert job.id is not None
    assert job.status == "pending"
