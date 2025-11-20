from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
import structlog
import asyncio
import random

from app.models.content import QuizContent, ContentVersion, RefreshJob, ContentState, ContentLifecycle
from app.services.ai_service import AIService
from app.services.metrics_service import MetricsService
from app.core.config import settings

logger = structlog.get_logger()

class RefreshService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.ai_service = AIService()
    
    async def calculate_freshness_score(self, content: QuizContent) -> float:
        """Calculate composite freshness score (0-100)"""
        # Age score (newer = higher)
        if content.last_refreshed_at:
            age_days = (datetime.utcnow() - content.last_refreshed_at).days
        else:
            age_days = (datetime.utcnow() - content.created_at).days
        
        age_score = max(0, 100 - (age_days * 1.5))
        
        # Engagement score from metrics
        engagement_score = 50.0
        if content.metrics:
            engagement_score = content.metrics.engagement_score
        
        # Accuracy score (optimal is 60-80%)
        accuracy_score = 50.0
        if content.metrics and content.metrics.total_attempts > 0:
            accuracy = content.metrics.accuracy_rate
            if 60 <= accuracy <= 80:
                accuracy_score = 100
            elif accuracy > 80:
                accuracy_score = max(0, 100 - (accuracy - 80) * 2)
            else:
                accuracy_score = max(0, accuracy * 1.5)
        
        # Composite score
        score = (age_score * 0.3) + (engagement_score * 0.4) + (accuracy_score * 0.3)
        return round(score, 2)
    
    def determine_lifecycle(self, score: float, age_days: int) -> ContentLifecycle:
        """Determine lifecycle stage based on score and age"""
        if age_days <= 7 and score >= 70:
            return ContentLifecycle.FRESH
        elif age_days <= 30 and score >= 50:
            return ContentLifecycle.CURRENT
        elif age_days <= 90 and score >= 30:
            return ContentLifecycle.AGING
        else:
            return ContentLifecycle.STALE
    
    async def scan_and_update_freshness(self):
        """Scan all content and update freshness scores"""
        logger.info("Starting freshness scan")
        
        result = await self.db.execute(select(QuizContent))
        contents = result.scalars().all()
        
        updated = 0
        for content in contents:
            score = await self.calculate_freshness_score(content)
            
            if content.last_refreshed_at:
                age_days = (datetime.utcnow() - content.last_refreshed_at).days
            else:
                age_days = (datetime.utcnow() - content.created_at).days
            
            lifecycle = self.determine_lifecycle(score, age_days)
            
            content.freshness_score = score
            content.lifecycle = lifecycle
            
            # Flag stale content
            if score < settings.FRESHNESS_THRESHOLD and content.state == ContentState.ACTIVE:
                content.state = ContentState.FLAGGED
                await self.create_refresh_job(content.id, "auto_refresh", priority=3)
            
            updated += 1
        
        await self.db.commit()
        logger.info("Freshness scan complete", updated=updated)
        return updated
    
    async def create_refresh_job(self, content_id: UUID, job_type: str, priority: int = 5) -> RefreshJob:
        """Create a refresh job in the queue"""
        job = RefreshJob(
            content_id=content_id,
            job_type=job_type,
            priority=priority
        )
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        
        logger.info("Refresh job created", job_id=str(job.id), content_id=str(content_id))
        return job
    
    async def process_refresh_job(self, job_id: UUID) -> bool:
        """Process a single refresh job"""
        result = await self.db.execute(
            select(RefreshJob).where(RefreshJob.id == job_id)
        )
        job = result.scalar_one_or_none()
        
        if not job:
            return False
        
        job.started_at = datetime.utcnow()
        job.status = "processing"
        await self.db.commit()
        
        try:
            # Get content with metrics eagerly loaded
            content_result = await self.db.execute(
                select(QuizContent)
                .options(selectinload(QuizContent.metrics))
                .where(QuizContent.id == job.content_id)
            )
            content = content_result.scalar_one_or_none()
            
            if not content:
                raise ValueError("Content not found")
            
            # Get metrics for context BEFORE any commits (to avoid greenlet issues)
            metrics_data = {}
            if content.metrics:
                metrics_data = {
                    "accuracy_rate": content.metrics.accuracy_rate,
                    "skip_rate": content.metrics.skip_rate,
                    "total_attempts": content.metrics.total_attempts
                }
            
            # Store freshness score before updating state
            current_freshness_score = content.freshness_score
            
            # Update state
            content.state = ContentState.REFRESHING
            await self.db.commit()
            
            # Generate new content with AI
            new_content = await self.ai_service.regenerate_content(
                {
                    "topic": content.topic,
                    "question": content.question,
                    "options": content.options,
                    "correct_answer": content.correct_answer,
                    "difficulty": content.difficulty
                },
                metrics_data
            )
            
            # Get current version number
            version_result = await self.db.execute(
                select(func.max(ContentVersion.version_number))
                .where(ContentVersion.content_id == content.id)
            )
            current_version = version_result.scalar() or 0
            
            # Create new version
            new_version = ContentVersion(
                content_id=content.id,
                version_number=current_version + 1,
                content_data=new_content,
                performance_snapshot=metrics_data,
                refresh_reason=f"Auto-refresh: freshness score {current_freshness_score}"
            )
            self.db.add(new_version)
            
            # Deactivate old versions
            await self.db.execute(
                update(ContentVersion)
                .where(ContentVersion.content_id == content.id)
                .where(ContentVersion.version_number < current_version + 1)
                .values(is_active=False)
            )
            
            # Update content
            content.question = new_content["question"]
            content.options = new_content["options"]
            content.correct_answer = new_content["correct_answer"]
            content.explanation = new_content.get("explanation", content.explanation)
            content.state = ContentState.VALIDATING
            content.last_refreshed_at = datetime.utcnow()
            content.freshness_score = 100.0
            content.lifecycle = ContentLifecycle.FRESH
            
            # Complete job
            job.status = "completed"
            job.completed_at = datetime.utcnow()
            job.result = {"new_version": current_version + 1}
            
            await self.db.commit()
            
            logger.info(
                "Content refreshed",
                content_id=str(content.id),
                new_version=current_version + 1
            )
            
            # Simulate validation (in production, would wait for user feedback)
            await asyncio.sleep(1)
            
            # Re-query content to avoid detached instance issues
            content_result = await self.db.execute(
                select(QuizContent).where(QuizContent.id == content.id)
            )
            content = content_result.scalar_one_or_none()
            if content:
                content.state = ContentState.ACTIVE
                await self.db.commit()
            
            return True
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.utcnow()
            job.retry_count += 1
            await self.db.commit()
            
            logger.error("Refresh job failed", job_id=str(job_id), error=str(e))
            return False
    
    async def process_pending_jobs(self, batch_size: int = 10):
        """Process pending refresh jobs in batch"""
        result = await self.db.execute(
            select(RefreshJob)
            .where(RefreshJob.status == "pending")
            .order_by(RefreshJob.priority.asc(), RefreshJob.created_at.asc())
            .limit(batch_size)
        )
        jobs = result.scalars().all()
        
        logger.info("Processing refresh jobs", count=len(jobs))
        
        for i, job in enumerate(jobs, 1):
            logger.info(f"Processing job {i}/{len(jobs)}", job_id=str(job.id))
            await self.process_refresh_job(job.id)
            # Slow down processing to make it visible (2 seconds between jobs)
            if i < len(jobs):  # Don't sleep after the last job
                await asyncio.sleep(2.0)
        
        return len(jobs)
    
    async def rollback_content(self, content_id: UUID, version_number: int) -> bool:
        """Rollback content to a specific version"""
        result = await self.db.execute(
            select(ContentVersion)
            .where(ContentVersion.content_id == content_id)
            .where(ContentVersion.version_number == version_number)
        )
        version = result.scalar_one_or_none()
        
        if not version:
            return False
        
        content_result = await self.db.execute(
            select(QuizContent).where(QuizContent.id == content_id)
        )
        content = content_result.scalar_one_or_none()
        
        if not content:
            return False
        
        # Restore content from version
        content.question = version.content_data["question"]
        content.options = version.content_data["options"]
        content.correct_answer = version.content_data["correct_answer"]
        content.explanation = version.content_data.get("explanation")
        content.state = ContentState.ROLLED_BACK
        content.updated_at = datetime.utcnow()
        
        # Update version active states
        await self.db.execute(
            update(ContentVersion)
            .where(ContentVersion.content_id == content_id)
            .values(is_active=False)
        )
        version.is_active = True
        
        await self.db.commit()
        
        logger.info(
            "Content rolled back",
            content_id=str(content_id),
            version=version_number
        )
        
        return True
    
    async def get_queue_depth(self) -> int:
        """Get number of pending refresh jobs"""
        result = await self.db.execute(
            select(func.count(RefreshJob.id))
            .where(RefreshJob.status == "pending")
        )
        return result.scalar()
    
    async def get_queue_breakdown(self) -> dict:
        """Get breakdown of jobs by status"""
        result = await self.db.execute(
            select(RefreshJob.status, func.count(RefreshJob.id))
            .group_by(RefreshJob.status)
        )
        breakdown = {row[0]: row[1] for row in result.all()}
        return {
            "pending": breakdown.get("pending", 0),
            "processing": breakdown.get("processing", 0),
            "completed": breakdown.get("completed", 0),
            "failed": breakdown.get("failed", 0)
        }
    
    async def get_rollback_rate(self) -> float:
        """Calculate rollback rate for recent refreshes"""
        # Count jobs in last 7 days
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        total_result = await self.db.execute(
            select(func.count(RefreshJob.id))
            .where(RefreshJob.completed_at >= week_ago)
            .where(RefreshJob.status.in_(["completed", "failed"]))
        )
        total = total_result.scalar()
        
        # Count content in rolled_back state
        rollback_result = await self.db.execute(
            select(func.count(QuizContent.id))
            .where(QuizContent.state == ContentState.ROLLED_BACK)
        )
        rollbacks = rollback_result.scalar()
        
        if total == 0:
            return 0.0
        
        return round(rollbacks / total, 3)
