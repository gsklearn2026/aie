import google.generativeai as genai
import time
from typing import Dict, Any, Optional
from ..config.manager import config
import logging

logger = logging.getLogger(__name__)

class GeminiService:
    """Environment-aware Gemini AI service"""
    
    def __init__(self):
        self.client = None
        self.model = None
        self.rate_limiter = RateLimiter()
        self.setup_client()
    
    def setup_client(self):
        """Setup Gemini client with environment-specific configuration"""
        gemini_config = config.get_gemini_config()
        
        api_key = gemini_config.get('api_key')
        if not api_key and not config.is_development():
            raise ValueError("Gemini API key not configured")
        
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel(gemini_config.get('model', 'gemini-pro'))
            
        # Setup rate limiter
        self.rate_limiter.set_limit(gemini_config.get('rate_limit_per_minute', 60))
        
        logger.info("Gemini AI service configured")
    
    async def generate_quiz_question(self, topic: str, difficulty: str) -> Optional[Dict[str, Any]]:
        """Generate quiz question with environment-aware rate limiting"""
        if not self.model and not config.is_development():
            logger.error("Gemini model not available")
            return None
        
        # Rate limiting check
        if not self.rate_limiter.can_proceed():
            logger.warning("Rate limit exceeded")
            return None
        
        try:
            # In development, return mock data if no API key
            if config.is_development() and not config.get('gemini.api_key'):
                return self._get_mock_question(topic, difficulty)
            
            prompt = f"""
            Generate a {difficulty} level quiz question about {topic}.
            Return a JSON object with:
            - question: the question text
            - options: array of 4 multiple choice options
            - correct_answer: index of correct option (0-3)
            - explanation: brief explanation of the answer
            """
            
            response = self.model.generate_content(prompt)
            
            # Track rate limiting
            self.rate_limiter.record_request()
            
            # Parse response (simplified for demo)
            return {
                "question": f"What is the main concept of {topic}?",
                "options": [
                    "Option A - Correct concept",
                    "Option B - Incorrect",
                    "Option C - Incorrect",
                    "Option D - Incorrect"
                ],
                "correct_answer": 0,
                "explanation": f"The correct answer demonstrates understanding of {topic}."
            }
            
        except Exception as e:
            logger.error(f"Error generating quiz question: {e}")
            return None
    
    def _get_mock_question(self, topic: str, difficulty: str) -> Dict[str, Any]:
        """Generate mock question for development environment"""
        return {
            "question": f"[DEV MODE] What is a key aspect of {topic}?",
            "options": [
                f"Primary concept of {topic}",
                "Unrelated concept A",
                "Unrelated concept B",  
                "Unrelated concept C"
            ],
            "correct_answer": 0,
            "explanation": f"This is a development mode mock question for {topic} at {difficulty} level."
        }
    
    def health_check(self) -> bool:
        """Check Gemini service health"""
        try:
            if not self.model:
                return config.is_development()  # OK in dev mode without API key
            
            # Simple test request
            response = self.model.generate_content("Hello")
            return bool(response)
        except Exception as e:
            logger.error(f"Gemini health check failed: {e}")
            return False

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self):
        self.requests = []
        self.limit = 60  # requests per minute
    
    def set_limit(self, limit: int):
        """Set rate limit"""
        self.limit = limit
    
    def can_proceed(self) -> bool:
        """Check if request can proceed"""
        now = time.time()
        # Remove requests older than 1 minute
        self.requests = [req_time for req_time in self.requests if now - req_time < 60]
        
        return len(self.requests) < self.limit
    
    def record_request(self):
        """Record a request"""
        self.requests.append(time.time())

# Global Gemini service instance
gemini_service = GeminiService()
