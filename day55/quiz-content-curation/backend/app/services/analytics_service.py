from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import datetime, timedelta
from typing import Dict, Any, List
from collections import Counter

from app.models.models import ContentCuration, CurationAuditLog, CurationStatus

class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_curation_analytics(self, days: int = 7) -> Dict[str, Any]:
        """Get comprehensive curation analytics"""
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        # Status distribution
        status_query = select(
            ContentCuration.status,
            func.count(ContentCuration.id)
        ).group_by(ContentCuration.status)
        result = await self.db.execute(status_query)
        status_distribution = dict(result.all())
        
        # Total items (all-time)
        total_items_query = select(func.count(ContentCuration.id))
        total_items = await self.db.scalar(total_items_query) or 0
        
        # Total reviewed (7-day)
        reviewed_query = select(func.count(ContentCuration.id)).where(
            and_(
                ContentCuration.reviewed_at.isnot(None),
                ContentCuration.reviewed_at >= cutoff
            )
        )
        total_reviewed = await self.db.scalar(reviewed_query) or 0
        
        # Total reviewed (all-time)
        reviewed_alltime_query = select(func.count(ContentCuration.id)).where(
            ContentCuration.reviewed_at.isnot(None)
        )
        total_reviewed_alltime = await self.db.scalar(reviewed_alltime_query) or 0
        
        # Approval rate (7-day)
        approved_query = select(func.count(ContentCuration.id)).where(
            and_(
                ContentCuration.status == CurationStatus.APPROVED.value,
                ContentCuration.reviewed_at >= cutoff
            )
        )
        approved_count = await self.db.scalar(approved_query) or 0
        approval_rate = approved_count / total_reviewed if total_reviewed > 0 else 0
        
        # Approval rate (all-time)
        approved_alltime_query = select(func.count(ContentCuration.id)).where(
            ContentCuration.status == CurationStatus.APPROVED.value
        )
        approved_alltime_count = await self.db.scalar(approved_alltime_query) or 0
        approval_rate_alltime = approved_alltime_count / total_reviewed_alltime if total_reviewed_alltime > 0 else 0
        
        # Average review time (7-day)
        review_times = []
        time_query = select(ContentCuration).where(
            and_(
                ContentCuration.reviewed_at.isnot(None),
                ContentCuration.reviewed_at >= cutoff
            )
        )
        result = await self.db.execute(time_query)
        for curation in result.scalars().all():
            if curation.reviewed_at and curation.created_at:
                delta = (curation.reviewed_at - curation.created_at).total_seconds() / 60
                review_times.append(delta)
        
        avg_review_time = sum(review_times) / len(review_times) if review_times else 0
        
        # Average review time (all-time)
        review_times_alltime = []
        time_alltime_query = select(ContentCuration).where(
            ContentCuration.reviewed_at.isnot(None)
        )
        result_alltime = await self.db.execute(time_alltime_query)
        for curation in result_alltime.scalars().all():
            if curation.reviewed_at and curation.created_at:
                delta = (curation.reviewed_at - curation.created_at).total_seconds() / 60
                review_times_alltime.append(delta)
        
        avg_review_time_alltime = sum(review_times_alltime) / len(review_times_alltime) if review_times_alltime else 0
        
        # Daily stats
        daily_stats = await self._get_daily_stats(cutoff)
        
        # Top rejection reasons
        rejection_reasons = await self._get_rejection_reasons(cutoff)
        
        # Model performance
        model_performance = await self._get_model_performance()
        
        return {
            "total_items": total_items,
            "total_reviewed": total_reviewed,
            "total_reviewed_alltime": total_reviewed_alltime,
            "approval_rate": round(approval_rate, 3),
            "approval_rate_alltime": round(approval_rate_alltime, 3),
            "avg_review_time_minutes": round(avg_review_time, 1),
            "avg_review_time_alltime_minutes": round(avg_review_time_alltime, 1),
            "status_distribution": status_distribution,
            "daily_stats": daily_stats,
            "top_rejection_reasons": rejection_reasons,
            "model_performance": model_performance
        }
    
    async def _get_daily_stats(self, cutoff: datetime) -> List[Dict[str, Any]]:
        """Get daily curation statistics"""
        # Simplified daily stats
        stats = []
        for i in range(7):
            day = datetime.utcnow() - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
            
            count_query = select(func.count(ContentCuration.id)).where(
                and_(
                    ContentCuration.reviewed_at >= day_start,
                    ContentCuration.reviewed_at < day_end
                )
            )
            count = await self.db.scalar(count_query) or 0
            
            stats.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "reviewed": count
            })
        
        return list(reversed(stats))
    
    async def _get_rejection_reasons(self, cutoff: datetime) -> List[Dict[str, Any]]:
        """Get top rejection reasons"""
        query = select(ContentCuration.feedback).where(
            and_(
                ContentCuration.status == CurationStatus.REJECTED.value,
                ContentCuration.feedback.isnot(None),
                ContentCuration.reviewed_at >= cutoff
            )
        )
        result = await self.db.execute(query)
        feedbacks = [r[0] for r in result.all() if r[0]]
        
        # Simple word frequency for reasons
        reasons = Counter()
        for feedback in feedbacks:
            # Extract key phrases
            words = feedback.lower().split()
            for word in words:
                if len(word) > 4:
                    reasons[word] += 1
        
        return [{"reason": k, "count": v} for k, v in reasons.most_common(5)]
    
    async def _get_model_performance(self) -> Dict[str, Dict[str, float]]:
        """Get performance metrics by source model"""
        from app.models.models import Question
        
        query = select(
            Question.source_model,
            func.count(ContentCuration.id).label('total'),
            func.avg(ContentCuration.quality_score).label('avg_score')
        ).join(ContentCuration).group_by(Question.source_model)
        
        result = await self.db.execute(query)
        
        performance = {}
        for row in result.all():
            model, total, avg_score = row
            performance[model] = {
                "total_generated": total,
                "avg_quality_score": round(float(avg_score or 0), 3)
            }
        
        return performance
