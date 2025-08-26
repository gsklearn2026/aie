from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional

Base = declarative_base()

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    quiz_id = Column(String, index=True)
    topic_id = Column(String, index=True)
    score = Column(Float)
    max_score = Column(Float)
    time_spent = Column(Integer)  # seconds
    completed_at = Column(DateTime, default=func.now())
    answers = Column(JSON)
    metadata_json = Column(JSON)

class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    user_id = Column(String, index=True)
    quiz_id = Column(String, index=True)
    topic_id = Column(String, index=True)
    data = Column(JSON)
    timestamp = Column(DateTime, default=func.now())
    processed = Column(Boolean, default=False)

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    topic_id = Column(String, index=True)
    metric_type = Column(String, index=True)  # mastery_level, learning_velocity, etc.
    value = Column(Float)
    aggregation_window = Column(String)  # daily, weekly, monthly
    calculated_at = Column(DateTime, default=func.now())
    metadata_json = Column(JSON)

class LearningInsight(Base):
    __tablename__ = "learning_insights"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    insight_type = Column(String, index=True)
    title = Column(String)
    description = Column(Text)
    confidence_score = Column(Float)
    action_items = Column(JSON)
    generated_at = Column(DateTime, default=func.now())
    is_active = Column(Boolean, default=True)
