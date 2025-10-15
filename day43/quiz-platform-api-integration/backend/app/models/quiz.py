"""Quiz related data models"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class QuizQuestion(BaseModel):
    """Quiz question model"""
    id: str
    question: str
    options: List[str]
    correct_answer: str
    difficulty: str = "medium"
    category: str = "general"

class QuizResponse(BaseModel):
    """User quiz response model"""
    question_id: str
    selected_answer: str
    user_id: str
    timestamp: datetime = Field(default_factory=datetime.now)

class QuizResult(BaseModel):
    """Quiz result model"""
    user_id: str
    questions: List[QuizQuestion]
    responses: List[QuizResponse]
    score: int
    total_questions: int
    completed_at: datetime = Field(default_factory=datetime.now)

class APIResponse(BaseModel):
    """Standard API response wrapper"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    request_id: Optional[str] = None

class APIError(BaseModel):
    """API error model"""
    code: str
    message: str
    details: Optional[Dict[str, Any]] = None
