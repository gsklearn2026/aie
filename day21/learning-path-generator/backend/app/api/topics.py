from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database.connection import get_db
from ..models.learning_path import Topic, TopicRelationship

router = APIRouter()

class TopicCreate(BaseModel):
    name: str
    description: str
    difficulty_level: float
    estimated_duration: int
    prerequisites: Optional[List[int]] = []
    learning_objectives: Optional[List[str]] = []
    content_type: str = "text"

@router.get("/")
async def get_topics(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all topics with pagination"""
    topics = db.query(Topic).offset(skip).limit(limit).all()
    
    return {
        "topics": [
            {
                "id": topic.id,
                "name": topic.name,
                "description": topic.description,
                "difficulty_level": topic.difficulty_level,
                "estimated_duration": topic.estimated_duration,
                "content_type": topic.content_type
            }
            for topic in topics
        ],
        "total": db.query(Topic).count()
    }

@router.post("/")
async def create_topic(
    topic: TopicCreate,
    db: Session = Depends(get_db)
):
    """Create a new topic"""
    db_topic = Topic(
        name=topic.name,
        description=topic.description,
        difficulty_level=topic.difficulty_level,
        estimated_duration=topic.estimated_duration,
        prerequisites=topic.prerequisites,
        learning_objectives=topic.learning_objectives,
        content_type=topic.content_type
    )
    
    db.add(db_topic)
    db.commit()
    db.refresh(db_topic)
    
    return {"message": "Topic created successfully", "topic_id": db_topic.id}

@router.get("/{topic_id}/relationships")
async def get_topic_relationships(
    topic_id: int,
    db: Session = Depends(get_db)
):
    """Get relationships for a specific topic"""
    relationships = db.query(TopicRelationship).filter(
        (TopicRelationship.source_topic_id == topic_id) |
        (TopicRelationship.target_topic_id == topic_id)
    ).all()
    
    return {
        "topic_id": topic_id,
        "relationships": [
            {
                "source_topic_id": rel.source_topic_id,
                "target_topic_id": rel.target_topic_id,
                "relationship_type": rel.relationship_type,
                "strength": rel.strength
            }
            for rel in relationships
        ]
    }
