import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from topic_analyzer import TopicAnalyzer
from models import AnalysisOptions
from cache import CacheManager

@pytest.fixture
def mock_cache_manager():
    return Mock(spec=CacheManager)

@pytest.fixture
def mock_anthropic_client():
    return AsyncMock()

@pytest.fixture
def topic_analyzer(mock_cache_manager):
    with patch('topic_analyzer.AsyncAnthropic') as mock_anthropic:
        analyzer = TopicAnalyzer("fake-api-key", mock_cache_manager)
        analyzer.client = AsyncMock()
        return analyzer

@pytest.fixture
def sample_content():
    return """
    Machine learning is a powerful subset of artificial intelligence that enables
    computers to learn and make decisions without being explicitly programmed.
    It involves algorithms that can identify patterns in data and make predictions.
    """

@pytest.fixture
def sample_options():
    return AnalysisOptions(
        max_topics=5,
        confidence_threshold=0.6,
        include_subtopics=True,
        extract_concepts=True
    )

class TestTopicAnalyzer:
    
    @pytest.mark.asyncio
    async def test_analyze_with_cache_hit(self, topic_analyzer, sample_content, sample_options):
        """Test analysis with cache hit"""
        cached_result = {
            "topics": [
                {
                    "name": "Machine Learning",
                    "confidence": 0.9,
                    "category": "Technology",
                    "subtopics": ["AI", "Algorithms"],
                    "concepts": ["Pattern Recognition"],
                    "keywords": ["machine", "learning"]
                }
            ],
            "summary": "Content about ML",
            "word_count": 25,
            "processing_time": 0.1,
            "cache_hit": True
        }
        
        topic_analyzer.cache_manager.get = AsyncMock(return_value=cached_result)
        
        result = await topic_analyzer.analyze(sample_content, sample_options)
        
        assert result.cache_hit is True
        assert len(result.topics) == 1
        assert result.topics[0].name == "Machine Learning"
    
    @pytest.mark.asyncio
    async def test_analyze_with_cache_miss(self, topic_analyzer, sample_content, sample_options):
        """Test analysis with cache miss and AI processing"""
        # Setup cache miss
        topic_analyzer.cache_manager.get = AsyncMock(return_value=None)
        topic_analyzer.cache_manager.set = AsyncMock(return_value=True)
        
        # Mock AI response
        mock_ai_response = Mock()
        mock_ai_response.content = [Mock()]
        mock_ai_response.content[0].text = '''
        {
            "topics": [
                {
                    "name": "Machine Learning",
                    "confidence": 0.92,
                    "category": "Artificial Intelligence",
                    "subtopics": ["Algorithms", "Pattern Recognition"],
                    "concepts": ["Supervised Learning", "Neural Networks"],
                    "keywords": ["machine", "learning", "algorithms", "data"]
                },
                {
                    "name": "Artificial Intelligence",
                    "confidence": 0.85,
                    "category": "Technology",
                    "subtopics": ["ML", "Deep Learning"],
                    "concepts": ["Computer Vision", "NLP"],
                    "keywords": ["ai", "intelligence", "computers"]
                }
            ],
            "summary": "Content discusses machine learning as a subset of AI, focusing on algorithms and pattern recognition."
        }
        '''
        
        topic_analyzer.client.messages.create = AsyncMock(return_value=mock_ai_response)
        
        result = await topic_analyzer.analyze(sample_content, sample_options)
        
        assert result.cache_hit is False
        assert len(result.topics) == 2
        assert result.topics[0].name == "Machine Learning"
        assert result.topics[0].confidence == 0.92
        assert "Algorithms" in result.topics[0].subtopics
        assert result.word_count > 0
        assert result.processing_time > 0
    
    @pytest.mark.asyncio
    async def test_analyze_with_ai_error(self, topic_analyzer, sample_content, sample_options):
        """Test error handling when AI service fails"""
        topic_analyzer.cache_manager.get = AsyncMock(return_value=None)
        topic_analyzer.client.messages.create = AsyncMock(side_effect=Exception("API Error"))
        
        with pytest.raises(Exception) as exc_info:
            await topic_analyzer.analyze(sample_content, sample_options)
        
        assert "Topic analysis failed" in str(exc_info.value)
    
    def test_generate_cache_key(self, topic_analyzer, sample_content, sample_options):
        """Test cache key generation"""
        key1 = topic_analyzer._generate_cache_key(sample_content, sample_options)
        key2 = topic_analyzer._generate_cache_key(sample_content, sample_options)
        
        # Same input should generate same key
        assert key1 == key2
        
        # Different content should generate different key
        different_content = "Different content for testing"
        key3 = topic_analyzer._generate_cache_key(different_content, sample_options)
        assert key1 != key3
    
    def test_parse_ai_response_valid_json(self, topic_analyzer):
        """Test parsing valid AI response"""
        response_text = '''
        {
            "topics": [
                {
                    "name": "Test Topic",
                    "confidence": 0.8,
                    "category": "Test Category",
                    "subtopics": ["sub1", "sub2"],
                    "concepts": ["concept1"],
                    "keywords": ["key1", "key2"]
                }
            ],
            "summary": "Test summary"
        }
        '''
        
        result = topic_analyzer._parse_ai_response(response_text)
        
        assert len(result["topics"]) == 1
        assert result["topics"][0].name == "Test Topic"
        assert result["topics"][0].confidence == 0.8
        assert result["summary"] == "Test summary"
    
    def test_parse_ai_response_invalid_json(self, topic_analyzer):
        """Test parsing invalid AI response"""
        response_text = "Invalid JSON response"
        
        result = topic_analyzer._parse_ai_response(response_text)
        
        # Should return fallback response
        assert len(result["topics"]) == 1
        assert result["topics"][0].name == "Parse Error"
        assert result["topics"][0].confidence == 0.1

if __name__ == "__main__":
    pytest.main([__file__])
