from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from ..models.schemas import (
    Topic, TopicCreate, TopicRelationship, RelationshipCreate,
    RelatedTopicsResponse, RelationshipDiscoveryRequest,
    GraphVisualizationData
)
from ..services.relationship_service import RelationshipService
from ..database import get_db

router = APIRouter(prefix="/relationships", tags=["relationships"])
relationship_service = RelationshipService()

@router.post("/topics/", response_model=Topic)
async def create_topic(topic: TopicCreate, db: Session = Depends(get_db)):
    """Create a new topic"""
    return await relationship_service.create_topic(db, topic)

@router.get("/topics/{topic_id}", response_model=Topic)
async def get_topic(topic_id: int, db: Session = Depends(get_db)):
    """Get topic by ID"""
    from ..models.relationship import Topic as TopicModel
    topic = db.query(TopicModel).filter(TopicModel.id == topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic

@router.get("/topics/", response_model=List[Topic])
async def list_topics(
    skip: int = 0, 
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List topics with optional filtering"""
    from ..models.relationship import Topic as TopicModel
    query = db.query(TopicModel)
    
    if category:
        query = query.filter(TopicModel.category == category)
    
    topics = query.offset(skip).limit(limit).all()
    return topics

@router.post("/", response_model=TopicRelationship)
async def create_relationship(relationship: RelationshipCreate, db: Session = Depends(get_db)):
    """Create a new topic relationship"""
    return await relationship_service.create_relationship(db, relationship)

@router.get("/topics/{topic_id}/related")
async def get_related_topics(
    topic_id: int,
    relationship_types: Optional[List[str]] = Query(None),
    max_results: int = Query(20, le=100),
    db: Session = Depends(get_db)
):
    """Get topics related to specified topic"""
    return await relationship_service.get_related_topics(
        db, topic_id, relationship_types, max_results
    )

@router.post("/discover")
async def discover_relationships(
    request: RelationshipDiscoveryRequest,
    db: Session = Depends(get_db)
):
    """Use AI to discover relationships between topics"""
    if len(request.topic_ids) < 2:
        raise HTTPException(status_code=400, detail="Need at least 2 topics for relationship discovery")
    
    relationships = await relationship_service.discover_ai_relationships(db, request.topic_ids)
    return {
        "discovered_relationships": relationships,
        "count": len(relationships)
    }

@router.post("/validate/{relationship_id}")
async def validate_relationship(
    relationship_id: int,
    educator_id: str,
    status: str = Query(..., pattern="^(approved|rejected|needs_review)$"),
    feedback: str = "",
    db: Session = Depends(get_db)
):
    """Validate an AI-discovered relationship"""
    success = await relationship_service.validate_relationship(
        db, relationship_id, educator_id, status, feedback
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Relationship not found")
    
    return {"status": "validated", "relationship_id": relationship_id}

@router.get("/learning-path")
async def get_learning_path(
    start_topic_id: int = Query(...),
    end_topic_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """Get learning path between two topics"""
    path = await relationship_service.get_learning_path(db, start_topic_id, end_topic_id)
    return {
        "start_topic_id": start_topic_id,
        "end_topic_id": end_topic_id,
        "path": path,
        "path_length": len(path)
    }

@router.get("/clusters")
async def get_topic_clusters(db: Session = Depends(get_db)):
    """Get topic clusters"""
    clusters = await relationship_service.get_topic_clusters(db)
    return {
        "clusters": clusters,
        "cluster_count": len(clusters)
    }

@router.get("/visualization")
async def get_graph_visualization(db: Session = Depends(get_db)):
    """Get graph visualization data"""
    return await relationship_service.get_graph_visualization_data(db)

@router.get("/statistics")
async def get_relationship_statistics(db: Session = Depends(get_db)):
    """Get relationship statistics"""
    from ..services.graph_service import GraphService
    graph_service = GraphService()
    graph_service.build_graph_from_db(db)
    return graph_service.get_graph_statistics()
