import google.generativeai as genai
from app.config import get_settings
from app.monitoring import ai_requests, ai_request_duration
import time
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

genai.configure(api_key=settings.gemini_api_key)

class AIService:
    def __init__(self):
        self.model = genai.GenerativeModel(settings.gemini_model)
    
    async def generate_quiz(self, topic: str, num_questions: int = 5):
        """Generate quiz questions using AI"""
        start_time = time.time()
        
        try:
            prompt = f"""Generate {num_questions} multiple-choice quiz questions about {topic}.
            
Return a JSON array with this exact structure:
[
  {{
    "question": "question text",
    "options": ["option1", "option2", "option3", "option4"],
    "correct_answer": 0,
    "explanation": "why this is correct"
  }}
]

Make questions challenging but fair. Include detailed explanations."""
            
            response = self.model.generate_content(prompt)
            duration = time.time() - start_time
            
            ai_requests.labels(status="success").inc()
            ai_request_duration.observe(duration)
            
            # Parse response
            import json
            text = response.text
            # Clean markdown code blocks if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            
            questions = json.loads(text.strip())
            return questions
            
        except Exception as e:
            logger.error(f"AI generation failed: {e}", exc_info=True)
            ai_requests.labels(status="error").inc()
            
            # Check for quota/rate limit errors
            error_str = str(e)
            
            # Extract retry delay if available
            retry_seconds = None
            if "retry_delay" in error_str or "retry in" in error_str.lower():
                import re
                retry_match = re.search(r'retry in ([\d.]+)s', error_str, re.IGNORECASE)
                if retry_match:
                    retry_seconds = int(float(retry_match.group(1))) + 1  # Add 1 second buffer
            
            # Check for quota/rate limit errors - be more specific
            if ("429" in error_str or 
                "quota exceeded" in error_str.lower() or 
                "quota" in error_str.lower() and "exceeded" in error_str.lower() or
                "rate limit" in error_str.lower()):
                
                # Create a clean, user-friendly error message
                message = "The AI service quota has been exceeded. "
                if retry_seconds:
                    message += f"Please try again in {retry_seconds} seconds."
                else:
                    message += "Please try again later."
                
                # Store retry info in a format the router can parse
                raise ValueError(f"QUOTA_ERROR:{message}:RETRY:{retry_seconds or 60}")
            elif "api key" in error_str.lower() or "authentication" in error_str.lower() or "unauthorized" in error_str.lower():
                raise ValueError(
                    "AUTH_ERROR:AI service authentication failed. Please check your Google Generative AI API key configuration."
                )
            else:
                # For other errors, provide a generic message to avoid exposing technical details
                raise ValueError("GENERAL_ERROR:AI generation failed. Please try again later or contact support if the issue persists.")
