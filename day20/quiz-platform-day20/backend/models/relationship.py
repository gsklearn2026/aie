from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Topic(Base):
    __tablename__ = "topics"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100))
    difficulty_level = Column(Integer, default=1)
    content_keywords = Column(Text)  # JSON string of keywords
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class TopicRelationship(Base):
    __tablename__ = "topic_relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    source_topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    target_topic_id = Column(Integer, ForeignKey("topics.id"), nullable=False)
    relationship_type = Column(String(50), nullable=False)  # prerequisite, similar, builds_on, etc.
    strength = Column(Float, default=0.5)  # 0.0 to 1.0
    bidirectional = Column(Boolean, default=False)
    ai_generated = Column(Boolean, default=False)
    validated_by_educator = Column(Boolean, default=False)
    source_evidence = Column(Text)  # Why this relationship exists
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    source_topic = relationship("Topic", foreign_keys=[source_topic_id])
    target_topic = relationship("Topic", foreign_keys=[target_topic_id])

class RelationshipValidation(Base):
    __tablename__ = "relationship_validations"
    
    id = Column(Integer, primary_key=True, index=True)
    relationship_id = Column(Integer, ForeignKey("topic_relationships.id"), nullable=False)
    educator_id = Column(String(100))  # Reference to user system
    validation_status = Column(String(20))  # approved, rejected, needs_review
    feedback = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
