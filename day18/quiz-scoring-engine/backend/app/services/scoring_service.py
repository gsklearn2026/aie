import json
import numpy as np
from typing import List, Dict, Any, Optional
from redis import Redis
from ..models.scoring_models import QuizSubmission, ScoreResult, ScoringStrategy, UserPerformanceMetrics
from .scoring_strategies import ScoringStrategyFactory
from config.settings import settings
import logging

logger = logging.getLogger(__name__)

class ScoringService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client
        self.strategy_factory = ScoringStrategyFactory()
    
    async def calculate_score(self, submission: QuizSubmission) -> ScoreResult:
        """Calculate score for a quiz submission"""
        try:
            # Get user performance history for adaptive scoring
            user_history = await self._get_user_history(submission.user_id)
            
            # Select and execute scoring strategy
            strategy = self.strategy_factory.create_strategy(submission.strategy)
            
            # Calculate raw score
            score_data = strategy.calculate_score(
                submission.answers,
                user_history=user_history
            )
            
            # Normalize score
            normalized_score = await self._normalize_score(
                score_data["raw_score"],
                submission.quiz_id,
                submission.strategy
            )
            
            # Calculate percentile rank
            percentile_rank = await self._calculate_percentile_rank(
                normalized_score,
                submission.quiz_id
            )
            
            # Create result
            result = ScoreResult(
                quiz_id=submission.quiz_id,
                user_id=submission.user_id,
                raw_score=score_data["raw_score"],
                normalized_score=normalized_score,
                percentile_rank=percentile_rank,
                strategy_used=submission.strategy,
                breakdown=score_data["details"]
            )
            
            # Cache result and update user history
            await self._cache_score_result(result)
            await self._update_user_history(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating score: {e}")
            # Fallback to basic scoring
            return await self._fallback_basic_scoring(submission)
    
    async def _normalize_score(self, raw_score: float, quiz_id: str, strategy: ScoringStrategy) -> float:
        """Normalize score using z-score normalization"""
        cache_key = f"normalization:{quiz_id}:{strategy.value}"
        
        # Try to get cached normalization data
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            norm_data = json.loads(cached_data)
            mean = norm_data["mean"]
            std = norm_data["std"]
        else:
            # Calculate from historical data (simplified - would use real data)
            mean = 65.0  # Default mean score
            std = 15.0   # Default standard deviation
            
            # Cache normalization data
            norm_data = {"mean": mean, "std": std}
            self.redis.setex(cache_key, settings.cache_ttl, json.dumps(norm_data))
        
        # Apply z-score normalization then scale to 0-100
        if std > 0:
            z_score = (raw_score - mean) / std
            # Convert z-score to 0-100 scale (approximately)
            normalized = 50 + (z_score * 15)
            return max(0, min(100, normalized))
        
        return raw_score
    
    async def _calculate_percentile_rank(self, score: float, quiz_id: str) -> Optional[float]:
        """Calculate percentile rank based on historical scores"""
        try:
            # Get historical scores for this quiz
            scores_key = f"quiz_scores:{quiz_id}"
            historical_scores = self.redis.lrange(scores_key, 0, -1)
            
            if not historical_scores:
                return None
            
            scores = [float(s) for s in historical_scores]
            scores.append(score)
            scores.sort()
            
            rank = scores.index(score)
            percentile = (rank / len(scores)) * 100
            
            return round(percentile, 2)
            
        except Exception as e:
            logger.error(f"Error calculating percentile rank: {e}")
            return None
    
    async def _get_user_history(self, user_id: str) -> Dict[str, Any]:
        """Get user performance history"""
        cache_key = f"user_history:{user_id}"
        cached_history = self.redis.get(cache_key)
        
        if cached_history:
            return json.loads(cached_history)
        
        # Default history for new users
        return {
            "average_score": 50.0,
            "total_quizzes": 0,
            "performance_trend": [],
            "difficulty_preferences": {}
        }
    
    async def _cache_score_result(self, result: ScoreResult):
        """Cache score result"""
        cache_key = f"score_result:{result.quiz_id}:{result.user_id}"
        result_data = result.model_dump_json()
        self.redis.setex(cache_key, settings.cache_ttl, result_data)
        
        # Add to quiz scores list for percentile calculations
        scores_key = f"quiz_scores:{result.quiz_id}"
        self.redis.lpush(scores_key, result.normalized_score)
        self.redis.ltrim(scores_key, 0, 999)  # Keep last 1000 scores
    
    async def _update_user_history(self, result: ScoreResult):
        """Update user performance history"""
        history = await self._get_user_history(result.user_id)
        
        # Update metrics
        total_quizzes = history["total_quizzes"] + 1
        current_avg = history["average_score"]
        new_avg = ((current_avg * history["total_quizzes"]) + result.normalized_score) / total_quizzes
        
        # Update performance trend
        trend = history["performance_trend"][-20:]  # Keep last 20 scores
        trend.append(result.normalized_score)
        
        updated_history = {
            "average_score": new_avg,
            "total_quizzes": total_quizzes,
            "performance_trend": trend,
            "difficulty_preferences": history["difficulty_preferences"]
        }
        
        cache_key = f"user_history:{result.user_id}"
        self.redis.setex(cache_key, settings.cache_ttl * 24, json.dumps(updated_history))
    
    async def _fallback_basic_scoring(self, submission: QuizSubmission) -> ScoreResult:
        """Fallback to basic scoring if main scoring fails"""
        logger.warning("Using fallback basic scoring")
        
        correct_count = sum(1 for answer in submission.answers if answer.is_correct)
        total_count = len(submission.answers)
        
        raw_score = (correct_count / total_count) * 100 if total_count > 0 else 0
        
        return ScoreResult(
            quiz_id=submission.quiz_id,
            user_id=submission.user_id,
            raw_score=raw_score,
            normalized_score=raw_score,
            percentile_rank=None,
            strategy_used=ScoringStrategy.BASIC,
            breakdown={"correct": correct_count, "total": total_count, "fallback": True}
        )
    
    async def get_user_performance_metrics(self, user_id: str) -> UserPerformanceMetrics:
        """Get comprehensive user performance metrics"""
        history = await self._get_user_history(user_id)
        
        return UserPerformanceMetrics(
            user_id=user_id,
            average_score=history["average_score"],
            total_quizzes=history["total_quizzes"],
            performance_trend=history["performance_trend"],
            difficulty_preferences=history["difficulty_preferences"]
        )
