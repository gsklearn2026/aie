"""AI service for quiz generation using Google Gemini."""

import json
import logging
from typing import Any, Dict, Optional

import google.generativeai as genai

from src.config import settings
from src.models import (
    DifficultyLevel,
    Question,
    QuestionType,
    Quiz,
    QuizGenerationRequest,
)

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Custom exception for AI service errors."""

    pass


class QuizAIService:
    """Service for AI-powered quiz generation and content creation."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize AI service with API key."""
        self.api_key = api_key or settings.gemini_api_key
        if not self.api_key:
            raise AIServiceError("Gemini API key is required")

        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(settings.gemini_model)
        self._generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

    async def generate_quiz(self, request: QuizGenerationRequest) -> Quiz:
        """Generate a complete quiz using AI."""
        try:
            logger.info(f"Generating quiz for topic: {request.topic}")

            # Create prompt for quiz generation
            prompt = self._build_quiz_prompt(request)

            # Generate content using AI
            response = self._call_ai_model(prompt)

            # Parse AI response into quiz structure
            quiz_data = self._parse_ai_response(response)

            # Create Quiz object
            questions = [Question(**q) for q in quiz_data.get("questions", [])]

            quiz = Quiz(
                title=quiz_data.get("title", f"Quiz: {request.topic}"),
                description=quiz_data.get("description"),
                questions=questions,
                difficulty=request.difficulty,
                time_limit=request.time_limit,
            )

            logger.info(f"Successfully generated quiz with {len(quiz.questions)} questions")
            return quiz

        except Exception as e:
            logger.error(f"Quiz generation failed: {str(e)}")
            raise AIServiceError(f"Failed to generate quiz: {str(e)}")

    async def generate_question(
        self,
        topic: str,
        difficulty: DifficultyLevel,
        question_type: QuestionType = QuestionType.MULTIPLE_CHOICE,
    ) -> Question:
        """Generate a single question using AI."""
        try:
            prompt = self._build_question_prompt(topic, difficulty, question_type)
            response = self._call_ai_model(prompt)
            question_data = self._parse_question_response(response)

            return Question(**question_data)

        except Exception as e:
            logger.error(f"Question generation failed: {str(e)}")
            raise AIServiceError(f"Failed to generate question: {str(e)}")

    async def improve_question(self, question: Question, feedback: str) -> Question:
        """Improve an existing question based on feedback."""
        try:
            prompt = self._build_improvement_prompt(question, feedback)
            response = self._call_ai_model(prompt)
            improved_data = self._parse_question_response(response)

            # Preserve original ID and creation time
            improved_data["id"] = question.id
            improved_data["created_at"] = question.created_at

            return Question(**improved_data)

        except Exception as e:
            logger.error(f"Question improvement failed: {str(e)}")
            raise AIServiceError(f"Failed to improve question: {str(e)}")

    def _build_quiz_prompt(self, request: QuizGenerationRequest) -> str:
        """Build prompt for quiz generation."""
        focus_areas_text = ""
        if request.focus_areas:
            focus_areas_text = f"Focus on these specific areas: {', '.join(request.focus_areas)}"

        return f"""Create a comprehensive quiz about "{request.topic}" with the following specifications:

        - Difficulty Level: {request.difficulty.value}
        - Number of Questions: {request.question_count}
        - Question Types: {[qt.value for qt in request.question_types]}
        {focus_areas_text}

        Return the quiz in JSON format with this structure:
        {{
            "title": "Quiz title",
            "description": "Brief description",
            "questions": [
                {{
                    "text": "Question text",
                    "type": "multiple_choice|true_false|short_answer",
                    "difficulty": "beginner|intermediate|advanced|expert",
                    "options": ["option1", "option2", "option3", "option4"],
                    "correct_answer": "correct answer",
                    "explanation": "why this is correct",
                    "points": 1,
                    "tags": ["tag1", "tag2"]
                }}
            ]
        }}

        Ensure questions are appropriate for {request.difficulty.value} level and
        cover the topic comprehensively."""

    def _build_question_prompt(
        self, topic: str, difficulty: DifficultyLevel, question_type: QuestionType
    ) -> str:
        """Build prompt for single question generation."""
        return f"""Generate a {difficulty.value} level {question_type.value} question about "{topic}".

        Return in JSON format:
        {{
            "text": "Clear, well-formed question",
            "type": "{question_type.value}",
            "difficulty": "{difficulty.value}",
            "options": ["option1", "option2", "option3", "option4"],
            "correct_answer": "correct answer",
            "explanation": "clear explanation of why this is correct",
            "points": 1,
            "tags": ["relevant", "tags"]
        }}"""

    def _build_improvement_prompt(self, question: Question, feedback: str) -> str:
        """Build prompt for question improvement."""
        return f"""Improve this question based on the feedback:

        Original Question: {question.text}
        Question Type: {question.type.value}
        Current Options: {question.options}
        Feedback: {feedback}

        Return improved question in JSON format with the same structure."""

    def _call_ai_model(self, prompt: str) -> str:
        """Call the AI model with error handling and retries."""
        try:
            response = self.model.generate_content(
                prompt, generation_config=self._generation_config
            )
            return response.text
        except Exception as e:
            raise AIServiceError(f"AI model call failed: {str(e)}")

    def _parse_ai_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response into structured data."""
        try:
            # Clean response (remove markdown code blocks if present)
            clean_response = response.strip()
            if clean_response.startswith("```json"):
                clean_response = clean_response[7:]
            if clean_response.endswith("```"):
                clean_response = clean_response[:-3]

            return json.loads(clean_response.strip())
        except json.JSONDecodeError as e:
            raise AIServiceError(f"Failed to parse AI response as JSON: {str(e)}")

    def _parse_question_response(self, response: str) -> Dict[str, Any]:
        """Parse AI response for single question."""
        data = self._parse_ai_response(response)

        # Validate required fields
        required_fields = ["text", "type", "difficulty", "correct_answer"]
        for field in required_fields:
            if field not in data:
                raise AIServiceError(f"Missing required field in AI response: {field}")

        return data


# Service instance
ai_service = QuizAIService()
