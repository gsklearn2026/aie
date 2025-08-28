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
