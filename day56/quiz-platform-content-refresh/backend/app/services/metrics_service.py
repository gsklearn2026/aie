from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from uuid import UUID
from datetime import datetime
import structlog

from app.models.content import ContentMetrics, QuizContent

logger = structlog.get_logger()

class MetricsService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def record_attempt(self, content_id: UUID, correct: bool, time_seconds: float, skipped: bool = False):
        """Record a quiz attempt"""
        result = await self.db.execute(
            select(ContentMetrics).where(ContentMetrics.content_id == content_id)
        )
        metrics = result.scalar_one_or_none()
        
        if not metrics:
            metrics = ContentMetrics(content_id=content_id)
            self.db.add(metrics)
        
        if skipped:
            metrics.skip_count += 1
        else:
            metrics.total_attempts += 1
            if correct:
                metrics.correct_attempts += 1
            
            # Update average time
            if metrics.avg_time_seconds == 0:
                metrics.avg_time_seconds = time_seconds
            else:
                metrics.avg_time_seconds = (
                    (metrics.avg_time_seconds * (metrics.total_attempts - 1) + time_seconds) 
                    / metrics.total_attempts
                )
        
        # Calculate rates
        total = metrics.total_attempts + metrics.skip_count
        if metrics.total_attempts > 0:
            metrics.accuracy_rate = (metrics.correct_attempts / metrics.total_attempts) * 100
        if total > 0:
            metrics.skip_rate = (metrics.skip_count / total) * 100
        
        # Calculate engagement score
        metrics.engagement_score = self._calculate_engagement(metrics)
        metrics.last_calculated_at = datetime.utcnow()
        
        await self.db.commit()
        
        logger.debug(
            "Attempt recorded",
            content_id=str(content_id),
            correct=correct,
            accuracy_rate=metrics.accuracy_rate
        )
        
        return metrics
    
    def _calculate_engagement(self, metrics: ContentMetrics) -> float:
        """Calculate engagement score (0-100)"""
        # Skip penalty
        skip_penalty = min(metrics.skip_rate, 50)
        
        # Time bonus (optimal: 30-120 seconds)
        time_score = 50
        if 30 <= metrics.avg_time_seconds <= 120:
            time_score = 100
        elif metrics.avg_time_seconds < 30:
            time_score = max(0, metrics.avg_time_seconds * 2)
        else:
            time_score = max(0, 100 - (metrics.avg_time_seconds - 120) * 0.5)
        
        # Combine scores
        engagement = ((100 - skip_penalty) * 0.6) + (time_score * 0.4)
        return round(engagement, 2)
    
    async def get_metrics(self, content_id: UUID) -> ContentMetrics:
        result = await self.db.execute(
            select(ContentMetrics).where(ContentMetrics.content_id == content_id)
        )
        return result.scalar_one_or_none()
    
    async def get_average_freshness(self) -> float:
        result = await self.db.execute(
            select(QuizContent.freshness_score)
        )
        scores = [row[0] for row in result.all()]
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)
