from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, Dict, List
import redis.asyncio as redis
import uuid
import json
from datetime import datetime

from ..services.difficulty_service import ProgressiveDifficultyService
from ..services.google_ai_service import GoogleAIService
from ..models.difficulty import Question

router = APIRouter(prefix="/api/difficulty", tags=["difficulty"])

# Pydantic models
class QuestionResponse(BaseModel):
    id: int
    content: str
    options: Optional[str] = None
    correct_answer: Optional[str] = None
    difficulty_score: float
    category: Optional[str] = None
    
    class Config:
        from_attributes = True

class AnswerResponse(BaseModel):
    question_id: int
    correct_answer: str
    explanation: Optional[str] = None

class NextQuestionRequest(BaseModel):
    user_id: str
    session_id: str
    last_response: Optional[Dict] = None

class NextQuestionResponse(BaseModel):
    question: Optional[QuestionResponse]
    target_difficulty: float
    performance_analytics: Dict

class SubmitResponseRequest(BaseModel):
    user_id: str
    session_id: str
    question_id: int
    user_answer: str
    is_correct: bool
    response_time_ms: int

class GenerateQuestionRequest(BaseModel):
    category: str
    difficulty: float
    topic: Optional[str] = None

class GenerateQuestionResponse(BaseModel):
    content: str
    options: List[str]
    correct_answer: str
    difficulty_score: float
    category: str
    explanation: Optional[str] = None

# Dependency functions
def get_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os
    
    database_url = os.getenv('DATABASE_URL', 'postgresql://quiz_user:quiz_pass@db:5432/quiz_db')
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def get_redis():
    import os
    redis_url = os.getenv('REDIS_URL', 'redis://redis:6379/0')
    return redis.from_url(redis_url)

@router.post("/next-question", response_model=NextQuestionResponse)
async def get_next_question(
    request: NextQuestionRequest,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Get the next optimal question for user based on progressive difficulty"""
    try:
        service = ProgressiveDifficultyService(db, redis_client)
        
        question, target_difficulty = await service.get_next_question_for_user(
            user_id=request.user_id,
            session_id=request.session_id,
            last_response=request.last_response
        )
        
        if not question:
            raise HTTPException(status_code=404, detail="No suitable questions found")
        
        # Get performance analytics
        analytics = await service.get_performance_analytics(
            request.user_id, request.session_id
        )
        
        # Don't include the answer in the question response
        question_response = QuestionResponse(
            id=question.id,
            content=question.content,
            options=question.options,
            correct_answer=None,  # Hide the answer
            difficulty_score=question.difficulty_score,
            category=question.category
        )
        
        return NextQuestionResponse(
            question=question_response,
            target_difficulty=target_difficulty,
            performance_analytics=analytics
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/question/{question_id}/answer", response_model=AnswerResponse)
async def get_question_answer(
    question_id: int,
    db: Session = Depends(get_db)
):
    """Get the answer for a specific question"""
    try:
        question = db.query(Question).filter(Question.id == question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        return AnswerResponse(
            question_id=question.id,
            correct_answer=question.correct_answer,
            explanation=None  # Could be added to the model later
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/generate-question", response_model=GenerateQuestionResponse)
async def generate_question(
    request: GenerateQuestionRequest,
    db: Session = Depends(get_db)
):
    """Generate a new question using Google AI"""
    try:
        ai_service = GoogleAIService()
        question_data = await ai_service.generate_question(
            category=request.category,
            difficulty=request.difficulty,
            topic=request.topic
        )
        
        # Save the generated question to database
        question = Question(
            content=question_data['content'],
            options=json.dumps(question_data['options']),
            correct_answer=question_data['correct_answer'],
            difficulty_score=question_data['difficulty_score'],
            category=question_data['category']
        )
        db.add(question)
        db.commit()
        db.refresh(question)
        
        return GenerateQuestionResponse(
            content=question_data['content'],
            options=question_data['options'],
            correct_answer=question_data['correct_answer'],
            difficulty_score=question_data['difficulty_score'],
            category=question_data['category'],
            explanation=question_data.get('explanation')
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating question: {str(e)}")

@router.post("/submit-response")
async def submit_response(
    request: SubmitResponseRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Submit user response and update performance metrics"""
    try:
        service = ProgressiveDifficultyService(db, redis_client)
        
        # Get question to determine difficulty at time of response
        question = db.query(Question).filter(Question.id == request.question_id).first()
        if not question:
            raise HTTPException(status_code=404, detail="Question not found")
        
        # Record response in background
        background_tasks.add_task(
            service.record_response,
            user_id=request.user_id,
            session_id=request.session_id,
            question_id=request.question_id,
            user_answer=request.user_answer,
            is_correct=request.is_correct,
            response_time_ms=request.response_time_ms,
            difficulty_at_time=question.difficulty_score
        )
        
        return {"status": "success", "message": "Response recorded"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/analytics/{user_id}/{session_id}")
async def get_performance_analytics(
    user_id: str,
    session_id: str,
    db: Session = Depends(get_db),
    redis_client: redis.Redis = Depends(get_redis)
):
    """Get detailed performance analytics for user session"""
    try:
        service = ProgressiveDifficultyService(db, redis_client)
        analytics = await service.get_performance_analytics(user_id, session_id)
        return analytics
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.post("/create-session")
async def create_session(
    user_id: str,
    db: Session = Depends(get_db)
):
    """Create a new quiz session for user"""
    session_id = str(uuid.uuid4())
    return {"session_id": session_id, "user_id": user_id}
