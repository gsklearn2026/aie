from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    quiz_sessions = relationship("QuizSession", back_populates="user")

class Quiz(Base):
    __tablename__ = "quizzes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(Text)
    category = Column(String)
    difficulty_level = Column(String)
    total_questions = Column(Integer)
    time_limit = Column(Integer)  # in minutes
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    questions = relationship("Question", back_populates="quiz")
    sessions = relationship("QuizSession", back_populates="quiz")

class Question(Base):
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    question_text = Column(Text)
    question_type = Column(String)  # multiple_choice, true_false, text
    options = Column(Text)  # JSON string for multiple choice
    correct_answer = Column(String)
    difficulty_score = Column(Float)
    topic = Column(String)
    
    # Relationships
    quiz = relationship("Quiz", back_populates="questions")
    responses = relationship("QuestionResponse", back_populates="question")

class QuizSession(Base):
    __tablename__ = "quiz_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    quiz_id = Column(Integer, ForeignKey("quizzes.id"))
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    score = Column(Float)
    total_questions = Column(Integer)
    correct_answers = Column(Integer)
    time_taken = Column(Integer)  # in seconds
    is_completed = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="quiz_sessions")
    quiz = relationship("Quiz", back_populates="sessions")
    responses = relationship("QuestionResponse", back_populates="session")

class QuestionResponse(Base):
    __tablename__ = "question_responses"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("quiz_sessions.id"))
    question_id = Column(Integer, ForeignKey("questions.id"))
    user_answer = Column(String)
    is_correct = Column(Boolean)
    time_taken = Column(Integer)  # in seconds
    answered_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("QuizSession", back_populates="responses")
    question = relationship("Question", back_populates="responses")
