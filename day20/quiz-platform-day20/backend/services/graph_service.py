import networkx as nx
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.relationship import Topic, TopicRelationship

class GraphService:
    def __init__(self):
        self.graph = nx.DiGraph()
    
    def build_graph_from_db(self, db: Session) -> nx.DiGraph:
        """Build NetworkX graph from database relationships"""
        self.graph.clear()
        
        # Add nodes (topics)
        topics = db.query(Topic).all()
        for topic in topics:
            self.graph.add_node(
                topic.id,
                name=topic.name,
                description=topic.description,
                category=topic.category,
                difficulty=topic.difficulty_level
            )
        
        # Add edges (relationships)
        relationships = db.query(TopicRelationship).all()
        for rel in relationships:
            self.graph.add_edge(
                rel.source_topic_id,
                rel.target_topic_id,
                relationship_type=rel.relationship_type,
                strength=rel.strength,
                bidirectional=rel.bidirectional,
                ai_generated=rel.ai_generated,
                validated=rel.validated_by_educator
            )
            
            # Add reverse edge if bidirectional
            if rel.bidirectional:
                self.graph.add_edge(
                    rel.target_topic_id,
                    rel.source_topic_id,
                    relationship_type=rel.relationship_type,
                    strength=rel.strength,
                    bidirectional=True,
                    ai_generated=rel.ai_generated,
                    validated=rel.validated_by_educator
                )
        
        return self.graph
    
    def find_related_topics(self, topic_id: int, relationship_types: Optional[List[str]] = None,
                          max_depth: int = 2, max_results: int = 20) -> List[Dict[str, Any]]:
        """Find topics related to given topic within specified depth"""
        if topic_id not in self.graph:
            return []
        
        related = []
        visited = {topic_id}
        
        # BFS traversal with depth limit
        current_level = [(topic_id, 0)]
        
        while current_level and len(related) < max_results:
            next_level = []
            
            for node_id, depth in current_level:
                if depth >= max_depth:
                    continue
                
                # Get neighbors
                for neighbor_id in self.graph.neighbors(node_id):
                    if neighbor_id in visited:
                        continue
                    
                    edge_data = self.graph[node_id][neighbor_id]
                    
                    # Filter by relationship type if specified
                    if relationship_types and edge_data.get('relationship_type') not in relationship_types:
                        continue
                    
                    visited.add(neighbor_id)
                    node_data = self.graph.nodes[neighbor_id]
                    
                    related.append({
                        'topic_id': neighbor_id,
                        'topic_name': node_data.get('name', ''),
                        'relationship_type': edge_data.get('relationship_type'),
                        'strength': edge_data.get('strength', 0.0),
                        'depth': depth + 1,
                        'ai_generated': edge_data.get('ai_generated', False),
                        'validated': edge_data.get('validated', False)
                    })
                    
                    next_level.append((neighbor_id, depth + 1))
            
            current_level = next_level
        
        # Sort by strength and depth
        related.sort(key=lambda x: (x['depth'], -x['strength']))
        return related[:max_results]
    
    def find_shortest_learning_path(self, start_topic_id: int, end_topic_id: int) -> List[Dict[str, Any]]:
        """Find shortest path between two topics considering prerequisites"""
        if start_topic_id not in self.graph or end_topic_id not in self.graph:
            return []
        
        try:
            # Create subgraph with only prerequisite relationships
            prereq_graph = nx.DiGraph()
            for u, v, data in self.graph.edges(data=True):
                if data.get('relationship_type') == 'prerequisite':
                    prereq_graph.add_edge(u, v, **data)
            
            path = nx.shortest_path(prereq_graph, start_topic_id, end_topic_id)
            
            path_details = []
            for i in range(len(path) - 1):
                current = path[i]
                next_topic = path[i + 1]
                edge_data = prereq_graph[current][next_topic]
                
                path_details.append({
                    'from_topic_id': current,
                    'to_topic_id': next_topic,
                    'from_topic_name': self.graph.nodes[current].get('name', ''),
                    'to_topic_name': self.graph.nodes[next_topic].get('name', ''),
                    'relationship_type': edge_data.get('relationship_type'),
                    'strength': edge_data.get('strength', 0.0)
                })
            
            return path_details
        except nx.NetworkXNoPath:
            return []
    
    def get_topic_clusters(self, min_cluster_size: int = 3) -> List[Dict[str, Any]]:
        """Find clusters of related topics"""
        # Convert to undirected for clustering
        undirected = self.graph.to_undirected()
        
        # Find connected components
        components = list(nx.connected_components(undirected))
        
        clusters = []
        for i, component in enumerate(components):
            if len(component) >= min_cluster_size:
                cluster_topics = []
                for topic_id in component:
                    node_data = self.graph.nodes[topic_id]
                    cluster_topics.append({
                        'topic_id': topic_id,
                        'topic_name': node_data.get('name', ''),
                        'category': node_data.get('category', '')
                    })
                
                clusters.append({
                    'cluster_id': i,
                    'size': len(component),
                    'topics': cluster_topics
                })
        
        return clusters
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get graph analysis statistics"""
        if not self.graph.nodes():
            return {}
        
        return {
            'total_topics': self.graph.number_of_nodes(),
            'total_relationships': self.graph.number_of_edges(),
            'average_connections': sum(dict(self.graph.degree()).values()) / self.graph.number_of_nodes(),
            'most_connected_topics': [
                {
                    'topic_id': node_id,
                    'topic_name': self.graph.nodes[node_id].get('name', ''),
                    'connections': degree
                }
                for node_id, degree in sorted(dict(self.graph.degree()).items(), 
                                             key=lambda x: x[1], reverse=True)[:10]
            ],
            'relationship_type_distribution': self._get_relationship_distribution()
        }
    
    def _get_relationship_distribution(self) -> Dict[str, int]:
        """Get distribution of relationship types"""
        distribution = {}
        for u, v, data in self.graph.edges(data=True):
            rel_type = data.get('relationship_type', 'unknown')
            distribution[rel_type] = distribution.get(rel_type, 0) + 1
        return distribution
