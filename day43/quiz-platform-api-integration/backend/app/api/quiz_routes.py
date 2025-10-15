"""Quiz API routes with integration layer"""
import uuid
from fastapi import APIRouter, HTTPException, Depends, Request, BackgroundTasks
from typing import List, Dict, Any
import structlog
from ..models.quiz import QuizQuestion, QuizResponse, QuizResult, APIResponse
from ..services.cache_service import CacheService
from ..services.ai_service import AIService

logger = structlog.get_logger()
router = APIRouter()

def get_cache_service(request: Request) -> CacheService:
    """Get cache service dependency"""
    return request.app.state.cache_service

def get_ai_service(request: Request) -> AIService:
    """Get AI service dependency"""
    return request.app.state.ai_service

@router.post("/generate", response_model=APIResponse)
async def generate_quiz(
    topic: str,
    difficulty: str = "medium",
    count: int = 5,
    cache_service: CacheService = Depends(get_cache_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate quiz questions with caching"""
    request_id = str(uuid.uuid4())
    cache_key = f"quiz:{topic}:{difficulty}:{count}"
    
    logger.info("Quiz generation request", 
                request_id=request_id, 
                topic=topic, 
                difficulty=difficulty, 
                count=count)
    
    try:
        # Check cache first
        cached_questions = await cache_service.get(cache_key)
        if cached_questions:
            logger.info("Returning cached quiz questions", request_id=request_id)
            return APIResponse(
                success=True,
                data=cached_questions,
                request_id=request_id
            )
        
        # Generate new questions
        questions = await ai_service.generate_quiz_questions(topic, difficulty, count)
        questions_data = [q.dict() for q in questions]
        
        # Cache the result
        await cache_service.set(cache_key, questions_data, ttl=3600)
        
        logger.info("Quiz questions generated successfully", 
                   request_id=request_id, 
                   questions_count=len(questions))
        
        return APIResponse(
            success=True,
            data=questions_data,
            request_id=request_id
        )
        
    except Exception as e:
        logger.error("Quiz generation failed", 
                    request_id=request_id, 
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate quiz: {str(e)}"
        )

@router.post("/submit", response_model=APIResponse)
async def submit_quiz_response(
    response: QuizResponse,
    cache_service: CacheService = Depends(get_cache_service),
    ai_service: AIService = Depends(get_ai_service)
):
    """Submit quiz response and get validation"""
    request_id = str(uuid.uuid4())
    
    logger.info("Quiz response submission", 
                request_id=request_id,
                question_id=response.question_id,
                user_id=response.user_id)
    
    try:
        # Extract topic and difficulty from question ID to find the quiz cache
        question_id_parts = response.question_id.split('_')
        if len(question_id_parts) >= 3:
            topic = question_id_parts[1]
            difficulty = question_id_parts[2]
            
            # Try to find the question in quiz cache - check multiple possible counts
            quiz_data = None
            for count in [3, 5, 10]:  # Common quiz sizes
                quiz_cache_key = f"quiz:{topic}:{difficulty}:{count}"
                quiz_data = await cache_service.get(quiz_cache_key)
                if quiz_data:
                    break
            
            if quiz_data:
                # Find the specific question in the quiz data
                question_data = None
                for q in quiz_data:
                    if q.get('id') == response.question_id:
                        question_data = q
                        break
                
                if question_data:
                    question = QuizQuestion(**question_data)
                    validation = await ai_service.validate_answer(question, response.selected_answer)
                else:
                    logger.warning("Question not found in quiz cache", 
                                  request_id=request_id,
                                  question_id=response.question_id)
                    return APIResponse(
                        success=False,
                        error="Question not found in quiz",
                        request_id=request_id
                    )
            else:
                logger.warning("Quiz not found in cache", 
                              request_id=request_id,
                              question_id=response.question_id)
                return APIResponse(
                    success=False,
                    error="Quiz not found",
                    request_id=request_id
                )
        else:
            logger.warning("Invalid question ID format", 
                          request_id=request_id,
                          question_id=response.question_id)
            return APIResponse(
                success=False,
                error="Invalid question ID",
                request_id=request_id
            )
        
        # Store response in cache
        response_key = f"response:{response.user_id}:{response.question_id}"
        await cache_service.set(response_key, response.dict(), ttl=86400)  # 24 hours
        
        logger.info("Quiz response processed", 
                   request_id=request_id,
                   correct=validation["correct"])
        
        return APIResponse(
            success=True,
            data=validation,
            request_id=request_id
        )
        
    except Exception as e:
        logger.error("Quiz response processing failed", 
                    request_id=request_id, 
                    error=str(e))
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process response: {str(e)}"
        )
