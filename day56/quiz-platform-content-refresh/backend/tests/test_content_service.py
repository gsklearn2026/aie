import pytest
from app.services.content_service import ContentService
from app.schemas.content import ContentCreate

@pytest.mark.asyncio
async def test_create_content(db_session):
    service = ContentService(db_session)
    
    content_data = ContentCreate(
        topic="Python Basics",
        question="What keyword is used to define a function in Python?",
        options=["func", "def", "function", "define"],
        correct_answer="def",
        explanation="The 'def' keyword is used to define functions in Python",
        difficulty="easy",
        category="Programming"
    )
    
    content = await service.create_content(content_data)
    
    assert content.id is not None
    assert content.topic == "Python Basics"
    assert content.freshness_score == 100.0
    assert content.state.value == "active"

@pytest.mark.asyncio
async def test_get_stale_content(db_session):
    service = ContentService(db_session)
    
    # Create content with low freshness
    content_data = ContentCreate(
        topic="Test Topic",
        question="Test question?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty="medium"
    )
    content = await service.create_content(content_data)
    
    # Manually set low freshness
    content.freshness_score = 30.0
    await db_session.commit()
    
    stale = await service.get_stale_content(threshold=40.0)
    assert len(stale) >= 1
