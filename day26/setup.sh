#!/bin/bash

# Day 26: Background Job Processing Implementation Script
# AI Engineering Quiz Platform - Background Job Processing

set -e

echo "🚀 Starting Day 26: Background Job Processing Implementation"

# Create project structure
echo "📁 Creating project structure..."
mkdir -p quiz-platform-day26/{backend/{app/{api,core,models,services,workers},tests},frontend/{src/{components,services,pages},public},docker,scripts}

cd quiz-platform-day26

# Create backend requirements
echo "📦 Creating backend requirements..."
cat > backend/requirements.txt << 'EOF'
fastapi==0.109.2
uvicorn==0.27.1
celery==5.3.6
redis==5.0.1
sqlalchemy==2.0.27
psycopg2-binary==2.9.9
alembic==1.13.1
pydantic==2.6.1
python-multipart==0.0.9
google-generativeai==0.3.2
python-dotenv==1.0.1
pytest==8.0.0
pytest-asyncio==0.23.5
httpx==0.27.0
asyncpg==0.29.0
flower==2.0.1
EOF

# Create backend environment
echo "🔧 Creating backend environment configuration..."
cat > backend/.env << 'EOF'
DATABASE_URL=postgresql://quiz_user:quiz_pass@localhost:5432/quiz_db
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=your_gemini_api_key_here
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/1
EOF

# Create backend main app
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
from app.api.jobs import router as jobs_router
from app.core.database import init_db
from app.core.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    yield
    # Shutdown

app = FastAPI(
    title="Quiz Platform - Background Jobs",
    description="AI-powered quiz platform with background job processing",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jobs_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Quiz Platform Background Jobs API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "background-jobs"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
EOF

# Create configuration
cat > backend/app/core/config.py << 'EOF'
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    database_url: str = "postgresql://quiz_user:quiz_pass@localhost:5432/quiz_db"
    redis_url: str = "redis://localhost:6379/0"
    gemini_api_key: str = ""
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    
    class Config:
        env_file = ".env"

settings = Settings()
EOF

# Create database models
cat > backend/app/models/job.py << 'EOF'
from sqlalchemy import Column, Integer, String, DateTime, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"

class Job(Base):
    __tablename__ = "jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    job_type = Column(String, index=True)
    status = Column(String, default=JobStatus.PENDING)
    input_data = Column(JSON)
    result_data = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0)
    max_retries = Column(Integer, default=3)
EOF

# Create database connection
cat > backend/app/core/database.py << 'EOF'
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings
from app.models.job import Base

# Convert sync URL to async URL
database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(database_url, echo=True)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
EOF

# Create Celery app
cat > backend/app/core/celery_app.py << 'EOF'
from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "quiz_platform",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.workers.ai_tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_routes={
        "app.workers.ai_tasks.generate_quiz_questions": {"queue": "ai_generation"},
        "app.workers.ai_tasks.process_batch_quiz": {"queue": "batch_processing"},
    },
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    worker_max_tasks_per_child=1000,
)
EOF

# Create AI service
cat > backend/app/services/ai_service.py << 'EOF'
import google.generativeai as genai
from app.core.config import settings
from typing import List, Dict, Any
import json
import asyncio

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_quiz_questions(self, topic: str, num_questions: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate quiz questions using Gemini AI"""
        prompt = f"""Generate {num_questions} multiple choice questions about {topic} at {difficulty} difficulty level.

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Brief explanation of the correct answer"
  }}
]

Topic: {topic}
Difficulty: {difficulty}
Number of questions: {num_questions}

Ensure questions are educational, accurate, and appropriate for learning."""

        try:
            # Simulate async by running in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            # Clean the response text
            content = response.text.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            questions = json.loads(content)
            
            # Validate structure
            if not isinstance(questions, list):
                raise ValueError("Response is not a list")
            
            for q in questions:
                required_fields = ["question", "options", "correct_answer", "explanation"]
                if not all(field in q for field in required_fields):
                    raise ValueError(f"Missing required fields in question: {q}")
                if not isinstance(q["options"], list) or len(q["options"]) != 4:
                    raise ValueError("Each question must have exactly 4 options")
                if not (0 <= q["correct_answer"] <= 3):
                    raise ValueError("correct_answer must be between 0 and 3")
            
            return questions
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {e}")
        except Exception as e:
            raise ValueError(f"AI generation failed: {e}")

ai_service = AIService()
EOF

# Create job service
cat > backend/app/services/job_service.py << 'EOF'
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from app.models.job import Job, JobStatus
from app.core.database import get_db
from typing import Optional, Dict, Any
import uuid
from datetime import datetime

class JobService:
    @staticmethod
    async def create_job(
        session: AsyncSession,
        job_type: str,
        input_data: Dict[str, Any],
        max_retries: int = 3
    ) -> Job:
        """Create a new job record"""
        job_id = str(uuid.uuid4())
        
        job = Job(
            job_id=job_id,
            job_type=job_type,
            input_data=input_data,
            max_retries=max_retries,
            status=JobStatus.PENDING
        )
        
        session.add(job)
        await session.commit()
        await session.refresh(job)
        return job
    
    @staticmethod
    async def get_job(session: AsyncSession, job_id: str) -> Optional[Job]:
        """Get job by ID"""
        result = await session.execute(select(Job).where(Job.job_id == job_id))
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_job_status(
        session: AsyncSession,
        job_id: str,
        status: JobStatus,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ) -> bool:
        """Update job status and result"""
        update_data = {
            "status": status,
            "updated_at": datetime.utcnow()
        }
        
        if status == JobStatus.PROCESSING:
            update_data["started_at"] = datetime.utcnow()
        elif status in [JobStatus.COMPLETED, JobStatus.FAILED]:
            update_data["completed_at"] = datetime.utcnow()
        
        if result_data is not None:
            update_data["result_data"] = result_data
        
        if error_message is not None:
            update_data["error_message"] = error_message
        
        result = await session.execute(
            update(Job)
            .where(Job.job_id == job_id)
            .values(**update_data)
        )
        
        await session.commit()
        return result.rowcount > 0
    
    @staticmethod
    async def get_recent_jobs(session: AsyncSession, limit: int = 20) -> list[Job]:
        """Get recent jobs for monitoring"""
        result = await session.execute(
            select(Job)
            .order_by(Job.created_at.desc())
            .limit(limit)
        )
        return result.scalars().all()

job_service = JobService()
EOF

# Create Celery workers
cat > backend/app/workers/ai_tasks.py << 'EOF'
from celery import current_task
from app.core.celery_app import celery_app
from app.services.ai_service import ai_service
from app.services.job_service import job_service
from app.core.database import SessionLocal
from app.models.job import JobStatus
import asyncio
import logging

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, max_retries=3)
def generate_quiz_questions(self, job_id: str, topic: str, num_questions: int = 5, difficulty: str = "medium"):
    """Background task to generate quiz questions using AI"""
    
    async def _generate_quiz():
        async with SessionLocal() as session:
            try:
                # Update job status to processing
                await job_service.update_job_status(
                    session, job_id, JobStatus.PROCESSING
                )
                
                # Generate questions using AI service
                questions = await ai_service.generate_quiz_questions(
                    topic=topic,
                    num_questions=num_questions,
                    difficulty=difficulty
                )
                
                # Update job with results
                await job_service.update_job_status(
                    session, 
                    job_id, 
                    JobStatus.COMPLETED,
                    result_data={
                        "questions": questions,
                        "metadata": {
                            "topic": topic,
                            "num_questions": len(questions),
                            "difficulty": difficulty
                        }
                    }
                )
                
                logger.info(f"Successfully generated {len(questions)} questions for job {job_id}")
                return {"status": "success", "questions_generated": len(questions)}
                
            except Exception as e:
                logger.error(f"Error generating questions for job {job_id}: {str(e)}")
                
                # Update job with error
                await job_service.update_job_status(
                    session,
                    job_id,
                    JobStatus.FAILED,
                    error_message=str(e)
                )
                
                # Retry if we haven't exceeded max retries
                if self.request.retries < self.max_retries:
                    logger.info(f"Retrying job {job_id}, attempt {self.request.retries + 1}")
                    await job_service.update_job_status(
                        session, job_id, JobStatus.RETRYING
                    )
                    raise self.retry(countdown=60 * (2 ** self.request.retries))
                
                raise e
    
    # Run the async function
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_generate_quiz())
    finally:
        loop.close()

@celery_app.task(bind=True)
def process_batch_quiz(self, job_id: str, topics: list, num_questions_per_topic: int = 5):
    """Process multiple quiz generation requests in batch"""
    
    async def _process_batch():
        async with SessionLocal() as session:
            try:
                await job_service.update_job_status(
                    session, job_id, JobStatus.PROCESSING
                )
                
                all_questions = []
                for i, topic in enumerate(topics):
                    # Update progress
                    current_task.update_state(
                        state='PROGRESS',
                        meta={'current': i + 1, 'total': len(topics), 'status': f'Processing {topic}'}
                    )
                    
                    questions = await ai_service.generate_quiz_questions(
                        topic=topic,
                        num_questions=num_questions_per_topic
                    )
                    
                    all_questions.append({
                        "topic": topic,
                        "questions": questions
                    })
                
                await job_service.update_job_status(
                    session,
                    job_id,
                    JobStatus.COMPLETED,
                    result_data={
                        "batch_results": all_questions,
                        "total_topics": len(topics),
                        "total_questions": len(topics) * num_questions_per_topic
                    }
                )
                
                return {"status": "success", "topics_processed": len(topics)}
                
            except Exception as e:
                await job_service.update_job_status(
                    session, job_id, JobStatus.FAILED, error_message=str(e)
                )
                raise e
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(_process_batch())
    finally:
        loop.close()
EOF

# Create API routes
cat > backend/app/api/jobs.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.services.job_service import job_service
from app.workers.ai_tasks import generate_quiz_questions, process_batch_quiz
from app.models.job import JobStatus
from pydantic import BaseModel
from typing import List, Optional
import redis
from app.core.config import settings

router = APIRouter()

# Redis connection for job monitoring
redis_client = redis.from_url(settings.redis_url)

class QuizGenerationRequest(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"

class BatchQuizRequest(BaseModel):
    topics: List[str]
    num_questions_per_topic: int = 5

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

@router.post("/jobs/generate-quiz", response_model=JobResponse)
async def create_quiz_generation_job(
    request: QuizGenerationRequest,
    session: AsyncSession = Depends(get_db)
):
    """Create a background job to generate quiz questions"""
    
    # Create job record
    job = await job_service.create_job(
        session=session,
        job_type="quiz_generation",
        input_data={
            "topic": request.topic,
            "num_questions": request.num_questions,
            "difficulty": request.difficulty
        }
    )
    
    # Queue the background task
    generate_quiz_questions.delay(
        job_id=job.job_id,
        topic=request.topic,
        num_questions=request.num_questions,
        difficulty=request.difficulty
    )
    
    return JobResponse(
        job_id=job.job_id,
        status="queued",
        message=f"Quiz generation job created for topic: {request.topic}"
    )

@router.post("/jobs/batch-quiz", response_model=JobResponse)
async def create_batch_quiz_job(
    request: BatchQuizRequest,
    session: AsyncSession = Depends(get_db)
):
    """Create a background job to process multiple quiz topics"""
    
    job = await job_service.create_job(
        session=session,
        job_type="batch_quiz",
        input_data={
            "topics": request.topics,
            "num_questions_per_topic": request.num_questions_per_topic
        }
    )
    
    process_batch_quiz.delay(
        job_id=job.job_id,
        topics=request.topics,
        num_questions_per_topic=request.num_questions_per_topic
    )
    
    return JobResponse(
        job_id=job.job_id,
        status="queued",
        message=f"Batch quiz generation job created for {len(request.topics)} topics"
    )

@router.get("/jobs/{job_id}")
async def get_job_status(
    job_id: str,
    session: AsyncSession = Depends(get_db)
):
    """Get job status and results"""
    
    job = await job_service.get_job(session, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    response = {
        "job_id": job.job_id,
        "status": job.status,
        "job_type": job.job_type,
        "input_data": job.input_data,
        "created_at": job.created_at.isoformat(),
        "updated_at": job.updated_at.isoformat(),
        "retry_count": job.retry_count
    }
    
    if job.started_at:
        response["started_at"] = job.started_at.isoformat()
    
    if job.completed_at:
        response["completed_at"] = job.completed_at.isoformat()
    
    if job.result_data:
        response["result_data"] = job.result_data
    
    if job.error_message:
        response["error_message"] = job.error_message
    
    return response

@router.get("/jobs")
async def list_recent_jobs(
    limit: int = 20,
    session: AsyncSession = Depends(get_db)
):
    """List recent jobs for monitoring"""
    
    jobs = await job_service.get_recent_jobs(session, limit)
    
    return [
        {
            "job_id": job.job_id,
            "job_type": job.job_type,
            "status": job.status,
            "created_at": job.created_at.isoformat(),
            "input_data": job.input_data
        }
        for job in jobs
    ]

@router.get("/jobs/stats/summary")
async def get_job_stats():
    """Get job queue statistics"""
    
    try:
        # Get queue information from Redis
        queue_length = redis_client.llen("celery")
        
        # You can add more Redis-based stats here
        return {
            "queue_length": queue_length,
            "active_workers": "Check Flower dashboard",
            "redis_status": "connected"
        }
    except Exception as e:
        return {
            "queue_length": 0,
            "error": str(e),
            "redis_status": "disconnected"
        }
EOF

# Create frontend package.json
echo "🎨 Creating frontend structure..."
cat > frontend/package.json << 'EOF'
{
  "name": "quiz-platform-frontend",
  "version": "0.1.0",
  "private": true,
  "dependencies": {
    "@testing-library/jest-dom": "^5.17.0",
    "@testing-library/react": "^13.4.0",
    "@testing-library/user-event": "^14.5.2",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.7",
    "react-router-dom": "^6.21.3",
    "lucide-react": "^0.344.0",
    "recharts": "^2.12.0"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

# Create frontend components
cat > frontend/src/services/api.js << 'EOF'
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

export const jobsAPI = {
  // Create quiz generation job
  createQuizJob: async (data) => {
    const response = await api.post('/jobs/generate-quiz', data);
    return response.data;
  },

  // Create batch quiz job
  createBatchJob: async (data) => {
    const response = await api.post('/jobs/batch-quiz', data);
    return response.data;
  },

  // Get job status
  getJobStatus: async (jobId) => {
    const response = await api.get(`/jobs/${jobId}`);
    return response.data;
  },

  // List recent jobs
  listJobs: async (limit = 20) => {
    const response = await api.get(`/jobs?limit=${limit}`);
    return response.data;
  },

  // Get job statistics
  getJobStats: async () => {
    const response = await api.get('/jobs/stats/summary');
    return response.data;
  }
};

export default api;
EOF

cat > frontend/src/components/JobStatus.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { Clock, CheckCircle, XCircle, AlertCircle, RefreshCw } from 'lucide-react';

const JobStatus = ({ jobId, onJobComplete }) => {
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!jobId) return;

    const pollJobStatus = async () => {
      try {
        const response = await fetch(`http://localhost:8000/api/v1/jobs/${jobId}`);
        const jobData = await response.json();
        
        setJob(jobData);
        setLoading(false);

        // If job is complete, notify parent and stop polling
        if (jobData.status === 'completed' || jobData.status === 'failed') {
          if (onJobComplete) {
            onJobComplete(jobData);
          }
          return;
        }

        // Continue polling if job is still running
        if (jobData.status === 'pending' || jobData.status === 'processing' || jobData.status === 'retrying') {
          setTimeout(pollJobStatus, 2000); // Poll every 2 seconds
        }
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    pollJobStatus();
  }, [jobId, onJobComplete]);

  if (loading) {
    return (
      <div className="flex items-center space-x-2 p-4 bg-blue-50 rounded-lg">
        <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />
        <span>Loading job status...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center space-x-2 p-4 bg-red-50 rounded-lg">
        <XCircle className="w-5 h-5 text-red-500" />
        <span className="text-red-700">Error: {error}</span>
      </div>
    );
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-5 h-5 text-yellow-500" />;
      case 'processing':
        return <RefreshCw className="w-5 h-5 animate-spin text-blue-500" />;
      case 'retrying':
        return <AlertCircle className="w-5 h-5 text-orange-500" />;
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'failed':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Clock className="w-5 h-5 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-50 border-yellow-200';
      case 'processing':
        return 'bg-blue-50 border-blue-200';
      case 'retrying':
        return 'bg-orange-50 border-orange-200';
      case 'completed':
        return 'bg-green-50 border-green-200';
      case 'failed':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  return (
    <div className={`p-4 rounded-lg border ${getStatusColor(job.status)}`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center space-x-2">
          {getStatusIcon(job.status)}
          <span className="font-medium capitalize">{job.status}</span>
        </div>
        <span className="text-sm text-gray-500">Job ID: {job.job_id.slice(0, 8)}...</span>
      </div>

      <div className="space-y-2 text-sm">
        <div>
          <span className="font-medium">Type:</span> {job.job_type}
        </div>
        <div>
          <span className="font-medium">Created:</span> {new Date(job.created_at).toLocaleString()}
        </div>
        {job.started_at && (
          <div>
            <span className="font-medium">Started:</span> {new Date(job.started_at).toLocaleString()}
          </div>
        )}
        {job.completed_at && (
          <div>
            <span className="font-medium">Completed:</span> {new Date(job.completed_at).toLocaleString()}
          </div>
        )}
        {job.retry_count > 0 && (
          <div>
            <span className="font-medium">Retries:</span> {job.retry_count}
          </div>
        )}
      </div>

      {job.error_message && (
        <div className="mt-3 p-2 bg-red-100 rounded text-sm text-red-700">
          <span className="font-medium">Error:</span> {job.error_message}
        </div>
      )}

      {job.result_data && (
        <div className="mt-3">
          <span className="font-medium text-sm">Results:</span>
          <div className="mt-1 p-2 bg-white rounded border text-sm">
            {job.result_data.questions && (
              <div>Generated {job.result_data.questions.length} questions</div>
            )}
            {job.result_data.batch_results && (
              <div>Processed {job.result_data.total_topics} topics, {job.result_data.total_questions} questions</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default JobStatus;
EOF

cat > frontend/src/components/QuizGenerator.js << 'EOF'
import React, { useState } from 'react';
import { Play, List, Upload } from 'lucide-react';
import JobStatus from './JobStatus';

const QuizGenerator = () => {
  const [activeTab, setActiveTab] = useState('single');
  const [singleForm, setSingleForm] = useState({
    topic: '',
    num_questions: 5,
    difficulty: 'medium'
  });
  const [batchForm, setBatchForm] = useState({
    topics: '',
    num_questions_per_topic: 5
  });
  const [currentJob, setCurrentJob] = useState(null);
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSingleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResults(null);

    try {
      const response = await fetch('http://localhost:8000/api/v1/jobs/generate-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(singleForm),
      });

      const data = await response.json();
      setCurrentJob(data.job_id);
    } catch (error) {
      console.error('Error creating job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setResults(null);

    const topics = batchForm.topics.split('\n').filter(topic => topic.trim());

    try {
      const response = await fetch('http://localhost:8000/api/v1/jobs/batch-quiz', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          topics,
          num_questions_per_topic: batchForm.num_questions_per_topic
        }),
      });

      const data = await response.json();
      setCurrentJob(data.job_id);
    } catch (error) {
      console.error('Error creating batch job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleJobComplete = (jobData) => {
    if (jobData.status === 'completed') {
      setResults(jobData.result_data);
    }
    // Reset current job to stop polling
    setCurrentJob(null);
  };

  const renderQuestions = (questions) => {
    return questions.map((q, index) => (
      <div key={index} className="p-4 border rounded-lg bg-white">
        <div className="font-medium mb-2">{index + 1}. {q.question}</div>
        <div className="space-y-1 mb-2">
          {q.options.map((option, optIndex) => (
            <div
              key={optIndex}
              className={`p-2 rounded text-sm ${
                optIndex === q.correct_answer
                  ? 'bg-green-100 text-green-800 font-medium'
                  : 'bg-gray-50'
              }`}
            >
              {String.fromCharCode(65 + optIndex)}. {option}
            </div>
          ))}
        </div>
        <div className="text-sm text-gray-600 italic">
          <strong>Explanation:</strong> {q.explanation}
        </div>
      </div>
    ));
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-lg">
        <div className="border-b border-gray-200">
          <nav className="flex">
            <button
              onClick={() => setActiveTab('single')}
              className={`py-4 px-6 text-sm font-medium ${
                activeTab === 'single'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <Play className="w-4 h-4 inline mr-2" />
              Single Quiz
            </button>
            <button
              onClick={() => setActiveTab('batch')}
              className={`py-4 px-6 text-sm font-medium ${
                activeTab === 'batch'
                  ? 'border-b-2 border-blue-500 text-blue-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              <List className="w-4 h-4 inline mr-2" />
              Batch Quiz
            </button>
          </nav>
        </div>

        <div className="p-6">
          {activeTab === 'single' && (
            <form onSubmit={handleSingleSubmit} className="space-y-4">
              <h3 className="text-lg font-medium mb-4">Generate Single Quiz</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Topic
                </label>
                <input
                  type="text"
                  value={singleForm.topic}
                  onChange={(e) => setSingleForm({...singleForm, topic: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="Enter quiz topic (e.g., Python Programming)"
                  required
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Number of Questions
                  </label>
                  <select
                    value={singleForm.num_questions}
                    onChange={(e) => setSingleForm({...singleForm, num_questions: parseInt(e.target.value)})}
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value={5}>5 Questions</option>
                    <option value={10}>10 Questions</option>
                    <option value={15}>15 Questions</option>
                    <option value={20}>20 Questions</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Difficulty
                  </label>
                  <select
                    value={singleForm.difficulty}
                    onChange={(e) => setSingleForm({...singleForm, difficulty: e.target.value})}
                    className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating Job...' : 'Generate Quiz'}
              </button>
            </form>
          )}

          {activeTab === 'batch' && (
            <form onSubmit={handleBatchSubmit} className="space-y-4">
              <h3 className="text-lg font-medium mb-4">Generate Batch Quizzes</h3>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Topics (one per line)
                </label>
                <textarea
                  value={batchForm.topics}
                  onChange={(e) => setBatchForm({...batchForm, topics: e.target.value})}
                  rows={6}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  placeholder="JavaScript Fundamentals&#10;React Hooks&#10;Node.js Basics&#10;MongoDB Operations"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Questions per Topic
                </label>
                <select
                  value={batchForm.num_questions_per_topic}
                  onChange={(e) => setBatchForm({...batchForm, num_questions_per_topic: parseInt(e.target.value)})}
                  className="w-full p-2 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value={3}>3 Questions</option>
                  <option value={5}>5 Questions</option>
                  <option value={10}>10 Questions</option>
                </select>
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Creating Batch Job...' : 'Generate Batch Quizzes'}
              </button>
            </form>
          )}

          {currentJob && (
            <div className="mt-6">
              <h4 className="text-md font-medium mb-3">Job Status</h4>
              <JobStatus jobId={currentJob} onJobComplete={handleJobComplete} />
            </div>
          )}

          {results && (
            <div className="mt-6">
              <h4 className="text-lg font-medium mb-4">Generated Questions</h4>
              
              {results.questions && (
                <div className="space-y-4">
                  {renderQuestions(results.questions)}
                </div>
              )}

              {results.batch_results && (
                <div className="space-y-6">
                  {results.batch_results.map((batch, index) => (
                    <div key={index} className="border-l-4 border-blue-500 pl-4">
                      <h5 className="text-md font-medium mb-3 text-blue-700">
                        {batch.topic}
                      </h5>
                      <div className="space-y-3">
                        {renderQuestions(batch.questions)}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuizGenerator;
EOF

cat > frontend/src/pages/Dashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { Activity, Clock, CheckCircle, XCircle, BarChart3 } from 'lucide-react';

const Dashboard = () => {
  const [jobs, setJobs] = useState([]);
  const [stats, setStats] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchJobs();
    fetchStats();
    
    // Refresh data every 10 seconds
    const interval = setInterval(() => {
      fetchJobs();
      fetchStats();
    }, 10000);

    return () => clearInterval(interval);
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/jobs?limit=50');
      const data = await response.json();
      setJobs(data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/v1/jobs/stats/summary');
      const data = await response.json();
      setStats(data);
    } catch (error) {
      console.error('Error fetching stats:', error);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-yellow-500" />;
      case 'processing':
        return <Activity className="w-4 h-4 text-blue-500" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'failed':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      case 'processing':
        return 'bg-blue-100 text-blue-800';
      case 'completed':
        return 'bg-green-100 text-green-800';
      case 'failed':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const jobStats = jobs.reduce((acc, job) => {
    acc[job.status] = (acc[job.status] || 0) + 1;
    return acc;
  }, {});

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Job Processing Dashboard</h1>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Activity className="w-4 h-4" />
          <span>Auto-refresh every 10s</span>
        </div>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-blue-100 rounded-lg">
              <BarChart3 className="w-6 h-6 text-blue-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Queue Length</p>
              <p className="text-2xl font-semibold text-gray-900">{stats.queue_length || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-green-100 rounded-lg">
              <CheckCircle className="w-6 h-6 text-green-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Completed</p>
              <p className="text-2xl font-semibold text-gray-900">{jobStats.completed || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-yellow-100 rounded-lg">
              <Clock className="w-6 h-6 text-yellow-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Pending</p>
              <p className="text-2xl font-semibold text-gray-900">{jobStats.pending || 0}</p>
            </div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow">
          <div className="flex items-center">
            <div className="p-2 bg-red-100 rounded-lg">
              <XCircle className="w-6 h-6 text-red-600" />
            </div>
            <div className="ml-4">
              <p className="text-sm font-medium text-gray-600">Failed</p>
              <p className="text-2xl font-semibold text-gray-900">{jobStats.failed || 0}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Jobs Table */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-medium text-gray-900">Recent Jobs</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Job ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Input
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Created
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {jobs.map((job) => (
                <tr key={job.job_id} className="hover:bg-gray-50">
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-900">
                    {job.job_id.slice(0, 8)}...
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className="capitalize">{job.job_type.replace('_', ' ')}</span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getStatusColor(job.status)}`}>
                      {getStatusIcon(job.status)}
                      <span className="ml-1 capitalize">{job.status}</span>
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900 max-w-xs truncate">
                    {job.input_data.topic && (
                      <span>Topic: {job.input_data.topic}</span>
                    )}
                    {job.input_data.topics && (
                      <span>{job.input_data.topics.length} topics</span>
                    )}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {new Date(job.created_at).toLocaleString()}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {jobs.length === 0 && (
        <div className="text-center py-12">
          <Clock className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No jobs yet</h3>
          <p className="mt-1 text-sm text-gray-500">
            Create your first quiz generation job to see it here.
          </p>
        </div>
      )}
    </div>
  );
};

export default Dashboard;
EOF

cat > frontend/src/App.js << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom';
import { Play, BarChart3 } from 'lucide-react';
import QuizGenerator from './components/QuizGenerator';
import Dashboard from './pages/Dashboard';

const Navigation = () => {
  const location = useLocation();
  
  return (
    <nav className="bg-white shadow-lg">
      <div className="max-w-6xl mx-auto px-6">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <h1 className="text-xl font-bold text-gray-800">Quiz Platform</h1>
            <span className="ml-2 text-sm text-gray-500">Background Jobs</span>
          </div>
          
          <div className="flex space-x-4">
            <Link
              to="/"
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                location.pathname === '/'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <Play className="w-4 h-4 mr-2" />
              Generator
            </Link>
            
            <Link
              to="/dashboard"
              className={`flex items-center px-3 py-2 rounded-md text-sm font-medium ${
                location.pathname === '/dashboard'
                  ? 'bg-blue-100 text-blue-700'
                  : 'text-gray-600 hover:text-gray-900 hover:bg-gray-100'
              }`}
            >
              <BarChart3 className="w-4 h-4 mr-2" />
              Dashboard
            </Link>
          </div>
        </div>
      </div>
    </nav>
  );
};

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-100">
        <Navigation />
        <main className="py-6">
          <Routes>
            <Route path="/" element={<QuizGenerator />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
EOF

cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="Quiz Platform with Background Job Processing" />
    <title>Quiz Platform - Background Jobs</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# Create Docker configurations
echo "🐳 Creating Docker configurations..."
cat > docker/docker-compose.yml << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: quiz_db
      POSTGRES_USER: quiz_user
      POSTGRES_PASSWORD: quiz_pass
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U quiz_user -d quiz_db"]
      interval: 10s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ../backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://quiz_user:quiz_pass@postgres:5432/quiz_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ../backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery-worker:
    build:
      context: ../backend
      dockerfile: Dockerfile
    environment:
      - DATABASE_URL=postgresql://quiz_user:quiz_pass@postgres:5432/quiz_db
      - REDIS_URL=redis://redis:6379/0
      - CELERY_BROKER_URL=redis://redis:6379/0
      - CELERY_RESULT_BACKEND=redis://redis:6379/1
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    volumes:
      - ../backend:/app
    command: celery -A app.core.celery_app worker --loglevel=info --queues=ai_generation,batch_processing

  flower:
    build:
      context: ../backend
      dockerfile: Dockerfile
    ports:
      - "5555:5555"
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0
    depends_on:
      - redis
    volumes:
      - ../backend:/app
    command: celery -A app.core.celery_app flower --port=5555

  frontend:
    build:
      context: ../frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000/api/v1
    volumes:
      - ../frontend:/app
      - /app/node_modules
    command: npm start

volumes:
  postgres_data:
EOF

cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
EOF

# Create test files
echo "🧪 Creating test files..."
cat > backend/tests/test_job_service.py << 'EOF'
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
EOF

cat > backend/tests/test_api.py << 'EOF'
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Quiz Platform" in response.json()["message"]

def test_create_quiz_job():
    """Test creating a quiz generation job"""
    job_data = {
        "topic": "Python Programming",
        "num_questions": 5,
        "difficulty": "medium"
    }
    
    response = client.post("/api/v1/jobs/generate-quiz", json=job_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "Python Programming" in data["message"]

def test_create_batch_job():
    """Test creating a batch quiz job"""
    job_data = {
        "topics": ["JavaScript", "React", "Node.js"],
        "num_questions_per_topic": 3
    }
    
    response = client.post("/api/v1/jobs/batch-quiz", json=job_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "job_id" in data
    assert data["status"] == "queued"
    assert "3 topics" in data["message"]

def test_list_jobs():
    """Test listing jobs"""
    response = client.get("/api/v1/jobs")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_job_stats():
    """Test job statistics endpoint"""
    response = client.get("/api/v1/jobs/stats/summary")
    assert response.status_code == 200
    
    data = response.json()
    assert "queue_length" in data
EOF

# Create startup script
cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Quiz Platform - Day 26: Background Job Processing"

# Check if .env exists and has API key
if [ ! -f backend/.env ]; then
    echo "❌ backend/.env file not found!"
    exit 1
fi

if ! grep -q "GEMINI_API_KEY=your_gemini_api_key_here" backend/.env; then
    echo "⚠️  Please update your GEMINI_API_KEY in backend/.env"
    echo "Get your API key from: https://aistudio.google.com/app/apikey"
    read -p "Press Enter to continue anyway..."
fi

# Create Python virtual environment
echo "🐍 Creating Python virtual environment..."
python -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start services with Docker
echo "🐳 Starting Docker services..."
cd docker
docker-compose down
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for database and Redis..."
sleep 10

# Start backend
echo "🖥️  Starting backend server..."
cd ../backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Celery worker
echo "👷 Starting Celery worker..."
python -m celery -A app.core.celery_app worker --loglevel=info &
WORKER_PID=$!

# Start Flower monitoring
echo "🌸 Starting Flower monitoring..."
python -m celery -A app.core.celery_app flower --port=5555 &
FLOWER_PID=$!

# Wait for backend to start
sleep 5

# Run tests
echo "🧪 Running backend tests..."
python -m pytest tests/ -v

# Start frontend
echo "🎨 Starting frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo ""
echo "✅ All services started successfully!"
echo ""
echo "🌐 Access points:"
echo "   Frontend:    http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   Flower:      http://localhost:5555"
echo "   API Docs:    http://localhost:8000/docs"
echo ""
echo "📝 Test the application:"
echo "   1. Go to http://localhost:3000"
echo "   2. Create a quiz generation job"
echo "   3. Monitor progress in real-time"
echo "   4. Check Flower dashboard for worker stats"
echo ""
echo "⚠️  Remember to set your GEMINI_API_KEY in backend/.env"
echo ""

# Save PIDs for cleanup
echo $BACKEND_PID $WORKER_PID $FLOWER_PID $FRONTEND_PID > .pids

echo "Press Ctrl+C to stop all services"
wait
EOF

cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping Quiz Platform services..."

# Kill processes if PID file exists
if [ -f .pids ]; then
    PIDS=$(cat .pids)
    for PID in $PIDS; do
        if ps -p $PID > /dev/null; then
            echo "Stopping process $PID..."
            kill $PID
        fi
    done
    rm .pids
fi

# Stop Docker services
echo "🐳 Stopping Docker services..."
cd docker
docker-compose down

echo "✅ All services stopped!"
EOF

chmod +x start.sh stop.sh

echo ""
echo "✅ Day 26: Background Job Processing - Implementation Complete!"
echo ""
echo "📁 Project structure created:"
echo "   - Backend: FastAPI + Celery + Redis"
echo "   - Frontend: React with real-time monitoring"
echo "   - Database: PostgreSQL"
echo "   - Queue: Redis"
echo "   - Monitoring: Flower"
echo ""
echo "🚀 To start the application:"
echo "   1. Set your GEMINI_API_KEY in backend/.env"
echo "   2. Run: ./start.sh"
echo ""
echo "🧪 Features implemented:"
echo "   ✅ Asynchronous job processing"
echo "   ✅ Real-time status monitoring"
echo "   ✅ Automatic retry logic"
echo "   ✅ Batch processing capabilities"
echo "   ✅ Worker monitoring with Flower"
echo "   ✅ Comprehensive test suite"
echo ""
echo "📊 Monitor your jobs at:"
echo "   - Frontend: http://localhost:3000"
echo "   - Flower: http://localhost:5555"
echo "   - API Docs: http://localhost:8000/docs"
echo ""