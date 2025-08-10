from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from ..models.relationship import Topic, TopicRelationship, RelationshipValidation
from ..models.schemas import RelationshipCreate, TopicCreate
from ..services.ai_relationship_service import AIRelationshipService
from ..services.graph_service import GraphService
import redis
import json
from ..config.settings import settings

class RelationshipService:
    def __init__(self):
        self.ai_service = AIRelationshipService()
        self.graph_service = GraphService()
        self.redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        self.cache_ttl = 3600  # 1 hour
    
    async def create_topic(self, db: Session, topic_data: TopicCreate) -> Topic:
        """Create a new topic"""
        topic = Topic(**topic_data.dict())
        db.add(topic)
        db.commit()
        db.refresh(topic)
        
        # Invalidate cache
        self._invalidate_related_caches(topic.id)
        
        return topic
    
    async def create_relationship(self, db: Session, relationship_data: RelationshipCreate) -> TopicRelationship:
        """Create a new topic relationship"""
        relationship = TopicRelationship(**relationship_data.dict())
        db.add(relationship)
        db.commit()
        db.refresh(relationship)
        
        # Invalidate related caches
        self._invalidate_related_caches(relationship.source_topic_id)
        self._invalidate_related_caches(relationship.target_topic_id)
        
        return relationship
    
    async def get_related_topics(self, db: Session, topic_id: int, 
                               relationship_types: Optional[List[str]] = None,
                               max_results: int = 20) -> Dict[str, Any]:
        """Get topics related to given topic"""
        cache_key = f"related:{topic_id}:{':'.join(relationship_types or [])}:{max_results}"
        
        # Check cache first
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        # Get topic
        topic = db.query(Topic).filter(Topic.id == topic_id).first()
        if not topic:
            return {"error": "Topic not found"}
        
        # Build graph and find relationships
        self.graph_service.build_graph_from_db(db)
        related = self.graph_service.find_related_topics(
            topic_id, relationship_types, max_results=max_results
        )
        
        result = {
            "topic_id": topic_id,
            "topic_name": topic.name,
            "relationships": related,
            "relationship_count": len(related)
        }
        
        # Cache result
        self.redis_client.setex(cache_key, self.cache_ttl, json.dumps(result))
        return result
    
    async def discover_ai_relationships(self, db: Session, topic_ids: List[int]) -> List[Dict[str, Any]]:
        """Use AI to discover relationships between topics"""
        topics = db.query(Topic).filter(Topic.id.in_(topic_ids)).all()
        if len(topics) < 2:
            return []
        
        relationships = await self.ai_service.discover_relationships(topics)
        
        # Store AI-discovered relationships
        created_relationships = []
        for rel_data in relationships:
            # Check if relationship already exists
            existing = db.query(TopicRelationship).filter(
                TopicRelationship.source_topic_id == rel_data["source_topic_id"],
                TopicRelationship.target_topic_id == rel_data["target_topic_id"],
                TopicRelationship.relationship_type == rel_data["relationship_type"]
            ).first()
            
            if not existing:
                relationship = TopicRelationship(**rel_data)
                db.add(relationship)
                db.commit()
                db.refresh(relationship)
                created_relationships.append(relationship)
        
        return [
            {
                "id": rel.id,
                "source_topic_id": rel.source_topic_id,
                "target_topic_id": rel.target_topic_id,
                "relationship_type": rel.relationship_type,
                "strength": rel.strength,
                "source_evidence": rel.source_evidence,
                "ai_generated": rel.ai_generated
            }
            for rel in created_relationships
        ]
    
    async def validate_relationship(self, db: Session, relationship_id: int, 
                                  educator_id: str, status: str, feedback: str = "") -> bool:
        """Validate an AI-generated relationship"""
        relationship = db.query(TopicRelationship).filter(
            TopicRelationship.id == relationship_id
        ).first()
        
        if not relationship:
            return False
        
        # Update relationship validation status
        if status == "approved":
            relationship.validated_by_educator = True
        
        # Create validation record
        validation = RelationshipValidation(
            relationship_id=relationship_id,
            educator_id=educator_id,
            validation_status=status,
            feedback=feedback
        )
        
        db.add(validation)
        db.commit()
        
        # Invalidate caches
        self._invalidate_related_caches(relationship.source_topic_id)
        self._invalidate_related_caches(relationship.target_topic_id)
        
        return True
    
    async def get_learning_path(self, db: Session, start_topic_id: int, 
                              end_topic_id: int) -> List[Dict[str, Any]]:
        """Get learning path between two topics"""
        self.graph_service.build_graph_from_db(db)
        return self.graph_service.find_shortest_learning_path(start_topic_id, end_topic_id)
    
    async def get_topic_clusters(self, db: Session) -> List[Dict[str, Any]]:
        """Get topic clusters"""
        cache_key = "topic_clusters"
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        self.graph_service.build_graph_from_db(db)
        clusters = self.graph_service.get_topic_clusters()
        
        # Cache for longer time as clusters change less frequently
        self.redis_client.setex(cache_key, self.cache_ttl * 6, json.dumps(clusters))
        return clusters
    
    async def get_graph_visualization_data(self, db: Session) -> Dict[str, Any]:
        """Get data for graph visualization"""
        cache_key = "graph_visualization"
        cached = self.redis_client.get(cache_key)
        if cached:
            return json.loads(cached)
        
        self.graph_service.build_graph_from_db(db)
        
        # Prepare nodes
        nodes = []
        for node_id, data in self.graph_service.graph.nodes(data=True):
            nodes.append({
                "id": node_id,
                "label": data.get("name", f"Topic {node_id}"),
                "category": data.get("category", "General"),
                "difficulty": data.get("difficulty", 1),
                "group": hash(data.get("category", "General")) % 10
            })
        
        # Prepare edges
        edges = []
        for source, target, data in self.graph_service.graph.edges(data=True):
            edges.append({
                "from": source,
                "to": target,
                "label": data.get("relationship_type", "related"),
                "strength": data.get("strength", 0.5),
                "color": self._get_relationship_color(data.get("relationship_type")),
                "width": max(1, data.get("strength", 0.5) * 5),
                "validated": data.get("validated", False)
            })
        
        statistics = self.graph_service.get_graph_statistics()
        
        result = {
            "nodes": nodes,
            "edges": edges,
            "statistics": statistics
        }
        
        # Cache for moderate time
        self.redis_client.setex(cache_key, self.cache_ttl * 2, json.dumps(result))
        return result
    
    def _get_relationship_color(self, relationship_type: str) -> str:
        """Get color for relationship type"""
        colors = {
            "prerequisite": "#FF6B6B",
            "corequisite": "#4ECDC4", 
            "similar": "#45B7D1",
            "builds_on": "#96CEB4",
            "applies_to": "#FECA57"
        }
        return colors.get(relationship_type, "#BDC3C7")
    
    def _invalidate_related_caches(self, topic_id: int):
        """Invalidate caches related to a topic"""
        pattern = f"related:{topic_id}:*"
        for key in self.redis_client.scan_iter(match=pattern):
            self.redis_client.delete(key)
        
        # Also invalidate graph-wide caches
        self.redis_client.delete("topic_clusters")
        self.redis_client.delete("graph_visualization")
