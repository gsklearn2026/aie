from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import re
from loguru import logger
import asyncio
import time

@dataclass
class SemanticValidationResult:
    is_valid: bool
    score: float
    details: Dict[str, Any]
    errors: List[str]
    metrics: Dict[str, float]

class SemanticValidator:
    """
    Validates semantic quality of AI responses
    """
    
    def __init__(self):
        self.min_coherence_score = 0.6
        self.min_relevance_score = 0.7
        self.min_completeness_score = 0.5
        
    def validate_response(self, response: str, criteria: Optional[Dict[str, Any]] = None) -> SemanticValidationResult:
        """
        Validate semantic quality of AI response
        
        Args:
            response: The AI response to validate
            criteria: Optional validation criteria
            
        Returns:
            SemanticValidationResult object with validation results
        """
        if criteria is None:
            criteria = {}
            
        errors = []
        metrics = {}
        details = {}
        
        try:
            # Basic semantic checks
            coherence_score = self._check_coherence(response)
            relevance_score = self._check_relevance(response, criteria)
            completeness_score = self._check_completeness(response, criteria)
            readability_score = self._check_readability(response)
            
            metrics = {
                'coherence': coherence_score,
                'relevance': relevance_score,
                'completeness': completeness_score,
                'readability': readability_score
            }
            
            # Check against thresholds
            if coherence_score < self.min_coherence_score:
                errors.append(f"Coherence score {coherence_score:.2f} below minimum {self.min_coherence_score}")
                
            if relevance_score < self.min_relevance_score:
                errors.append(f"Relevance score {relevance_score:.2f} below minimum {self.min_relevance_score}")
                
            if completeness_score < self.min_completeness_score:
                errors.append(f"Completeness score {completeness_score:.2f} below minimum {self.min_completeness_score}")
            
            # Overall score calculation
            overall_score = (coherence_score + relevance_score + completeness_score + readability_score) / 4
            
            # Detailed analysis
            details = {
                'word_count': len(response.split()),
                'sentence_count': len(re.findall(r'[.!?]+', response)),
                'paragraph_count': len(response.split('\n\n')),
                'avg_sentence_length': self._calculate_avg_sentence_length(response),
                'topic_coverage': self._analyze_topic_coverage(response, criteria),
                'structure_quality': self._analyze_structure(response)
            }
            
            is_valid = len(errors) == 0 and overall_score >= 0.6
            
            return SemanticValidationResult(
                is_valid=is_valid,
                score=overall_score,
                details=details,
                errors=errors,
                metrics=metrics
            )
            
        except Exception as e:
            logger.error(f"Semantic validation failed: {e}")
            return SemanticValidationResult(
                is_valid=False,
                score=0.0,
                details={'error': str(e)},
                errors=[f"Validation error: {str(e)}"],
                metrics={}
            )
    
    def _check_coherence(self, response: str) -> float:
        """Check response coherence using simple heuristics"""
        if not response or len(response.strip()) < 10:
            return 0.0
            
        # Simple coherence checks
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 1:
            return 0.0
            
        coherence_score = 0.5  # Base score
        
        # Check for repeated words/phrases (indicates coherence issues)
        words = response.lower().split()
        if len(set(words)) / len(words) > 0.7:  # Good vocabulary diversity
            coherence_score += 0.2
            
        # Check for logical flow markers
        flow_markers = ['however', 'therefore', 'furthermore', 'moreover', 'consequently', 'thus']
        if any(marker in response.lower() for marker in flow_markers):
            coherence_score += 0.2
            
        # Check sentence length variation (coherent text has varied sentence lengths)
        sentence_lengths = [len(s.split()) for s in sentences]
        if len(sentence_lengths) > 1:
            length_variance = max(sentence_lengths) - min(sentence_lengths)
            if length_variance > 5:  # Good variation
                coherence_score += 0.1
                
        return min(coherence_score, 1.0)
    
    def _check_relevance(self, response: str, criteria: Dict[str, Any]) -> float:
        """Check response relevance to expected topics"""
        if not response:
            return 0.0
            
        relevance_score = 0.5  # Base score
        
        # Check for expected keywords
        expected_keywords = criteria.get('expected_keywords', [])
        if expected_keywords:
            response_lower = response.lower()
            found_keywords = [kw for kw in expected_keywords if kw.lower() in response_lower]
            keyword_score = len(found_keywords) / len(expected_keywords)
            relevance_score += keyword_score * 0.4
            
        # Check for expected topics
        expected_topics = criteria.get('expected_topics', [])
        if expected_topics:
            response_lower = response.lower()
            found_topics = [topic for topic in expected_topics if topic.lower() in response_lower]
            topic_score = len(found_topics) / len(expected_topics)
            relevance_score += topic_score * 0.3
            
        return min(relevance_score, 1.0)
    
    def _check_completeness(self, response: str, criteria: Dict[str, Any]) -> float:
        """Check response completeness"""
        if not response:
            return 0.0
            
        completeness_score = 0.0
        
        # Check minimum length
        min_length = criteria.get('min_length', 50)
        if len(response) >= min_length:
            completeness_score += 0.4
        else:
            completeness_score += (len(response) / min_length) * 0.4
            
        # Check for complete sentences
        sentences = re.findall(r'[.!?]+', response)
        if len(sentences) >= 2:
            completeness_score += 0.3
            
        # Check for structured content
        if any(marker in response for marker in [':', '-', '•', '1.', '2.', '3.']):
            completeness_score += 0.2
            
        # Check for conclusion indicators
        conclusion_markers = ['conclusion', 'summary', 'in summary', 'to conclude', 'finally']
        if any(marker in response.lower() for marker in conclusion_markers):
            completeness_score += 0.1
            
        return min(completeness_score, 1.0)
    
    def _check_readability(self, response: str) -> float:
        """Check response readability using simple metrics"""
        if not response:
            return 0.0
            
        readability_score = 0.5  # Base score
        
        # Check average sentence length (10-20 words is good)
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if sentences:
            avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
            if 10 <= avg_sentence_length <= 20:
                readability_score += 0.3
            elif 5 <= avg_sentence_length <= 30:
                readability_score += 0.2
                
        # Check for complex punctuation usage
        if any(punct in response for punct in [';', ':', '—', '–']):
            readability_score += 0.1
            
        # Check for paragraph structure
        paragraphs = response.split('\n\n')
        if len(paragraphs) > 1:
            readability_score += 0.1
            
        return min(readability_score, 1.0)
    
    def _calculate_avg_sentence_length(self, response: str) -> float:
        """Calculate average sentence length in words"""
        sentences = re.split(r'[.!?]+', response)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
            
        total_words = sum(len(s.split()) for s in sentences)
        return total_words / len(sentences)
    
    def _analyze_topic_coverage(self, response: str, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how well the response covers expected topics"""
        expected_topics = criteria.get('expected_topics', [])
        if not expected_topics:
            return {'coverage': 'N/A', 'topics_found': []}
            
        response_lower = response.lower()
        topics_found = [topic for topic in expected_topics if topic.lower() in response_lower]
        coverage_percent = (len(topics_found) / len(expected_topics)) * 100
        
        return {
            'coverage': f"{coverage_percent:.1f}%",
            'topics_found': topics_found,
            'topics_missing': [topic for topic in expected_topics if topic not in topics_found]
        }
    
    def _analyze_structure(self, response: str) -> Dict[str, Any]:
        """Analyze response structure quality"""
        structure_analysis = {
            'has_introduction': False,
            'has_body': False,
            'has_conclusion': False,
            'uses_lists': False,
            'uses_examples': False
        }
        
        response_lower = response.lower()
        
        # Check for introduction indicators
        intro_markers = ['introduction', 'first', 'initially', 'to begin', 'starting']
        structure_analysis['has_introduction'] = any(marker in response_lower for marker in intro_markers)
        
        # Check for body content (middle section)
        body_markers = ['furthermore', 'additionally', 'moreover', 'also', 'next']
        structure_analysis['has_body'] = any(marker in response_lower for marker in body_markers)
        
        # Check for conclusion indicators
        conclusion_markers = ['conclusion', 'finally', 'in summary', 'to conclude']
        structure_analysis['has_conclusion'] = any(marker in response_lower for marker in conclusion_markers)
        
        # Check for lists
        structure_analysis['uses_lists'] = any(marker in response for marker in ['•', '-', '1.', '2.', '3.'])
        
        # Check for examples
        example_markers = ['example', 'instance', 'such as', 'for example']
        structure_analysis['uses_examples'] = any(marker in response_lower for marker in example_markers)
        
        return structure_analysis
    
    async def validate_response_async(self, response: str, criteria: Optional[Dict[str, Any]] = None) -> SemanticValidationResult:
        """Async version of validate_response"""
        # Run validation in executor to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.validate_response, response, criteria) 