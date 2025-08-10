from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    learning_preferences = Column(JSON)
    
    # Relationships
    progress_records = relationship("UserProgress", back_populates="user")
    learning_paths = relationship("LearningPath", back_populates="user")

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    difficulty_level = Column(Float)  # 1.0 to 10.0
    estimated_duration = Column(Integer)  # minutes
    prerequisites = Column(JSON)  # List of topic IDs
    learning_objectives = Column(JSON)
    content_type = Column(String)  # video, text, quiz, interactive
    created_at = Column(DateTime, default=datetime.utcnow)

class UserProgress(Base):
    __tablename__ = "user_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic_id = Column(Integer, ForeignKey("topics.id"))
    mastery_level = Column(Float)  # 0.0 to 1.0
    completion_status = Column(String)  # not_started, in_progress, completed
    time_spent = Column(Integer)  # minutes
    last_accessed = Column(DateTime, default=datetime.utcnow)
    attempts = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User", back_populates="progress_records")
    topic = relationship("Topic")

class LearningPath(Base):
    __tablename__ = "learning_paths"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    path_name = Column(String)
    topic_sequence = Column(JSON)  # Ordered list of topic IDs
    difficulty_progression = Column(JSON)  # Difficulty curve data
    estimated_completion_time = Column(Integer)  # minutes
    completion_rate = Column(Float, default=0.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learning_paths")

class TopicRelationship(Base):
    __tablename__ = "topic_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    source_topic_id = Column(Integer, ForeignKey("topics.id"))
    target_topic_id = Column(Integer, ForeignKey("topics.id"))
    relationship_type = Column(String)  # prerequisite, related, continuation
    strength = Column(Float)  # 0.0 to 1.0
    created_at = Column(DateTime, default=datetime.utcnow)
