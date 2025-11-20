from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.content import RefreshJob
from app.schemas.content import JobResponse
from app.services.refresh_service import RefreshService

router = APIRouter()

@router.get("/", response_model=List[JobResponse])
async def get_jobs(
    status: str = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    query = select(RefreshJob).order_by(RefreshJob.created_at.desc()).limit(limit)
    if status:
        query = query.where(RefreshJob.status == status)
    
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/process")
async def process_jobs(
    batch_size: int = 10,
    db: AsyncSession = Depends(get_db)
):
    service = RefreshService(db)
    processed = await service.process_pending_jobs(batch_size)
    return {"processed": processed}

@router.post("/scan-freshness")
async def trigger_freshness_scan(db: AsyncSession = Depends(get_db)):
    service = RefreshService(db)
    updated = await service.scan_and_update_freshness()
    return {"updated": updated}

@router.post("/retry-failed")
async def retry_failed_jobs(db: AsyncSession = Depends(get_db)):
    """Reset failed jobs back to pending status for retry"""
    service = RefreshService(db)
    result = await db.execute(
        select(RefreshJob).where(RefreshJob.status == "failed")
    )
    failed_jobs = result.scalars().all()
    
    count = 0
    for job in failed_jobs:
        job.status = "pending"
        job.error_message = None
        job.started_at = None
        job.completed_at = None
        count += 1
    
    await db.commit()
    return {"retried": count}

@router.get("/{job_id}", response_model=JobResponse)
async def get_job(
    job_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(RefreshJob).where(RefreshJob.id == job_id)
    )
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job
