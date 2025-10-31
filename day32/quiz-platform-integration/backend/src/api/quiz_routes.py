from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from database.connection import get_db
from services.quiz_service import QuizService
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()
quiz_service = QuizService()

class QuizCreate(BaseModel):
    title: str
    description: str
    creator_id: int

class QuizResponse(BaseModel):
    id: int
    title: str
    description: str
    creator_id: int
    created_at: str

class GenerateQuestionsRequest(BaseModel):
    topic: str
    count: int = 5

@router.post("/", response_model=QuizResponse)
async def create_quiz(quiz_data: QuizCreate, db: AsyncSession = Depends(get_db)):
    return await quiz_service.create_quiz(
        db, quiz_data.title, quiz_data.description, quiz_data.creator_id
    )

@router.get("/{quiz_id}")
async def get_quiz(quiz_id: int, db: AsyncSession = Depends(get_db)):
    quiz = await quiz_service.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("/{quiz_id}/questions")
async def generate_and_add_questions(
    quiz_id: int, 
    request: GenerateQuestionsRequest, 
    db: AsyncSession = Depends(get_db)
):
    # Verify quiz exists
    quiz = await quiz_service.get_quiz(db, quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Generate questions
    questions = await quiz_service.generate_questions(request.topic, request.count)
    
    # Add to quiz
    await quiz_service.add_questions_to_quiz(db, quiz_id, questions)
    
    return {"message": f"Added {len(questions)} questions to quiz"}

@router.delete("/{quiz_id}")
async def delete_quiz(quiz_id: int, db: AsyncSession = Depends(get_db)):
    success = await quiz_service.delete_quiz(db, quiz_id)
    if not success:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {"message": "Quiz deleted successfully"}
