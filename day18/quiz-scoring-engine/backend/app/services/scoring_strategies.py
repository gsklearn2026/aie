import numpy as np
from typing import List, Dict, Any
from ..models.scoring_models import QuestionAnswer, ScoringStrategy
import math

class ScoringStrategyBase:
    def calculate_score(self, answers: List[QuestionAnswer], **kwargs) -> Dict[str, Any]:
        raise NotImplementedError

class BasicScoringStrategy(ScoringStrategyBase):
    def calculate_score(self, answers: List[QuestionAnswer], **kwargs) -> Dict[str, Any]:
        correct_count = sum(1 for answer in answers if answer.is_correct)
        total_count = len(answers)
        
        if total_count == 0:
            return {"raw_score": 0, "details": {"correct": 0, "total": 0}}
        
        raw_score = (correct_count / total_count) * 100
        
        return {
            "raw_score": raw_score,
            "details": {
                "correct": correct_count,
                "total": total_count,
                "accuracy": raw_score / 100
            }
        }

class WeightedScoringStrategy(ScoringStrategyBase):
    def calculate_score(self, answers: List[QuestionAnswer], **kwargs) -> Dict[str, Any]:
        if not answers:
            return {"raw_score": 0, "details": {"weighted_correct": 0, "total_weight": 0}}
        
        weighted_correct = sum(
            answer.weight * answer.difficulty if answer.is_correct else 0
            for answer in answers
        )
        
        total_weight = sum(answer.weight * answer.difficulty for answer in answers)
        
        if total_weight == 0:
            return {"raw_score": 0, "details": {"weighted_correct": 0, "total_weight": 0}}
        
        raw_score = (weighted_correct / total_weight) * 100
        
        return {
            "raw_score": raw_score,
            "details": {
                "weighted_correct": weighted_correct,
                "total_weight": total_weight,
                "efficiency": weighted_correct / total_weight,
                "difficulty_bonus": sum(answer.difficulty for answer in answers if answer.is_correct) / len(answers)
            }
        }

class AdaptiveScoringStrategy(ScoringStrategyBase):
    def calculate_score(self, answers: List[QuestionAnswer], **kwargs) -> Dict[str, Any]:
        user_history = kwargs.get('user_history', {})
        avg_performance = user_history.get('average_score', 50)
        
        # Base weighted score
        weighted_strategy = WeightedScoringStrategy()
        base_result = weighted_strategy.calculate_score(answers)
        base_score = base_result["raw_score"]
        
        # Performance factor (how user performs relative to their history)
        performance_factor = self._calculate_performance_factor(answers, avg_performance)
        
        # Difficulty progression factor
        difficulty_factor = self._calculate_difficulty_progression(answers)
        
        # Time efficiency factor
        time_factor = self._calculate_time_efficiency(answers)
        
        # Adaptive adjustment
        adaptive_multiplier = (performance_factor + difficulty_factor + time_factor) / 3
        adaptive_score = base_score * adaptive_multiplier
        
        # Ensure score stays within bounds
        adaptive_score = max(0, min(100, adaptive_score))
        
        return {
            "raw_score": adaptive_score,
            "details": {
                **base_result["details"],
                "performance_factor": performance_factor,
                "difficulty_factor": difficulty_factor,
                "time_factor": time_factor,
                "adaptive_multiplier": adaptive_multiplier,
                "base_score": base_score
            }
        }
    
    def _calculate_performance_factor(self, answers: List[QuestionAnswer], avg_performance: float) -> float:
        current_accuracy = sum(1 for a in answers if a.is_correct) / len(answers) * 100
        if avg_performance == 0:
            return 1.0
        return min(1.5, max(0.5, current_accuracy / avg_performance))
    
    def _calculate_difficulty_progression(self, answers: List[QuestionAnswer]) -> float:
        difficulties = [a.difficulty for a in answers]
        if len(difficulties) < 2:
            return 1.0
        
        # Reward consistent performance on increasing difficulty
        progression_score = 1.0
        for i in range(1, len(answers)):
            if answers[i].difficulty > answers[i-1].difficulty and answers[i].is_correct:
                progression_score += 0.05
        
        return min(1.3, progression_score)
    
    def _calculate_time_efficiency(self, answers: List[QuestionAnswer]) -> float:
        if not answers:
            return 1.0
        
        # Calculate time efficiency relative to difficulty
        efficiency_scores = []
        for answer in answers:
            expected_time = answer.difficulty * 30  # 30 seconds per difficulty level
            if answer.time_taken > 0:
                efficiency = expected_time / answer.time_taken
                efficiency_scores.append(min(1.5, max(0.5, efficiency)))
        
        return np.mean(efficiency_scores) if efficiency_scores else 1.0

class ConfidenceScoringStrategy(ScoringStrategyBase):
    def calculate_score(self, answers: List[QuestionAnswer], **kwargs) -> Dict[str, Any]:
        if not answers:
            return {"raw_score": 0, "details": {"confidence_adjusted": 0, "penalties": 0}}
        
        # Base weighted score
        weighted_strategy = WeightedScoringStrategy()
        base_result = weighted_strategy.calculate_score(answers)
        base_score = base_result["raw_score"]
        
        confidence_bonus = 0
        confidence_penalty = 0
        
        for answer in answers:
            if answer.confidence is None:
                continue
                
            # Confidence factor (1-5 scale)
            confidence_factor = answer.confidence / 5.0
            
            if answer.is_correct:
                # Reward high confidence on correct answers
                confidence_bonus += confidence_factor * answer.weight * 2
            else:
                # Penalize high confidence on wrong answers
                confidence_penalty += confidence_factor * answer.weight * 3
        
        # Apply confidence adjustments
        confidence_adjusted_score = base_score + confidence_bonus - confidence_penalty
        confidence_adjusted_score = max(0, min(100, confidence_adjusted_score))
        
        return {
            "raw_score": confidence_adjusted_score,
            "details": {
                **base_result["details"],
                "base_score": base_score,
                "confidence_bonus": confidence_bonus,
                "confidence_penalty": confidence_penalty,
                "confidence_adjustment": confidence_bonus - confidence_penalty
            }
        }

class ScoringStrategyFactory:
    _strategies = {
        ScoringStrategy.BASIC: BasicScoringStrategy,
        ScoringStrategy.WEIGHTED: WeightedScoringStrategy,
        ScoringStrategy.ADAPTIVE: AdaptiveScoringStrategy,
        ScoringStrategy.CONFIDENCE: ConfidenceScoringStrategy
    }
    
    @classmethod
    def create_strategy(cls, strategy_type: ScoringStrategy) -> ScoringStrategyBase:
        strategy_class = cls._strategies.get(strategy_type)
        if not strategy_class:
            raise ValueError(f"Unknown scoring strategy: {strategy_type}")
        return strategy_class()
