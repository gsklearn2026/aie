from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.models.database import get_db
from app.services.question_service import QuestionService
from app.services.curation_service import CurationService
from app.schemas.schemas import QuestionCreate, QuestionResponse, CurationResponse

router = APIRouter()

@router.post("/generate", response_model=CurationResponse)
async def generate_question(
    topic: str,
    difficulty: str = "medium",
    db: AsyncSession = Depends(get_db)
):
    """Generate a new question and submit for curation"""
    question_service = QuestionService(db)
    curation_service = CurationService(db)
    
    try:
        question, metrics = await question_service.generate_question(topic, difficulty)
        curation = await curation_service.submit_for_curation(question.id, metrics)
        
        # Reload with question relationship
        curation = await curation_service.get_curation(curation.id)
        return curation
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/regenerate/{question_id}", response_model=CurationResponse)
async def regenerate_question(
    question_id: str,
    feedback: str,
    db: AsyncSession = Depends(get_db)
):
    """Regenerate question with feedback and submit for curation"""
    question_service = QuestionService(db)
    curation_service = CurationService(db)
    
    try:
        question, metrics = await question_service.regenerate_with_feedback(question_id, feedback)
        curation = await curation_service.submit_for_curation(question.id, metrics)
        curation = await curation_service.get_curation(curation.id)
        return curation
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/approved", response_model=list[QuestionResponse])
async def get_approved_questions(
    topic: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all approved questions"""
    service = QuestionService(db)
    return await service.get_approved_questions(topic)

@router.get("/{question_id}", response_model=QuestionResponse)
async def get_question(
    question_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get question by ID"""
    service = QuestionService(db)
    question = await service.get_question(question_id)
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")
    return question
