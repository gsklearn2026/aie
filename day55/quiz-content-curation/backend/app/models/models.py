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
