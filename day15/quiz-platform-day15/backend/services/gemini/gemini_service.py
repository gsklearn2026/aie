import google.generativeai as genai
from app.core.config import settings
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    def __init__(self):
        """Initialize Gemini service with API key"""
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def classify_question_difficulty(
        self, 
        question_text: str, 
        subject: str, 
        question_type: str
    ) -> Dict[str, Any]:
        """
        Classify question difficulty using Gemini AI
        
        Args:
            question_text: The question text to analyze
            subject: Subject area (e.g., mathematics, physics, etc.)
            question_type: Type of question (multiple_choice, essay, etc.)
            
        Returns:
            Dictionary containing difficulty classification and confidence
        """
        try:
            # Create a detailed prompt for difficulty classification
            prompt = f"""
            Analyze the following question and classify its difficulty level.
            
            Question: {question_text}
            Subject: {subject}
            Question Type: {question_type}
            
            Please classify the difficulty as one of the following:
            - "beginner": Basic concepts, simple calculations, straightforward answers
            - "intermediate": Moderate complexity, requires some analysis or multi-step thinking
            - "advanced": Complex concepts, requires deep understanding, synthesis of multiple ideas
            - "expert": Very complex, requires expert-level knowledge, advanced problem-solving
            
            Consider factors like:
            - Vocabulary complexity
            - Conceptual depth
            - Required background knowledge
            - Problem-solving complexity
            - Cognitive load
            
            Respond with a JSON object containing:
            {{
                "difficulty": "beginner|intermediate|advanced|expert",
                "confidence": 0.0-1.0,
                "reasoning": "Brief explanation of the classification",
                "features": {{
                    "vocabulary_complexity": "low|medium|high",
                    "conceptual_depth": "low|medium|high",
                    "problem_solving_complexity": "low|medium|high"
                }}
            }}
            """
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            # Parse the response (assuming it returns valid JSON)
            import json
            try:
                result = json.loads(response.text)
                return {
                    "difficulty": result.get("difficulty", "intermediate"),
                    "confidence": result.get("confidence", 0.5),
                    "reasoning": result.get("reasoning", "AI analysis completed"),
                    "features": result.get("features", {}),
                    "model": "gemini-pro",
                    "api_provider": "google"
                }
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                logger.warning("Failed to parse Gemini response as JSON, using fallback")
                return {
                    "difficulty": "intermediate",
                    "confidence": 0.5,
                    "reasoning": "AI analysis completed (fallback response)",
                    "features": {
                        "vocabulary_complexity": "medium",
                        "conceptual_depth": "medium", 
                        "problem_solving_complexity": "medium"
                    },
                    "model": "gemini-pro",
                    "api_provider": "google"
                }
                
        except Exception as e:
            logger.error(f"Error in Gemini classification: {str(e)}")
            return {
                "difficulty": "intermediate",
                "confidence": 0.0,
                "reasoning": f"Error occurred: {str(e)}",
                "features": {},
                "model": "gemini-pro",
                "api_provider": "google"
            }
    
    async def get_question_analysis(
        self, 
        question_text: str, 
        subject: str, 
        question_type: str
    ) -> Dict[str, Any]:
        """
        Get detailed analysis of a question including difficulty and educational insights
        
        Args:
            question_text: The question text to analyze
            subject: Subject area
            question_type: Type of question
            
        Returns:
            Dictionary containing comprehensive analysis
        """
        try:
            prompt = f"""
            Provide a comprehensive analysis of the following educational question:
            
            Question: {question_text}
            Subject: {subject}
            Question Type: {question_type}
            
            Please provide a detailed analysis including:
            1. Difficulty level assessment
            2. Key concepts being tested
            3. Prerequisites needed
            4. Learning objectives
            5. Potential misconceptions
            6. Suggested teaching strategies
            
            Respond with a JSON object containing:
            {{
                "difficulty": "beginner|intermediate|advanced|expert",
                "confidence": 0.0-1.0,
                "key_concepts": ["concept1", "concept2"],
                "prerequisites": ["prerequisite1", "prerequisite2"],
                "learning_objectives": ["objective1", "objective2"],
                "potential_misconceptions": ["misconception1", "misconception2"],
                "teaching_strategies": ["strategy1", "strategy2"],
                "estimated_time": "time_estimate",
                "cognitive_demand": "low|medium|high"
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            import json
            try:
                result = json.loads(response.text)
                return {
                    **result,
                    "model": "gemini-pro",
                    "api_provider": "google"
                }
            except json.JSONDecodeError:
                logger.warning("Failed to parse detailed analysis response as JSON")
                return {
                    "difficulty": "intermediate",
                    "confidence": 0.5,
                    "key_concepts": [],
                    "prerequisites": [],
                    "learning_objectives": [],
                    "potential_misconceptions": [],
                    "teaching_strategies": [],
                    "estimated_time": "5-10 minutes",
                    "cognitive_demand": "medium",
                    "model": "gemini-pro",
                    "api_provider": "google"
                }
                
        except Exception as e:
            logger.error(f"Error in detailed question analysis: {str(e)}")
            return {
                "difficulty": "intermediate",
                "confidence": 0.0,
                "error": str(e),
                "model": "gemini-pro",
                "api_provider": "google"
            } 