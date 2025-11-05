from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from ..database.base import get_db
from ..services.optimized_queries import OptimizedQueries
from ..models.models import Quiz, Question

router = APIRouter(prefix="/api/quizzes", tags=["quizzes"])

class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: str
    difficulty: str
    question_count: int
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[QuizResponse])
def get_quizzes(category: Optional[str] = None, db: Session = Depends(get_db)):
    """Get all quizzes with questions (OPTIMIZED)"""
    queries = OptimizedQueries(db)
    quizzes = queries.get_quizzes_with_questions(category)
    
    return [
        QuizResponse(
            id=q.id,
            title=q.title,
            description=q.description,
            category=q.category,
            difficulty=q.difficulty,
            question_count=len(q.questions)
        )
        for q in quizzes
    ]

@router.get("/{quiz_id}/statistics")
def get_quiz_statistics(quiz_id: int, db: Session = Depends(get_db)):
    """Get quiz statistics (OPTIMIZED)"""
    queries = OptimizedQueries(db)
    return queries.get_quiz_statistics(quiz_id)

@router.get("/leaderboard")
def get_leaderboard(quiz_id: Optional[int] = None, limit: int = 10, db: Session = Depends(get_db)):
    """Get leaderboard (OPTIMIZED)"""
    queries = OptimizedQueries(db)
    leaders = queries.get_leaderboard(quiz_id, limit)
    
    return {
        'leaderboard': [
            {
                'username': l[0],
                'average_score': round(l[1], 2),
                'attempts': l[2]
            }
            for l in leaders
        ]
    }
