#!/bin/bash

# Day 56: Automated Content Refreshing - Complete Project Implementation
# This script creates the full project structure with all source files

set -e

echo "=============================================="
echo "Day 56: Automated Content Refreshing"
echo "Quiz Platform - Content Lifecycle Management"
echo "=============================================="

# Project root
PROJECT_ROOT="$(pwd)/quiz-platform-content-refresh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Create project structure
echo ""
echo "Creating project structure..."

mkdir -p "$PROJECT_ROOT"/{backend/{app/{api,core,models,services,schemas,jobs},tests,migrations},frontend/{src/{components,hooks,services,pages},public},scripts,monitoring}

print_status "Project directories created"

# Create backend requirements.txt
cat > "$PROJECT_ROOT/backend/requirements.txt" << 'EOF'
fastapi==0.115.6
uvicorn[standard]==0.34.0
sqlalchemy==2.0.36
asyncpg==0.30.0
psycopg2-binary==2.9.10
redis==5.2.1
google-generativeai==0.8.4
apscheduler==3.10.4
alembic==1.14.0
pydantic==2.10.4
pydantic-settings==2.7.0
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
httpx==0.28.1
pytest==8.3.4
pytest-asyncio==0.24.0
pytest-cov==6.0.0
structlog==24.4.0
prometheus-client==0.21.1
EOF

print_status "Backend requirements.txt created"

# Create backend main application
cat > "$PROJECT_ROOT/backend/app/main.py" << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import structlog

from app.core.config import settings
from app.core.database import engine, Base
from app.api import content, jobs, metrics, versions
from app.jobs.scheduler import start_scheduler, shutdown_scheduler

logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting application", version="1.0.0")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    start_scheduler()
    yield
    # Shutdown
    shutdown_scheduler()
    logger.info("Application shutdown complete")

app = FastAPI(
    title="Quiz Platform - Content Refresh Service",
    description="Automated content lifecycle management with AI-powered refresh",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(content.router, prefix="/api/content", tags=["Content"])
app.include_router(jobs.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(versions.router, prefix="/api/versions", tags=["Versions"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "content-refresh"}
EOF

print_status "Backend main.py created"

# Create config
cat > "$PROJECT_ROOT/backend/app/core/config.py" << 'EOF'
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/quiz_content"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/quiz_content"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Gemini AI
    GEMINI_API_KEY: str = "AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8"
    
    # Content Refresh Settings
    FRESHNESS_THRESHOLD: float = 40.0
    REFRESH_BATCH_SIZE: int = 10
    MAX_REFRESH_RETRIES: int = 3
    
    # Scheduler Settings
    FRESHNESS_SCAN_HOURS: int = 6
    STALE_PROCESS_HOUR: int = 2
    
    # Alert Thresholds
    ALERT_QUEUE_DEPTH: int = 100
    ALERT_ROLLBACK_RATE: float = 0.15
    ALERT_REFRESH_TIME_P95: int = 300
    ALERT_STALE_CONTENT_PCT: float = 0.2
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
EOF

print_status "Backend config.py created"

# Create database connection
cat > "$PROJECT_ROOT/backend/app/core/database.py" << 'EOF'
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
EOF

print_status "Backend database.py created"

# Create models
cat > "$PROJECT_ROOT/backend/app/models/__init__.py" << 'EOF'
from app.models.content import QuizContent, ContentVersion, ContentMetrics, RefreshJob
EOF

cat > "$PROJECT_ROOT/backend/app/models/content.py" << 'EOF'
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey, Enum, Text
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.core.database import Base

class ContentState(str, enum.Enum):
    ACTIVE = "active"
    FLAGGED = "flagged"
    REFRESHING = "refreshing"
    VALIDATING = "validating"
    ROLLED_BACK = "rolled_back"

class ContentLifecycle(str, enum.Enum):
    FRESH = "fresh"
    CURRENT = "current"
    AGING = "aging"
    STALE = "stale"

class QuizContent(Base):
    __tablename__ = "quiz_content"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    topic = Column(String(255), nullable=False, index=True)
    question = Column(Text, nullable=False)
    options = Column(JSONB, nullable=False)
    correct_answer = Column(String(255), nullable=False)
    explanation = Column(Text)
    difficulty = Column(String(50), default="medium")
    category = Column(String(100), index=True)
    
    # Lifecycle management
    state = Column(Enum(ContentState), default=ContentState.ACTIVE, index=True)
    lifecycle = Column(Enum(ContentLifecycle), default=ContentLifecycle.FRESH)
    freshness_score = Column(Float, default=100.0, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_refreshed_at = Column(DateTime)
    
    # Relationships
    versions = relationship("ContentVersion", back_populates="content", cascade="all, delete-orphan")
    metrics = relationship("ContentMetrics", back_populates="content", uselist=False, cascade="all, delete-orphan")

class ContentVersion(Base):
    __tablename__ = "content_versions"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("quiz_content.id"), nullable=False)
    version_number = Column(Integer, nullable=False)
    content_data = Column(JSONB, nullable=False)
    performance_snapshot = Column(JSONB)
    refresh_reason = Column(String(255))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content = relationship("QuizContent", back_populates="versions")

class ContentMetrics(Base):
    __tablename__ = "content_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("quiz_content.id"), unique=True, nullable=False)
    
    # Engagement metrics
    total_attempts = Column(Integer, default=0)
    correct_attempts = Column(Integer, default=0)
    skip_count = Column(Integer, default=0)
    avg_time_seconds = Column(Float, default=0.0)
    
    # Calculated scores
    accuracy_rate = Column(Float, default=0.0)
    skip_rate = Column(Float, default=0.0)
    engagement_score = Column(Float, default=50.0)
    
    # Tracking
    last_calculated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    content = relationship("QuizContent", back_populates="metrics")

class RefreshJob(Base):
    __tablename__ = "refresh_jobs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content_id = Column(UUID(as_uuid=True), ForeignKey("quiz_content.id"), nullable=False)
    job_type = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")
    priority = Column(Integer, default=5)
    
    # Execution details
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    error_message = Column(Text)
    result = Column(JSONB)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    retry_count = Column(Integer, default=0)
EOF

print_status "Backend models created"

# Create schemas
cat > "$PROJECT_ROOT/backend/app/schemas/__init__.py" << 'EOF'
from app.schemas.content import (
    ContentCreate, ContentResponse, ContentUpdate,
    MetricsResponse, VersionResponse, JobResponse,
    RefreshRequest, DashboardStats
)
EOF

cat > "$PROJECT_ROOT/backend/app/schemas/content.py" << 'EOF'
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ContentCreate(BaseModel):
    topic: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: str = "medium"
    category: Optional[str] = None

class ContentUpdate(BaseModel):
    question: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[str] = None

class ContentResponse(BaseModel):
    id: UUID
    topic: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str]
    difficulty: str
    category: Optional[str]
    state: str
    lifecycle: str
    freshness_score: float
    created_at: datetime
    updated_at: datetime
    last_refreshed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class MetricsResponse(BaseModel):
    content_id: UUID
    total_attempts: int
    correct_attempts: int
    skip_count: int
    accuracy_rate: float
    skip_rate: float
    engagement_score: float
    last_calculated_at: datetime
    
    class Config:
        from_attributes = True

class VersionResponse(BaseModel):
    id: UUID
    content_id: UUID
    version_number: int
    content_data: Dict[str, Any]
    performance_snapshot: Optional[Dict[str, Any]]
    refresh_reason: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: UUID
    content_id: UUID
    job_type: str
    status: str
    priority: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class RefreshRequest(BaseModel):
    content_id: UUID
    priority: int = 5
    force: bool = False

class DashboardStats(BaseModel):
    total_content: int
    fresh_count: int
    current_count: int
    aging_count: int
    stale_count: int
    queue_depth: int
    avg_freshness_score: float
    rollback_rate: float
    recent_refreshes: int
    alerts: List[Dict[str, Any]]
EOF

print_status "Backend schemas created"

# Create services
cat > "$PROJECT_ROOT/backend/app/services/__init__.py" << 'EOF'
from app.services.content_service import ContentService
from app.services.refresh_service import RefreshService
from app.services.metrics_service import MetricsService
from app.services.ai_service import AIService
EOF

cat > "$PROJECT_ROOT/backend/app/services/content_service.py" << 'EOF'
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
EOF

cat > "$PROJECT_ROOT/backend/app/services/refresh_service.py" << 'EOF'
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update
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
            # Get content
            content_result = await self.db.execute(
                select(QuizContent).where(QuizContent.id == job.content_id)
            )
            content = content_result.scalar_one_or_none()
            
            if not content:
                raise ValueError("Content not found")
            
            # Update state
            content.state = ContentState.REFRESHING
            await self.db.commit()
            
            # Get metrics for context
            metrics_data = {}
            if content.metrics:
                metrics_data = {
                    "accuracy_rate": content.metrics.accuracy_rate,
                    "skip_rate": content.metrics.skip_rate,
                    "total_attempts": content.metrics.total_attempts
                }
            
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
                refresh_reason=f"Auto-refresh: freshness score {content.freshness_score}"
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
        
        for job in jobs:
            await self.process_refresh_job(job.id)
            await asyncio.sleep(0.5)  # Rate limiting
        
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
EOF

cat > "$PROJECT_ROOT/backend/app/services/metrics_service.py" << 'EOF'
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
EOF

cat > "$PROJECT_ROOT/backend/app/services/ai_service.py" << 'EOF'
import google.generativeai as genai
from typing import Dict, Any
import json
import structlog
import asyncio
import random

from app.core.config import settings

logger = structlog.get_logger()

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def regenerate_content(
        self,
        original_content: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Regenerate quiz content based on performance data"""
        
        accuracy = performance_data.get("accuracy_rate", 50)
        skip_rate = performance_data.get("skip_rate", 0)
        
        # Build improvement instructions
        improvements = []
        if accuracy > 85:
            improvements.append("Increase difficulty - current version is too easy")
        elif accuracy < 40:
            improvements.append("Simplify the question or add helpful context")
        
        if skip_rate > 30:
            improvements.append("Make the question more engaging and relevant")
        
        improvement_text = "\n".join(f"- {imp}" for imp in improvements) if improvements else "Maintain similar difficulty"
        
        prompt = f"""Regenerate this quiz question to improve engagement and effectiveness.

Original Question:
Topic: {original_content['topic']}
Question: {original_content['question']}
Options: {json.dumps(original_content['options'])}
Correct Answer: {original_content['correct_answer']}
Difficulty: {original_content['difficulty']}

Performance Data:
- Accuracy Rate: {accuracy}%
- Skip Rate: {skip_rate}%
- Total Attempts: {performance_data.get('total_attempts', 0)}

Improvements Needed:
{improvement_text}

Generate a new version that addresses these issues while maintaining the same learning objective.
Respond with valid JSON only:
{{
    "question": "new question text",
    "options": ["option1", "option2", "option3", "option4"],
    "correct_answer": "correct option text",
    "explanation": "brief explanation of the answer"
}}"""

        try:
            # Run in executor for async compatibility
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            # Parse response
            response_text = response.text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            new_content = json.loads(response_text)
            
            logger.info(
                "Content regenerated",
                topic=original_content['topic'],
                accuracy_before=accuracy
            )
            
            return new_content
            
        except Exception as e:
            logger.error("AI regeneration failed", error=str(e))
            # Return improved version of original
            return {
                "question": f"Updated: {original_content['question']}",
                "options": original_content['options'],
                "correct_answer": original_content['correct_answer'],
                "explanation": f"This question was automatically refreshed to improve engagement."
            }
    
    async def generate_quiz_content(self, topic: str, difficulty: str = "medium") -> Dict[str, Any]:
        """Generate new quiz content for a topic"""
        prompt = f"""Create a quiz question about {topic} at {difficulty} difficulty level.

The question should be:
- Clear and unambiguous
- Educational and engaging
- Appropriate for the difficulty level

Respond with valid JSON only:
{{
    "question": "question text",
    "options": ["option1", "option2", "option3", "option4"],
    "correct_answer": "correct option text",
    "explanation": "brief explanation"
}}"""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            response_text = response.text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.error("AI generation failed", error=str(e))
            raise
EOF

print_status "Backend services created"

# Create API routes
cat > "$PROJECT_ROOT/backend/app/api/__init__.py" << 'EOF'
from app.api import content, jobs, metrics, versions
EOF

cat > "$PROJECT_ROOT/backend/app/api/content.py" << 'EOF'
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
    rollback_rate = await refresh_service.get_rollback_rate()
    avg_freshness = await metrics_service.get_average_freshness()
    
    # Check alerts
    alerts = []
    if queue_depth > settings.ALERT_QUEUE_DEPTH:
        alerts.append({"type": "warning", "message": f"High queue depth: {queue_depth}"})
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
EOF

cat > "$PROJECT_ROOT/backend/app/api/jobs.py" << 'EOF'
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
EOF

cat > "$PROJECT_ROOT/backend/app/api/metrics.py" << 'EOF'
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.schemas.content import MetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter()

@router.get("/{content_id}", response_model=MetricsResponse)
async def get_metrics(
    content_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = MetricsService(db)
    metrics = await service.get_metrics(content_id)
    return metrics
EOF

cat > "$PROJECT_ROOT/backend/app/api/versions.py" << 'EOF'
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from uuid import UUID

from app.core.database import get_db
from app.models.content import ContentVersion
from app.schemas.content import VersionResponse
from app.services.refresh_service import RefreshService

router = APIRouter()

@router.get("/{content_id}", response_model=List[VersionResponse])
async def get_versions(
    content_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(ContentVersion)
        .where(ContentVersion.content_id == content_id)
        .order_by(ContentVersion.version_number.desc())
    )
    return result.scalars().all()

@router.post("/{content_id}/rollback/{version_number}")
async def rollback_version(
    content_id: UUID,
    version_number: int,
    db: AsyncSession = Depends(get_db)
):
    service = RefreshService(db)
    success = await service.rollback_content(content_id, version_number)
    if not success:
        raise HTTPException(status_code=404, detail="Version not found")
    return {"status": "rolled_back", "version": version_number}
EOF

print_status "Backend API routes created"

# Create scheduler jobs
cat > "$PROJECT_ROOT/backend/app/jobs/__init__.py" << 'EOF'
from app.jobs.scheduler import start_scheduler, shutdown_scheduler
EOF

cat > "$PROJECT_ROOT/backend/app/jobs/scheduler.py" << 'EOF'
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
import structlog

from app.core.config import settings
from app.jobs.refresh_jobs import freshness_scan_job, stale_content_job

logger = structlog.get_logger()

scheduler = None

def start_scheduler():
    global scheduler
    
    jobstores = {
        'default': SQLAlchemyJobStore(url=settings.DATABASE_URL_SYNC)
    }
    
    executors = {
        'default': ThreadPoolExecutor(20),
        'processpool': ProcessPoolExecutor(5)
    }
    
    job_defaults = {
        'coalesce': False,
        'max_instances': 3
    }
    
    scheduler = AsyncIOScheduler(
        jobstores=jobstores,
        executors=executors,
        job_defaults=job_defaults
    )
    
    # Add jobs
    scheduler.add_job(
        freshness_scan_job,
        'interval',
        hours=settings.FRESHNESS_SCAN_HOURS,
        id='freshness_scan',
        replace_existing=True
    )
    
    scheduler.add_job(
        stale_content_job,
        'cron',
        hour=settings.STALE_PROCESS_HOUR,
        id='stale_content_process',
        replace_existing=True
    )
    
    scheduler.start()
    logger.info("Scheduler started", jobs=len(scheduler.get_jobs()))

def shutdown_scheduler():
    global scheduler
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler shutdown")

def get_scheduler():
    return scheduler
EOF

cat > "$PROJECT_ROOT/backend/app/jobs/refresh_jobs.py" << 'EOF'
import asyncio
import structlog
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker

from app.core.config import settings
from app.services.refresh_service import RefreshService

logger = structlog.get_logger()

async def _run_freshness_scan():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        service = RefreshService(session)
        updated = await service.scan_and_update_freshness()
        logger.info("Scheduled freshness scan complete", updated=updated)
    
    await engine.dispose()

async def _run_stale_processing():
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        service = RefreshService(session)
        processed = await service.process_pending_jobs(settings.REFRESH_BATCH_SIZE)
        logger.info("Scheduled stale processing complete", processed=processed)
    
    await engine.dispose()

def freshness_scan_job():
    asyncio.run(_run_freshness_scan())

def stale_content_job():
    asyncio.run(_run_stale_processing())
EOF

print_status "Backend scheduler jobs created"

# Create tests
cat > "$PROJECT_ROOT/backend/tests/__init__.py" << 'EOF'
EOF

cat > "$PROJECT_ROOT/backend/tests/conftest.py" << 'EOF'
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.core.database import Base
from app.core.config import settings

TEST_DATABASE_URL = settings.DATABASE_URL.replace("quiz_content", "quiz_content_test")

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.fixture
async def db_session(test_engine):
    async_session = async_sessionmaker(
        test_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        await session.rollback()
EOF

cat > "$PROJECT_ROOT/backend/tests/test_content_service.py" << 'EOF'
import pytest
from app.services.content_service import ContentService
from app.schemas.content import ContentCreate

@pytest.mark.asyncio
async def test_create_content(db_session):
    service = ContentService(db_session)
    
    content_data = ContentCreate(
        topic="Python Basics",
        question="What keyword is used to define a function in Python?",
        options=["func", "def", "function", "define"],
        correct_answer="def",
        explanation="The 'def' keyword is used to define functions in Python",
        difficulty="easy",
        category="Programming"
    )
    
    content = await service.create_content(content_data)
    
    assert content.id is not None
    assert content.topic == "Python Basics"
    assert content.freshness_score == 100.0
    assert content.state.value == "active"

@pytest.mark.asyncio
async def test_get_stale_content(db_session):
    service = ContentService(db_session)
    
    # Create content with low freshness
    content_data = ContentCreate(
        topic="Test Topic",
        question="Test question?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty="medium"
    )
    content = await service.create_content(content_data)
    
    # Manually set low freshness
    content.freshness_score = 30.0
    await db_session.commit()
    
    stale = await service.get_stale_content(threshold=40.0)
    assert len(stale) >= 1
EOF

cat > "$PROJECT_ROOT/backend/tests/test_refresh_service.py" << 'EOF'
import pytest
from datetime import datetime, timedelta
from app.services.refresh_service import RefreshService
from app.services.content_service import ContentService
from app.schemas.content import ContentCreate
from app.models.content import ContentLifecycle

@pytest.mark.asyncio
async def test_calculate_freshness_score(db_session):
    content_service = ContentService(db_session)
    refresh_service = RefreshService(db_session)
    
    content_data = ContentCreate(
        topic="Test",
        question="Test?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty="medium"
    )
    content = await content_service.create_content(content_data)
    
    score = await refresh_service.calculate_freshness_score(content)
    assert 0 <= score <= 100

@pytest.mark.asyncio
async def test_determine_lifecycle(db_session):
    refresh_service = RefreshService(db_session)
    
    # Fresh content
    lifecycle = refresh_service.determine_lifecycle(85.0, 3)
    assert lifecycle == ContentLifecycle.FRESH
    
    # Stale content
    lifecycle = refresh_service.determine_lifecycle(20.0, 100)
    assert lifecycle == ContentLifecycle.STALE

@pytest.mark.asyncio
async def test_create_refresh_job(db_session):
    content_service = ContentService(db_session)
    refresh_service = RefreshService(db_session)
    
    content_data = ContentCreate(
        topic="Test",
        question="Test?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty="medium"
    )
    content = await content_service.create_content(content_data)
    
    job = await refresh_service.create_refresh_job(content.id, "test_refresh")
    
    assert job.id is not None
    assert job.status == "pending"
EOF

cat > "$PROJECT_ROOT/backend/tests/test_metrics_service.py" << 'EOF'
import pytest
from app.services.metrics_service import MetricsService
from app.services.content_service import ContentService
from app.schemas.content import ContentCreate

@pytest.mark.asyncio
async def test_record_attempt(db_session):
    content_service = ContentService(db_session)
    metrics_service = MetricsService(db_session)
    
    content_data = ContentCreate(
        topic="Test",
        question="Test?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty="medium"
    )
    content = await content_service.create_content(content_data)
    
    # Record correct attempt
    metrics = await metrics_service.record_attempt(content.id, True, 45.0)
    
    assert metrics.total_attempts == 1
    assert metrics.correct_attempts == 1
    assert metrics.accuracy_rate == 100.0

@pytest.mark.asyncio
async def test_skip_recording(db_session):
    content_service = ContentService(db_session)
    metrics_service = MetricsService(db_session)
    
    content_data = ContentCreate(
        topic="Test",
        question="Test?",
        options=["A", "B", "C", "D"],
        correct_answer="A",
        difficulty="medium"
    )
    content = await content_service.create_content(content_data)
    
    # Record skip
    metrics = await metrics_service.record_attempt(content.id, False, 0, skipped=True)
    
    assert metrics.skip_count == 1
    assert metrics.skip_rate > 0
EOF

print_status "Backend tests created"

# Create frontend
cat > "$PROJECT_ROOT/frontend/package.json" << 'EOF'
{
  "name": "content-refresh-dashboard",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "@mui/material": "^6.3.0",
    "@mui/icons-material": "^6.3.0",
    "@emotion/react": "^11.14.0",
    "@emotion/styled": "^11.14.0",
    "recharts": "^2.15.0",
    "axios": "^1.7.9"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.3.4",
    "vite": "^6.0.7"
  }
}
EOF

cat > "$PROJECT_ROOT/frontend/vite.config.js" << 'EOF'
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
EOF

cat > "$PROJECT_ROOT/frontend/index.html" << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Content Refresh Dashboard</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
EOF

cat > "$PROJECT_ROOT/frontend/src/main.jsx" << 'EOF'
import React from 'react'
import ReactDOM from 'react-dom/client'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import App from './App'

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#2196f3',
    },
    secondary: {
      main: '#ff9800',
    },
  },
})

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
)
EOF

cat > "$PROJECT_ROOT/frontend/src/App.jsx" << 'EOF'
import React, { useState, useEffect } from 'react'
import {
  Container, Grid, Paper, Typography, Box, Button, Chip,
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  Alert, CircularProgress, LinearProgress, IconButton, Tooltip
} from '@mui/material'
import {
  Refresh, PlayArrow, History, Warning, CheckCircle, Error
} from '@mui/icons-material'
import {
  PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis
} from 'recharts'
import { api } from './services/api'

const COLORS = ['#4caf50', '#2196f3', '#ff9800', '#f44336']

function App() {
  const [stats, setStats] = useState(null)
  const [content, setContent] = useState([])
  const [jobs, setJobs] = useState([])
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const fetchData = async () => {
    try {
      const [statsRes, contentRes, jobsRes] = await Promise.all([
        api.get('/api/content/dashboard'),
        api.get('/api/content/?limit=20'),
        api.get('/api/jobs/?limit=10')
      ])
      setStats(statsRes.data)
      setContent(contentRes.data)
      setJobs(jobsRes.data)
    } catch (error) {
      console.error('Failed to fetch data:', error)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [])

  const triggerScan = async () => {
    setRefreshing(true)
    try {
      await api.post('/api/jobs/scan-freshness')
      await fetchData()
    } finally {
      setRefreshing(false)
    }
  }

  const processJobs = async () => {
    setRefreshing(true)
    try {
      await api.post('/api/jobs/process?batch_size=5')
      await fetchData()
    } finally {
      setRefreshing(false)
    }
  }

  const requestRefresh = async (contentId) => {
    try {
      await api.post('/api/content/refresh', {
        content_id: contentId,
        priority: 1
      })
      await fetchData()
    } catch (error) {
      console.error('Failed to request refresh:', error)
    }
  }

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="100vh">
        <CircularProgress />
      </Box>
    )
  }

  const lifecycleData = stats ? [
    { name: 'Fresh', value: stats.fresh_count },
    { name: 'Current', value: stats.current_count },
    { name: 'Aging', value: stats.aging_count },
    { name: 'Stale', value: stats.stale_count }
  ] : []

  return (
    <Container maxWidth="xl" sx={{ py: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" fontWeight="bold">
          Content Refresh Dashboard
        </Typography>
        <Box>
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={triggerScan}
            disabled={refreshing}
            sx={{ mr: 1 }}
          >
            Scan Freshness
          </Button>
          <Button
            variant="contained"
            startIcon={<PlayArrow />}
            onClick={processJobs}
            disabled={refreshing}
          >
            Process Queue
          </Button>
        </Box>
      </Box>

      {refreshing && <LinearProgress sx={{ mb: 2 }} />}

      {/* Alerts */}
      {stats?.alerts?.map((alert, i) => (
        <Alert severity={alert.type} sx={{ mb: 2 }} key={i}>
          {alert.message}
        </Alert>
      ))}

      {/* Stats Cards */}
      <Grid container spacing={3} mb={3}>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color="primary">
              {stats?.total_content || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Total Content
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color="secondary">
              {stats?.queue_depth || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Queue Depth
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color="success.main">
              {stats?.avg_freshness_score?.toFixed(1) || 0}
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Avg Freshness Score
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="h3" color={stats?.rollback_rate > 0.1 ? 'error' : 'success.main'}>
              {((stats?.rollback_rate || 0) * 100).toFixed(1)}%
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Rollback Rate
            </Typography>
          </Paper>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Lifecycle Distribution */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Content Lifecycle Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={lifecycleData}
                  dataKey="value"
                  nameKey="name"
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  label={({ name, value }) => `${name}: ${value}`}
                >
                  {lifecycleData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Recent Jobs */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Recent Refresh Jobs
            </Typography>
            <TableContainer>
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>Type</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Priority</TableCell>
                    <TableCell>Created</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {jobs.map((job) => (
                    <TableRow key={job.id}>
                      <TableCell>{job.job_type}</TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={job.status}
                          color={
                            job.status === 'completed' ? 'success' :
                            job.status === 'failed' ? 'error' :
                            job.status === 'processing' ? 'warning' : 'default'
                          }
                        />
                      </TableCell>
                      <TableCell>{job.priority}</TableCell>
                      <TableCell>
                        {new Date(job.created_at).toLocaleString()}
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Content List */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Content Status
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Topic</TableCell>
                    <TableCell>Question</TableCell>
                    <TableCell>State</TableCell>
                    <TableCell>Lifecycle</TableCell>
                    <TableCell>Freshness</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {content.map((item) => (
                    <TableRow key={item.id}>
                      <TableCell>{item.topic}</TableCell>
                      <TableCell sx={{ maxWidth: 300, overflow: 'hidden', textOverflow: 'ellipsis' }}>
                        {item.question}
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={item.state}
                          color={
                            item.state === 'active' ? 'success' :
                            item.state === 'flagged' ? 'warning' :
                            item.state === 'refreshing' ? 'info' : 'default'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          size="small"
                          label={item.lifecycle}
                          variant="outlined"
                          color={
                            item.lifecycle === 'fresh' ? 'success' :
                            item.lifecycle === 'current' ? 'info' :
                            item.lifecycle === 'aging' ? 'warning' : 'error'
                          }
                        />
                      </TableCell>
                      <TableCell>
                        <Box display="flex" alignItems="center">
                          <LinearProgress
                            variant="determinate"
                            value={item.freshness_score}
                            sx={{ width: 60, mr: 1 }}
                            color={
                              item.freshness_score >= 70 ? 'success' :
                              item.freshness_score >= 40 ? 'warning' : 'error'
                            }
                          />
                          {item.freshness_score.toFixed(0)}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Request Refresh">
                          <IconButton
                            size="small"
                            onClick={() => requestRefresh(item.id)}
                            disabled={item.state !== 'active'}
                          >
                            <Refresh />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  )
}

export default App
EOF

cat > "$PROJECT_ROOT/frontend/src/services/api.js" << 'EOF'
import axios from 'axios'

export const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})
EOF

print_status "Frontend created"

# Create Docker files
cat > "$PROJECT_ROOT/docker-compose.yml" << 'EOF'
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: quiz_content
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql+asyncpg://postgres:postgres@postgres:5432/quiz_content
      DATABASE_URL_SYNC: postgresql://postgres:postgres@postgres:5432/quiz_content
      REDIS_URL: redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
EOF

cat > "$PROJECT_ROOT/backend/Dockerfile" << 'EOF'
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

cat > "$PROJECT_ROOT/frontend/Dockerfile" << 'EOF'
FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev", "--", "--host"]
EOF

print_status "Docker configuration created"

# Create seed data script
cat > "$PROJECT_ROOT/scripts/seed_data.py" << 'EOF'
import asyncio
import httpx
import random

API_URL = "http://localhost:8000"

SAMPLE_CONTENT = [
    {
        "topic": "Python Basics",
        "question": "What is the correct way to create a variable in Python?",
        "options": ["var x = 5", "x := 5", "x = 5", "int x = 5"],
        "correct_answer": "x = 5",
        "explanation": "Python uses dynamic typing, so variables are created by simple assignment.",
        "difficulty": "easy",
        "category": "Programming"
    },
    {
        "topic": "Data Structures",
        "question": "Which data structure uses LIFO (Last In First Out) principle?",
        "options": ["Queue", "Stack", "Array", "Linked List"],
        "correct_answer": "Stack",
        "explanation": "Stacks follow LIFO - the last element added is the first one removed.",
        "difficulty": "medium",
        "category": "Computer Science"
    },
    {
        "topic": "Machine Learning",
        "question": "What type of learning uses labeled training data?",
        "options": ["Unsupervised", "Reinforcement", "Supervised", "Transfer"],
        "correct_answer": "Supervised",
        "explanation": "Supervised learning trains on labeled data to predict outputs.",
        "difficulty": "medium",
        "category": "AI"
    },
    {
        "topic": "Databases",
        "question": "What does SQL stand for?",
        "options": ["Strong Query Language", "Structured Query Language", "Simple Question Language", "Standard Query Logic"],
        "correct_answer": "Structured Query Language",
        "explanation": "SQL is the standard language for managing relational databases.",
        "difficulty": "easy",
        "category": "Databases"
    },
    {
        "topic": "Networking",
        "question": "Which protocol is used for secure web communication?",
        "options": ["HTTP", "FTP", "HTTPS", "SMTP"],
        "correct_answer": "HTTPS",
        "explanation": "HTTPS adds encryption to HTTP using TLS/SSL.",
        "difficulty": "easy",
        "category": "Networking"
    },
    {
        "topic": "Algorithms",
        "question": "What is the time complexity of binary search?",
        "options": ["O(n)", "O(n²)", "O(log n)", "O(1)"],
        "correct_answer": "O(log n)",
        "explanation": "Binary search halves the search space with each comparison.",
        "difficulty": "medium",
        "category": "Algorithms"
    },
    {
        "topic": "Web Development",
        "question": "Which HTML tag is used for the largest heading?",
        "options": ["<h6>", "<heading>", "<h1>", "<head>"],
        "correct_answer": "<h1>",
        "explanation": "h1 is the largest heading, h6 is the smallest.",
        "difficulty": "easy",
        "category": "Web"
    },
    {
        "topic": "Cloud Computing",
        "question": "What does IaaS stand for?",
        "options": ["Internet as a Service", "Infrastructure as a Service", "Integration as a Service", "Information as a Service"],
        "correct_answer": "Infrastructure as a Service",
        "explanation": "IaaS provides virtualized computing resources over the internet.",
        "difficulty": "medium",
        "category": "Cloud"
    }
]

async def seed_content():
    async with httpx.AsyncClient() as client:
        print("Seeding content...")
        
        for item in SAMPLE_CONTENT:
            try:
                response = await client.post(f"{API_URL}/api/content/", json=item)
                if response.status_code == 200:
                    content = response.json()
                    print(f"Created: {item['topic']} - {content['id']}")
                    
                    # Simulate some usage
                    for _ in range(random.randint(5, 20)):
                        correct = random.random() > 0.3
                        time_taken = random.uniform(20, 180)
                        await client.post(
                            f"{API_URL}/api/content/{content['id']}/attempt",
                            params={
                                "correct": correct,
                                "time_seconds": time_taken,
                                "skipped": random.random() > 0.9
                            }
                        )
                else:
                    print(f"Failed to create: {item['topic']} - {response.text}")
            except Exception as e:
                print(f"Error: {e}")
        
        # Trigger freshness scan
        print("\nTriggering freshness scan...")
        await client.post(f"{API_URL}/api/jobs/scan-freshness")
        
        print("\nSeeding complete!")

if __name__ == "__main__":
    asyncio.run(seed_content())
EOF

print_status "Seed data script created"

# Create build.sh
cat > "$PROJECT_ROOT/build.sh" << 'EOF'
#!/bin/bash

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() { echo -e "${GREEN}[✓]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[!]${NC} $1"; }
print_error() { echo -e "${RED}[✗]${NC} $1"; }

echo "=============================================="
echo "Day 56: Content Refresh - Build Script"
echo "=============================================="
echo ""

# Check for Docker mode
USE_DOCKER=false
if [[ "$1" == "--docker" ]]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    echo "Building with Docker..."
    
    # Build and start containers
    docker-compose build
    docker-compose up -d
    
    # Wait for services
    echo "Waiting for services to start..."
    sleep 10
    
    # Run migrations
    docker-compose exec -T backend python -c "
from app.core.database import engine, Base
import asyncio
async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(init())
"
    
    # Seed data
    docker-compose exec -T backend python /app/../scripts/seed_data.py
    
    # Run tests
    docker-compose exec -T backend pytest tests/ -v
    
    print_status "Docker build complete!"
    echo ""
    echo "Services running:"
    echo "  Backend:  http://localhost:8000"
    echo "  Frontend: http://localhost:3000"
    echo "  API Docs: http://localhost:8000/docs"
    
else
    echo "Building without Docker (local development)..."
    
    # Create virtual environment
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_status "Virtual environment created"
    fi
    
    source venv/bin/activate
    
    # Install backend dependencies
    cd backend
    pip install -r requirements.txt -q
    print_status "Backend dependencies installed"
    
    # Check PostgreSQL
    if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
        print_warning "PostgreSQL not running. Please start PostgreSQL."
        echo "  On macOS: brew services start postgresql"
        echo "  On Linux: sudo systemctl start postgresql"
        exit 1
    fi
    
    # Create database
    psql -h localhost -U postgres -c "CREATE DATABASE quiz_content;" 2>/dev/null || true
    psql -h localhost -U postgres -c "CREATE DATABASE quiz_content_test;" 2>/dev/null || true
    print_status "Databases created"
    
    # Run tests
    echo ""
    echo "Running tests..."
    pytest tests/ -v --tb=short
    print_status "Tests passed"
    
    cd ..
    
    # Install frontend dependencies
    cd frontend
    npm install --silent
    print_status "Frontend dependencies installed"
    cd ..
    
    print_status "Build complete!"
    echo ""
    echo "Next steps:"
    echo "  1. Run: ./start.sh"
    echo "  2. Open: http://localhost:3000"
fi
EOF

chmod +x "$PROJECT_ROOT/build.sh"
print_status "build.sh created"

# Create start.sh
cat > "$PROJECT_ROOT/start.sh" << 'EOF'
#!/bin/bash

set -e

echo "=============================================="
echo "Day 56: Content Refresh - Starting Services"
echo "=============================================="

USE_DOCKER=false
if [[ "$1" == "--docker" ]]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    echo "Starting with Docker..."
    docker-compose up -d
    
    echo ""
    echo "Services started:"
    echo "  Backend:  http://localhost:8000"
    echo "  Frontend: http://localhost:3000"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "View logs: docker-compose logs -f"
    
else
    echo "Starting local services..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Start backend
    echo "Starting backend..."
    cd backend
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend
    sleep 3
    
    # Seed data
    echo "Seeding data..."
    python scripts/seed_data.py
    
    # Start frontend
    echo "Starting frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "Services started:"
    echo "  Backend:  http://localhost:8000 (PID: $BACKEND_PID)"
    echo "  Frontend: http://localhost:3000 (PID: $FRONTEND_PID)"
    echo "  API Docs: http://localhost:8000/docs"
    echo ""
    echo "Press Ctrl+C to stop all services"
    
    # Save PIDs
    echo $BACKEND_PID > .backend.pid
    echo $FRONTEND_PID > .frontend.pid
    
    # Wait for interrupt
    trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
    wait
fi
EOF

chmod +x "$PROJECT_ROOT/start.sh"
print_status "start.sh created"

# Create stop.sh
cat > "$PROJECT_ROOT/stop.sh" << 'EOF'
#!/bin/bash

echo "=============================================="
echo "Day 56: Content Refresh - Stopping Services"
echo "=============================================="

USE_DOCKER=false
if [[ "$1" == "--docker" ]]; then
    USE_DOCKER=true
fi

if [ "$USE_DOCKER" = true ]; then
    echo "Stopping Docker services..."
    docker-compose down
    echo "Docker services stopped"
    
else
    echo "Stopping local services..."
    
    if [ -f .backend.pid ]; then
        kill $(cat .backend.pid) 2>/dev/null || true
        rm .backend.pid
        echo "Backend stopped"
    fi
    
    if [ -f .frontend.pid ]; then
        kill $(cat .frontend.pid) 2>/dev/null || true
        rm .frontend.pid
        echo "Frontend stopped"
    fi
    
    # Kill any remaining processes
    pkill -f "uvicorn app.main:app" 2>/dev/null || true
    pkill -f "vite" 2>/dev/null || true
    
    echo "All services stopped"
fi
EOF

chmod +x "$PROJECT_ROOT/stop.sh"
print_status "stop.sh created"

# Create .env file
cat > "$PROJECT_ROOT/backend/.env" << 'EOF'
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/quiz_content
DATABASE_URL_SYNC=postgresql://postgres:postgres@localhost:5432/quiz_content
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8
EOF

print_status ".env file created"

# Verify all files
echo ""
echo "Verifying created files..."

FILES_TO_CHECK=(
    "backend/app/main.py"
    "backend/app/core/config.py"
    "backend/app/core/database.py"
    "backend/app/models/content.py"
    "backend/app/services/content_service.py"
    "backend/app/services/refresh_service.py"
    "backend/app/services/metrics_service.py"
    "backend/app/services/ai_service.py"
    "backend/app/api/content.py"
    "backend/app/api/jobs.py"
    "backend/app/jobs/scheduler.py"
    "backend/tests/test_content_service.py"
    "frontend/src/App.jsx"
    "frontend/src/main.jsx"
    "docker-compose.yml"
    "build.sh"
    "start.sh"
    "stop.sh"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        print_status "Verified: $file"
    else
        print_error "Missing: $file"
    fi
done

echo ""
echo "=============================================="
echo "Project Implementation Complete!"
echo "=============================================="
echo ""
echo "Project location: $PROJECT_ROOT"
echo ""
echo "Next steps:"
echo "  cd $PROJECT_ROOT"
echo "  ./build.sh          # Local development"
echo "  ./build.sh --docker # Docker deployment"
echo ""