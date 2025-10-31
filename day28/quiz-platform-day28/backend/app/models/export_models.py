from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, Float
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
import enum

from ..config.database import Base

class ExportFormat(str, enum.Enum):
    CSV = "csv"
    JSON = "json"
    XML = "xml"
    PDF = "pdf"
    EXCEL = "excel"

class ExportStatus(str, enum.Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ExportJob(Base):
    __tablename__ = "export_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    export_format = Column(Enum(ExportFormat))
    status = Column(Enum(ExportStatus), default=ExportStatus.QUEUED)
    progress = Column(Float, default=0.0)
    total_records = Column(Integer, default=0)
    processed_records = Column(Integer, default=0)
    file_path = Column(String, nullable=True)
    file_size = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    parameters = Column(Text)  # JSON string of export parameters
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

# Pydantic models for API
class ExportRequest(BaseModel):
    format: ExportFormat
    filters: Optional[Dict[str, Any]] = {}
    date_range: Optional[Dict[str, str]] = {}
    include_ai_insights: bool = True
    template_id: Optional[str] = None

class ExportJobResponse(BaseModel):
    job_id: str
    status: ExportStatus
    progress: float
    total_records: int
    processed_records: int
    file_size: Optional[int]
    download_url: Optional[str]
    created_at: datetime
    completed_at: Optional[datetime]
    error_message: Optional[str]

class ExportProgress(BaseModel):
    job_id: str
    status: ExportStatus
    progress: float
    current_record: int
    total_records: int
    estimated_completion: Optional[datetime]
