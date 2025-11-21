#!/bin/bash

# Day 55: Content Curation Workflow - Project Implementation Script
# This script creates a complete human-in-the-loop content curation system

set -e

PROJECT_NAME="quiz-content-curation"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$SCRIPT_DIR/$PROJECT_NAME"

echo "=========================================="
echo "Day 55: Content Curation Workflow Setup"
echo "=========================================="

# Clean up existing project
if [ -d "$PROJECT_DIR" ]; then
    echo "Removing existing project directory..."
    rm -rf "$PROJECT_DIR"
fi

# Create project structure
echo "Creating project structure..."
mkdir -p "$PROJECT_DIR"/{backend/{app/{api,models,services,schemas},tests},frontend/src/{components,services,pages},scripts}

cd "$PROJECT_DIR"

# ============================================
# Backend Implementation
# ============================================

echo "Creating backend files..."

# Main application entry point
cat > backend/app/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import curation, questions, analytics
from app.models.database import engine, Base

app = FastAPI(
    title="Quiz Content Curation API",
    description="Human-in-the-loop content curation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(curation.router, prefix="/api/curation", tags=["curation"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "content-curation"}
EOF

# Database configuration
cat > backend/app/models/database.py << 'EOF'
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./curation.db")

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
EOF

# Models
cat > backend/app/models/models.py << 'EOF'
from sqlalchemy import Column, String, Float, DateTime, Text, JSON, ForeignKey, Integer, Enum
from sqlalchemy.dialects.sqlite import JSON as SQLiteJSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.models.database import Base

def generate_uuid():
    return str(uuid.uuid4())

class CurationStatus(str, enum.Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"
    ARCHIVED = "archived"

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(Integer, nullable=False)
    explanation = Column(Text)
    topic = Column(String, nullable=False)
    difficulty = Column(String, nullable=False)
    source_model = Column(String, default="gemini-1.5-flash")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    curation = relationship("ContentCuration", back_populates="question", uselist=False)

class ContentCuration(Base):
    __tablename__ = "content_curations"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    question_id = Column(String, ForeignKey("questions.id"), unique=True)
    status = Column(String, default=CurationStatus.PENDING.value)
    quality_score = Column(Float, nullable=False)
    quality_metrics = Column(JSON, nullable=False)
    priority_score = Column(Float, default=0.5)
    reviewer_id = Column(String, nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    feedback = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    question = relationship("Question", back_populates="curation")
    audit_logs = relationship("CurationAuditLog", back_populates="curation")

class CurationAuditLog(Base):
    __tablename__ = "curation_audit_logs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    curation_id = Column(String, ForeignKey("content_curations.id"))
    action = Column(String, nullable=False)
    previous_status = Column(String)
    new_status = Column(String)
    reviewer_id = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    curation = relationship("ContentCuration", back_populates="audit_logs")
EOF

# Schemas
cat > backend/app/schemas/schemas.py << 'EOF'
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class QuestionCreate(BaseModel):
    text: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None
    topic: str
    difficulty: str
    source_model: str = "gemini-1.5-flash"

class QuestionResponse(BaseModel):
    id: str
    text: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str]
    topic: str
    difficulty: str
    source_model: str
    created_at: datetime

    class Config:
        from_attributes = True

class QualityMetrics(BaseModel):
    readability_score: float = Field(ge=0, le=1)
    factual_confidence: float = Field(ge=0, le=1)
    distractor_quality: float = Field(ge=0, le=1)
    topic_alignment: float = Field(ge=0, le=1)
    difficulty_match: float = Field(ge=0, le=1)

class CurationCreate(BaseModel):
    question_id: str
    quality_metrics: QualityMetrics

class CurationResponse(BaseModel):
    id: str
    question_id: str
    status: str
    quality_score: float
    quality_metrics: Dict[str, float]
    priority_score: float
    reviewer_id: Optional[str]
    reviewed_at: Optional[datetime]
    feedback: Optional[str]
    created_at: datetime
    question: Optional[QuestionResponse] = None

    class Config:
        from_attributes = True

class CurationAction(BaseModel):
    reviewer_id: str
    feedback: Optional[str] = None

class QueueItem(BaseModel):
    id: str
    question_id: str
    preview: str
    quality_score: float
    priority_score: float
    topic: str
    difficulty: str
    created_at: datetime
    time_in_queue: str

class QueueResponse(BaseModel):
    items: List[QueueItem]
    total: int
    page: int
    page_size: int

class AnalyticsResponse(BaseModel):
    total_reviewed: int
    approval_rate: float
    avg_review_time_minutes: float
    status_distribution: Dict[str, int]
    daily_stats: List[Dict[str, Any]]
    top_rejection_reasons: List[Dict[str, Any]]
    model_performance: Dict[str, Dict[str, float]]

class AuditLogResponse(BaseModel):
    id: str
    curation_id: str
    action: str
    previous_status: Optional[str]
    new_status: str
    reviewer_id: str
    details: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True
EOF

# Curation Service
cat > backend/app/services/curation_service.py << 'EOF'
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
EOF

# Question Service with Gemini Integration
cat > backend/app/services/question_service.py << 'EOF'
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import google.generativeai as genai
import json
import os
import re

from app.models.models import Question
from app.schemas.schemas import QuestionCreate, QualityMetrics

class QuestionService:
    def __init__(self, db: AsyncSession):
        self.db = db
        api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def create_question(self, question_data: QuestionCreate) -> Question:
        """Create a new question"""
        question = Question(
            text=question_data.text,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            explanation=question_data.explanation,
            topic=question_data.topic,
            difficulty=question_data.difficulty,
            source_model=question_data.source_model
        )
        self.db.add(question)
        await self.db.commit()
        await self.db.refresh(question)
        return question
    
    async def generate_question(self, topic: str, difficulty: str) -> tuple[Question, QualityMetrics]:
        """Generate a question using Gemini AI"""
        prompt = f"""Generate a multiple choice quiz question about {topic} at {difficulty} difficulty level.

Return a JSON object with this exact structure:
{{
    "text": "The question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Why this answer is correct",
    "quality_metrics": {{
        "readability_score": 0.85,
        "factual_confidence": 0.90,
        "distractor_quality": 0.80,
        "topic_alignment": 0.95,
        "difficulty_match": 0.85
    }}
}}

The correct_answer should be the index (0-3) of the correct option.
Ensure quality_metrics values are between 0 and 1.
Return only valid JSON, no additional text."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            # Clean up response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            data = json.loads(response_text)
            
            question = Question(
                text=data["text"],
                options=data["options"],
                correct_answer=data["correct_answer"],
                explanation=data.get("explanation", ""),
                topic=topic,
                difficulty=difficulty,
                source_model="gemini-1.5-flash"
            )
            self.db.add(question)
            await self.db.commit()
            await self.db.refresh(question)
            
            metrics = QualityMetrics(**data.get("quality_metrics", {
                "readability_score": 0.8,
                "factual_confidence": 0.85,
                "distractor_quality": 0.75,
                "topic_alignment": 0.9,
                "difficulty_match": 0.8
            }))
            
            return question, metrics
            
        except Exception as e:
            raise ValueError(f"Failed to generate question: {str(e)}")
    
    async def regenerate_with_feedback(
        self, 
        question_id: str, 
        feedback: str
    ) -> tuple[Question, QualityMetrics]:
        """Regenerate question incorporating human feedback"""
        original = await self.get_question(question_id)
        if not original:
            raise ValueError("Original question not found")
        
        prompt = f"""The following quiz question needs improvement based on this feedback:
"{feedback}"

Original question:
{original.text}

Options: {json.dumps(original.options)}
Topic: {original.topic}
Difficulty: {original.difficulty}

Generate an improved version addressing the feedback.
Return a JSON object with this exact structure:
{{
    "text": "The improved question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Why this answer is correct",
    "quality_metrics": {{
        "readability_score": 0.85,
        "factual_confidence": 0.90,
        "distractor_quality": 0.80,
        "topic_alignment": 0.95,
        "difficulty_match": 0.85
    }}
}}

Return only valid JSON, no additional text."""

        try:
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()
            
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()
            
            data = json.loads(response_text)
            
            question = Question(
                text=data["text"],
                options=data["options"],
                correct_answer=data["correct_answer"],
                explanation=data.get("explanation", ""),
                topic=original.topic,
                difficulty=original.difficulty,
                source_model="gemini-1.5-flash"
            )
            self.db.add(question)
            await self.db.commit()
            await self.db.refresh(question)
            
            metrics = QualityMetrics(**data.get("quality_metrics", {
                "readability_score": 0.85,
                "factual_confidence": 0.88,
                "distractor_quality": 0.82,
                "topic_alignment": 0.92,
                "difficulty_match": 0.85
            }))
            
            return question, metrics
            
        except Exception as e:
            raise ValueError(f"Failed to regenerate question: {str(e)}")
    
    async def get_question(self, question_id: str) -> Optional[Question]:
        """Get question by ID"""
        query = select(Question).where(Question.id == question_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_approved_questions(self, topic: Optional[str] = None) -> List[Question]:
        """Get all approved questions, optionally filtered by topic"""
        from app.models.models import ContentCuration, CurationStatus
        
        query = select(Question).join(ContentCuration).where(
            ContentCuration.status == CurationStatus.APPROVED.value
        )
        if topic:
            query = query.where(Question.topic == topic)
        
        result = await self.db.execute(query)
        return result.scalars().all()
EOF

# Analytics Service
cat > backend/app/services/analytics_service.py << 'EOF'
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
        
        # Total reviewed
        reviewed_query = select(func.count(ContentCuration.id)).where(
            and_(
                ContentCuration.reviewed_at.isnot(None),
                ContentCuration.reviewed_at >= cutoff
            )
        )
        total_reviewed = await self.db.scalar(reviewed_query) or 0
        
        # Approval rate
        approved_query = select(func.count(ContentCuration.id)).where(
            and_(
                ContentCuration.status == CurationStatus.APPROVED.value,
                ContentCuration.reviewed_at >= cutoff
            )
        )
        approved_count = await self.db.scalar(approved_query) or 0
        approval_rate = approved_count / total_reviewed if total_reviewed > 0 else 0
        
        # Average review time
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
        
        # Daily stats
        daily_stats = await self._get_daily_stats(cutoff)
        
        # Top rejection reasons
        rejection_reasons = await self._get_rejection_reasons(cutoff)
        
        # Model performance
        model_performance = await self._get_model_performance()
        
        return {
            "total_reviewed": total_reviewed,
            "approval_rate": round(approval_rate, 3),
            "avg_review_time_minutes": round(avg_review_time, 1),
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
EOF

# API Routes - Curation
cat > backend/app/api/curation.py << 'EOF'
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
EOF

# API Routes - Questions
cat > backend/app/api/questions.py << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.database import get_db
from app.services.question_service import QuestionService
from app.services.curation_service import CurationService
from app.schemas.schemas import QuestionCreate, QuestionResponse, CurationResponse

router = APIRouter()

@router.post("/generate", response_model=CurationResponse)
async def generate_question(
    topic: str,
    difficulty: str = "medium",
    db: AsyncSession = Depends(get_db)
):
    """Generate a new question and submit for curation"""
    question_service = QuestionService(db)
    curation_service = CurationService(db)
    
    try:
        question, metrics = await question_service.generate_question(topic, difficulty)
        curation = await curation_service.submit_for_curation(question.id, metrics)
        
        # Reload with question relationship
        curation = await curation_service.get_curation(curation.id)
        return curation
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/regenerate/{question_id}", response_model=CurationResponse)
async def regenerate_question(
    question_id: str,
    feedback: str,
    db: AsyncSession = Depends(get_db)
):
    """Regenerate question with feedback and submit for curation"""
    question_service = QuestionService(db)
    curation_service = CurationService(db)
    
    try:
        question, metrics = await question_service.regenerate_with_feedback(question_id, feedback)
        curation = await curation_service.submit_for_curation(question.id, metrics)
        curation = await curation_service.get_curation(curation.id)
        return curation
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approved", response_model=list[QuestionResponse])
async def get_approved_questions(
    topic: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all approved questions"""
    service = QuestionService(db)
    return await service.get_approved_questions(topic)

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get question by ID"""
    service = QuestionService(db)
    question = await service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question
EOF

# API Routes - Analytics
cat > backend/app/api/analytics.py << 'EOF'
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.schemas import AnalyticsResponse

router = APIRouter()

@router.get("/curation", response_model=AnalyticsResponse)
async def get_curation_analytics(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get curation performance analytics"""
    service = AnalyticsService(db)
    return await service.get_curation_analytics(days)
EOF

# Create __init__ files
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
touch backend/app/schemas/__init__.py

# Backend requirements
cat > backend/requirements.txt << 'EOF'
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy[asyncio]==2.0.36
aiosqlite==0.20.0
google-generativeai==0.8.3
pydantic==2.10.3
python-multipart==0.0.18
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.25.0
EOF

# Backend tests
cat > backend/tests/test_curation.py << 'EOF'
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.models.database import Base, get_db
from app.models.models import Question, ContentCuration
from app.services.curation_service import CurationService
from app.schemas.schemas import QualityMetrics

# Test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_curation.db"
engine = create_async_engine(TEST_DATABASE_URL, echo=False)
TestSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def override_get_db():
    async with TestSessionLocal() as session:
        yield session

app.dependency_overrides[get_db] = override_get_db

@pytest_asyncio.fixture
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def db_session(setup_database):
    async with TestSessionLocal() as session:
        yield session

@pytest_asyncio.fixture
async def client(setup_database):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest_asyncio.fixture
async def sample_question(db_session):
    question = Question(
        text="What is 2 + 2?",
        options=["3", "4", "5", "6"],
        correct_answer=1,
        explanation="Basic arithmetic",
        topic="Mathematics",
        difficulty="easy"
    )
    db_session.add(question)
    await db_session.commit()
    await db_session.refresh(question)
    return question

@pytest.mark.asyncio
async def test_submit_for_curation(db_session, sample_question):
    """Test submitting content for curation"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    
    assert curation.status == "pending"
    assert curation.quality_score > 0
    assert curation.question_id == sample_question.id

@pytest.mark.asyncio
async def test_claim_and_approve(db_session, sample_question):
    """Test claiming and approving content"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    
    # Claim
    curation = await service.claim_for_review(curation.id, "reviewer1")
    assert curation.status == "under_review"
    assert curation.reviewer_id == "reviewer1"
    
    # Approve
    curation = await service.approve_content(curation.id, "reviewer1")
    assert curation.status == "approved"
    assert curation.reviewed_at is not None

@pytest.mark.asyncio
async def test_reject_content(db_session, sample_question):
    """Test rejecting content with reason"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    await service.claim_for_review(curation.id, "reviewer1")
    
    curation = await service.reject_content(curation.id, "reviewer1", "Incorrect answer")
    
    assert curation.status == "rejected"
    assert curation.feedback == "Incorrect answer"

@pytest.mark.asyncio
async def test_request_revision(db_session, sample_question):
    """Test requesting content revision"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    await service.claim_for_review(curation.id, "reviewer1")
    
    curation = await service.request_revision(curation.id, "reviewer1", "Make distractors more plausible")
    
    assert curation.status == "needs_revision"
    assert "distractors" in curation.feedback.lower()

@pytest.mark.asyncio
async def test_invalid_state_transition(db_session, sample_question):
    """Test invalid state transitions raise errors"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    
    # Cannot approve without claiming
    with pytest.raises(ValueError):
        await service.approve_content(curation.id, "reviewer1")

@pytest.mark.asyncio
async def test_queue_endpoint(client, db_session, sample_question):
    """Test queue API endpoint"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    await service.submit_for_curation(sample_question.id, metrics)
    
    response = await client.get("/api/curation/queue")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["items"]) == 1

@pytest.mark.asyncio
async def test_audit_logs(db_session, sample_question):
    """Test audit log creation"""
    service = CurationService(db_session)
    metrics = QualityMetrics(
        readability_score=0.85,
        factual_confidence=0.90,
        distractor_quality=0.80,
        topic_alignment=0.95,
        difficulty_match=0.88
    )
    
    curation = await service.submit_for_curation(sample_question.id, metrics)
    await service.claim_for_review(curation.id, "reviewer1")
    await service.approve_content(curation.id, "reviewer1")
    
    logs = await service.get_audit_logs(curation.id)
    
    assert len(logs) == 3
    actions = [log.action for log in logs]
    assert "submitted" in actions
    assert "claimed" in actions
    assert "approved" in actions
EOF

# ============================================
# Frontend Implementation
# ============================================

echo "Creating frontend files..."

# Package.json
cat > frontend/package.json << 'EOF'
{
  "name": "content-curation-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@emotion/react": "^11.13.5",
    "@emotion/styled": "^11.13.5",
    "@mui/icons-material": "^6.1.8",
    "@mui/material": "^6.1.8",
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^7.0.2",
    "react-scripts": "5.0.1",
    "recharts": "^2.14.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": ["react-app"]
  },
  "browserslist": {
    "production": [">0.2%", "not dead", "not op_mini all"],
    "development": ["last 1 chrome version", "last 1 firefox version", "last 1 safari version"]
  },
  "proxy": "http://localhost:8000"
}
EOF

# Public files
mkdir -p frontend/public
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <title>Content Curation Dashboard</title>
</head>
<body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
</body>
</html>
EOF

# Main App
cat > frontend/src/App.js << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import Layout from './components/Layout';
import QueuePage from './pages/QueuePage';
import ReviewPage from './pages/ReviewPage';
import AnalyticsPage from './pages/AnalyticsPage';
import GeneratePage from './pages/GeneratePage';

const theme = createTheme({
  palette: {
    primary: { main: '#2e7d32' },
    secondary: { main: '#f57c00' },
    background: { default: '#f5f5f5' }
  }
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/queue" replace />} />
            <Route path="/queue" element={<QueuePage />} />
            <Route path="/review/:id" element={<ReviewPage />} />
            <Route path="/analytics" element={<AnalyticsPage />} />
            <Route path="/generate" element={<GeneratePage />} />
          </Routes>
        </Layout>
      </Router>
    </ThemeProvider>
  );
}

export default App;
EOF

# Index.js
cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# API Service
cat > frontend/src/services/api.js << 'EOF'
const API_BASE = '/api';

export const curationApi = {
  getQueue: async (status = 'pending', page = 1, limit = 20) => {
    const response = await fetch(
      `${API_BASE}/curation/queue?status=${status}&page=${page}&limit=${limit}`
    );
    return response.json();
  },

  getCuration: async (id) => {
    const response = await fetch(`${API_BASE}/curation/${id}`);
    return response.json();
  },

  claim: async (id, reviewerId) => {
    const response = await fetch(`${API_BASE}/curation/${id}/claim`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId })
    });
    return response.json();
  },

  approve: async (id, reviewerId) => {
    const response = await fetch(`${API_BASE}/curation/${id}/approve`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId })
    });
    return response.json();
  },

  reject: async (id, reviewerId, feedback) => {
    const response = await fetch(`${API_BASE}/curation/${id}/reject`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId, feedback })
    });
    return response.json();
  },

  requestRevision: async (id, reviewerId, feedback) => {
    const response = await fetch(`${API_BASE}/curation/${id}/revise`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId, feedback })
    });
    return response.json();
  },

  release: async (id, reviewerId) => {
    const response = await fetch(`${API_BASE}/curation/${id}/release`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ reviewer_id: reviewerId })
    });
    return response.json();
  },

  getAuditLogs: async (id) => {
    const response = await fetch(`${API_BASE}/curation/${id}/audit`);
    return response.json();
  }
};

export const questionApi = {
  generate: async (topic, difficulty = 'medium') => {
    const response = await fetch(
      `${API_BASE}/questions/generate?topic=${encodeURIComponent(topic)}&difficulty=${difficulty}`,
      { method: 'POST' }
    );
    return response.json();
  },

  getApproved: async (topic = null) => {
    const url = topic 
      ? `${API_BASE}/questions/approved?topic=${encodeURIComponent(topic)}`
      : `${API_BASE}/questions/approved`;
    const response = await fetch(url);
    return response.json();
  }
};

export const analyticsApi = {
  getCurationAnalytics: async (days = 7) => {
    const response = await fetch(`${API_BASE}/analytics/curation?days=${days}`);
    return response.json();
  }
};
EOF

# Layout Component
cat > frontend/src/components/Layout.js << 'EOF'
import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  AppBar, Toolbar, Typography, Drawer, List, ListItem,
  ListItemIcon, ListItemText, Box
} from '@mui/material';
import {
  Queue as QueueIcon,
  Analytics as AnalyticsIcon,
  Add as AddIcon
} from '@mui/icons-material';

const drawerWidth = 240;

function Layout({ children }) {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { text: 'Review Queue', icon: <QueueIcon />, path: '/queue' },
    { text: 'Generate', icon: <AddIcon />, path: '/generate' },
    { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' }
  ];

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
        <Toolbar>
          <Typography variant="h6" noWrap>
            Content Curation Dashboard
          </Typography>
        </Toolbar>
      </AppBar>
      <Drawer
        variant="permanent"
        sx={{
          width: drawerWidth,
          '& .MuiDrawer-paper': { width: drawerWidth, boxSizing: 'border-box' }
        }}
      >
        <Toolbar />
        <List>
          {menuItems.map((item) => (
            <ListItem
              button
              key={item.text}
              onClick={() => navigate(item.path)}
              selected={location.pathname === item.path}
              sx={{ cursor: 'pointer' }}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItem>
          ))}
        </List>
      </Drawer>
      <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
        {children}
      </Box>
    </Box>
  );
}

export default Layout;
EOF

# Quality Badge Component
cat > frontend/src/components/QualityBadge.js << 'EOF'
import React from 'react';
import { Chip } from '@mui/material';

function QualityBadge({ score }) {
  let color = 'default';
  let label = `${(score * 100).toFixed(0)}%`;

  if (score >= 0.9) {
    color = 'success';
  } else if (score >= 0.7) {
    color = 'warning';
  } else {
    color = 'error';
  }

  return <Chip label={label} color={color} size="small" />;
}

export default QualityBadge;
EOF

# Queue Page
cat > frontend/src/pages/QueuePage.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead,
  TableRow, Button, Typography, Box, Chip, Tabs, Tab,
  CircularProgress, Alert
} from '@mui/material';
import QualityBadge from '../components/QualityBadge';
import { curationApi } from '../services/api';

function QueuePage() {
  const [queue, setQueue] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('pending');
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  const reviewerId = 'admin';

  useEffect(() => {
    fetchQueue();
  }, [status]);

  const fetchQueue = async () => {
    setLoading(true);
    try {
      const data = await curationApi.getQueue(status);
      setQueue(data.items);
      setTotal(data.total);
      setError(null);
    } catch (err) {
      setError('Failed to load queue');
    }
    setLoading(false);
  };

  const handleClaim = async (id) => {
    try {
      await curationApi.claim(id, reviewerId);
      navigate(`/review/${id}`);
    } catch (err) {
      setError('Failed to claim content');
    }
  };

  const handleViewReview = (id) => {
    navigate(`/review/${id}`);
  };

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Curation Queue
      </Typography>

      <Tabs value={status} onChange={(e, v) => setStatus(v)} sx={{ mb: 2 }}>
        <Tab value="pending" label="Pending" />
        <Tab value="under_review" label="Under Review" />
        <Tab value="approved" label="Approved" />
        <Tab value="rejected" label="Rejected" />
        <Tab value="needs_revision" label="Needs Revision" />
      </Tabs>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {loading ? (
        <Box display="flex" justifyContent="center" p={4}>
          <CircularProgress />
        </Box>
      ) : (
        <TableContainer component={Paper}>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Preview</TableCell>
                <TableCell>Quality</TableCell>
                <TableCell>Topic</TableCell>
                <TableCell>Difficulty</TableCell>
                <TableCell>Age</TableCell>
                <TableCell>Action</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {queue.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} align="center">
                    No items in queue
                  </TableCell>
                </TableRow>
              ) : (
                queue.map((item) => (
                  <TableRow key={item.id}>
                    <TableCell sx={{ maxWidth: 300 }}>
                      {item.preview}
                    </TableCell>
                    <TableCell>
                      <QualityBadge score={item.quality_score} />
                    </TableCell>
                    <TableCell>
                      <Chip label={item.topic} size="small" />
                    </TableCell>
                    <TableCell>{item.difficulty}</TableCell>
                    <TableCell>{item.time_in_queue}</TableCell>
                    <TableCell>
                      {status === 'pending' ? (
                        <Button
                          variant="contained"
                          size="small"
                          onClick={() => handleClaim(item.id)}
                        >
                          Review
                        </Button>
                      ) : (
                        <Button
                          variant="outlined"
                          size="small"
                          onClick={() => handleViewReview(item.id)}
                        >
                          View
                        </Button>
                      )}
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      )}

      <Typography variant="body2" color="textSecondary" sx={{ mt: 2 }}>
        Total: {total} items
      </Typography>
    </Box>
  );
}

export default QueuePage;
EOF

# Review Page
cat > frontend/src/pages/ReviewPage.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  Paper, Typography, Box, Button, TextField, Card, CardContent,
  Divider, List, ListItem, ListItemText, Chip, Alert,
  CircularProgress, ButtonGroup, Grid
} from '@mui/material';
import QualityBadge from '../components/QualityBadge';
import { curationApi } from '../services/api';

function ReviewPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [curation, setCuration] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [auditLogs, setAuditLogs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionLoading, setActionLoading] = useState(false);

  const reviewerId = 'admin';

  useEffect(() => {
    fetchData();
  }, [id]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [curationData, logs] = await Promise.all([
        curationApi.getCuration(id),
        curationApi.getAuditLogs(id)
      ]);
      setCuration(curationData);
      setAuditLogs(logs);
      setError(null);
    } catch (err) {
      setError('Failed to load content');
    }
    setLoading(false);
  };

  const handleAction = async (action) => {
    setActionLoading(true);
    try {
      switch (action) {
        case 'approve':
          await curationApi.approve(id, reviewerId);
          break;
        case 'reject':
          if (!feedback) {
            setError('Please provide rejection reason');
            setActionLoading(false);
            return;
          }
          await curationApi.reject(id, reviewerId, feedback);
          break;
        case 'revise':
          if (!feedback) {
            setError('Please provide revision feedback');
            setActionLoading(false);
            return;
          }
          await curationApi.requestRevision(id, reviewerId, feedback);
          break;
        case 'release':
          await curationApi.release(id, reviewerId);
          break;
        default:
          break;
      }
      navigate('/queue');
    } catch (err) {
      setError(`Failed to ${action} content`);
    }
    setActionLoading(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (!curation) {
    return <Alert severity="error">Content not found</Alert>;
  }

  const question = curation.question;
  const isUnderReview = curation.status === 'under_review';

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Content Review
      </Typography>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography variant="h6">Question</Typography>
                <Box>
                  <Chip label={question.topic} sx={{ mr: 1 }} />
                  <Chip label={question.difficulty} variant="outlined" />
                </Box>
              </Box>

              <Typography variant="body1" paragraph>
                {question.text}
              </Typography>

              <Divider sx={{ my: 2 }} />

              <Typography variant="subtitle2" gutterBottom>
                Options:
              </Typography>
              <List dense>
                {question.options.map((option, index) => (
                  <ListItem
                    key={index}
                    sx={{
                      bgcolor: index === question.correct_answer ? 'success.light' : 'transparent',
                      borderRadius: 1
                    }}
                  >
                    <ListItemText
                      primary={`${String.fromCharCode(65 + index)}. ${option}`}
                    />
                    {index === question.correct_answer && (
                      <Chip label="Correct" color="success" size="small" />
                    )}
                  </ListItem>
                ))}
              </List>

              {question.explanation && (
                <>
                  <Divider sx={{ my: 2 }} />
                  <Typography variant="subtitle2" gutterBottom>
                    Explanation:
                  </Typography>
                  <Typography variant="body2" color="textSecondary">
                    {question.explanation}
                  </Typography>
                </>
              )}
            </CardContent>
          </Card>

          {isUnderReview && (
            <Card sx={{ mb: 3 }}>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  Review Actions
                </Typography>

                <TextField
                  fullWidth
                  multiline
                  rows={3}
                  label="Feedback (required for reject/revise)"
                  value={feedback}
                  onChange={(e) => setFeedback(e.target.value)}
                  sx={{ mb: 2 }}
                />

                <ButtonGroup fullWidth disabled={actionLoading}>
                  <Button
                    color="success"
                    variant="contained"
                    onClick={() => handleAction('approve')}
                  >
                    Approve
                  </Button>
                  <Button
                    color="warning"
                    variant="contained"
                    onClick={() => handleAction('revise')}
                  >
                    Request Revision
                  </Button>
                  <Button
                    color="error"
                    variant="contained"
                    onClick={() => handleAction('reject')}
                  >
                    Reject
                  </Button>
                </ButtonGroup>

                <Button
                  fullWidth
                  variant="outlined"
                  sx={{ mt: 1 }}
                  onClick={() => handleAction('release')}
                  disabled={actionLoading}
                >
                  Release Back to Queue
                </Button>
              </CardContent>
            </Card>
          )}
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Quality Metrics
              </Typography>

              <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                <Typography>Overall Score</Typography>
                <QualityBadge score={curation.quality_score} />
              </Box>

              <Divider sx={{ my: 1 }} />

              {Object.entries(curation.quality_metrics).map(([key, value]) => (
                <Box
                  key={key}
                  display="flex"
                  justifyContent="space-between"
                  alignItems="center"
                  py={0.5}
                >
                  <Typography variant="body2">
                    {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </Typography>
                  <Typography variant="body2">
                    {(value * 100).toFixed(0)}%
                  </Typography>
                </Box>
              ))}
            </CardContent>
          </Card>

          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Audit History
              </Typography>

              <List dense>
                {auditLogs.map((log) => (
                  <ListItem key={log.id} sx={{ flexDirection: 'column', alignItems: 'flex-start' }}>
                    <ListItemText
                      primary={log.action.replace(/_/g, ' ').toUpperCase()}
                      secondary={`${log.reviewer_id} - ${new Date(log.timestamp).toLocaleString()}`}
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Button variant="outlined" onClick={() => navigate('/queue')} sx={{ mt: 2 }}>
        Back to Queue
      </Button>
    </Box>
  );
}

export default ReviewPage;
EOF

# Generate Page
cat > frontend/src/pages/GeneratePage.js << 'EOF'
import React, { useState } from 'react';
import {
  Paper, Typography, Box, Button, TextField, MenuItem,
  Alert, CircularProgress, Card, CardContent
} from '@mui/material';
import { questionApi } from '../services/api';

function GeneratePage() {
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const handleGenerate = async () => {
    if (!topic) {
      setError('Please enter a topic');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await questionApi.generate(topic, difficulty);
      setResult(data);
    } catch (err) {
      setError('Failed to generate question');
    }
    setLoading(false);
  };

  const topics = [
    'Mathematics', 'Science', 'History', 'Geography',
    'Literature', 'Computer Science', 'Physics', 'Chemistry'
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Generate Question
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }}>
        <Box display="flex" gap={2} flexDirection="column">
          <TextField
            select
            label="Topic"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            fullWidth
          >
            {topics.map((t) => (
              <MenuItem key={t} value={t}>{t}</MenuItem>
            ))}
          </TextField>

          <TextField
            select
            label="Difficulty"
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            fullWidth
          >
            <MenuItem value="easy">Easy</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="hard">Hard</MenuItem>
          </TextField>

          <Button
            variant="contained"
            onClick={handleGenerate}
            disabled={loading || !topic}
            size="large"
          >
            {loading ? <CircularProgress size={24} /> : 'Generate & Submit for Curation'}
          </Button>
        </Box>
      </Paper>

      {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

      {result && (
        <Card>
          <CardContent>
            <Alert severity="success" sx={{ mb: 2 }}>
              Question generated and submitted for curation!
            </Alert>

            <Typography variant="h6" gutterBottom>
              Generated Question:
            </Typography>
            <Typography paragraph>
              {result.question?.text}
            </Typography>

            <Typography variant="subtitle2">
              Quality Score: {(result.quality_score * 100).toFixed(0)}%
            </Typography>
            <Typography variant="subtitle2">
              Status: {result.status}
            </Typography>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}

export default GeneratePage;
EOF

# Analytics Page
cat > frontend/src/pages/AnalyticsPage.js << 'EOF'
import React, { useState, useEffect } from 'react';
import {
  Paper, Typography, Box, Grid, Card, CardContent,
  CircularProgress, Alert
} from '@mui/material';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, PieChart, Pie, Cell
} from 'recharts';
import { analyticsApi } from '../services/api';

const COLORS = ['#2e7d32', '#f57c00', '#1976d2', '#d32f2f', '#7b1fa2'];

function AnalyticsPage() {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      const data = await analyticsApi.getCurationAnalytics(7);
      setAnalytics(data);
      setError(null);
    } catch (err) {
      setError('Failed to load analytics');
    }
    setLoading(false);
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" p={4}>
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return <Alert severity="error">{error}</Alert>;
  }

  const statusData = Object.entries(analytics.status_distribution).map(([key, value]) => ({
    name: key.replace(/_/g, ' '),
    value
  }));

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Curation Analytics
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Total Reviewed (7d)
              </Typography>
              <Typography variant="h4">
                {analytics.total_reviewed}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Approval Rate
              </Typography>
              <Typography variant="h4">
                {(analytics.approval_rate * 100).toFixed(1)}%
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Avg Review Time
              </Typography>
              <Typography variant="h4">
                {analytics.avg_review_time_minutes.toFixed(0)}m
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Typography color="textSecondary" gutterBottom>
                Pending Items
              </Typography>
              <Typography variant="h4">
                {analytics.status_distribution.pending || 0}
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Daily Review Activity
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={analytics.daily_stats}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="reviewed" fill="#2e7d32" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Status Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={5}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {statusData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {analytics.model_performance && Object.keys(analytics.model_performance).length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 3 }}>
              <Typography variant="h6" gutterBottom>
                Model Performance
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(analytics.model_performance).map(([model, stats]) => (
                  <Grid item xs={12} sm={6} md={4} key={model}>
                    <Card variant="outlined">
                      <CardContent>
                        <Typography variant="subtitle1">{model}</Typography>
                        <Typography variant="body2">
                          Generated: {stats.total_generated}
                        </Typography>
                        <Typography variant="body2">
                          Avg Score: {(stats.avg_quality_score * 100).toFixed(1)}%
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                ))}
              </Grid>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
}

export default AnalyticsPage;
EOF

# ============================================
# Docker Configuration
# ============================================

echo "Creating Docker configuration..."

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - GEMINI_API_KEY=AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8
      - DATABASE_URL=sqlite+aiosqlite:///./curation.db
    volumes:
      - ./backend:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    depends_on:
      - backend
    volumes:
      - ./frontend:/app
      - /app/node_modules
    environment:
      - CHOKIDAR_USEPOLLING=true

volumes:
  node_modules:
EOF

cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > frontend/Dockerfile << 'EOF'
FROM node:20-alpine

WORKDIR /app

COPY package.json .
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
EOF

# ============================================
# Build and Start Scripts
# ============================================

echo "Creating build and start scripts..."

cat > build.sh << 'EOF'
#!/bin/bash

set -e

echo "=========================================="
echo "Building Content Curation System"
echo "=========================================="

# Check for Docker or local mode
if [ "$1" == "--docker" ]; then
    echo "Building with Docker..."
    docker-compose build
    echo "Docker build complete!"
    echo ""
    echo "To start: docker-compose up"
else
    echo "Building locally..."
    
    # Backend setup
    echo "Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    # Frontend setup
    echo "Setting up frontend..."
    cd frontend
    npm install
    cd ..
    
    echo ""
    echo "Local build complete!"
    echo ""
    echo "To start backend: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    echo "To start frontend: cd frontend && npm start"
fi

# Run tests
echo ""
echo "Running tests..."
cd backend
if [ -d "venv" ]; then
    source venv/bin/activate
fi
python -m pytest tests/ -v
cd ..

echo ""
echo "=========================================="
echo "Build Complete!"
echo "=========================================="
EOF

cat > start.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "Starting Content Curation System"
echo "=========================================="

if [ "$1" == "--docker" ]; then
    echo "Starting with Docker..."
    docker-compose up -d
    echo ""
    echo "Services starting..."
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
else
    echo "Starting locally..."
    
    # Start backend
    echo "Starting backend..."
    cd backend
    source venv/bin/activate
    export GEMINI_API_KEY=AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend
    sleep 3
    
    # Start frontend
    echo "Starting frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "Services started!"
    echo "Backend PID: $BACKEND_PID"
    echo "Frontend PID: $FRONTEND_PID"
    echo ""
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    echo "API Docs: http://localhost:8000/docs"
    
    # Save PIDs for stop script
    echo "$BACKEND_PID" > .backend.pid
    echo "$FRONTEND_PID" > .frontend.pid
    
    wait
fi
EOF

cat > stop.sh << 'EOF'
#!/bin/bash

echo "Stopping Content Curation System..."

if [ "$1" == "--docker" ]; then
    docker-compose down
else
    if [ -f .backend.pid ]; then
        kill $(cat .backend.pid) 2>/dev/null
        rm .backend.pid
    fi
    
    if [ -f .frontend.pid ]; then
        kill $(cat .frontend.pid) 2>/dev/null
        rm .frontend.pid
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" 2>/dev/null
    pkill -f "react-scripts start" 2>/dev/null
fi

echo "Services stopped."
EOF

chmod +x build.sh start.sh stop.sh

# ============================================
# Demo Script
# ============================================

cat > demo.sh << 'EOF'
#!/bin/bash

echo "=========================================="
echo "Content Curation System Demo"
echo "=========================================="

API_URL="http://localhost:8000"

# Wait for backend
echo "Waiting for backend..."
for i in {1..30}; do
    if curl -s "$API_URL/health" > /dev/null; then
        echo "Backend is ready!"
        break
    fi
    sleep 1
done

echo ""
echo "1. Generating sample questions..."
echo ""

# Generate questions
for topic in "Mathematics" "Science" "History"; do
    echo "Generating $topic question..."
    curl -s -X POST "$API_URL/api/questions/generate?topic=$topic&difficulty=medium" | python3 -m json.tool | head -20
    echo ""
done

echo "2. Checking curation queue..."
curl -s "$API_URL/api/curation/queue?status=pending" | python3 -m json.tool

echo ""
echo "3. Demonstrating review workflow..."

# Get first item from queue
CURATION_ID=$(curl -s "$API_URL/api/curation/queue?status=pending" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data['items'][0]['id'] if data['items'] else '')")

if [ -n "$CURATION_ID" ]; then
    echo "Claiming item $CURATION_ID..."
    curl -s -X POST "$API_URL/api/curation/$CURATION_ID/claim" \
        -H "Content-Type: application/json" \
        -d '{"reviewer_id": "demo_admin"}' | python3 -m json.tool | head -10
    
    echo ""
    echo "Approving content..."
    curl -s -X POST "$API_URL/api/curation/$CURATION_ID/approve" \
        -H "Content-Type: application/json" \
        -d '{"reviewer_id": "demo_admin"}' | python3 -m json.tool | head -10
    
    echo ""
    echo "Checking audit logs..."
    curl -s "$API_URL/api/curation/$CURATION_ID/audit" | python3 -m json.tool
fi

echo ""
echo "4. Getting analytics..."
curl -s "$API_URL/api/analytics/curation?days=7" | python3 -m json.tool

echo ""
echo "=========================================="
echo "Demo Complete!"
echo ""
echo "Access the dashboard at: http://localhost:3000"
echo "API documentation at: http://localhost:8000/docs"
echo "=========================================="
EOF

chmod +x demo.sh

echo ""
echo "=========================================="
echo "Project Structure Created Successfully!"
echo "=========================================="
echo ""
echo "Project location: $PROJECT_DIR"
echo ""
echo "Next steps:"
echo "1. cd $PROJECT_DIR"
echo "2. ./build.sh          # Build without Docker"
echo "   ./build.sh --docker # Build with Docker"
echo "3. ./start.sh          # Start without Docker"
echo "   ./start.sh --docker # Start with Docker"
echo "4. ./demo.sh           # Run demonstration"
echo ""
echo "Dashboard: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""