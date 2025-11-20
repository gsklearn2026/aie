from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

class ContentCreate(BaseModel):
    topic: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str] = None
    difficulty: str = "medium"
    category: Optional[str] = None

class ContentUpdate(BaseModel):
    question: Optional[str] = None
    options: Optional[List[str]] = None
    correct_answer: Optional[str] = None
    explanation: Optional[str] = None
    difficulty: Optional[str] = None

class ContentResponse(BaseModel):
    id: UUID
    topic: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: Optional[str]
    difficulty: str
    category: Optional[str]
    state: str
    lifecycle: str
    freshness_score: float
    created_at: datetime
    updated_at: datetime
    last_refreshed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class MetricsResponse(BaseModel):
    content_id: UUID
    total_attempts: int
    correct_attempts: int
    skip_count: int
    accuracy_rate: float
    skip_rate: float
    engagement_score: float
    last_calculated_at: datetime
    
    class Config:
        from_attributes = True

class VersionResponse(BaseModel):
    id: UUID
    content_id: UUID
    version_number: int
    content_data: Dict[str, Any]
    performance_snapshot: Optional[Dict[str, Any]]
    refresh_reason: Optional[str]
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class JobResponse(BaseModel):
    id: UUID
    content_id: UUID
    job_type: str
    status: str
    priority: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class RefreshRequest(BaseModel):
    content_id: UUID
    priority: int = 5
    force: bool = False

class DashboardStats(BaseModel):
    total_content: int
    fresh_count: int
    current_count: int
    aging_count: int
    stale_count: int
    queue_depth: int
    queue_breakdown: Optional[Dict[str, int]] = None
    avg_freshness_score: float
    rollback_rate: float
    recent_refreshes: int
    alerts: List[Dict[str, Any]]
