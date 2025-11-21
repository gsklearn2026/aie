from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.cache import cache_manager
from app.models.quiz import Quiz
from app.services.ai_service import AIService
from app.services.fallback_quiz_generator import generate_fallback_quiz
from app.monitoring import cache_hits, cache_misses
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/quizzes", tags=["quizzes"])
ai_service = AIService()

class QuizCreate(BaseModel):
    topic: str
    num_questions: int = 5
    difficulty: str = "medium"
    category: Optional[str] = None

class QuizResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: Optional[str]
    difficulty: str
    questions: list
    total_questions: int
    created_at: str

@router.post("/generate", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
async def generate_quiz(
    quiz_data: QuizCreate,
    db: AsyncSession = Depends(get_db)
):
    """Generate a new quiz using AI, with fallback to template-based generation"""
    questions = None
    use_fallback = False
    
    try:
        # Try to generate questions using AI
        questions = await ai_service.generate_quiz(
            quiz_data.topic,
            quiz_data.num_questions
        )
        logger.info(f"Successfully generated quiz using AI for topic: {quiz_data.topic}")
    except (ValueError, Exception) as e:
        # Check if it's a quota error - use fallback
        error_msg = str(e)
        if error_msg.startswith("QUOTA_ERROR:") or "429" in error_msg or "quota exceeded" in error_msg.lower():
            logger.warning(f"AI quota exceeded, using fallback generator for topic: {quiz_data.topic}")
            use_fallback = True
            # Generate using fallback
            questions = generate_fallback_quiz(quiz_data.topic, quiz_data.num_questions)
        else:
            # For other errors, re-raise to be handled by error handler below
            raise
    
    # Ensure we have questions (fallback should have generated them)
    if not questions:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Quiz generation failed",
                "message": "Unable to generate quiz questions. Please try again later."
            }
        )
    
    # Create quiz record
    try:
        quiz = Quiz(
            title=f"{quiz_data.topic} Quiz",
            description=f"{'Template-based' if use_fallback else 'AI-generated'} quiz about {quiz_data.topic}",
            category=quiz_data.category or quiz_data.topic,
            difficulty=quiz_data.difficulty,
            questions=questions,
            total_questions=len(questions)
        )
        
        db.add(quiz)
        await db.commit()
        await db.refresh(quiz)
        
        # Cache the quiz
        await cache_manager.set(f"quiz:{quiz.id}", quiz.to_dict(), ttl=3600)
        
        return quiz.to_dict()
    except Exception as db_error:
        logger.error(f"Database error creating quiz: {db_error}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Database error",
                "message": "Failed to save quiz. Please try again."
            }
        )

@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(
    quiz_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get quiz by ID with caching"""
    # Check cache first
    cache_key = f"quiz:{quiz_id}"
    cached_quiz = await cache_manager.get(cache_key)
    
    if cached_quiz:
        cache_hits.inc()
        return cached_quiz
    
    cache_misses.inc()
    
    # Fetch from database
    result = await db.execute(
        select(Quiz).where(Quiz.id == quiz_id, Quiz.is_active == True)
    )
    quiz = result.scalar_one_or_none()
    
    if not quiz:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quiz not found"
        )
    
    quiz_dict = quiz.to_dict()
    await cache_manager.set(cache_key, quiz_dict, ttl=3600)
    
    return quiz_dict

@router.get("/", response_model=List[QuizResponse])
async def list_quizzes(
    skip: int = 0,
    limit: int = 10,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List quizzes with pagination and filtering"""
    query = select(Quiz).where(Quiz.is_active == True)
    
    if category:
        query = query.where(Quiz.category == category)
    
    query = query.offset(skip).limit(limit).order_by(Quiz.created_at.desc())
    
    result = await db.execute(query)
    quizzes = result.scalars().all()
    
    return [quiz.to_dict() for quiz in quizzes]
