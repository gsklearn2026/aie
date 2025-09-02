import pytest
import asyncio
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch
import json
import tempfile
import os

from app.config.database import Base
from app.services.export_service import ExportService
from app.models.export_models import ExportJob, ExportStatus, ExportFormat
from app.models.quiz_models import QuizResult

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def sample_quiz_data(db_session):
    """Create sample quiz data for testing"""
    quiz_results = [
        QuizResult(
            user_id="user_1",
            quiz_id="quiz_1", 
            score=85.5,
            total_questions=20,
            correct_answers=17,
            time_taken=1200,
            difficulty_level="Medium",
            subject_area="Mathematics"
        ),
        QuizResult(
            user_id="user_2",
            quiz_id="quiz_2",
            score=92.0,
            total_questions=15,
            correct_answers=14,
            time_taken=900,
            difficulty_level="Hard",
            subject_area="Science"
        )
    ]
    
    for result in quiz_results:
        db_session.add(result)
    db_session.commit()
    
    return quiz_results

class TestExportService:
    
    @pytest.mark.asyncio
    async def test_create_export_job(self, db_session):
        """Test creating an export job"""
        export_service = ExportService(db_session)
        
        request = {
            'format': 'csv',
            'filters': {'subject_area': 'Mathematics'},
            'include_ai_insights': True
        }
        
        with patch('app.services.export_service.redis_client') as mock_redis:
            job_id = await export_service.create_export_job(request, "test_user")
            
            # Verify job was created in database
            job = db_session.query(ExportJob).filter(ExportJob.job_id == job_id).first()
            assert job is not None
            assert job.user_id == "test_user"
            assert job.export_format == ExportFormat.CSV
            assert job.status == ExportStatus.QUEUED
            
            # Verify job was queued in Redis
            mock_redis.lpush.assert_called_once_with("export_queue", job_id)

    @pytest.mark.asyncio
    async def test_get_export_data(self, db_session, sample_quiz_data):
        """Test getting export data with filters"""
        export_service = ExportService(db_session)
        
        # Test without filters
        params = {'include_ai_insights': False}
        data = await export_service._get_export_data(params)
        assert len(data) == 2
        
        # Test with subject filter
        params = {
            'filters': {'subject_area': 'Mathematics'},
            'include_ai_insights': False
        }
        data = await export_service._get_export_data(params)
        assert len(data) == 1
        assert data[0]['subject_area'] == 'Mathematics'

    @pytest.mark.asyncio 
    async def test_generate_csv_export(self, db_session, sample_quiz_data):
        """Test CSV export generation"""
        export_service = ExportService(db_session)
        
        params = {'include_ai_insights': False}
        data = await export_service._get_export_data(params)
        
        # Generate CSV
        file_path = await export_service._generate_csv(data, "test_job", "20241201_120000")
        
        # Verify file was created
        assert os.path.exists(file_path)
        assert file_path.endswith('.csv.gz')
        
        # Clean up
        os.remove(file_path)

    @pytest.mark.asyncio
    async def test_generate_json_export(self, db_session, sample_quiz_data):
        """Test JSON export generation"""
        export_service = ExportService(db_session)
        
        params = {'include_ai_insights': False}
        data = await export_service._get_export_data(params)
        
        # Generate JSON
        file_path = await export_service._generate_json(data, "test_job", "20241201_120000")
        
        # Verify file was created
        assert os.path.exists(file_path)
        assert file_path.endswith('.json.gz')
        
        # Clean up
        os.remove(file_path)

    def test_get_job_status(self, db_session):
        """Test getting job status"""
        # Create a test job
        job = ExportJob(
            job_id="test_job_123",
            user_id="test_user",
            export_format=ExportFormat.CSV,
            status=ExportStatus.COMPLETED,
            progress=100.0,
            total_records=100,
            processed_records=100
        )
        db_session.add(job)
        db_session.commit()
        
        export_service = ExportService(db_session)
        status = export_service.get_job_status("test_job_123")
        
        assert status is not None
        assert status['job_id'] == "test_job_123"
        assert status['status'] == 'completed'
        assert status['progress'] == 100.0

    def test_get_job_status_not_found(self, db_session):
        """Test getting status for non-existent job"""
        export_service = ExportService(db_session)
        status = export_service.get_job_status("non_existent_job")
        assert status is None
