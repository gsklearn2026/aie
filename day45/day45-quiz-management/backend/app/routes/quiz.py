from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime
from ..models.database import get_db, Quiz, User
from .auth import get_current_user

router = APIRouter()

class QuestionCreate(BaseModel):
    text: str
    type: str  # multiple_choice, true_false, text
    options: Optional[List[str]] = None
    correct_answer: str

class QuizCreate(BaseModel):
    title: str
    description: str
    questions: List[QuestionCreate]
    tags: Optional[List[str]] = None

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    questions: Optional[List[QuestionCreate]] = None
    tags: Optional[List[str]] = None

class QuizResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    title: str
    description: str
    questions: List[dict]
    created_by: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    view_count: int
    tags: Optional[List[str]]

@router.post("/", response_model=QuizResponse)
async def create_quiz(quiz: QuizCreate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    questions_data = [q.dict() for q in quiz.questions]
    db_quiz = Quiz(
        title=quiz.title,
        description=quiz.description,
        questions=questions_data,
        created_by=current_user.id,
        tags=quiz.tags or []
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

@router.get("/", response_model=List[QuizResponse])
async def get_quizzes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Quiz).filter(Quiz.created_by == current_user.id, Quiz.is_active == True)
    
    if search:
        query = query.filter(Quiz.title.contains(search))
    
    if tags:
        tag_list = tags.split(",")
        for tag in tag_list:
            query = query.filter(Quiz.tags.contains([tag.strip()]))
    
    quizzes = query.offset(skip).limit(limit).all()
    return quizzes

@router.get("/{quiz_id}", response_model=QuizResponse)
async def get_quiz(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Increment view count
    quiz.view_count += 1
    db.commit()
    
    return quiz

@router.put("/{quiz_id}", response_model=QuizResponse)
async def update_quiz(quiz_id: int, quiz_update: QuizUpdate, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    if quiz_update.title is not None:
        quiz.title = quiz_update.title
    if quiz_update.description is not None:
        quiz.description = quiz_update.description
    if quiz_update.questions is not None:
        quiz.questions = [q.dict() for q in quiz_update.questions]
    if quiz_update.tags is not None:
        quiz.tags = quiz_update.tags
    
    db.commit()
    db.refresh(quiz)
    return quiz

@router.delete("/{quiz_id}")
async def delete_quiz(quiz_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.created_by == current_user.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz.is_active = False
    db.commit()
    return {"message": "Quiz deleted successfully"}

@router.post("/bulk-delete")
async def bulk_delete_quizzes(quiz_ids: List[int], current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).filter(Quiz.id.in_(quiz_ids), Quiz.created_by == current_user.id).all()
    
    for quiz in quizzes:
        quiz.is_active = False
    
    db.commit()
    return {"message": f"Deleted {len(quizzes)} quizzes successfully"}
