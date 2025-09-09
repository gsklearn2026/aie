"""Mock utilities for AI service testing."""

import json
from typing import Any, Dict, Optional
from unittest.mock import AsyncMock, Mock


class MockAIResponse:
    """Mock AI response object."""

    def __init__(self, response_data: Dict[str, Any]):
        self.text = json.dumps(response_data)


class MockAIService:
    """Mock AI service for testing."""

    def __init__(self):
        self.generate_quiz = AsyncMock()
        self.generate_question = AsyncMock()
        self.improve_question = AsyncMock()
        self._call_ai_model = AsyncMock()
        self._responses = {}

    def set_quiz_response(self, quiz_data: Dict[str, Any]):
        """Set mock response for quiz generation."""
        self.generate_quiz.return_value = quiz_data

    def set_question_response(self, question_data: Dict[str, Any]):
        """Set mock response for question generation."""
        self.generate_question.return_value = question_data

    def set_ai_model_response(self, response_text: str):
        """Set mock response for AI model calls."""
        mock_response = Mock()
        mock_response.text = response_text
        self._call_ai_model.return_value = response_text

    def simulate_ai_error(self, error_message: str = "AI service unavailable"):
        """Simulate AI service error."""
        from src.services.ai_service import AIServiceError

        self.generate_quiz.side_effect = AIServiceError(error_message)
        self.generate_question.side_effect = AIServiceError(error_message)
        self._call_ai_model.side_effect = AIServiceError(error_message)

    def reset_mocks(self):
        """Reset all mock configurations."""
        self.generate_quiz.reset_mock()
        self.generate_question.reset_mock()
        self.improve_question.reset_mock()
        self._call_ai_model.reset_mock()

        # Clear side effects
        self.generate_quiz.side_effect = None
        self.generate_question.side_effect = None
        self._call_ai_model.side_effect = None


def create_mock_genai():
    """Create mock for google.generativeai module."""
    mock_genai = Mock()
    mock_model_instance = Mock()

    # Mock the GenerativeModel class
    mock_genai.GenerativeModel.return_value = mock_model_instance

    return mock_genai, mock_model_instance


def create_quiz_response_mock(questions_count: int = 2) -> Dict[str, Any]:
    """Create mock quiz response data."""
    questions = []
    for i in range(questions_count):
        questions.append(
            {
                "text": f"Test question {i+1}",
                "type": "multiple_choice",
                "difficulty": "intermediate",
                "options": [f"Option {j+1}" for j in range(4)],
                "correct_answer": "Option 1",
                "explanation": f"Explanation for question {i+1}",
                "points": 1,
                "tags": ["test", f"topic{i+1}"],
            }
        )

    return {
        "title": "Mock Quiz Title",
        "description": "Mock quiz description",
        "questions": questions,
    }


def create_question_response_mock(question_id: Optional[str] = None) -> Dict[str, Any]:
    """Create mock single question response data."""
    return {
        "text": "What is the mock question?",
        "type": "multiple_choice",
        "difficulty": "beginner",
        "options": ["Mock option 1", "Mock option 2", "Mock option 3", "Mock option 4"],
        "correct_answer": "Mock option 1",
        "explanation": "This is a mock explanation",
        "points": 1,
        "tags": ["mock", "testing"],
    }
