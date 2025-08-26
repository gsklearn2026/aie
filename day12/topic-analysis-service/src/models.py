from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum

class AnalysisOptions(BaseModel):
    """Configuration options for topic analysis"""
    max_topics: int = Field(default=10, ge=1, le=50, description="Maximum number of topics to extract")
    include_subtopics: bool = Field(default=True, description="Include subtopic extraction")
    confidence_threshold: float = Field(default=0.5, ge=0.0, le=1.0, description="Minimum confidence threshold")
    extract_concepts: bool = Field(default=True, description="Extract related concepts")
    domain_filter: Optional[str] = Field(default=None, description="Domain-specific filtering")

class TopicInfo(BaseModel):
    """Information about an extracted topic"""
    name: str = Field(description="Topic name")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")
    category: str = Field(description="Topic category")
    subtopics: List[str] = Field(default_factory=list, description="Related subtopics")
    concepts: List[str] = Field(default_factory=list, description="Related concepts")
    keywords: List[str] = Field(default_factory=list, description="Key terms")

class TopicAnalysisRequest(BaseModel):
    """Request for topic analysis"""
    content: str = Field(min_length=10, max_length=50000, description="Content to analyze")
    options: AnalysisOptions = Field(default_factory=AnalysisOptions, description="Analysis options")

class TopicAnalysisResponse(BaseModel):
    """Response from topic analysis"""
    topics: List[TopicInfo] = Field(description="Extracted topics")
    summary: str = Field(description="Content summary")
    word_count: int = Field(description="Word count of analyzed content")
    processing_time: float = Field(description="Processing time in seconds")
    cache_hit: bool = Field(description="Whether result came from cache")

class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(description="Service status")
    service: str = Field(description="Service name")
    version: str = Field(description="Service version")
