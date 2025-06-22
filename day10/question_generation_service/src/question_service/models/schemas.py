"""Pydantic models for API requests and responses"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class JobSubmission(BaseModel):
    """Request model for job submission"""

    topic: str = Field(..., description="Topic for question generation")
    count: int = Field(5, ge=1, le=20, description="Number of questions to generate")
    difficulty: str = Field("medium", description="Question difficulty level")
    context: Optional[str] = Field(None, description="Additional context")


class JobResponse(BaseModel):
    """Response model for job submission"""

    job_id: str
    status: str
    message: str


class Question(BaseModel):
    """Individual question model"""

    id: str
    question: str
    type: str
    difficulty: str
    topic: str
    generated_at: str


class QuestionResponse(BaseModel):
    """Response model for job status and results"""

    job_id: str
    status: str
    topic: Optional[str] = None
    questions: List[Question] = []
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    error_message: Optional[str] = None
    retry_count: int = 0
    question_count: int = 0


class HealthResponse(BaseModel):
    """Health check response"""

    status: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None
