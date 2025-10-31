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
