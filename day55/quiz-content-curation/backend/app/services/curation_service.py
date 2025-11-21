from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import json

from app.models.models import ContentCuration, CurationAuditLog, Question, CurationStatus
from app.schemas.schemas import QualityMetrics

class CurationService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    def _calculate_composite_score(self, metrics: QualityMetrics) -> float:
        """Calculate weighted composite quality score"""
        return (
            metrics.readability_score * 0.15 +
            metrics.factual_confidence * 0.30 +
            metrics.distractor_quality * 0.25 +
            metrics.topic_alignment * 0.20 +
            metrics.difficulty_match * 0.10
        )
    
    def _calculate_priority(self, quality_score: float, created_at: datetime) -> float:
        """Calculate priority score for queue ordering"""
        age_hours = (datetime.utcnow() - created_at).total_seconds() / 3600
        age_boost = min(age_hours * 0.01, 0.2)
        
        # Borderline scores get attention
        confidence_factor = 0.1 if 0.65 < quality_score < 0.75 else 0
        
        return quality_score + age_boost + confidence_factor
    
    async def submit_for_curation(self, question_id: str, metrics: QualityMetrics) -> ContentCuration:
        """Add new content to curation queue"""
        composite_score = self._calculate_composite_score(metrics)
        priority_score = self._calculate_priority(composite_score, datetime.utcnow())
        
        curation = ContentCuration(
            question_id=question_id,
            quality_score=composite_score,
            quality_metrics=metrics.model_dump(),
            priority_score=priority_score,
            status=CurationStatus.PENDING.value
        )
        self.db.add(curation)
        await self.db.commit()
        await self.db.refresh(curation)
        
        await self._create_audit_log(
            curation.id, 
            "submitted", 
            None, 
            CurationStatus.PENDING.value,
            "system",
            {"quality_score": composite_score}
        )
        
        return curation
    
    async def get_queue(
        self, 
        status: str = "pending", 
        limit: int = 20, 
        offset: int = 0,
        sort_by: str = "priority"
    ) -> tuple[List[ContentCuration], int]:
        """Get items in curation queue"""
        query = select(ContentCuration).options(
            selectinload(ContentCuration.question)
        ).where(ContentCuration.status == status)
        
        if sort_by == "priority":
            query = query.order_by(ContentCuration.priority_score.desc())
        elif sort_by == "created":
            query = query.order_by(ContentCuration.created_at.asc())
        elif sort_by == "quality":
            query = query.order_by(ContentCuration.quality_score.desc())
        
        # Get total count
        count_query = select(func.count(ContentCuration.id)).where(
            ContentCuration.status == status
        )
        total = await self.db.scalar(count_query)
        
        # Get items
        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        items = result.scalars().all()
        
        return items, total
    
    async def get_curation(self, curation_id: str) -> Optional[ContentCuration]:
        """Get single curation by ID"""
        query = select(ContentCuration).options(
            selectinload(ContentCuration.question)
        ).where(ContentCuration.id == curation_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def claim_for_review(self, curation_id: str, reviewer_id: str) -> ContentCuration:
        """Curator claims content for review"""
        curation = await self.get_curation(curation_id)
        if not curation:
            raise ValueError("Curation not found")
        if curation.status != CurationStatus.PENDING.value:
            raise ValueError(f"Content not available for review (status: {curation.status})")
        
        previous_status = curation.status
        curation.status = CurationStatus.UNDER_REVIEW.value
        curation.reviewer_id = reviewer_id
        
        await self._create_audit_log(
            curation_id, "claimed", previous_status, 
            CurationStatus.UNDER_REVIEW.value, reviewer_id
        )
        
        await self.db.commit()
        await self.db.refresh(curation)
        return curation
    
    async def approve_content(self, curation_id: str, reviewer_id: str) -> ContentCuration:
        """Mark content as approved"""
        curation = await self._validate_reviewer(curation_id, reviewer_id)
        previous_status = curation.status
        
        curation.status = CurationStatus.APPROVED.value
        curation.reviewed_at = datetime.utcnow()
        
        await self._create_audit_log(
            curation_id, "approved", previous_status,
            CurationStatus.APPROVED.value, reviewer_id
        )
        
        await self.db.commit()
        await self.db.refresh(curation)
        return curation
    
    async def reject_content(self, curation_id: str, reviewer_id: str, reason: str) -> ContentCuration:
        """Mark content as rejected with reason"""
        curation = await self._validate_reviewer(curation_id, reviewer_id)
        previous_status = curation.status
        
        curation.status = CurationStatus.REJECTED.value
        curation.feedback = reason
        curation.reviewed_at = datetime.utcnow()
        
        await self._create_audit_log(
            curation_id, "rejected", previous_status,
            CurationStatus.REJECTED.value, reviewer_id,
            {"reason": reason}
        )
        
        await self.db.commit()
        await self.db.refresh(curation)
        return curation
    
    async def request_revision(self, curation_id: str, reviewer_id: str, feedback: str) -> ContentCuration:
        """Send back for AI regeneration with specific feedback"""
        curation = await self._validate_reviewer(curation_id, reviewer_id)
        previous_status = curation.status
        
        curation.status = CurationStatus.NEEDS_REVISION.value
        curation.feedback = feedback
        curation.reviewed_at = datetime.utcnow()
        
        await self._create_audit_log(
            curation_id, "revision_requested", previous_status,
            CurationStatus.NEEDS_REVISION.value, reviewer_id,
            {"feedback": feedback}
        )
        
        await self.db.commit()
        await self.db.refresh(curation)
        return curation
    
    async def release_claim(self, curation_id: str, reviewer_id: str) -> ContentCuration:
        """Release claimed content back to queue"""
        curation = await self._validate_reviewer(curation_id, reviewer_id)
        previous_status = curation.status
        
        curation.status = CurationStatus.PENDING.value
        curation.reviewer_id = None
        
        await self._create_audit_log(
            curation_id, "released", previous_status,
            CurationStatus.PENDING.value, reviewer_id
        )
        
        await self.db.commit()
        await self.db.refresh(curation)
        return curation
    
    async def _validate_reviewer(self, curation_id: str, reviewer_id: str) -> ContentCuration:
        """Validate reviewer has claimed the content"""
        curation = await self.get_curation(curation_id)
        if not curation:
            raise ValueError("Curation not found")
        if curation.status != CurationStatus.UNDER_REVIEW.value:
            raise ValueError(f"Content not under review (status: {curation.status})")
        if curation.reviewer_id != reviewer_id:
            raise ValueError("Content claimed by different reviewer")
        return curation
    
    async def _create_audit_log(
        self, 
        curation_id: str, 
        action: str, 
        previous_status: Optional[str],
        new_status: str, 
        reviewer_id: str,
        details: Optional[Dict[str, Any]] = None
    ):
        """Create audit log entry"""
        log = CurationAuditLog(
            curation_id=curation_id,
            action=action,
            previous_status=previous_status,
            new_status=new_status,
            reviewer_id=reviewer_id,
            details=details
        )
        self.db.add(log)
    
    async def get_audit_logs(self, curation_id: str) -> List[CurationAuditLog]:
        """Get audit logs for a curation"""
        query = select(CurationAuditLog).where(
            CurationAuditLog.curation_id == curation_id
        ).order_by(CurationAuditLog.timestamp.desc())
        result = await self.db.execute(query)
        return result.scalars().all()
