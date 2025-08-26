import asyncio
import numpy as np
from typing import Dict, List, Tuple
import time
import anthropic
import json
from app.core.config import settings
from services.feature_extraction.extractor import FeatureExtractor
from models.schemas.difficulty import (
    DifficultyLevel, QuestionRequest, DifficultyResponse, 
    FeatureVector, QuestionType
)

class DifficultyClassifier:
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.anthropic_client = None
        self.cache = {}  # Simple in-memory cache
        
    async def initialize(self):
        """Initialize the classifier and its dependencies"""
        if settings.anthropic_api_key != "your-anthropic-api-key":
            self.anthropic_client = anthropic.Anthropic(
                api_key=settings.anthropic_api_key
            )
        print("✅ Difficulty Classifier initialized")
    
    def _compute_base_difficulty(self, features: Dict[str, float]) -> float:
        """Compute base difficulty score from extracted features"""
        # Weighted combination of key features
        weights = {
            'flesch_kincaid': 0.15,
            'gunning_fog': 0.15,
            'avg_sentence_length': 0.10,
            'difficult_word_ratio': 0.20,
            'vocabulary_diversity': 0.10,
            'question_type_complexity': 0.15,
            'subject_complexity': 0.10,
            'dependency_depth': 0.05
        }
        
        # Normalize features to 0-1 range
        normalized_features = self._normalize_features(features)
        
        # Calculate weighted score
        score = 0.0
        total_weight = 0.0
        
        for feature, weight in weights.items():
            if feature in normalized_features:
                score += normalized_features[feature] * weight
                total_weight += weight
        
        # Ensure score is between 0 and 1
        final_score = score / max(total_weight, 1.0)
        return max(0.0, min(1.0, final_score))
    
    def _normalize_features(self, features: Dict[str, float]) -> Dict[str, float]:
        """Normalize features to 0-1 range using reasonable bounds"""
        normalization_bounds = {
            'flesch_kincaid': (0, 18),
            'gunning_fog': (6, 20),
            'avg_sentence_length': (5, 30),
            'difficult_word_ratio': (0, 0.5),
            'vocabulary_diversity': (0.2, 1.0),
            'question_type_complexity': (0, 1),
            'subject_complexity': (0, 1),
            'dependency_depth': (0, 10)
        }
        
        normalized = {}
        for feature, value in features.items():
            if feature in normalization_bounds:
                min_val, max_val = normalization_bounds[feature]
                normalized[feature] = (value - min_val) / max(max_val - min_val, 1)
                normalized[feature] = max(0.0, min(1.0, normalized[feature]))
            else:
                normalized[feature] = value
        
        return normalized
    
    def _score_to_difficulty_level(self, score: float) -> DifficultyLevel:
        """Convert difficulty score to categorical level"""
        if score < 0.25:
            return DifficultyLevel.BEGINNER
        elif score < 0.5:
            return DifficultyLevel.INTERMEDIATE  
        elif score < 0.75:
            return DifficultyLevel.ADVANCED
        else:
            return DifficultyLevel.EXPERT
    
    async def _get_ai_enhancement(self, question_text: str, base_score: float) -> Tuple[float, str, float]:
        """Use Anthropic Claude to enhance classification with reasoning"""
        if not self.anthropic_client:
            return base_score, "Rule-based classification only", 0.8
        
        prompt = f"""Analyze this educational question for difficulty level:

Question: "{question_text}"

Base difficulty score (0-1): {base_score:.2f}

Consider these factors:
1. Cognitive complexity (recall vs analysis vs synthesis)
2. Prior knowledge requirements  
3. Multi-step reasoning needs
4. Abstract vs concrete concepts

Respond with JSON only:
{{
    "adjusted_score": <float 0-1>,
    "confidence": <float 0-1>, 
    "reasoning": "<brief explanation>"
}}"""

        try:
            response = await asyncio.to_thread(
                self.anthropic_client.messages.create,
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            result = json.loads(response.content[0].text.strip())
            return (
                float(result.get("adjusted_score", base_score)),
                result.get("reasoning", "AI-enhanced classification"),
                float(result.get("confidence", 0.8))
            )
        except Exception as e:
            print(f"AI enhancement failed: {e}")
            return base_score, "Rule-based classification (AI unavailable)", 0.7
    
    async def classify_question(self, request: QuestionRequest) -> DifficultyResponse:
        """Classify a single question's difficulty"""
        start_time = time.time()
        
        # Check cache first
        cache_key = f"{hash(request.question_text)}_{request.question_type}_{request.subject}"
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            cached_result.processing_time_ms = (time.time() - start_time) * 1000
            return cached_result
        
        # Extract features
        features = self.feature_extractor.extract_all_features(
            request.question_text, 
            request.question_type,
            request.subject
        )
        
        # Compute base difficulty
        base_score = self._compute_base_difficulty(features)
        
        # Enhance with AI if available
        adjusted_score, reasoning, confidence = await self._get_ai_enhancement(
            request.question_text, base_score
        )
        
        # Create feature vector for response
        feature_vector = FeatureVector(
            readability_score=features.get('flesch_kincaid', 0),
            syntactic_complexity=features.get('avg_sentence_length', 0) / 30,
            vocabulary_difficulty=features.get('difficult_word_ratio', 0),
            concept_density=features.get('vocabulary_diversity', 0),
            cognitive_load=adjusted_score,
            question_type_complexity=features.get('question_type_complexity', 0)
        )
        
        # Create response
        result = DifficultyResponse(
            difficulty_level=self._score_to_difficulty_level(adjusted_score),
            difficulty_score=adjusted_score,
            confidence=confidence,
            features=feature_vector,
            processing_time_ms=(time.time() - start_time) * 1000,
            reasoning=reasoning
        )
        
        # Cache result
        self.cache[cache_key] = result
        
        return result
    
    async def classify_batch(self, questions: List[QuestionRequest]) -> List[DifficultyResponse]:
        """Classify multiple questions efficiently"""
        tasks = [self.classify_question(q) for q in questions]
        return await asyncio.gather(*tasks)
