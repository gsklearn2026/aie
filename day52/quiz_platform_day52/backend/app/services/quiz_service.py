import os
import json
import random
from typing import Dict, Any, List

import google.generativeai as genai

from app.services.cache_manager import CacheManager


class QuizService:
    def __init__(self):
        self.cache = CacheManager()
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None

        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash-exp')
            except Exception as exc:
                print(f"[QuizService] Failed to initialize Gemini model: {exc}")
                self.model = None
    
    async def generate_quiz(self, topic: str, num_questions: int = 5) -> Dict[str, Any]:
        """Generate quiz using Gemini AI with caching"""
        cache_key = f"quiz:{topic}:{num_questions}"
        
        # Check cache first
        cached = self.cache.get_cache(cache_key)
        if cached:
            return {'questions': cached, 'cached': True, 'ai_generated': False}
        
        questions: List[Dict[str, Any]] = []
        used_ai = False

        if self.model:
            prompt = f"""Generate {num_questions} multiple choice questions about {topic}.
Return ONLY a JSON array with this exact format:
[{{"question": "...", "options": ["A", "B", "C", "D"], "correct": 0, "explanation": "..."}}]
Make questions practical and educational."""
            try:
                response = self.model.generate_content(prompt)
                text = getattr(response, "text", "") or ""
                text = text.strip()

                if text.startswith("```json"):
                    text = text[7:-3].strip()
                elif text.startswith("```"):
                    text = text[3:-3].strip()

                parsed = json.loads(text)
                if isinstance(parsed, list):
                    questions = parsed
                    used_ai = True
            except Exception as exc:
                print(f"[QuizService] Gemini generation failed: {exc}")

        if not questions:
            questions = self._generate_fallback_quiz(topic, num_questions)

        # Cache with TTL
        self.cache.set_cache(cache_key, questions)
        
        return {'questions': questions, 'cached': False, 'ai_generated': used_ai}
    
    async def grade_answer(self, question_id: int, user_answer: int, 
                          correct_answer: int) -> Dict[str, Any]:
        """Grade user answer"""
        is_correct = user_answer == correct_answer
        return {
            'question_id': question_id,
            'is_correct': is_correct,
            'user_answer': user_answer,
            'correct_answer': correct_answer
        }

    def _generate_fallback_quiz(self, topic: str, num_questions: int) -> List[Dict[str, Any]]:
        """Generate deterministic fallback questions when AI is unavailable."""
        base_topic = topic if topic else "General Knowledge"
        templates = [
            {
                "question": f"Which statement about {base_topic} is correct?",
                "options": [
                    f"{base_topic} fundamentals involve core concepts and consistent practice.",
                    f"{base_topic} requires no prior knowledge or preparation.",
                    f"{base_topic} is only useful during exams.",
                    f"{base_topic} cannot be learned without expensive tools."
                ],
                "correct": 0,
                "explanation": f"Solid understanding of {base_topic} grows from mastering fundamentals and repeated application."
            },
            {
                "question": f"What is a best practice when studying {base_topic}?",
                "options": [
                    f"Review real-world examples related to {base_topic}.",
                    f"Ignore mistakes and avoid feedback.",
                    f"Memorize random facts unrelated to {base_topic}.",
                    f"Avoid collaboration or discussion."
                ],
                "correct": 0,
                "explanation": f"Connecting {base_topic} to real scenarios builds intuition and practical skill."
            },
            {
                "question": f"How can you assess progress in {base_topic}?",
                "options": [
                    f"Track goals, practice regularly, and reflect on outcomes.",
                    f"Wait for inspiration without measuring anything.",
                    f"Compare yourself only to experts.",
                    f"Avoid testing your understanding."
                ],
                "correct": 0,
                "explanation": f"Consistent practice, measurement, and reflection provide meaningful feedback when learning {base_topic}."
            },
            {
                "question": f"What resource can support learning {base_topic}?",
                "options": [
                    f"Documentation, tutorials, and community discussions about {base_topic}.",
                    f"Unverified rumors unrelated to {base_topic}.",
                    f"Random social media trends.",
                    f"Ignoring all available resources."
                ],
                "correct": 0,
                "explanation": f"Trustworthy references and community knowledge offer practical guidance for {base_topic}."
            },
            {
                "question": f"Why is deliberate practice important for {base_topic}?",
                "options": [
                    f"It identifies skill gaps and reinforces strong mental models.",
                    f"It guarantees instant mastery without effort.",
                    f"It replaces the need for feedback.",
                    f"It discourages experimentation."
                ],
                "correct": 0,
                "explanation": f"Focused practice highlights weaknesses and helps build durable expertise in {base_topic}."
            },
        ]

        random.seed(base_topic)
        questions: List[Dict[str, Any]] = []
        for idx in range(num_questions):
            template = templates[idx % len(templates)]
            # Copy to avoid mutating template
            question_data = {
                "question": template["question"],
                "options": template["options"],
                "correct": template["correct"],
                "explanation": template["explanation"],
            }
            questions.append(question_data)

        return questions
