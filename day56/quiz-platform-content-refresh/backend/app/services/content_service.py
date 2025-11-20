from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
from sqlalchemy.orm import selectinload
from typing import List, Optional
from uuid import UUID
from datetime import datetime, timedelta
import structlog

from app.models.content import QuizContent, ContentVersion, ContentMetrics, ContentState, ContentLifecycle
from app.schemas.content import ContentCreate, ContentUpdate

logger = structlog.get_logger()

class ContentService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_content(self, content_data: ContentCreate) -> QuizContent:
        content = QuizContent(
            topic=content_data.topic,
            question=content_data.question,
            options=content_data.options,
            correct_answer=content_data.correct_answer,
            explanation=content_data.explanation,
            difficulty=content_data.difficulty,
            category=content_data.category
        )
        self.db.add(content)
        await self.db.flush()  # Flush to get the content.id
        
        # Create initial metrics
        metrics = ContentMetrics(content_id=content.id)
        self.db.add(metrics)
        
        # Create initial version
        version = ContentVersion(
            content_id=content.id,
            version_number=1,
            content_data={
                "question": content_data.question,
                "options": content_data.options,
                "correct_answer": content_data.correct_answer,
                "explanation": content_data.explanation
            },
            refresh_reason="Initial creation"
        )
        self.db.add(version)
        
        await self.db.commit()
        await self.db.refresh(content)
        
        logger.info("Content created", content_id=str(content.id), topic=content.topic)
        return content
    
    async def get_content(self, content_id: UUID) -> Optional[QuizContent]:
        result = await self.db.execute(
            select(QuizContent)
            .options(selectinload(QuizContent.metrics))
            .where(QuizContent.id == content_id)
        )
        return result.scalar_one_or_none()
    
    async def get_all_content(self, skip: int = 0, limit: int = 100) -> List[QuizContent]:
        result = await self.db.execute(
            select(QuizContent)
            .options(selectinload(QuizContent.metrics))
            .offset(skip)
            .limit(limit)
            .order_by(QuizContent.freshness_score.asc())
        )
        return result.scalars().all()
    
    async def get_stale_content(self, threshold: float = 40.0) -> List[QuizContent]:
        result = await self.db.execute(
            select(QuizContent)
            .where(QuizContent.freshness_score < threshold)
            .where(QuizContent.state == ContentState.ACTIVE)
            .order_by(QuizContent.freshness_score.asc())
        )
        return result.scalars().all()
    
    async def update_state(self, content_id: UUID, state: ContentState) -> QuizContent:
        await self.db.execute(
            update(QuizContent)
            .where(QuizContent.id == content_id)
            .values(state=state, updated_at=datetime.utcnow())
        )
        await self.db.commit()
        return await self.get_content(content_id)
    
    async def update_freshness_score(self, content_id: UUID, score: float, lifecycle: ContentLifecycle):
        await self.db.execute(
            update(QuizContent)
            .where(QuizContent.id == content_id)
            .values(
                freshness_score=score,
                lifecycle=lifecycle,
                updated_at=datetime.utcnow()
            )
        )
        await self.db.commit()
    
    async def get_lifecycle_distribution(self) -> dict:
        result = await self.db.execute(
            select(
                QuizContent.lifecycle,
                func.count(QuizContent.id)
            ).group_by(QuizContent.lifecycle)
        )
        return {str(row[0].value): row[1] for row in result.all()}
    
    async def get_content_count(self) -> int:
        result = await self.db.execute(select(func.count(QuizContent.id)))
        return result.scalar()
