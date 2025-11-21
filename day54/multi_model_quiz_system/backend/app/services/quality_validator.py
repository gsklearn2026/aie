from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class QualityValidator:
    """Validates generated question quality"""
    
    def validate_question(self, question_data: Dict[str, Any], question_type: str) -> float:
        """Validate question and return quality score (0-5)"""
        
        score = 5.0  # Start with perfect score
        
        # Check required fields
        if not question_data.get("question"):
            logger.warning("Missing question text")
            return 0
        
        # Type-specific validation
        if question_type == "multiple_choice":
            score = self._validate_multiple_choice(question_data, score)
        elif question_type == "true_false":
            score = self._validate_true_false(question_data, score)
        elif question_type == "short_answer":
            score = self._validate_short_answer(question_data, score)
        elif question_type == "essay":
            score = self._validate_essay(question_data, score)
        elif question_type == "coding":
            score = self._validate_coding(question_data, score)
        
        # General quality checks
        question_text = question_data.get("question", "")
        
        # Check length
        if len(question_text) < 10:
            score -= 1.0
            logger.warning("Question too short")
        
        if len(question_text) > 500:
            score -= 0.5
            logger.warning("Question very long")
        
        # Check clarity (simple heuristics)
        if "?" not in question_text and question_type != "true_false":
            score -= 0.5
            logger.warning("Question missing question mark")
        
        return max(0, min(5.0, score))
    
    def _validate_multiple_choice(self, data: Dict[str, Any], score: float) -> float:
        """Validate multiple choice question"""
        
        if not data.get("options"):
            logger.warning("Missing options")
            return 0
        
        if len(data["options"]) != 4:
            score -= 1.0
            logger.warning(f"Expected 4 options, got {len(data['options'])}")
        
        if not data.get("correct_answer"):
            logger.warning("Missing correct answer")
            return 0
        
        if not data.get("explanation"):
            score -= 0.5
            logger.warning("Missing explanation")
        
        return score
    
    def _validate_true_false(self, data: Dict[str, Any], score: float) -> float:
        """Validate true/false question"""
        
        correct = data.get("correct_answer", "").lower()
        if correct not in ["true", "false"]:
            logger.warning("Invalid true/false answer")
            return 0
        
        if not data.get("explanation"):
            score -= 0.5
        
        return score
    
    def _validate_short_answer(self, data: Dict[str, Any], score: float) -> float:
        """Validate short answer question"""
        
        if not data.get("correct_answer"):
            logger.warning("Missing correct answer")
            return 0
        
        if len(data.get("correct_answer", "")) < 3:
            score -= 1.0
        
        return score
    
    def _validate_essay(self, data: Dict[str, Any], score: float) -> float:
        """Validate essay question"""
        
        if not data.get("guidance"):
            score -= 0.5
            logger.warning("Missing guidance")
        
        return score
    
    def _validate_coding(self, data: Dict[str, Any], score: float) -> float:
        """Validate coding question"""
        
        if not data.get("requirements"):
            score -= 1.0
        
        if not data.get("test_cases"):
            score -= 0.5
        
        return score

validator = QualityValidator()
