import google.generativeai as genai
from app.core.config import settings
from typing import List, Dict, Any
import json
import asyncio

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def generate_quiz_questions(self, topic: str, num_questions: int = 5, difficulty: str = "medium") -> List[Dict[str, Any]]:
        """Generate quiz questions using Gemini AI"""
        prompt = f"""Generate {num_questions} multiple choice questions about {topic} at {difficulty} difficulty level.

Return ONLY a valid JSON array with this exact structure:
[
  {{
    "question": "Question text here?",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": 0,
    "explanation": "Brief explanation of the correct answer"
  }}
]

Topic: {topic}
Difficulty: {difficulty}
Number of questions: {num_questions}

Ensure questions are educational, accurate, and appropriate for learning."""

        try:
            # Simulate async by running in thread pool
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            # Clean the response text
            content = response.text.strip()
            
            # Remove markdown code blocks if present
            if content.startswith('```json'):
                content = content[7:]
            if content.endswith('```'):
                content = content[:-3]
            
            content = content.strip()
            
            # Parse JSON
            questions = json.loads(content)
            
            # Validate structure
            if not isinstance(questions, list):
                raise ValueError("Response is not a list")
            
            for q in questions:
                required_fields = ["question", "options", "correct_answer", "explanation"]
                if not all(field in q for field in required_fields):
                    raise ValueError(f"Missing required fields in question: {q}")
                if not isinstance(q["options"], list) or len(q["options"]) != 4:
                    raise ValueError("Each question must have exactly 4 options")
                if not (0 <= q["correct_answer"] <= 3):
                    raise ValueError("correct_answer must be between 0 and 3")
            
            return questions
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from AI: {e}")
        except Exception as e:
            raise ValueError(f"AI generation failed: {e}")

ai_service = AIService()
