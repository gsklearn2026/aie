from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.services.quiz_service import QuizService

router = APIRouter()
quiz_service = QuizService()

class QuizRequest(BaseModel):
    topic: str
    num_questions: int = 5

class AnswerRequest(BaseModel):
    question_id: int
    user_answer: int
    correct_answer: int

@router.post("/generate")
async def generate_quiz(request: QuizRequest):
    """Generate quiz questions"""
    try:
        result = await quiz_service.generate_quiz(
            topic=request.topic,
            num_questions=request.num_questions
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/grade")
async def grade_answer(request: AnswerRequest):
    """Grade a quiz answer"""
    result = await quiz_service.grade_answer(
        question_id=request.question_id,
        user_answer=request.user_answer,
        correct_answer=request.correct_answer
    )
    return result
