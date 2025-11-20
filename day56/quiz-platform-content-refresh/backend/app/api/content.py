from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.schemas.content import ContentCreate, ContentResponse, RefreshRequest, DashboardStats
from app.services.content_service import ContentService
from app.services.refresh_service import RefreshService
from app.services.metrics_service import MetricsService
from app.core.config import settings

router = APIRouter()

@router.post("/", response_model=ContentResponse)
async def create_content(
    content_data: ContentCreate,
    db: AsyncSession = Depends(get_db)
):
    service = ContentService(db)
    content = await service.create_content(content_data)
    return content

@router.get("/", response_model=List[ContentResponse])
async def get_all_content(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    service = ContentService(db)
    return await service.get_all_content(skip, limit)

@router.get("/stale", response_model=List[ContentResponse])
async def get_stale_content(
    threshold: float = 40.0,
    db: AsyncSession = Depends(get_db)
):
    service = ContentService(db)
    return await service.get_stale_content(threshold)

@router.get("/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
    content_service = ContentService(db)
    refresh_service = RefreshService(db)
    metrics_service = MetricsService(db)
    
    # Get lifecycle distribution
    distribution = await content_service.get_lifecycle_distribution()
    total = await content_service.get_content_count()
    
    # Get queue and rates
    queue_depth = await refresh_service.get_queue_depth()
    queue_breakdown = await refresh_service.get_queue_breakdown()
    rollback_rate = await refresh_service.get_rollback_rate()
    avg_freshness = await metrics_service.get_average_freshness()
    
    # Check alerts
    alerts = []
    if queue_depth > settings.ALERT_QUEUE_DEPTH:
        alerts.append({"type": "warning", "message": f"High queue depth: {queue_depth}"})
    if queue_breakdown.get("failed", 0) > 0:
        alerts.append({"type": "error", "message": f"{queue_breakdown['failed']} job(s) failed"})
    if rollback_rate > settings.ALERT_ROLLBACK_RATE:
        alerts.append({"type": "error", "message": f"High rollback rate: {rollback_rate:.1%}"})
    
    stale_pct = distribution.get("stale", 0) / total if total > 0 else 0
    if stale_pct > settings.ALERT_STALE_CONTENT_PCT:
        alerts.append({"type": "warning", "message": f"High stale content: {stale_pct:.1%}"})
    
    return DashboardStats(
        total_content=total,
        fresh_count=distribution.get("fresh", 0),
        current_count=distribution.get("current", 0),
        aging_count=distribution.get("aging", 0),
        stale_count=distribution.get("stale", 0),
        queue_depth=queue_depth,
        queue_breakdown=queue_breakdown,
        avg_freshness_score=avg_freshness,
        rollback_rate=rollback_rate,
        recent_refreshes=0,
        alerts=alerts
    )

@router.get("/{content_id}", response_model=ContentResponse)
async def get_content(
    content_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = ContentService(db)
    content = await service.get_content(content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.post("/refresh", response_model=dict)
async def request_refresh(
    request: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    service = RefreshService(db)
    job = await service.create_refresh_job(
        request.content_id,
        "manual_refresh",
        request.priority
    )
    return {"job_id": str(job.id), "status": "queued"}

@router.post("/{content_id}/attempt")
async def record_attempt(
    content_id: UUID,
    correct: bool,
    time_seconds: float,
    skipped: bool = False,
    db: AsyncSession = Depends(get_db)
):
    service = MetricsService(db)
    metrics = await service.record_attempt(content_id, correct, time_seconds, skipped)
    return {"status": "recorded", "accuracy_rate": metrics.accuracy_rate}
