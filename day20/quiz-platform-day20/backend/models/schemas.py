from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

class TopicBase(BaseModel):
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty_level: int = Field(default=1, ge=1, le=10)
    content_keywords: Optional[str] = None

class TopicCreate(TopicBase):
    pass

class Topic(TopicBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class RelationshipBase(BaseModel):
    source_topic_id: int
    target_topic_id: int
    relationship_type: str = Field(..., pattern="^(prerequisite|corequisite|similar|builds_on|applies_to)$")
    strength: float = Field(default=0.5, ge=0.0, le=1.0)
    bidirectional: bool = False
    source_evidence: Optional[str] = None

class RelationshipCreate(RelationshipBase):
    pass

class TopicRelationship(RelationshipBase):
    id: int
    ai_generated: bool
    validated_by_educator: bool
    created_at: datetime
    source_topic: Topic
    target_topic: Topic
    
    class Config:
        from_attributes = True

class RelatedTopicsResponse(BaseModel):
    topic_id: int
    topic_name: str
    relationships: List[Dict[str, Any]]
    relationship_count: int

class RelationshipDiscoveryRequest(BaseModel):
    topic_ids: List[int]
    relationship_types: Optional[List[str]] = None
    include_ai_suggestions: bool = True
    max_relationships: int = Field(default=50, le=100)

class GraphVisualizationData(BaseModel):
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    statistics: Dict[str, Any]
