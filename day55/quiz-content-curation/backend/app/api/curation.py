from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime

from app.models.database import get_db
from app.services.curation_service import CurationService
from app.schemas.schemas import (
    CurationCreate, CurationResponse, CurationAction, 
    QueueResponse, QueueItem, AuditLogResponse
)

router = APIRouter()

def format_time_in_queue(created_at: datetime) -> str:
    delta = datetime.utcnow() - created_at
    hours = delta.total_seconds() / 3600
    if hours < 1:
        return f"{int(delta.total_seconds() / 60)}m"
    elif hours < 24:
        return f"{int(hours)}h"
    else:
        return f"{int(hours / 24)}d"

@router.get("/queue", response_model=QueueResponse)
async def get_curation_queue(
    status: str = "pending",
    limit: int = 20,
    page: int = 1,
    sort_by: str = "priority",
    db: AsyncSession = Depends(get_db)
):
    """Get items in curation queue"""
    service = CurationService(db)
    offset = (page - 1) * limit
    items, total = await service.get_queue(status, limit, offset, sort_by)
    
    queue_items = []
    for item in items:
        queue_items.append(QueueItem(
            id=item.id,
            question_id=item.question_id,
            preview=item.question.text[:100] + "..." if len(item.question.text) > 100 else item.question.text,
            quality_score=item.quality_score,
            priority_score=item.priority_score,
            topic=item.question.topic,
            difficulty=item.question.difficulty,
            created_at=item.created_at,
            time_in_queue=format_time_in_queue(item.created_at)
        ))
    
    return QueueResponse(
        items=queue_items,
        total=total,
        page=page,
        page_size=limit
    )

@router.get("/{curation_id}", response_model=CurationResponse)
async def get_curation(
    curation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get curation details"""
    service = CurationService(db)
    curation = await service.get_curation(curation_id)
    if not curation:
        raise HTTPException(status_code=404, detail="Curation not found")
    return curation

@router.post("/{curation_id}/claim", response_model=CurationResponse)
async def claim_content(
    curation_id: str,
    action: CurationAction,
    db: AsyncSession = Depends(get_db)
):
    """Claim content for review"""
    service = CurationService(db)
    try:
        return await service.claim_for_review(curation_id, action.reviewer_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{curation_id}/approve", response_model=CurationResponse)
async def approve_content(
    curation_id: str,
    action: CurationAction,
    db: AsyncSession = Depends(get_db)
):
    """Approve content for production"""
    service = CurationService(db)
    try:
        return await service.approve_content(curation_id, action.reviewer_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{curation_id}/reject", response_model=CurationResponse)
async def reject_content(
    curation_id: str,
    action: CurationAction,
    db: AsyncSession = Depends(get_db)
):
    """Reject content with reason"""
    service = CurationService(db)
    if not action.feedback:
        raise HTTPException(status_code=400, detail="Rejection reason required")
    try:
        return await service.reject_content(curation_id, action.reviewer_id, action.feedback)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{curation_id}/revise", response_model=CurationResponse)
async def request_revision(
    curation_id: str,
    action: CurationAction,
    db: AsyncSession = Depends(get_db)
):
    """Request content revision with feedback"""
    service = CurationService(db)
    if not action.feedback:
        raise HTTPException(status_code=400, detail="Revision feedback required")
    try:
        return await service.request_revision(curation_id, action.reviewer_id, action.feedback)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{curation_id}/release", response_model=CurationResponse)
async def release_claim(
    curation_id: str,
    action: CurationAction,
    db: AsyncSession = Depends(get_db)
):
    """Release claimed content back to queue"""
    service = CurationService(db)
    try:
        return await service.release_claim(curation_id, action.reviewer_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{curation_id}/audit", response_model=list[AuditLogResponse])
async def get_audit_logs(
    curation_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get audit logs for a curation"""
    service = CurationService(db)
    return await service.get_audit_logs(curation_id)
