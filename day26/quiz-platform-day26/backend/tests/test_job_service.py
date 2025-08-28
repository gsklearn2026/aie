import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool
from app.models.job import Base, Job, JobStatus
from app.services.job_service import job_service

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        yield session
    
    await engine.dispose()

@pytest.mark.asyncio
async def test_create_job(test_db):
    """Test creating a new job"""
    job = await job_service.create_job(
        session=test_db,
        job_type="quiz_generation",
        input_data={"topic": "Python", "num_questions": 5}
    )
    
    assert job.job_type == "quiz_generation"
    assert job.status == JobStatus.PENDING
    assert job.input_data["topic"] == "Python"
    assert job.retry_count == 0

@pytest.mark.asyncio
async def test_get_job(test_db):
    """Test retrieving a job"""
    # Create a job
    job = await job_service.create_job(
        session=test_db,
        job_type="quiz_generation",
        input_data={"topic": "JavaScript"}
    )
    
    # Retrieve the job
    retrieved_job = await job_service.get_job(test_db, job.job_id)
    
    assert retrieved_job is not None
    assert retrieved_job.job_id == job.job_id
    assert retrieved_job.input_data["topic"] == "JavaScript"

@pytest.mark.asyncio
async def test_update_job_status(test_db):
    """Test updating job status"""
    # Create a job
    job = await job_service.create_job(
        session=test_db,
        job_type="quiz_generation",
        input_data={"topic": "React"}
    )
    
    # Update to processing
    success = await job_service.update_job_status(
        session=test_db,
        job_id=job.job_id,
        status=JobStatus.PROCESSING
    )
    
    assert success is True
    
    # Verify update
    updated_job = await job_service.get_job(test_db, job.job_id)
    assert updated_job.status == JobStatus.PROCESSING
    assert updated_job.started_at is not None

@pytest.mark.asyncio
async def test_job_completion(test_db):
    """Test completing a job with results"""
    job = await job_service.create_job(
        session=test_db,
        job_type="quiz_generation",
        input_data={"topic": "Node.js"}
    )
    
    result_data = {
        "questions": [
            {
                "question": "What is Node.js?",
                "options": ["Runtime", "Framework", "Library", "Database"],
                "correct_answer": 0
            }
        ]
    }
    
    success = await job_service.update_job_status(
        session=test_db,
        job_id=job.job_id,
        status=JobStatus.COMPLETED,
        result_data=result_data
    )
    
    assert success is True
    
    completed_job = await job_service.get_job(test_db, job.job_id)
    assert completed_job.status == JobStatus.COMPLETED
    assert completed_job.result_data == result_data
    assert completed_job.completed_at is not None
