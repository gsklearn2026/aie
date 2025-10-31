"""Unit tests for AI service."""

import json
from unittest.mock import Mock, patch

import pytest

from src.models import (
    DifficultyLevel,
    Question,
    QuestionType,
    Quiz,
    QuizGenerationRequest,
)
from src.services.ai_service import AIServiceError, QuizAIService


class TestQuizAIService:
    """Test suite for QuizAIService class."""

    @pytest.fixture
    def ai_service(self):
        """Create AI service instance with mock API key."""
        with patch("src.services.ai_service.genai.configure"):
            with patch("src.services.ai_service.genai.GenerativeModel") as mock_model:
                mock_instance = Mock()
                mock_model.return_value = mock_instance
                service = QuizAIService(api_key="test_key")
                service.model = mock_instance
                return service

    @pytest.fixture
    def sample_request(self):
        """Sample quiz generation request."""
        return QuizGenerationRequest(
            topic="Python Programming",
            difficulty=DifficultyLevel.INTERMEDIATE,
            question_count=3,
            question_types=[QuestionType.MULTIPLE_CHOICE],
            focus_areas=["functions", "loops"],
        )

    @pytest.fixture
    def sample_ai_response(self):
        """Sample AI response in expected JSON format."""
        return {
            "title": "Python Programming Quiz",
            "description": "Test your Python knowledge",
            "questions": [
                {
                    "text": "What is a function in Python?",
                    "type": "multiple_choice",
                    "difficulty": "intermediate",
                    "options": ["A block of code", "A variable", "A loop", "A condition"],
                    "correct_answer": "A block of code",
                    "explanation": "Functions are reusable blocks of code",
                    "points": 1,
                    "tags": ["functions", "python"],
                },
                {
                    "text": "Which keyword is used to define a function?",
                    "type": "multiple_choice",
                    "difficulty": "intermediate",
                    "options": ["def", "function", "define", "func"],
                    "correct_answer": "def",
                    "explanation": "The 'def' keyword defines functions in Python",
                    "points": 1,
                    "tags": ["functions", "syntax"],
                },
            ],
        }

    # Initialization Tests
    def test_ai_service_init_with_api_key(self):
        """Test AI service initialization with provided API key."""
        with patch("src.services.ai_service.genai.configure") as mock_configure:
            with patch("src.services.ai_service.genai.GenerativeModel"):
                service = QuizAIService(api_key="test_key")
                assert service.api_key == "test_key"
                mock_configure.assert_called_once_with(api_key="test_key")

    def test_ai_service_init_no_api_key(self):
        """Test AI service initialization without API key raises error."""
        with patch("src.config.settings.gemini_api_key", None):
            with pytest.raises(AIServiceError) as exc_info:
                QuizAIService()
            assert "Gemini API key is required" in str(exc_info.value)

    def test_ai_service_init_from_settings(self):
        """Test AI service initialization using settings API key."""
        with patch("src.services.ai_service.genai.configure") as mock_configure:
            with patch("src.services.ai_service.genai.GenerativeModel"):
                with patch("src.config.settings.gemini_api_key", "settings_key"):
                    service = QuizAIService()
                    assert service.api_key == "settings_key"
                    mock_configure.assert_called_once_with(api_key="settings_key")

    # Quiz Generation Tests
    @pytest.mark.asyncio
    async def test_generate_quiz_success(self, ai_service, sample_request, sample_ai_response):
        """Test successful quiz generation."""
        # Mock AI model response
        mock_response = Mock()
        mock_response.text = json.dumps(sample_ai_response)
        ai_service.model.generate_content = Mock(return_value=mock_response)

        result = await ai_service.generate_quiz(sample_request)

        assert isinstance(result, Quiz)
        assert result.title == "Python Programming Quiz"
        assert result.description == "Test your Python knowledge"
        assert len(result.questions) == 2
        assert result.difficulty == DifficultyLevel.INTERMEDIATE

        # Verify questions are properly parsed
        first_question = result.questions[0]
        assert first_question.text == "What is a function in Python?"
        assert first_question.type == QuestionType.MULTIPLE_CHOICE
        assert first_question.difficulty == DifficultyLevel.INTERMEDIATE
        assert len(first_question.options) == 4
        assert first_question.correct_answer == "A block of code"

    @pytest.mark.asyncio
    async def test_generate_quiz_ai_model_error(self, ai_service, sample_request):
        """Test quiz generation with AI model error."""
        ai_service.model.generate_content = Mock(side_effect=Exception("Model unavailable"))

        with pytest.raises(AIServiceError) as exc_info:
            await ai_service.generate_quiz(sample_request)

        assert "AI model call failed" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_quiz_invalid_json_response(self, ai_service, sample_request):
        """Test quiz generation with invalid JSON response."""
        mock_response = Mock()
        mock_response.text = "Invalid JSON response"
        ai_service.model.generate_content = Mock(return_value=mock_response)

        with pytest.raises(AIServiceError) as exc_info:
            await ai_service.generate_quiz(sample_request)

        assert "Failed to parse AI response as JSON" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_quiz_markdown_code_blocks(
        self, ai_service, sample_request, sample_ai_response
    ):
        """Test quiz generation with markdown code blocks in response."""
        # Mock response with markdown code blocks
        mock_response = Mock()
        mock_response.text = f"```json\n{json.dumps(sample_ai_response)}\n```"
        ai_service.model.generate_content = Mock(return_value=mock_response)

        result = await ai_service.generate_quiz(sample_request)

        assert isinstance(result, Quiz)
        assert result.title == "Python Programming Quiz"

    # Single Question Generation Tests
    @pytest.mark.asyncio
    async def test_generate_question_success(self, ai_service):
        """Test successful single question generation."""
        question_data = {
            "text": "What is Python?",
            "type": "multiple_choice",
            "difficulty": "beginner",
            "options": ["Language", "Snake", "Tool", "Framework"],
            "correct_answer": "Language",
            "explanation": "Python is a programming language",
            "points": 1,
            "tags": ["python", "basics"],
        }

        mock_response = Mock()
        mock_response.text = json.dumps(question_data)
        ai_service.model.generate_content = Mock(return_value=mock_response)

        result = await ai_service.generate_question(
            topic="Python",
            difficulty=DifficultyLevel.BEGINNER,
            question_type=QuestionType.MULTIPLE_CHOICE,
        )

        assert isinstance(result, Question)
        assert result.text == "What is Python?"
        assert result.type == QuestionType.MULTIPLE_CHOICE
        assert result.difficulty == DifficultyLevel.BEGINNER
        assert result.correct_answer == "Language"

    @pytest.mark.asyncio
    async def test_generate_question_missing_required_field(self, ai_service):
        """Test question generation with missing required fields."""
        incomplete_data = {
            "text": "What is Python?",
            "type": "multiple_choice",
            # Missing difficulty and correct_answer
        }

        mock_response = Mock()
        mock_response.text = json.dumps(incomplete_data)
        ai_service.model.generate_content = Mock(return_value=mock_response)

        with pytest.raises(AIServiceError) as exc_info:
            await ai_service.generate_question(topic="Python", difficulty=DifficultyLevel.BEGINNER)

        assert "Missing required field in AI response" in str(exc_info.value)

    # Question Improvement Tests
    @pytest.mark.asyncio
    async def test_improve_question_success(self, ai_service):
        """Test successful question improvement."""
        original_question = Question(
            id="q1",
            text="What is Python?",
            type=QuestionType.MULTIPLE_CHOICE,
            difficulty=DifficultyLevel.BEGINNER,
            options=["Language", "Snake"],
            correct_answer="Language",
            points=1,
        )

        improved_data = {
            "text": "What is Python primarily used for?",
            "type": "multiple_choice",
            "difficulty": "beginner",
            "options": ["Programming", "Pet keeping", "Cooking", "Gardening"],
            "correct_answer": "Programming",
            "explanation": "Python is primarily used for programming",
            "points": 1,
            "tags": ["python", "programming"],
        }

        mock_response = Mock()
        mock_response.text = json.dumps(improved_data)
        ai_service.model.generate_content = Mock(return_value=mock_response)

        result = await ai_service.improve_question(original_question, "Make it more specific")

        assert isinstance(result, Question)
        assert result.id == original_question.id  # ID should be preserved
        assert result.text == "What is Python primarily used for?"
        assert result.correct_answer == "Programming"

    @pytest.mark.asyncio
    async def test_improve_question_ai_error(self, ai_service):
        """Test question improvement with AI error."""
        original_question = Question(
            text="What is Python?",
            type=QuestionType.TRUE_FALSE,
            difficulty=DifficultyLevel.BEGINNER,
            correct_answer="True",
        )

        ai_service.model.generate_content = Mock(side_effect=Exception("AI error"))

        with pytest.raises(AIServiceError) as exc_info:
            await ai_service.improve_question(original_question, "Make it better")

        assert "Failed to improve question" in str(exc_info.value)

    # Prompt Building Tests
    def test_build_quiz_prompt_basic(self, ai_service, sample_request):
        """Test quiz prompt building with basic request."""
        prompt = ai_service._build_quiz_prompt(sample_request)

        assert "Python Programming" in prompt
        assert "intermediate" in prompt
        assert "3" in prompt
        assert "multiple_choice" in prompt
        assert "functions, loops" in prompt  # focus areas

    def test_build_quiz_prompt_no_focus_areas(self, ai_service):
        """Test quiz prompt building without focus areas."""
        request = QuizGenerationRequest(
            topic="Math",
            difficulty=DifficultyLevel.BEGINNER,
            question_count=2,
            focus_areas=[],  # No focus areas
        )

        prompt = ai_service._build_quiz_prompt(request)

        assert "Math" in prompt
        assert "beginner" in prompt
        assert "Focus on these specific areas" not in prompt

    def test_build_question_prompt(self, ai_service):
        """Test single question prompt building."""
        prompt = ai_service._build_question_prompt(
            "JavaScript", DifficultyLevel.ADVANCED, QuestionType.SHORT_ANSWER
        )

        assert "JavaScript" in prompt
        assert "advanced" in prompt
        assert "short_answer" in prompt
        assert "JSON format" in prompt

    def test_build_improvement_prompt(self, ai_service):
        """Test question improvement prompt building."""
        question = Question(
            text="What is AI?",
            type=QuestionType.ESSAY,
            difficulty=DifficultyLevel.INTERMEDIATE,
            correct_answer="Artificial Intelligence",
        )

        prompt = ai_service._build_improvement_prompt(question, "Add more options")

        assert "What is AI?" in prompt
        assert "essay" in prompt
        assert "Add more options" in prompt
        assert "Improve this question" in prompt

    # Response Parsing Tests
    def test_parse_ai_response_clean_json(self, ai_service, sample_ai_response):
        """Test parsing clean JSON response."""
        json_string = json.dumps(sample_ai_response)
        result = ai_service._parse_ai_response(json_string)

        assert result == sample_ai_response

    def test_parse_ai_response_with_markdown(self, ai_service, sample_ai_response):
        """Test parsing JSON response wrapped in markdown."""
        json_string = f"```json\n{json.dumps(sample_ai_response)}\n```"
        result = ai_service._parse_ai_response(json_string)

        assert result == sample_ai_response

    def test_parse_ai_response_invalid_json(self, ai_service):
        """Test parsing invalid JSON response."""
        invalid_json = "This is not JSON"

        with pytest.raises(AIServiceError) as exc_info:
            ai_service._parse_ai_response(invalid_json)

        assert "Failed to parse AI response as JSON" in str(exc_info.value)

    def test_parse_question_response_valid(self, ai_service):
        """Test parsing valid question response."""
        question_data = {
            "text": "Test question",
            "type": "true_false",
            "difficulty": "beginner",
            "correct_answer": "True",
            "explanation": "Test explanation",
        }

        json_string = json.dumps(question_data)
        result = ai_service._parse_question_response(json_string)

        assert result == question_data

    def test_parse_question_response_missing_fields(self, ai_service):
        """Test parsing question response with missing required fields."""
        incomplete_data = {
            "text": "Test question"
            # Missing type, difficulty, correct_answer
        }

        json_string = json.dumps(incomplete_data)

        with pytest.raises(AIServiceError) as exc_info:
            ai_service._parse_question_response(json_string)

        assert "Missing required field in AI response" in str(exc_info.value)

    # Error Handling Tests
    def test_call_ai_model_success(self, ai_service):
        """Test successful AI model call."""
        mock_response = Mock()
        mock_response.text = "Success response"
        ai_service.model.generate_content = Mock(return_value=mock_response)

        result = ai_service._call_ai_model("Test prompt")

        assert result == "Success response"
        ai_service.model.generate_content.assert_called_once()

    def test_call_ai_model_failure(self, ai_service):
        """Test AI model call failure."""
        ai_service.model.generate_content = Mock(side_effect=Exception("API Error"))

        with pytest.raises(AIServiceError) as exc_info:
            ai_service._call_ai_model("Test prompt")

        assert "AI model call failed" in str(exc_info.value)
        assert "API Error" in str(exc_info.value)

    # Configuration Tests
    def test_generation_config(self, ai_service):
        """Test that generation configuration is properly set."""
        config = ai_service._generation_config

        assert "temperature" in config
        assert "top_p" in config
        assert "top_k" in config
        assert "max_output_tokens" in config

        # Verify reasonable values
        assert 0 <= config["temperature"] <= 1
        assert 0 <= config["top_p"] <= 1
        assert config["top_k"] > 0
        assert config["max_output_tokens"] > 0

    # Integration with Models Tests
    def test_question_model_validation_in_generation(self, ai_service):
        """Test that generated questions pass model validation."""
        # This test ensures AI responses create valid Question objects
        valid_question_data = {
            "text": "What is the capital of France?",
            "type": "multiple_choice",
            "difficulty": "beginner",
            "options": ["Paris", "London", "Berlin", "Madrid"],
            "correct_answer": "Paris",
            "explanation": "Paris is the capital city of France",
            "points": 1,
            "tags": ["geography", "europe"],
        }

        # This should not raise any validation errors
        question = Question(**valid_question_data)

        assert question.text == "What is the capital of France?"
        assert question.type == QuestionType.MULTIPLE_CHOICE
        assert question.difficulty == DifficultyLevel.BEGINNER
        assert len(question.options) == 4
