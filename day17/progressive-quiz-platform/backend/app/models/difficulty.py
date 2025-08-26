from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    options = Column(Text)  # JSON string
    correct_answer = Column(String(255))
    difficulty_score = Column(Float, default=1.0)
    category = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    responses = relationship("UserResponse", back_populates="question")

class UserPerformance(Base):
    __tablename__ = "user_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False, index=True)
    session_id = Column(String(255), nullable=False)
    current_difficulty = Column(Float, default=1.0)
    success_rate = Column(Float, default=0.0)
    momentum = Column(Float, default=0.0)
    question_count = Column(Integer, default=0)
    total_time_ms = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow)

class UserResponse(Base):
    __tablename__ = "user_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), nullable=False)
    session_id = Column(String(255), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"))
    user_answer = Column(String(255))
    is_correct = Column(Boolean)
    response_time_ms = Column(Integer)
    difficulty_at_time = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    question = relationship("Question", back_populates="responses")

class DifficultySession(Base):
    __tablename__ = "difficulty_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(String(255), nullable=False)
    current_difficulty = Column(Float, default=1.0)
    target_success_rate = Column(Float, default=0.7)
    adjustment_factor = Column(Float, default=0.3)
    window_size = Column(Integer, default=10)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
