from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from ....services.version_analytics import analytics_service

router = APIRouter(prefix="/quiz", tags=["quiz-v1"])

class QuestionV1(BaseModel):
    id: Optional[str] = None
    question: str
    options: List[str]
    correct_answer: int
    points: int = 1

class QuizV1(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    questions: List[QuestionV1]
    time_limit: Optional[int] = None
    created_at: Optional[datetime] = None

# In-memory storage for demo
quizzes_db = {}

@router.post("/create", response_model=QuizV1)
async def create_quiz_v1(quiz: QuizV1, request: Request):
    """Create a new quiz - V1 endpoint"""
    # Record analytics
    await analytics_service.record_usage(
        version="v1",
        endpoint="/api/v1/quiz/create",
        user_agent=request.headers.get("user-agent", "unknown"),
        client_ip=request.client.host
    )
    
    quiz.id = str(uuid.uuid4())
    quiz.created_at = datetime.now()
    
    # Assign IDs to questions
    for i, question in enumerate(quiz.questions):
        question.id = f"{quiz.id}_q{i}"
    
    quizzes_db[quiz.id] = quiz.dict()
    
    return quiz

@router.get("/list")
async def list_quizzes_v1(request: Request):
    """List all quizzes - V1 endpoint"""
    # Record analytics
    await analytics_service.record_usage(
        version="v1",
        endpoint="/api/v1/quiz/list",
        user_agent=request.headers.get("user-agent", "unknown"),
        client_ip=request.client.host
    )
    
    return {
        "quizzes": [
            {
                "id": quiz_id,
                "title": quiz_data["title"],
                "description": quiz_data["description"],
                "question_count": len(quiz_data["questions"]),
                "created_at": quiz_data["created_at"]
            }
            for quiz_id, quiz_data in quizzes_db.items()
        ]
    }

@router.get("/{quiz_id}")
async def get_quiz_v1(quiz_id: str, request: Request):
    """Get specific quiz - V1 endpoint"""
    # Record analytics
    await analytics_service.record_usage(
        version="v1",
        endpoint=f"/api/v1/quiz/{quiz_id}",
        user_agent=request.headers.get("user-agent", "unknown"),
        client_ip=request.client.host
    )
    
    if quiz_id not in quizzes_db:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    return quizzes_db[quiz_id]

@router.delete("/{quiz_id}")
async def delete_quiz_v1(quiz_id: str, request: Request):
    """Delete quiz - V1 endpoint"""
    # Record analytics
    await analytics_service.record_usage(
        version="v1",
        endpoint=f"/api/v1/quiz/{quiz_id}",
        user_agent=request.headers.get("user-agent", "unknown"),
        client_ip=request.client.host
    )
    
    if quiz_id not in quizzes_db:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    del quizzes_db[quiz_id]
    return {"message": "Quiz deleted successfully"}
