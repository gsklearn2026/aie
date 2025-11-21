from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class QuestionCreate(BaseModel):
    text: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str] = None
    topic: str
    difficulty: str
    source_model: str = "gemini-1.5-flash"

class QuestionResponse(BaseModel):
    id: str
    text: str
    options: List[str]
    correct_answer: int
    explanation: Optional[str]
    topic: str
    difficulty: str
    source_model: str
    created_at: datetime

    class Config:
        from_attributes = True

class QualityMetrics(BaseModel):
    readability_score: float = Field(ge=0, le=1)
    factual_confidence: float = Field(ge=0, le=1)
    distractor_quality: float = Field(ge=0, le=1)
    topic_alignment: float = Field(ge=0, le=1)
    difficulty_match: float = Field(ge=0, le=1)

class CurationCreate(BaseModel):
    question_id: str
    quality_metrics: QualityMetrics

class CurationResponse(BaseModel):
    id: str
    question_id: str
    status: str
    quality_score: float
    quality_metrics: Dict[str, float]
    priority_score: float
    reviewer_id: Optional[str]
    reviewed_at: Optional[datetime]
    feedback: Optional[str]
    created_at: datetime
    question: Optional[QuestionResponse] = None

    class Config:
        from_attributes = True

class CurationAction(BaseModel):
    reviewer_id: str
    feedback: Optional[str] = None

class QueueItem(BaseModel):
    id: str
    question_id: str
    preview: str
    quality_score: float
    priority_score: float
    topic: str
    difficulty: str
    created_at: datetime
    time_in_queue: str

class QueueResponse(BaseModel):
    items: List[QueueItem]
    total: int
    page: int
    page_size: int

class AnalyticsResponse(BaseModel):
    total_items: int
    total_reviewed: int
    total_reviewed_alltime: int
    approval_rate: float
    approval_rate_alltime: float
    avg_review_time_minutes: float
    avg_review_time_alltime_minutes: float
    status_distribution: Dict[str, int]
    daily_stats: List[Dict[str, Any]]
    top_rejection_reasons: List[Dict[str, Any]]
    model_performance: Dict[str, Dict[str, float]]

class AuditLogResponse(BaseModel):
    id: str
    curation_id: str
    action: str
    previous_status: Optional[str]
    new_status: str
    reviewer_id: str
    details: Optional[Dict[str, Any]]
    timestamp: datetime

    class Config:
        from_attributes = True
