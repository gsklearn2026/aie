import asyncio
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import redis.asyncio as redis
import structlog
from ..models.schemas import *
from config.settings import Settings

logger = structlog.get_logger()

class ProgressiveDifficultyEngine:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.redis_client = None
        
        # Algorithm parameters
        self.performance_window = settings.performance_window_size
        self.target_success_rate = settings.optimal_success_rate
        self.confidence_threshold = settings.confidence_threshold
        self.adaptation_rate = settings.adaptation_sensitivity
        
        # Difficulty level mappings
        self.difficulty_scores = {
            DifficultyLevel.BEGINNER: 0.1,
            DifficultyLevel.EASY: 0.3,
            DifficultyLevel.MEDIUM: 0.5,
            DifficultyLevel.HARD: 0.7,
            DifficultyLevel.EXPERT: 0.9
        }

    async def initialize(self):
        """Initialize Redis connection and cache"""
        self.redis_client = redis.from_url(
            f"redis://{self.settings.redis_host}:{self.settings.redis_port}",
            db=self.settings.redis_db
        )
        logger.info("Difficulty engine initialized")

    async def cleanup(self):
        """Cleanup resources"""
        if self.redis_client:
            await self.redis_client.close()

    async def calculate_next_difficulty(
        self, 
        user_id: str, 
        recent_performance: List[QuestionResponse],
        current_session_data: SessionData
    ) -> DifficultyResponse:
        """Main algorithm to calculate next difficulty level"""
        
        # Get user state from cache
        user_state = await self._get_cached_user_state(user_id)
        
        # Analyze current performance
        performance_metrics = self._analyze_performance(recent_performance)
        
        # Calculate confidence intervals
        confidence_metrics = self._calculate_confidence_metrics(recent_performance)
        
        # Determine learning state
        learning_state = self._determine_learning_state(
            performance_metrics, confidence_metrics, user_state
        )
        
        # Calculate next difficulty
        next_difficulty = self._calculate_difficulty_adjustment(
            learning_state, performance_metrics, user_state
        )
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            learning_state, performance_metrics, next_difficulty
        )
        
        # Update user state cache
        await self._update_user_state_cache(user_id, {
            'current_state': learning_state,
            'difficulty_level': next_difficulty,
            'last_updated': datetime.now().isoformat(),
            'performance_metrics': performance_metrics
        })
        
        return DifficultyResponse(
            recommended_difficulty=next_difficulty,
            confidence=confidence_metrics['overall_confidence'],
            reasoning=reasoning,
            user_state=learning_state,
            adjustment_factors={
                'accuracy': performance_metrics['accuracy'],
                'response_time': performance_metrics['avg_response_time'],
                'consistency': performance_metrics['consistency'],
                'trend': performance_metrics['trend']
            },
            next_question_criteria={
                'difficulty_range': self._get_difficulty_range(next_difficulty),
                'subject_focus': self._recommend_subject_focus(recent_performance),
                'question_types': self._recommend_question_types(learning_state)
            }
        )

    def _analyze_performance(self, responses: List[QuestionResponse]) -> Dict:
        """Analyze user performance metrics"""
        if not responses:
            return self._default_performance_metrics()
            
        # Calculate basic metrics
        accuracy = sum(1 for r in responses if r.is_correct) / len(responses)
        avg_response_time = np.mean([r.response_time_ms for r in responses])
        avg_confidence = np.mean([r.confidence_score for r in responses])
        
        # Calculate consistency (lower variance = higher consistency)
        response_times = [r.response_time_ms for r in responses]
        consistency = 1.0 - (np.std(response_times) / np.mean(response_times)) if response_times else 0.5
        
        # Calculate trend (recent vs older performance)
        if len(responses) >= 6:
            recent_accuracy = sum(1 for r in responses[-3:] if r.is_correct) / 3
            older_accuracy = sum(1 for r in responses[-6:-3] if r.is_correct) / 3
            trend = recent_accuracy - older_accuracy
        else:
            trend = 0.0
            
        return {
            'accuracy': accuracy,
            'avg_response_time': avg_response_time,
            'avg_confidence': avg_confidence,
            'consistency': max(0.0, min(1.0, consistency)),
            'trend': trend,
            'sample_size': len(responses)
        }

    def _calculate_confidence_metrics(self, responses: List[QuestionResponse]) -> Dict:
        """Calculate confidence-based metrics"""
        if not responses:
            return {'overall_confidence': 0.5, 'confidence_accuracy_correlation': 0.0}
            
        confidences = [r.confidence_score for r in responses]
        accuracies = [1.0 if r.is_correct else 0.0 for r in responses]
        
        overall_confidence = np.mean(confidences)
        
        # Calculate correlation between confidence and accuracy
        if len(responses) > 1:
            correlation = np.corrcoef(confidences, accuracies)[0, 1]
            if np.isnan(correlation):
                correlation = 0.0
        else:
            correlation = 0.0
            
        return {
            'overall_confidence': overall_confidence,
            'confidence_accuracy_correlation': correlation
        }

    def _determine_learning_state(self, performance_metrics: Dict, confidence_metrics: Dict, user_state: Dict) -> LearningState:
        """Determine current learning state"""
        accuracy = performance_metrics['accuracy']
        consistency = performance_metrics['consistency']
        trend = performance_metrics['trend']
        sample_size = performance_metrics['sample_size']
        
        # Warming up phase
        if sample_size < 5:
            return LearningState.WARMING_UP
            
        # Struggling state
        if accuracy < 0.6 or (trend < -0.2 and consistency < 0.4):
            return LearningState.STRUGGLING
            
        # Mastery state
        if accuracy > 0.9 and consistency > 0.8 and trend >= 0:
            return LearningState.MASTERY
            
        # Optimal challenge (default state)
        return LearningState.OPTIMAL_CHALLENGE

    def _calculate_difficulty_adjustment(self, learning_state: LearningState, performance_metrics: Dict, user_state: Dict) -> DifficultyLevel:
        """Calculate next difficulty level"""
        current_difficulty = user_state.get('difficulty_level', DifficultyLevel.MEDIUM)
        current_score = self.difficulty_scores[current_difficulty]
        
        accuracy = performance_metrics['accuracy']
        trend = performance_metrics['trend']
        
        if learning_state == LearningState.WARMING_UP:
            return DifficultyLevel.EASY
            
        elif learning_state == LearningState.STRUGGLING:
            # Decrease difficulty
            new_score = max(0.1, current_score - 0.2)
            
        elif learning_state == LearningState.MASTERY:
            # Increase difficulty
            new_score = min(0.9, current_score + 0.2)
            
        else:  # OPTIMAL_CHALLENGE
            # Fine-tune based on accuracy
            if accuracy > self.target_success_rate + 0.1:
                new_score = min(0.9, current_score + 0.1)
            elif accuracy < self.target_success_rate - 0.1:
                new_score = max(0.1, current_score - 0.1)
            else:
                new_score = current_score  # Stay at current level
        
        # Map score back to difficulty level
        return self._score_to_difficulty(new_score)

    def _score_to_difficulty(self, score: float) -> DifficultyLevel:
        """Convert difficulty score to difficulty level"""
        if score <= 0.2:
            return DifficultyLevel.BEGINNER
        elif score <= 0.4:
            return DifficultyLevel.EASY
        elif score <= 0.6:
            return DifficultyLevel.MEDIUM
        elif score <= 0.8:
            return DifficultyLevel.HARD
        else:
            return DifficultyLevel.EXPERT

    def _generate_reasoning(self, learning_state: LearningState, performance_metrics: Dict, difficulty: DifficultyLevel) -> str:
        """Generate human-readable reasoning for difficulty choice"""
        accuracy = performance_metrics['accuracy']
        trend = performance_metrics['trend']
        
        if learning_state == LearningState.WARMING_UP:
            return f"Starting with {difficulty.value} questions to establish baseline performance"
            
        elif learning_state == LearningState.STRUGGLING:
            return f"Reduced to {difficulty.value} difficulty (accuracy: {accuracy:.1%}) to build confidence"
            
        elif learning_state == LearningState.MASTERY:
            return f"Increased to {difficulty.value} difficulty (accuracy: {accuracy:.1%}) to maintain challenge"
            
        else:
            if trend > 0.1:
                return f"Maintaining {difficulty.value} difficulty with improving trend ({trend:+.1%})"
            elif trend < -0.1:
                return f"Adjusted to {difficulty.value} difficulty due to declining performance ({trend:+.1%})"
            else:
                return f"Continuing with {difficulty.value} difficulty for optimal challenge"

    def _get_difficulty_range(self, difficulty: DifficultyLevel) -> Dict[str, float]:
        """Get acceptable difficulty range for question selection"""
        base_score = self.difficulty_scores[difficulty]
        return {
            'min': max(0.0, base_score - 0.1),
            'max': min(1.0, base_score + 0.1)
        }

    def _recommend_subject_focus(self, responses: List[QuestionResponse]) -> Optional[str]:
        """Recommend subject area focus based on recent performance"""
        # This would integrate with subject classification from previous lessons
        return "core_concepts"  # Placeholder

    def _recommend_question_types(self, learning_state: LearningState) -> List[str]:
        """Recommend question types based on learning state"""
        if learning_state == LearningState.STRUGGLING:
            return ["multiple_choice", "basic_concepts"]
        elif learning_state == LearningState.MASTERY:
            return ["open_ended", "application", "analysis"]
        else:
            return ["multiple_choice", "short_answer", "application"]

    def _default_performance_metrics(self) -> Dict:
        """Default metrics for new users"""
        return {
            'accuracy': 0.5,
            'avg_response_time': 30000,
            'avg_confidence': 0.5,
            'consistency': 0.5,
            'trend': 0.0,
            'sample_size': 0
        }

    async def _get_cached_user_state(self, user_id: str) -> Dict:
        """Get user state from Redis cache"""
        try:
            cached_data = await self.redis_client.get(f"user_state:{user_id}")
            if cached_data:
                return json.loads(cached_data)
        except Exception as e:
            logger.warning("Failed to get cached user state", error=str(e))
        
        return {
            'current_state': LearningState.WARMING_UP,
            'difficulty_level': DifficultyLevel.MEDIUM,
            'sessions_completed': 0
        }

    async def _update_user_state_cache(self, user_id: str, state_data: Dict):
        """Update user state in Redis cache"""
        try:
            await self.redis_client.setex(
                f"user_state:{user_id}", 
                3600,  # 1 hour TTL
                json.dumps(state_data, default=str)
            )
        except Exception as e:
            logger.warning("Failed to update user state cache", error=str(e))

    async def update_user_performance(self, performance: UserPerformance):
        """Update user performance data"""
        # Store performance history
        try:
            await self.redis_client.lpush(
                f"performance_history:{performance.user_id}",
                json.dumps(performance.dict(), default=str)
            )
            # Keep only recent history
            await self.redis_client.ltrim(f"performance_history:{performance.user_id}", 0, 99)
        except Exception as e:
            logger.warning("Failed to update performance history", error=str(e))

    async def get_user_state(self, user_id: str) -> UserStateInfo:
        """Get comprehensive user state information"""
        cached_state = await self._get_cached_user_state(user_id)
        
        return UserStateInfo(
            user_id=user_id,
            current_state=cached_state.get('current_state', LearningState.WARMING_UP),
            difficulty_level=cached_state.get('difficulty_level', DifficultyLevel.MEDIUM),
            performance_trend="stable",  # Would calculate from history
            sessions_completed=cached_state.get('sessions_completed', 0),
            total_questions_answered=cached_state.get('total_questions', 0),
            current_accuracy=cached_state.get('current_accuracy', 0.5),
            confidence_level=cached_state.get('confidence_level', 0.5),
            last_updated=datetime.now()
        )
