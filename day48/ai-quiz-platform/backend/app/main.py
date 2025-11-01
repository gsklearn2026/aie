from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import os
import asyncio
import logging
from tenacity import retry, stop_after_attempt, wait_exponential
from pydantic import BaseModel
from typing import Optional, List
import json
import time
import traceback

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Quiz Platform", version="1.0.0")

# CORS configuration - allow common development origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Gemini AI
genai.configure(api_key="AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8")

class ErrorResponse(BaseModel):
    error: str
    error_code: str
    message: str
    timestamp: float
    request_id: Optional[str] = None

class QuizRequest(BaseModel):
    topic: str
    difficulty: str = "medium"
    num_questions: int = 5

class QuizResponse(BaseModel):
    questions: List[dict]
    quiz_id: str
    topic: str
    difficulty: str
    generated_at: float

# Global error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {str(exc)}")
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="internal_server_error",
            error_code="ISE_001",
            message="An unexpected error occurred. Please try again.",
            timestamp=time.time(),
            request_id=getattr(request.state, 'request_id', None)
        ).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error="http_error",
            error_code=f"HTTP_{exc.status_code}",
            message=exc.detail,
            timestamp=time.time(),
            request_id=getattr(request.state, 'request_id', None)
        ).dict()
    )

@retry(stop=stop_after_attempt(2), wait=wait_exponential(multiplier=1, min=2, max=5))
async def generate_quiz_with_retry(topic: str, difficulty: str, num_questions: int):
    """Generate quiz with exponential backoff retry"""
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""
        Generate a {difficulty} difficulty quiz about {topic} with {num_questions} multiple choice questions.
        Return ONLY valid JSON in this exact format:
        {{
            "questions": [
                {{
                    "question": "Question text here?",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": 0,
                    "explanation": "Brief explanation"
                }}
            ]
        }}
        """
        
        response = model.generate_content(prompt)
        
        # Get response text - the API returns a response object with a .text attribute
        if not hasattr(response, 'text') or not response.text:
            # Fallback: try to get text from candidates if available
            if hasattr(response, 'candidates') and response.candidates:
                if len(response.candidates) > 0 and hasattr(response.candidates[0], 'content'):
                    if hasattr(response.candidates[0].content, 'parts') and response.candidates[0].content.parts:
                        response_text = response.candidates[0].content.parts[0].text
                    else:
                        raise Exception("Empty response from Gemini AI - no content parts")
                else:
                    raise Exception("Empty response from Gemini AI - invalid candidate structure")
            else:
                logger.error(f"Unexpected response structure. Available attributes: {[x for x in dir(response) if not x.startswith('_')]}")
                raise Exception("Empty or unexpected response from Gemini AI")
        else:
            response_text = response.text
        
        if not response_text or not response_text.strip():
            raise Exception("Empty response from Gemini AI")
            
        # Clean and parse JSON
        json_text = response_text.strip()
        if json_text.startswith('```json'):
            json_text = json_text[7:].strip()
            if json_text.endswith('```'):
                json_text = json_text[:-3].strip()
        elif json_text.startswith('```'):
            json_text = json_text[3:].strip()
            if json_text.endswith('```'):
                json_text = json_text[:-3].strip()
            
        quiz_data = json.loads(json_text)
        
        if 'questions' not in quiz_data or not quiz_data['questions']:
            raise Exception("Invalid quiz format received")
            
        return quiz_data
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        logger.error(f"Response text was: {json_text[:500] if 'json_text' in locals() else 'N/A'}")
        raise HTTPException(
            status_code=502, 
            detail="Invalid response format from AI service"
        )
    except AttributeError as e:
        logger.error(f"Attribute error accessing Gemini response: {str(e)}")
        logger.error(f"Response object: {type(response)}")
        raise HTTPException(
            status_code=502,
            detail="AI service returned an unexpected response format"
        )
    except Exception as e:
        logger.error(f"Gemini API error: {str(e)}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        if "quota" in str(e).lower() or "rate limit" in str(e).lower():
            raise HTTPException(
                status_code=429,
                detail="AI service temporarily unavailable. Please try again in a moment."
            )
        raise HTTPException(
            status_code=502,
            detail="AI service error. Please try again."
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "ai-quiz-platform"
    }

@app.post("/api/generate-quiz", response_model=QuizResponse)
async def generate_quiz(request: QuizRequest):
    """Generate quiz with comprehensive error handling"""
    try:
        logger.info(f"Generating quiz: topic={request.topic}, difficulty={request.difficulty}")
        
        # Validate input
        if not request.topic or len(request.topic.strip()) < 2:
            raise HTTPException(
                status_code=400,
                detail="Topic must be at least 2 characters long"
            )
            
        if request.num_questions < 1 or request.num_questions > 20:
            raise HTTPException(
                status_code=400,
                detail="Number of questions must be between 1 and 20"
            )
        
        # Generate quiz with retry logic
        quiz_data = await generate_quiz_with_retry(
            request.topic, 
            request.difficulty, 
            request.num_questions
        )
        
        quiz_id = f"quiz_{int(time.time())}"
        
        # Store quiz in memory for answer validation
        quiz_storage[quiz_id] = {
            'questions': quiz_data['questions'],
            'topic': request.topic,
            'difficulty': request.difficulty
        }
        
        response = QuizResponse(
            questions=quiz_data['questions'],
            quiz_id=quiz_id,
            topic=request.topic,
            difficulty=request.difficulty,
            generated_at=time.time()
        )
        
        logger.info(f"Successfully generated quiz {quiz_id}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in generate_quiz: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to generate quiz. Please try again."
        )

# In-memory quiz storage (for answer validation)
# In production, use a proper database
quiz_storage = {}

@app.post("/api/submit-answer")
async def submit_answer(answer_data: dict):
    """Submit quiz answer with error handling"""
    try:
        # Simulate processing time
        await asyncio.sleep(0.3)
        
        required_fields = ['quiz_id', 'question_index', 'selected_answer']
        for field in required_fields:
            if field not in answer_data:
                raise HTTPException(
                    status_code=400,
                    detail=f"Missing required field: {field}"
                )
        
        quiz_id = answer_data.get('quiz_id')
        question_index = answer_data.get('question_index')
        selected_answer = answer_data.get('selected_answer')
        
        # Get quiz from storage (if available) or use provided correct_answer
        is_correct = False
        explanation = "Answer submitted."
        
        # If correct_answer is provided in the request, use it
        if 'correct_answer' in answer_data:
            correct_answer = answer_data.get('correct_answer')
            is_correct = selected_answer == correct_answer
        elif quiz_id in quiz_storage:
            # Check from stored quiz
            quiz = quiz_storage[quiz_id]
            if question_index < len(quiz.get('questions', [])):
                correct_answer = quiz['questions'][question_index].get('correct_answer')
                is_correct = selected_answer == correct_answer
                explanation = quiz['questions'][question_index].get('explanation', 'Answer submitted.')
        else:
            # Fallback: cannot verify, assume incorrect for safety
            logger.warning(f"Quiz {quiz_id} not found in storage, cannot verify answer")
            is_correct = False
        
        return {
            "correct": is_correct,
            "explanation": explanation,
            "score": 10 if is_correct else 0,
            "timestamp": time.time()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting answer: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process answer. Please try again."
        )

@app.get("/api/analytics/{quiz_id}")
async def get_quiz_analytics(quiz_id: str):
    """Get quiz analytics with error handling"""
    try:
        if not quiz_id:
            raise HTTPException(
                status_code=400,
                detail="Quiz ID is required"
            )
        
        # Simulate analytics data
        analytics = {
            "quiz_id": quiz_id,
            "total_questions": 5,
            "correct_answers": 3,
            "accuracy": 60.0,
            "time_spent": 180,
            "difficulty_breakdown": {
                "easy": 2,
                "medium": 2,
                "hard": 1
            },
            "performance_trend": [20, 40, 60, 80, 60],
            "generated_at": time.time()
        }
        
        return analytics
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching analytics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to load analytics. Please try again."
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
