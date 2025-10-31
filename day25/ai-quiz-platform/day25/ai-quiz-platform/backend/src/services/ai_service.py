import google.generativeai as genai
from typing import Dict, List, Any
from src.core.circuit_breaker import CircuitBreaker
from src.core.retry_handler import RetryHandler
from src.models.errors import ErrorType
import structlog
import os

logger = structlog.get_logger()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        
        # Circuit breaker for AI service
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        
        # Fallback questions for when AI fails
        self.fallback_questions = [
            {
                "question": "What is the primary goal of machine learning?",
                "options": ["To replace humans", "To find patterns in data", "To create robots", "To build websites"],
                "correct_answer": "To find patterns in data",
                "explanation": "Machine learning focuses on finding patterns and making predictions from data."
            },
            {
                "question": "Which algorithm is commonly used for classification?",
                "options": ["Linear Regression", "Decision Tree", "K-means", "PCA"],
                "correct_answer": "Decision Tree",
                "explanation": "Decision trees are popular classification algorithms that create decision rules."
            }
        ]
    
    async def generate_quiz_questions(self, topic: str, difficulty: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions with error handling and fallback"""
        
        try:
            # Use circuit breaker
            questions = await self.circuit_breaker.call(
                self._generate_questions_with_ai, topic, difficulty, count
            )
            return questions
            
        except Exception as e:
            logger.warning(
                "AI service failed, using fallback questions",
                error=str(e),
                topic=topic,
                difficulty=difficulty
            )
            # Return fallback questions
            return self.fallback_questions[:count]
    
    async def _generate_questions_with_ai(self, topic: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate questions using AI with retry logic"""
        
        if not self.api_key:
            raise Exception("Gemini API key not configured")
        
        prompt = f"""
        Generate {count} multiple choice questions about {topic} with {difficulty} difficulty level.
        
        Return as JSON array with this format:
        [
            {{
                "question": "Question text",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Correct option text",
                "explanation": "Brief explanation"
            }}
        ]
        """
        
        try:
            # Execute with retry logic for AI service errors
            response = await RetryHandler.execute_with_retry(
                self._call_gemini_api,
                ErrorType.AI_SERVICE_ERROR,
                max_attempts=3,
                prompt=prompt
            )
            
            # Parse response (simplified for demo)
            questions = self._parse_ai_response(response.text)
            
            if not questions:
                raise Exception("AI returned empty response")
                
            return questions
            
        except Exception as e:
            logger.error("Failed to generate questions with AI", error=str(e))
            raise
    
    def _call_gemini_api(self, prompt: str):
        """Call Gemini API"""
        return self.model.generate_content(prompt)
    
    def _parse_ai_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse AI response into question format"""
        # Simplified parsing - in production, use proper JSON parsing
        try:
            import json
            # Extract JSON from response
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end != 0:
                return json.loads(response_text[start:end])
        except:
            pass
        
        # Return fallback if parsing fails
        return self.fallback_questions
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for monitoring"""
        return self.circuit_breaker.get_state()
