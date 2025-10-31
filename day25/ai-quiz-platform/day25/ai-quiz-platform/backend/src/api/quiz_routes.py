from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from src.services.ai_service import AIService
from src.models.errors import ErrorType, ErrorContext
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/api/quiz", tags=["quiz"])

# Dependency injection
def get_ai_service():
    return AIService()

@router.post("/generate")
async def generate_quiz(
    topic: str,
    difficulty: str = "medium",
    count: int = 5,
    ai_service: AIService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """Generate quiz questions with error handling"""
    
    try:
        # Validate inputs
        if not topic or len(topic.strip()) == 0:
            raise HTTPException(status_code=400, detail="Topic is required")
        
        if count < 1 or count > 20:
            raise HTTPException(status_code=400, detail="Question count must be between 1 and 20")
        
        # Generate questions
        questions = await ai_service.generate_quiz_questions(topic, difficulty, count)
        
        return {
            "success": True,
            "data": {
                "questions": questions,
                "topic": topic,
                "difficulty": difficulty,
                "generated_count": len(questions)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate quiz", error=str(e), topic=topic)
        raise HTTPException(status_code=500, detail="Failed to generate quiz questions")

@router.get("/health")
async def health_check(ai_service: AIService = Depends(get_ai_service)):
    """Health check endpoint with service status"""
    
    circuit_breaker_status = ai_service.get_circuit_breaker_status()
    
    return {
        "status": "healthy",
        "timestamp": "2025-08-14T10:30:00Z",
        "services": {
            "ai_service": {
                "status": "up" if circuit_breaker_status["state"] == "closed" else "degraded",
                "circuit_breaker": circuit_breaker_status
            }
        }
    }

from pydantic import BaseModel

class QuizSubmission(BaseModel):
    quiz_id: str
    answers: List[Dict[str, Any]]

@router.post("/submit")
async def submit_quiz(
    submission: QuizSubmission
) -> Dict[str, Any]:
    """Submit quiz answers with validation"""
    
    try:
        if not submission.quiz_id:
            raise HTTPException(status_code=400, detail="Quiz ID is required")
        
        if not submission.answers:
            raise HTTPException(status_code=400, detail="Answers are required")
        
        # Simulate scoring logic
        score = len(submission.answers) * 0.8  # 80% for demo
        
        return {
            "success": True,
            "data": {
                "quiz_id": submission.quiz_id,
                "score": score,
                "total_questions": len(submission.answers),
                "percentage": (score / len(submission.answers)) * 100
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit quiz", error=str(e), quiz_id=submission.quiz_id)
        raise HTTPException(status_code=500, detail="Failed to process quiz submission")
