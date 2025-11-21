from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

Base = declarative_base()

class ModelProfile(Base):
    __tablename__ = "model_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    configuration = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class GenerationRequest(Base):
    __tablename__ = "generation_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    question_type = Column(String, index=True)
    subject = Column(String, index=True)
    difficulty = Column(String)
    profile_used = Column(String, index=True)
    status = Column(String, default="pending")
    latency_ms = Column(Float)
    estimated_cost = Column(Float)
    quality_score = Column(Float)
    fallback_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class GeneratedQuestion(Base):
    __tablename__ = "generated_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, index=True)
    question_type = Column(String, index=True)
    question_text = Column(Text)
    correct_answer = Column(Text)
    options = Column(JSON)
    explanation = Column(Text)
    subject = Column(String, index=True)
    difficulty = Column(String)
    profile_used = Column(String)
    quality_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class ModelMetrics(Base):
    __tablename__ = "model_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    profile_name = Column(String, index=True)
    question_type = Column(String, index=True)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    total_latency_ms = Column(Float, default=0)
    total_cost = Column(Float, default=0)
    avg_quality_score = Column(Float, default=0)
    date = Column(DateTime, default=datetime.utcnow, index=True)
