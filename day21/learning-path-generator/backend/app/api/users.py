from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, Any
from ..database.connection import get_db
from ..models.learning_path import User, UserProgress

router = APIRouter()

class UserCreate(BaseModel):
    username: str
    email: str
    learning_preferences: Optional[Dict[str, Any]] = {}

@router.post("/")
async def create_user(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    """Create a new user"""
    db_user = User(
        username=user.username,
        email=user.email,
        learning_preferences=user.learning_preferences
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return {
        "message": "User created successfully",
        "user_id": db_user.id,
        "username": db_user.username
    }

@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user details"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": user.id,
        "username": user.username,
        "email": user.email,
        "learning_preferences": user.learning_preferences,
        "created_at": user.created_at
    }

@router.get("/{user_id}/progress")
async def get_user_progress(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user's learning progress"""
    progress_records = db.query(UserProgress).filter(
        UserProgress.user_id == user_id
    ).all()
    
    return {
        "user_id": user_id,
        "progress": [
            {
                "topic_id": record.topic_id,
                "mastery_level": record.mastery_level,
                "completion_status": record.completion_status,
                "time_spent": record.time_spent,
                "attempts": record.attempts,
                "last_accessed": record.last_accessed
            }
            for record in progress_records
        ],
        "total_topics": len(progress_records),
        "completed_topics": len([r for r in progress_records if r.completion_status == "completed"])
    }
