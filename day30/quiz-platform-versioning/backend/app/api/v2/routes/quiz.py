from fastapi import APIRouter, Request, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime
from ....services.version_compatibility import VersionCompatibilityService
from ....services.version_analytics import analytics_service

router = APIRouter(prefix="/quiz", tags=["quiz-v2"])

class QuestionV2(BaseModel):
    id: Optional[str] = None
    question: str
    options: List[str]
    correct_answer: int
    points: int = 1
    difficulty_level: int = 5  # 1-10 scale
    cognitive_load: str = "medium"  # low, medium, high
    hint: Optional[str] = None

class QuizV2(BaseModel):
    id: Optional[str] = None
    title: str
    description: str
    questions: List[QuestionV2]
    time_limit: Optional[int] = None
    ai_difficulty_score: float = 5.0  # 1-10 AI-calculated difficulty
    ai_tags: List[str] = []
    estimated_duration: int = 0  # minutes
    adaptive_scoring: bool = False
    created_at: Optional[datetime] = None

# Import v1 database for compatibility
from ...v1.routes.quiz import quizzes_db

compatibility_service = VersionCompatibilityService()

@router.post("/create", response_model=QuizV2)
async def create_quiz_v2(quiz: QuizV2, request: Request):
    """Create a new quiz - V2 endpoint with AI enhancements"""
    # Record analytics
    await analytics_service.record_usage(
        version="v2",
        endpoint="/api/v2/quiz/create",
        user_agent=request.headers.get("user-agent", "unknown"),
        client_ip=request.client.host
    )
    
    quiz.id = str(uuid.uuid4())
    quiz.created_at = datetime.now()
    
    # Auto-calculate AI features if not provided
    if not quiz.ai_tags:
        quiz.ai_tags = compatibility_service.generate_ai_tags(
            quiz.title, 
            [q.dict() for q in quiz.questions]
        )
    
    if quiz.ai_difficulty_score == 5.0:  # Default value
        quiz.ai_difficulty_score = compatibility_service.calculate_ai_difficulty(
            [q.dict() for q in quiz.questions]
        )
    
    if quiz.estimated_duration == 0:
        quiz.estimated_duration = len(quiz.questions) * 90  # 1.5 min per question
    
    # Assign IDs to questions and enhance with AI
    for i, question in enumerate(quiz.questions):
        question.id = f"{quiz.id}_q{i}"
        if question.difficulty_level == 5:  # Default
            question.difficulty_level = compatibility_service.estimate_question_difficulty(
                question.dict()
            )
        if not question.hint:
            question.hint = compatibility_service.generate_hint(question.dict())
        if question.cognitive_load == "medium":  # Default
            question.cognitive_load = compatibility_service.calculate_cognitive_load(
                question.dict()
            )
    
    quizzes_db[quiz.id] = quiz.dict()
    
    return quiz

@router.get("/list")
async def list_quizzes_v2(request: Request):
    """List all quizzes - V2 endpoint with AI metadata"""
    # Record analytics
    await analytics_service.record_usage(
        version="v2",
        endpoint="/api/v2/quiz/list",
        user_agent=request.headers.get("user-agent", "unknown"),
        client_ip=request.client.host
    )
    enhanced_quizzes = []
    
    for quiz_id, quiz_data in quizzes_db.items():
        # Convert v1 data to v2 if needed
        if "ai_difficulty_score" not in quiz_data:
            quiz_data = compatibility_service.adapt_response(
                quiz_data, "v1", "v2", "quiz_response"
            )
        
        enhanced_quizzes.append({
            "id": quiz_id,
            "title": quiz_data["title"],
            "description": quiz_data["description"],
            "question_count": len(quiz_data["questions"]),
            "ai_difficulty_score": quiz_data.get("ai_difficulty_score", 5.0),
            "ai_tags": quiz_data.get("ai_tags", []),
            "estimated_duration": quiz_data.get("estimated_duration", 0),
            "created_at": quiz_data["created_at"]
        })
    
    return {"quizzes": enhanced_quizzes}

@router.get("/{quiz_id}")
async def get_quiz_v2(quiz_id: str, request: Request):
    """Get specific quiz - V2 endpoint with full AI features"""
    # Record analytics
    await analytics_service.record_usage(
        version="v2",
        endpoint=f"/api/v2/quiz/{quiz_id}",
        user_agent=request.headers.get("user-agent", "unknown"),
        client_ip=request.client.host
    )
    
    if quiz_id not in quizzes_db:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_data = quizzes_db[quiz_id]
    
    # Convert v1 data to v2 format if needed
    if "ai_difficulty_score" not in quiz_data:
        quiz_data = compatibility_service.adapt_response(
            quiz_data, "v1", "v2", "quiz_response"
        )
    
    return quiz_data

@router.delete("/{quiz_id}")
async def delete_quiz_v2(quiz_id: str, request: Request):
    """Delete quiz - V2 endpoint"""
    # Record analytics
    await analytics_service.record_usage(
        version="v2",
        endpoint=f"/api/v2/quiz/{quiz_id}",
        user_agent=request.headers.get("user-agent", "unknown"),
        client_ip=request.client.host
    )
    
    if quiz_id not in quizzes_db:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    del quizzes_db[quiz_id]
    return {
        "message": "Quiz deleted successfully",
        "deleted_at": datetime.now().isoformat(),
        "cleanup_status": "complete"
    }

@router.get("/{quiz_id}/analytics")
async def get_quiz_analytics_v2(quiz_id: str, request: Request):
    """Get quiz analytics - V2 only feature"""
    # Record analytics
    await analytics_service.record_usage(
        version="v2",
        endpoint=f"/api/v2/quiz/{quiz_id}/analytics",
        user_agent=request.headers.get("user-agent", "unknown"),
        client_ip=request.client.host
    )
    
    if quiz_id not in quizzes_db:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz_data = quizzes_db[quiz_id]
    
    return {
        "quiz_id": quiz_id,
        "title": quiz_data["title"],
        "total_questions": len(quiz_data["questions"]),
        "avg_difficulty": quiz_data.get("ai_difficulty_score", 5.0),
        "difficulty_distribution": {
            "easy": sum(1 for q in quiz_data["questions"] 
                       if q.get("difficulty_level", 5) <= 3),
            "medium": sum(1 for q in quiz_data["questions"] 
                         if 4 <= q.get("difficulty_level", 5) <= 7),
            "hard": sum(1 for q in quiz_data["questions"] 
                       if q.get("difficulty_level", 5) >= 8)
        },
        "cognitive_load_distribution": {
            load: sum(1 for q in quiz_data["questions"] 
                     if q.get("cognitive_load", "medium") == load)
            for load in ["low", "medium", "high"]
        }
    }
