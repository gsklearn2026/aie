from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean
from sqlalchemy.sql import func
from datetime import datetime

from ..config.database import Base

class QuizResult(Base):
    __tablename__ = "quiz_results"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    quiz_id = Column(String, index=True)
    score = Column(Float)
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    time_taken = Column(Float)  # in seconds
    difficulty_level = Column(String)
    subject_area = Column(String)
    ai_difficulty_prediction = Column(Float)
    learning_pattern = Column(String)
    improvement_areas = Column(Text)
    completed_at = Column(DateTime(timezone=True), server_default=func.now())
    
class QuestionAnalytics(Base):
    __tablename__ = "question_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    question_id = Column(String, index=True)
    quiz_id = Column(String, index=True)
    correct_rate = Column(Float)
    avg_time_spent = Column(Float)
    difficulty_rating = Column(Float)
    ai_complexity_score = Column(Float)
    common_mistakes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
