import networkx as nx
import numpy as np
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from ..models.learning_path import Topic, UserProgress, TopicRelationship
from ..database.connection import get_db
import logging
from sklearn.cluster import KMeans
import json

logger = logging.getLogger(__name__)

class LearningPathGenerator:
    """
    Advanced learning path generation using graph algorithms and ML
    """
    
    def __init__(self, db: Session):
        self.db = db
        self.topic_graph = None
        self._build_topic_graph()
    
    def _build_topic_graph(self):
        """Build directed graph of topic relationships"""
        self.topic_graph = nx.DiGraph()
        
        # Add all topics as nodes
        topics = self.db.query(Topic).all()
        logger.info(f"Found {len(topics)} topics in database")
        
        for topic in topics:
            logger.info(f"Adding topic {topic.id}: {topic.name}")
            self.topic_graph.add_node(
                topic.id,
                name=topic.name,
                difficulty=topic.difficulty_level,
                duration=topic.estimated_duration,
                prerequisites=topic.prerequisites or []
            )
        
        # Add edges from relationships
        relationships = self.db.query(TopicRelationship).all()
        logger.info(f"Found {len(relationships)} topic relationships")
        
        for rel in relationships:
            self.topic_graph.add_edge(
                rel.source_topic_id,
                rel.target_topic_id,
                type=rel.relationship_type,
                strength=rel.strength
            )
        
        logger.info(f"Built topic graph with {self.topic_graph.number_of_nodes()} nodes and {self.topic_graph.number_of_edges()} edges")
        logger.info(f"Topic IDs in graph: {list(self.topic_graph.nodes())}")
    
    def generate_personalized_path(
        self,
        user_id: int,
        target_topics: List[int],
        max_difficulty_jump: float = 1.5,
        preferred_duration: Optional[int] = None
    ) -> Dict:
        """
        Generate personalized learning path for user
        """
        try:
            # Validate input
            if not target_topics:
                raise ValueError("Target topics list cannot be empty")
            
            # Get user's current progress
            user_progress = self._get_user_progress(user_id)
            
            # Calculate user's knowledge profile
            knowledge_profile = self._calculate_knowledge_profile(user_progress)
            
            # Generate base path using topological sorting
            base_path = self._generate_prerequisite_path(target_topics)
            
            # Apply personalization
            personalized_path = self._personalize_path(
                base_path,
                knowledge_profile,
                max_difficulty_jump,
                preferred_duration
            )
            
            # Calculate path metrics
            path_metrics = self._calculate_path_metrics(personalized_path, user_progress)
            
            return {
                "path_id": f"path_{user_id}_{len(target_topics)}",
                "user_id": user_id,
                "topic_sequence": personalized_path,
                "total_topics": len(personalized_path),
                "estimated_duration": path_metrics["total_duration"],
                "difficulty_progression": path_metrics["difficulty_curve"],
                "completion_probability": path_metrics["success_probability"],
                "next_topics": personalized_path[:3] if personalized_path else [],  # Next 3 recommended
                "path_analysis": {
                    "prerequisite_coverage": path_metrics["prerequisite_coverage"],
                    "difficulty_balance": path_metrics["difficulty_balance"],
                    "knowledge_gaps": path_metrics["knowledge_gaps"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating learning path: {str(e)}")
            raise
    
    def _get_user_progress(self, user_id: int) -> Dict:
        """Get user's learning progress and mastery levels"""
        progress_records = self.db.query(UserProgress).filter(
            UserProgress.user_id == user_id
        ).all()
        
        progress_dict = {}
        for record in progress_records:
            progress_dict[record.topic_id] = {
                "mastery_level": record.mastery_level or 0.0,
                "completion_status": record.completion_status or "not_started",
                "time_spent": record.time_spent or 0,
                "attempts": record.attempts or 0
            }
        
        return progress_dict
    
    def _calculate_knowledge_profile(self, user_progress: Dict) -> Dict:
        """Calculate user's knowledge strengths and learning patterns"""
        if not user_progress:
            return {
                "avg_mastery": 0.0,
                "learning_velocity": 1.0,
                "difficulty_preference": 3.0,
                "strong_areas": [],
                "weak_areas": []
            }
        
        mastery_levels = [p["mastery_level"] for p in user_progress.values()]
        
        return {
            "avg_mastery": np.mean(mastery_levels),
            "learning_velocity": self._calculate_learning_velocity(user_progress),
            "difficulty_preference": self._estimate_difficulty_preference(user_progress),
            "strong_areas": self._identify_strong_areas(user_progress),
            "weak_areas": self._identify_weak_areas(user_progress)
        }
    
    def _generate_prerequisite_path(self, target_topics: List[int]) -> List[int]:
        """Generate path respecting prerequisite constraints using topological sort"""
        try:
            # Create subgraph with relevant topics
            relevant_topics = set(target_topics)
            
            # Add all prerequisite topics recursively
            for topic_id in target_topics:
                relevant_topics.update(self._get_all_prerequisites(topic_id))
            
            subgraph = self.topic_graph.subgraph(relevant_topics)
            
            # Topological sort to respect prerequisites
            if nx.is_directed_acyclic_graph(subgraph):
                sorted_topics = list(nx.topological_sort(subgraph))
            else:
                # Handle cycles by breaking them at weakest edges
                sorted_topics = self._break_cycles_and_sort(subgraph)
            
            return sorted_topics
            
        except Exception as e:
            logger.error(f"Error in prerequisite path generation: {str(e)}")
            return target_topics  # Fallback to original order
    
    def _personalize_path(
        self,
        base_path: List[int],
        knowledge_profile: Dict,
        max_difficulty_jump: float,
        preferred_duration: Optional[int]
    ) -> List[int]:
        """Apply personalization to base path"""
        
        # Sort by difficulty and user readiness
        path_with_scores = []
        for topic_id in base_path:
            topic_data = self.topic_graph.nodes[topic_id]
            readiness_score = self._calculate_readiness_score(
                topic_id, knowledge_profile
            )
            
            path_with_scores.append({
                "topic_id": topic_id,
                "difficulty": topic_data["difficulty"],
                "readiness": readiness_score,
                "duration": topic_data["duration"]
            })
        
        # Apply difficulty progression constraints
        optimized_path = self._optimize_difficulty_progression(
            path_with_scores, max_difficulty_jump
        )
        
        # Apply duration constraints if specified
        if preferred_duration:
            optimized_path = self._apply_duration_constraints(
                optimized_path, preferred_duration
            )
        
        return [item["topic_id"] for item in optimized_path]
    
    def _calculate_readiness_score(self, topic_id: int, knowledge_profile: Dict) -> float:
        """Calculate how ready user is for a specific topic"""
        topic_data = self.topic_graph.nodes[topic_id]
        
        # Base readiness from user's general progress
        base_readiness = knowledge_profile["avg_mastery"]
        
        # Adjust for topic difficulty vs user preference
        difficulty_match = 1.0 - abs(
            topic_data["difficulty"] - knowledge_profile["difficulty_preference"]
        ) / 10.0
        
        # Boost if in strong areas, reduce if in weak areas
        area_adjustment = 0.0
        if topic_id in knowledge_profile["strong_areas"]:
            area_adjustment = 0.2
        elif topic_id in knowledge_profile["weak_areas"]:
            area_adjustment = -0.1
        
        return min(1.0, base_readiness * difficulty_match + area_adjustment)
    
    def _optimize_difficulty_progression(
        self, path_with_scores: List[Dict], max_jump: float
    ) -> List[Dict]:
        """Optimize difficulty progression to maintain engagement"""
        
        if not path_with_scores:
            return []
        
        # Sort by readiness and prerequisites
        optimized = [path_with_scores[0]]  # Start with first topic
        remaining = path_with_scores[1:]
        
        while remaining:
            current_difficulty = optimized[-1]["difficulty"]
            
            # Find best next topic within difficulty constraints
            valid_next = []
            for topic in remaining:
                difficulty_jump = abs(topic["difficulty"] - current_difficulty)
                if difficulty_jump <= max_jump:
                    valid_next.append(topic)
            
            if not valid_next:
                # If no valid topics, pick the closest difficulty
                valid_next = [min(remaining, key=lambda x: abs(x["difficulty"] - current_difficulty))]
            
            # Choose highest readiness among valid options
            next_topic = max(valid_next, key=lambda x: x["readiness"])
            optimized.append(next_topic)
            remaining.remove(next_topic)
        
        return optimized
    
    def _calculate_path_metrics(self, path: List[int], user_progress: Dict) -> Dict:
        """Calculate comprehensive path metrics"""
        if not path:
            return {
                "total_duration": 0,
                "difficulty_curve": [],
                "success_probability": 0.0,
                "prerequisite_coverage": 0.0,
                "difficulty_balance": 0.0,
                "knowledge_gaps": []
            }
        
        total_duration = 0
        difficulty_curve = []
        
        for topic_id in path:
            topic_data = self.topic_graph.nodes[topic_id]
            total_duration += topic_data["duration"]
            difficulty_curve.append(topic_data["difficulty"])
        
        # Calculate success probability based on user progress
        success_factors = []
        for topic_id in path:
            if topic_id in user_progress:
                success_factors.append(user_progress[topic_id]["mastery_level"])
            else:
                success_factors.append(0.5)  # Neutral for unknown topics
        
        # Handle edge cases for numpy operations
        success_probability = np.mean(success_factors) if success_factors else 0.0
        difficulty_balance = np.std(difficulty_curve) if len(difficulty_curve) > 1 else 0.0
        
        return {
            "total_duration": total_duration,
            "difficulty_curve": difficulty_curve,
            "success_probability": float(success_probability),
            "prerequisite_coverage": self._calculate_prerequisite_coverage(path),
            "difficulty_balance": float(difficulty_balance),
            "knowledge_gaps": self._identify_path_gaps(path, user_progress)
        }
    
    def _get_all_prerequisites(self, topic_id: int, visited: set = None) -> set:
        """Recursively get all prerequisite topics"""
        if visited is None:
            visited = set()
        
        if topic_id in visited:
            return set()
        
        visited.add(topic_id)
        prerequisites = set()
        
        # Get direct prerequisites from predecessors in graph
        for pred in self.topic_graph.predecessors(topic_id):
            prerequisites.add(pred)
            prerequisites.update(self._get_all_prerequisites(pred, visited))
        
        return prerequisites
    
    def _calculate_learning_velocity(self, user_progress: Dict) -> float:
        """Estimate user's learning speed"""
        if not user_progress:
            return 1.0
        
        completion_times = []
        for progress in user_progress.values():
            completion_status = progress.get("completion_status", "")
            time_spent = progress.get("time_spent", 0)
            if completion_status == "completed" and time_spent > 0:
                # Normalize by topic difficulty (estimate)
                completion_times.append(time_spent)
        
        if not completion_times:
            return 1.0
        
        avg_time = np.mean(completion_times)
        return max(0.5, min(2.0, 60 / avg_time))  # Normalize to 0.5-2.0 range
    
    def _estimate_difficulty_preference(self, user_progress: Dict) -> float:
        """Estimate user's preferred difficulty level"""
        if not user_progress:
            return 3.0
        
        # This would typically use more sophisticated analysis
        # For now, return middle difficulty
        return 5.0
    
    def _identify_strong_areas(self, user_progress: Dict) -> List[int]:
        """Identify topics where user shows strength"""
        strong_topics = []
        for topic_id, progress in user_progress.items():
            mastery = progress.get("mastery_level", 0.0)
            attempts = progress.get("attempts", 0)
            if mastery > 0.8 and attempts <= 2:
                strong_topics.append(topic_id)
        return strong_topics
    
    def _identify_weak_areas(self, user_progress: Dict) -> List[int]:
        """Identify topics where user struggles"""
        weak_topics = []
        for topic_id, progress in user_progress.items():
            mastery = progress.get("mastery_level", 0.0)
            attempts = progress.get("attempts", 0)
            if mastery < 0.4 or attempts > 5:
                weak_topics.append(topic_id)
        return weak_topics
    
    def _break_cycles_and_sort(self, graph: nx.DiGraph) -> List[int]:
        """Handle cycles in topic graph"""
        # Simple cycle breaking - remove edge with lowest strength
        cycles = list(nx.simple_cycles(graph))
        graph_copy = graph.copy()
        
        for cycle in cycles:
            if len(cycle) > 1:
                # Find weakest edge in cycle
                min_strength = float('inf')
                weakest_edge = None
                
                for i in range(len(cycle)):
                    u, v = cycle[i], cycle[(i + 1) % len(cycle)]
                    if graph_copy.has_edge(u, v):
                        strength = graph_copy[u][v].get('strength', 0.5)
                        if strength < min_strength:
                            min_strength = strength
                            weakest_edge = (u, v)
                
                if weakest_edge:
                    graph_copy.remove_edge(*weakest_edge)
        
        return list(nx.topological_sort(graph_copy))
    
    def _apply_duration_constraints(self, path: List[Dict], max_duration: int) -> List[Dict]:
        """Limit path by total duration"""
        total_duration = 0
        constrained_path = []
        
        for topic in path:
            if total_duration + topic["duration"] <= max_duration:
                constrained_path.append(topic)
                total_duration += topic["duration"]
            else:
                break
        
        return constrained_path
    
    def _calculate_prerequisite_coverage(self, path: List[int]) -> float:
        """Calculate how well prerequisites are covered"""
        covered_topics = set()
        total_prerequisites = 0
        covered_prerequisites = 0
        
        for topic_id in path:
            covered_topics.add(topic_id)
            prerequisites = self._get_all_prerequisites(topic_id)
            total_prerequisites += len(prerequisites)
            covered_prerequisites += len(prerequisites.intersection(covered_topics))
        
        if total_prerequisites == 0:
            return 1.0
        
        return covered_prerequisites / total_prerequisites
    
    def _identify_path_gaps(self, path: List[int], user_progress: Dict) -> List[int]:
        """Identify potential knowledge gaps in path"""
        gaps = []
        for topic_id in path:
            if topic_id not in user_progress:
                gaps.append(topic_id)
            elif user_progress[topic_id]["mastery_level"] < 0.3:
                gaps.append(topic_id)
        return gaps

class CollaborativePathGenerator(LearningPathGenerator):
    """
    Extended generator using collaborative filtering
    """
    
    def generate_collaborative_path(
        self,
        user_id: int,
        target_topics: List[int]
    ) -> Dict:
        """Generate path using collaborative filtering insights"""
        
        # Get similar users
        similar_users = self._find_similar_users(user_id)
        
        # Analyze successful paths from similar users
        successful_patterns = self._analyze_successful_patterns(similar_users, target_topics)
        
        # Generate base personalized path
        base_result = self.generate_personalized_path(user_id, target_topics)
        
        # Enhance with collaborative insights
        enhanced_path = self._apply_collaborative_insights(
            base_result["topic_sequence"],
            successful_patterns
        )
        
        base_result["topic_sequence"] = enhanced_path
        base_result["collaborative_insights"] = {
            "similar_users_count": len(similar_users),
            "success_patterns": successful_patterns[:3],  # Top 3 patterns
            "confidence_boost": self._calculate_confidence_boost(successful_patterns)
        }
        
        return base_result
    
    def _find_similar_users(self, user_id: int, k: int = 10) -> List[int]:
        """Find users with similar learning patterns"""
        # This would implement user similarity calculation
        # For demo, return mock similar users
        return [user_id + i for i in range(1, k + 1)]
    
    def _analyze_successful_patterns(self, similar_users: List[int], target_topics: List[int]) -> List[Dict]:
        """Analyze successful learning patterns from similar users"""
        # Mock implementation for demo
        return [
            {"pattern": "video_first", "success_rate": 0.85, "avg_duration": 120},
            {"pattern": "practice_heavy", "success_rate": 0.78, "avg_duration": 180},
            {"pattern": "theory_foundation", "success_rate": 0.82, "avg_duration": 150}
        ]
    
    def _apply_collaborative_insights(self, base_path: List[int], patterns: List[Dict]) -> List[int]:
        """Apply collaborative filtering insights to base path"""
        # For demo, return base path with potential reordering
        return base_path
    
    def _calculate_confidence_boost(self, patterns: List[Dict]) -> float:
        """Calculate confidence boost from collaborative data"""
        if not patterns:
            return 0.0
        
        avg_success = np.mean([p["success_rate"] for p in patterns])
        return min(0.3, (avg_success - 0.5) * 0.6)  # Max 30% boost
