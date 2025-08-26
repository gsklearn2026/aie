from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database.connection import get_db
from ..services.path_generator import LearningPathGenerator, CollaborativePathGenerator
from ..models.learning_path import LearningPath, User
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class PathGenerationRequest(BaseModel):
    user_id: int
    target_topics: List[int]
    max_difficulty_jump: Optional[float] = 1.5
    preferred_duration: Optional[int] = None
    use_collaborative: Optional[bool] = False

class PathUpdateRequest(BaseModel):
    topic_id: int
    mastery_level: float
    completion_status: str
    time_spent: int

@router.post("/generate")
async def generate_learning_path(
    request: PathGenerationRequest,
    db: Session = Depends(get_db)
):
    """Generate personalized learning path for user"""
    try:
        if request.use_collaborative:
            generator = CollaborativePathGenerator(db)
            result = generator.generate_collaborative_path(
                request.user_id,
                request.target_topics
            )
        else:
            generator = LearningPathGenerator(db)
            result = generator.generate_personalized_path(
                request.user_id,
                request.target_topics,
                request.max_difficulty_jump,
                request.preferred_duration
            )
        
        # Save generated path to database
        learning_path = LearningPath(
            user_id=request.user_id,
            path_name=f"Generated Path {len(request.target_topics)} topics",
            topic_sequence=result["topic_sequence"],
            difficulty_progression=result["difficulty_progression"],
            estimated_completion_time=result["estimated_duration"]
        )
        
        db.add(learning_path)
        db.commit()
        db.refresh(learning_path)
        
        result["path_id"] = learning_path.id
        
        logger.info(f"Generated learning path for user {request.user_id}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error generating learning path: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error generating learning path: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}")
async def get_user_learning_paths(
    user_id: int,
    active_only: bool = Query(True),
    db: Session = Depends(get_db)
):
    """Get all learning paths for a user"""
    try:
        query = db.query(LearningPath).filter(LearningPath.user_id == user_id)
        
        if active_only:
            query = query.filter(LearningPath.is_active == True)
        
        paths = query.all()
        
        return {
            "user_id": user_id,
            "paths": [
                {
                    "path_id": path.id,
                    "path_name": path.path_name,
                    "topic_sequence": path.topic_sequence,
                    "estimated_duration": path.estimated_completion_time,
                    "completion_rate": path.completion_rate,
                    "created_at": path.created_at,
                    "is_active": path.is_active
                }
                for path in paths
            ]
        }
        
    except Exception as e:
        logger.error(f"Error fetching user paths: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/{user_id}/progress")
async def update_learning_progress(
    user_id: int,
    request: PathUpdateRequest,
    db: Session = Depends(get_db)
):
    """Update user's progress on a topic"""
    try:
        from ..models.learning_path import UserProgress
        
        # Check if progress record exists
        progress = db.query(UserProgress).filter(
            UserProgress.user_id == user_id,
            UserProgress.topic_id == request.topic_id
        ).first()
        
        if progress:
            # Update existing record
            progress.mastery_level = request.mastery_level
            progress.completion_status = request.completion_status
            progress.time_spent += request.time_spent
            progress.attempts += 1
        else:
            # Create new progress record
            progress = UserProgress(
                user_id=user_id,
                topic_id=request.topic_id,
                mastery_level=request.mastery_level,
                completion_status=request.completion_status,
                time_spent=request.time_spent,
                attempts=1
            )
            db.add(progress)
        
        db.commit()
        
        # Update learning path completion rates
        await _update_path_completion_rates(user_id, db)
        
        return {
            "message": "Progress updated successfully",
            "user_id": user_id,
            "topic_id": request.topic_id,
            "updated_progress": {
                "mastery_level": progress.mastery_level,
                "completion_status": progress.completion_status,
                "total_time": progress.time_spent
            }
        }
        
    except Exception as e:
        logger.error(f"Error updating progress: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{user_id}/next-topics")
async def get_next_recommended_topics(
    user_id: int,
    count: int = Query(3, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """Get next recommended topics for user"""
    try:
        # Get user's active learning path
        active_path = db.query(LearningPath).filter(
            LearningPath.user_id == user_id,
            LearningPath.is_active == True
        ).first()
        
        if not active_path:
            return {
                "message": "No active learning path found",
                "recommendations": []
            }
        
        # Get user's current progress
        from ..models.learning_path import UserProgress
        completed_topics = db.query(UserProgress.topic_id).filter(
            UserProgress.user_id == user_id,
            UserProgress.completion_status == "completed"
        ).all()
        
        completed_topic_ids = [topic[0] for topic in completed_topics]
        
        # Find next topics in sequence
        next_topics = []
        for topic_id in active_path.topic_sequence:
            if topic_id not in completed_topic_ids:
                next_topics.append(topic_id)
                if len(next_topics) >= count:
                    break
        
        # Get topic details
        from ..models.learning_path import Topic
        topic_details = db.query(Topic).filter(Topic.id.in_(next_topics)).all()
        
        recommendations = [
            {
                "topic_id": topic.id,
                "name": topic.name,
                "description": topic.description,
                "difficulty_level": topic.difficulty_level,
                "estimated_duration": topic.estimated_duration
            }
            for topic in topic_details
        ]
        
        return {
            "user_id": user_id,
            "path_id": active_path.id,
            "recommendations": recommendations,
            "total_remaining": len([t for t in active_path.topic_sequence if t not in completed_topic_ids])
        }
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def _update_path_completion_rates(user_id: int, db: Session):
    """Update completion rates for user's active paths"""
    try:
        from ..models.learning_path import UserProgress
        
        active_paths = db.query(LearningPath).filter(
            LearningPath.user_id == user_id,
            LearningPath.is_active == True
        ).all()
        
        for path in active_paths:
            total_topics = len(path.topic_sequence)
            
            completed_count = db.query(UserProgress).filter(
                UserProgress.user_id == user_id,
                UserProgress.topic_id.in_(path.topic_sequence),
                UserProgress.completion_status == "completed"
            ).count()
            
            path.completion_rate = completed_count / total_topics if total_topics > 0 else 0.0
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error updating completion rates: {str(e)}")

@router.delete("/{path_id}")
async def delete_learning_path(
    path_id: int,
    db: Session = Depends(get_db)
):
    """Delete a learning path"""
    try:
        path = db.query(LearningPath).filter(LearningPath.id == path_id).first()
        
        if not path:
            raise HTTPException(status_code=404, detail="Learning path not found")
        
        db.delete(path)
        db.commit()
        
        return {"message": "Learning path deleted successfully", "path_id": path_id}
        
    except Exception as e:
        logger.error(f"Error deleting learning path: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
