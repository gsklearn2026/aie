from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text, Float, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from ..database.base import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    quiz_attempts = relationship("QuizAttempt", back_populates="user")
    
    # Indexes for optimized queries
    __table_args__ = (
        Index('idx_user_email', 'email'),
        Index('idx_user_username', 'username'),
        Index('idx_user_created_at', 'created_at'),
    )

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100), nullable=False)
    difficulty = Column(String(50), default="medium")
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    questions = relationship("Question", back_populates="quiz", lazy="joined")  # Eager loading
    quiz_attempts = relationship("QuizAttempt", back_populates="quiz")
    
    # Optimized indexes
    __table_args__ = (
        Index('idx_quiz_category', 'category'),
        Index('idx_quiz_difficulty', 'difficulty'),
        Index('idx_quiz_active', 'is_active'),
        Index('idx_quiz_created_at', 'created_at'),
        Index('idx_quiz_category_active', 'category', 'is_active'),  # Composite index
    )

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    option_a = Column(String(500))
    option_b = Column(String(500))
    option_c = Column(String(500))
    option_d = Column(String(500))
    correct_answer = Column(String(1), nullable=False)
    explanation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    quiz = relationship("Quiz", back_populates="questions")
    
    # Optimized for JOIN operations
    __table_args__ = (
        Index('idx_question_quiz_id', 'quiz_id'),
    )

class QuizAttempt(Base):
    __tablename__ = "quiz_attempts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"), nullable=False)
    score = Column(Float, default=0.0)
    total_questions = Column(Integer)
    time_taken = Column(Integer)  # seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="quiz_attempts")
    quiz = relationship("Quiz", back_populates="quiz_attempts")
    
    # Critical composite indexes for performance
    __table_args__ = (
        Index('idx_attempt_user_id', 'user_id'),
        Index('idx_attempt_quiz_id', 'quiz_id'),
        Index('idx_attempt_created_at', 'created_at'),
        Index('idx_attempt_user_created', 'user_id', 'created_at'),  # User history queries
        Index('idx_attempt_score', 'score'),  # Leaderboard queries
        Index('idx_attempt_quiz_score', 'quiz_id', 'score'),  # Quiz-specific leaderboards
    )
