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
