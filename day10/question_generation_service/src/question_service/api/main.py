"""FastAPI application with async question generation endpoints"""

import asyncio
import os
import uuid
from contextlib import asynccontextmanager
from datetime import datetime
from typing import List, Optional

import redis.asyncio as redis
import structlog
from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..core.job_manager import JobManager
from ..core.question_generator import QuestionGenerator
from ..models.schemas import JobResponse, JobSubmission, QuestionResponse
from ..providers.ai_provider import AIProviderFactory

logger = structlog.get_logger()

# Global instances
redis_client: Optional[redis.Redis] = None
job_manager: Optional[JobManager] = None
question_generator: Optional[QuestionGenerator] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global redis_client, job_manager, question_generator

    # Startup
    logger.info("Starting Question Generation Service...")

    redis_client = redis.from_url("redis://localhost:6379", decode_responses=True)
    ai_provider = AIProviderFactory.create_provider(
        os.getenv("AI_PROVIDER", "anthropic")
    )

    job_manager = JobManager(redis_client)
    question_generator = QuestionGenerator(ai_provider, job_manager)

    await job_manager.initialize()

    logger.info("Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down...")
    if redis_client:
        await redis_client.close()


app = FastAPI(
    title="Question Generation Service",
    description="Asynchronous AI-powered question generation with retry logic",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        await redis_client.ping()
        return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
    except Exception as e:
        logger.error("Health check failed", error=str(e))
        raise HTTPException(status_code=503, detail="Service unavailable")


@app.post("/questions/generate", response_model=JobResponse)
async def generate_questions(
    submission: JobSubmission, background_tasks: BackgroundTasks
):
    """Submit question generation job"""
    job_id = str(uuid.uuid4())

    try:
        # Queue job for processing
        await job_manager.create_job(job_id, submission.dict())

        # Start background processing
        background_tasks.add_task(
            question_generator.process_job,
            job_id,
            submission.topic,
            submission.count,
            submission.difficulty,
        )

        logger.info("Job queued", job_id=job_id, topic=submission.topic)

        return JobResponse(
            job_id=job_id, status="pending", message="Job queued for processing"
        )

    except Exception as e:
        logger.error("Failed to queue job", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to queue job")


@app.get("/questions/jobs/{job_id}", response_model=QuestionResponse)
async def get_job_status(job_id: str):
    """Get job status and results"""
    try:
        job_data = await job_manager.get_job(job_id)

        if not job_data:
            raise HTTPException(status_code=404, detail="Job not found")

        return QuestionResponse(**job_data)

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to get job", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to retrieve job")


@app.websocket("/questions/jobs/{job_id}/status")
async def websocket_job_status(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job status updates"""
    await websocket.accept()

    try:
        while True:
            job_data = await job_manager.get_job(job_id)

            if job_data:
                await websocket.send_json(job_data)

                # Close connection if job is completed
                if job_data["status"] in ["completed", "failed", "cancelled"]:
                    break

            await asyncio.sleep(1)

    except Exception as e:
        logger.error("WebSocket error", job_id=job_id, error=str(e))
    finally:
        await websocket.close()


@app.get("/questions/jobs", response_model=List[QuestionResponse])
async def list_jobs(status: Optional[str] = None, limit: int = 10, offset: int = 0):
    """List jobs with optional filtering"""
    try:
        jobs = await job_manager.list_jobs(status, limit, offset)
        return [QuestionResponse(**job) for job in jobs]
    except Exception as e:
        logger.error("Failed to list jobs", error=str(e))
        raise HTTPException(status_code=500, detail="Failed to list jobs")


@app.delete("/questions/jobs/{job_id}")
async def cancel_job(job_id: str):
    """Cancel a job"""
    try:
        success = await job_manager.cancel_job(job_id)

        if not success:
            raise HTTPException(status_code=404, detail="Job not found")

        return {"message": "Job cancelled successfully"}

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to cancel job", job_id=job_id, error=str(e))
        raise HTTPException(status_code=500, detail="Failed to cancel job")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
