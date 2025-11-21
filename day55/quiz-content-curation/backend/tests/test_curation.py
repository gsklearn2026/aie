import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.models.database import Base, get_db
from app.models.models import Question, ContentCuration
from app.services.curation_service import CurationService
from app.schemas.schemas import QualityMetrics

# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_curation.db"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(setup_database):
    async with TestSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(setup_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def sample_question(db_session):
    question = Question(
        text="What is 2 + 2?",
        options=["3", "4", "5", "6"],
        correct_answer=1,
        explanation="Basic arithmetic",
        topic="Mathematics",
        difficulty="easy"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    return question

@pytest.mark.asyncio
async def test_submit_for_curation(db_session, sample_question):
    """Test submitting content for curation"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    
    assert curation.status == "pending"
    assert curation.quality_score > 0
    assert curation.question_id == sample_question.id

@pytest.mark.asyncio
async def test_claim_and_approve(db_session, sample_question):
    """Test claiming and approving content"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    
    # Claim
    curation = await service.claim_for_review(curation.id, "reviewer1")
    assert curation.status == "under_review"
    assert curation.reviewer_id == "reviewer1"
    
    # Approve
    curation = await service.approve_content(curation.id, "reviewer1")
    assert curation.status == "approved"
    assert curation.reviewed_at is not None

@pytest.mark.asyncio
async def test_reject_content(db_session, sample_question):
    """Test rejecting content with reason"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    await service.claim_for_review(curation.id, "reviewer1")
    
    curation = await service.reject_content(curation.id, "reviewer1", "Incorrect answer")
    
    assert curation.status == "rejected"
    assert curation.feedback == "Incorrect answer"

@pytest.mark.asyncio
async def test_request_revision(db_session, sample_question):
    """Test requesting content revision"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    await service.claim_for_review(curation.id, "reviewer1")
    
    curation = await service.request_revision(curation.id, "reviewer1", "Make distractors more plausible")
    
    assert curation.status == "needs_revision"
    assert "distractors" in curation.feedback.lower()

@pytest.mark.asyncio
async def test_invalid_state_transition(db_session, sample_question):
    """Test invalid state transitions raise errors"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    
    # Cannot approve without claiming
    with pytest.raises(ValueError):
        await service.approve_content(curation.id, "reviewer1")

@pytest.mark.asyncio
async def test_queue_endpoint(client, db_session, sample_question):
    """Test queue API endpoint"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    await service.submit_for_curation(sample_question.id, metrics)
    
    response = await client.get("/api/curation/queue")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1

@pytest.mark.asyncio
async def test_audit_logs(db_session, sample_question):
    """Test audit log creation"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    await service.claim_for_review(curation.id, "reviewer1")
    await service.approve_content(curation.id, "reviewer1")
    
    logs = await service.get_audit_logs(curation.id)
    
    assert len(logs) == 3
    actions = [log.action for log in logs]
    assert "submitted" in actions
    assert "claimed" in actions
    assert "approved" in actions
