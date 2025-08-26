import pytest
import pytest_asyncio
import asyncio
from httpx import AsyncClient, ASGITransport
from unittest.mock import Mock, AsyncMock, patch
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from main import app
from models import TopicAnalysisRequest, AnalysisOptions, TopicAnalysisResponse, TopicInfo

@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def mock_redis():
    return AsyncMock()

@pytest.fixture
def sample_request():
    return TopicAnalysisRequest(
        content="Machine learning is a subset of artificial intelligence that focuses on algorithms.",
        options=AnalysisOptions(
            max_topics=5,
            confidence_threshold=0.7,
            include_subtopics=True,
            extract_concepts=True
        )
    )

class TestTopicAnalysisService:
    
    @pytest.mark.asyncio
    async def test_health_check(self, client):
        """Test health check endpoint"""
        app.state.redis = AsyncMock()
        app.state.redis.ping = AsyncMock()
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "topic-analysis-service"
    
    @pytest.mark.asyncio
    async def test_analyze_topics_success(self, client, sample_request):
        """Test successful topic analysis"""
        mock_response = TopicAnalysisResponse(
            topics=[
                TopicInfo(
                    name="Machine Learning",
                    confidence=0.95,
                    category="Technology",
                    subtopics=["Algorithms", "AI"],
                    concepts=["Supervised Learning", "Neural Networks"],
                    keywords=["machine", "learning", "algorithms"]
                )
            ],
            summary="Content about machine learning and AI",
            word_count=15,
            processing_time=0.5,
            cache_hit=False
        )
        mock_analyzer = Mock()
        mock_analyzer.analyze = AsyncMock(return_value=mock_response)
        app.state.topic_analyzer = mock_analyzer
        response = await client.post(
            "/analyze",
            json=sample_request.dict()
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["topics"]) == 1
        assert data["topics"][0]["name"] == "Machine Learning"
    
    @pytest.mark.asyncio
    async def test_analyze_topics_validation_error(self, client):
        """Test validation error for invalid request"""
        invalid_request = {
            "content": "",  # Empty content should fail validation
            "options": {}
        }
        response = await client.post("/analyze", json=invalid_request)
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_analyze_topics_processing_error(self, client, sample_request):
        """Test error handling during processing"""
        mock_analyzer = Mock()
        mock_analyzer.analyze = AsyncMock(side_effect=Exception("AI service error"))
        app.state.topic_analyzer = mock_analyzer
        response = await client.post(
            "/analyze",
            json=sample_request.dict()
        )
        assert response.status_code == 500
        data = response.json()
        assert "Analysis failed" in data["detail"]
    
    @pytest.mark.asyncio
    async def test_cache_stats(self, client):
        """Test cache statistics endpoint"""
        mock_cache = Mock()
        mock_cache.get_stats = AsyncMock(return_value={
            "hits": 10,
            "misses": 5,
            "sets": 8,
            "errors": 0,
            "memory_usage": "1.2MB",
            "total_keys": 15
        })
        app.state.cache_manager = mock_cache
        response = await client.get("/cache/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["cache_stats"]["hits"] == 10
        assert data["cache_stats"]["misses"] == 5

if __name__ == "__main__":
    pytest.main([__file__])
