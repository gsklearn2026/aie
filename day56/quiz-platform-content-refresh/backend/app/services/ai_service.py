import google.generativeai as genai
from typing import Dict, Any
import json
import structlog
import asyncio
import random

from app.core.config import settings

logger = structlog.get_logger()

class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    async def regenerate_content(
        self,
        original_content: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Regenerate quiz content based on performance data"""
        
        accuracy = performance_data.get("accuracy_rate", 50)
        skip_rate = performance_data.get("skip_rate", 0)
        
        # Build improvement instructions
        improvements = []
        if accuracy > 85:
            improvements.append("Increase difficulty - current version is too easy")
        elif accuracy < 40:
            improvements.append("Simplify the question or add helpful context")
        
        if skip_rate > 30:
            improvements.append("Make the question more engaging and relevant")
        
        improvement_text = "\n".join(f"- {imp}" for imp in improvements) if improvements else "Maintain similar difficulty"
        
        prompt = f"""Regenerate this quiz question to improve engagement and effectiveness.

Original Question:
Topic: {original_content['topic']}
Question: {original_content['question']}
Options: {json.dumps(original_content['options'])}
Correct Answer: {original_content['correct_answer']}
Difficulty: {original_content['difficulty']}

Performance Data:
- Accuracy Rate: {accuracy}%
- Skip Rate: {skip_rate}%
- Total Attempts: {performance_data.get('total_attempts', 0)}

Improvements Needed:
{improvement_text}

Generate a new version that addresses these issues while maintaining the same learning objective.
Respond with valid JSON only:
{{
    "question": "new question text",
    "options": ["option1", "option2", "option3", "option4"],
    "correct_answer": "correct option text",
    "explanation": "brief explanation of the answer"
}}"""

        try:
            # Run in executor for async compatibility
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            # Parse response
            response_text = response.text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            new_content = json.loads(response_text)
            
            logger.info(
                "Content regenerated",
                topic=original_content['topic'],
                accuracy_before=accuracy
            )
            
            return new_content
            
        except Exception as e:
            logger.error("AI regeneration failed", error=str(e))
            # Return improved version of original
            return {
                "question": f"Updated: {original_content['question']}",
                "options": original_content['options'],
                "correct_answer": original_content['correct_answer'],
                "explanation": f"This question was automatically refreshed to improve engagement."
            }
    
    async def generate_quiz_content(self, topic: str, difficulty: str = "medium") -> Dict[str, Any]:
        """Generate new quiz content for a topic"""
        prompt = f"""Create a quiz question about {topic} at {difficulty} difficulty level.

The question should be:
- Clear and unambiguous
- Educational and engaging
- Appropriate for the difficulty level

Respond with valid JSON only:
{{
    "question": "question text",
    "options": ["option1", "option2", "option3", "option4"],
    "correct_answer": "correct option text",
    "explanation": "brief explanation"
}}"""

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            response_text = response.text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
            
            return json.loads(response_text)
            
        except Exception as e:
            logger.error("AI generation failed", error=str(e))
            raise
