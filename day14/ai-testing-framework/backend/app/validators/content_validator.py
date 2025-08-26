from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    score: float
    details: Dict[str, Any]
    errors: List[str]

class ContentValidator:
    def __init__(self):
        self.min_word_count = 5
        self.max_word_count = 2000
        self.required_patterns = []
        
    def validate_response(self, content: str, criteria: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate AI response content against criteria"""
        criteria = criteria or {}
        errors = []
        details = {}
        
        # Basic content validation
        word_count = len(content.split())
        details["word_count"] = word_count
        
        if word_count < criteria.get("min_words", self.min_word_count):
            errors.append(f"Content too short: {word_count} words")
        
        if word_count > criteria.get("max_words", self.max_word_count):
            errors.append(f"Content too long: {word_count} words")
        
        # Required keywords validation
        required_keywords = criteria.get("required_keywords", [])
        found_keywords = []
        for keyword in required_keywords:
            if keyword.lower() in content.lower():
                found_keywords.append(keyword)
        
        details["found_keywords"] = found_keywords
        details["keyword_coverage"] = len(found_keywords) / len(required_keywords) if required_keywords else 1.0
        
        if len(found_keywords) < len(required_keywords) * 0.5:  # At least 50% keyword coverage
            errors.append(f"Insufficient keyword coverage: {len(found_keywords)}/{len(required_keywords)}")
        
        # Content structure validation
        sentence_count = self._count_sentences(content)
        details["sentence_count"] = sentence_count
        
        if sentence_count == 0:
            errors.append("No complete sentences found")
        
        # Language quality checks
        details["has_profanity"] = self._check_profanity(content)
        details["coherence_score"] = self._assess_coherence(content)
        
        if details["has_profanity"]:
            errors.append("Content contains inappropriate language")
        
        # Calculate overall score
        score = self._calculate_score(details, criteria)
        details["overall_score"] = score
        
        return ValidationResult(
            is_valid=len(errors) == 0 and score >= criteria.get("min_score", 0.6),
            score=score,
            details=details,
            errors=errors
        )
    
    def _count_sentences(self, content: str) -> int:
        """Count sentences in content"""
        sentence_endings = ['.', '!', '?']
        return sum(content.count(ending) for ending in sentence_endings)
    
    def _check_profanity(self, content: str) -> bool:
        """Basic profanity check (can be enhanced with external libraries)"""
        profanity_words = ['damn', 'hell']  # Basic list, extend as needed
        return any(word in content.lower() for word in profanity_words)
    
    def _assess_coherence(self, content: str) -> float:
        """Simple coherence assessment based on text structure"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Simple heuristics for coherence
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        length_score = min(1.0, avg_sentence_length / 15)  # Optimal around 15 words
        
        # Check for repeated phrases (sign of poor coherence)
        words = content.lower().split()
        unique_words = set(words)
        uniqueness_score = len(unique_words) / len(words) if words else 0
        
        return (length_score + uniqueness_score) / 2
    
    def _calculate_score(self, details: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Calculate overall content score"""
        score_components = []
        
        # Word count score
        word_count = details["word_count"]
        target_words = criteria.get("target_words", 100)
        word_score = max(0, 1 - abs(word_count - target_words) / target_words)
        score_components.append(word_score * 0.2)
        
        # Keyword coverage score
        score_components.append(details["keyword_coverage"] * 0.3)
        
        # Structure score
        if details["sentence_count"] > 0:
            score_components.append(0.2)
        
        # Coherence score
        score_components.append(details["coherence_score"] * 0.2)
        
        # Quality penalty for profanity
        if not details["has_profanity"]:
            score_components.append(0.1)
        
        return sum(score_components)
