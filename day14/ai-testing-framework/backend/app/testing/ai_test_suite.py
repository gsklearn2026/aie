import asyncio
from typing import Dict, List, Any, Optional
from .base_test_runner import BaseTestRunner, TestResult, TestStatus
from ..providers.base_provider import BaseProvider
from ..services.ai_service import AIService
from loguru import logger
import time

class AITestSuite(BaseTestRunner):
    def __init__(self, ai_service: AIService, name: str = "AI_Test_Suite"):
        super().__init__(name)
        self.ai_service = ai_service
        self.test_providers = {}
        
    async def setup(self) -> None:
        """Initialize test environment"""
        logger.info("Setting up AI test environment")
        # Initialize any test-specific providers or configurations
        
    async def teardown(self) -> None:
        """Cleanup test environment"""
        logger.info("Tearing down AI test environment")
        
    async def run_test(self, test_case: Dict[str, Any]) -> TestResult:
        """Execute AI test case"""
        test_name = test_case.get("name", "unnamed_test")
        test_type = test_case.get("type", "basic")
        
        start_time = time.time()
        
        try:
            if test_type == "generation":
                result = await self._test_generation(test_case)
            elif test_type == "failover":
                result = await self._test_failover(test_case)
            elif test_type == "performance":
                result = await self._test_performance(test_case)
            elif test_type == "semantic":
                result = await self._test_semantic_quality(test_case)
            else:
                raise ValueError(f"Unknown test type: {test_type}")
            
            execution_time = time.time() - start_time
            
            return TestResult(
                test_name=test_name,
                status=TestStatus.PASSED if result["passed"] else TestStatus.FAILED,
                execution_time=execution_time,
                details=result,
                error_message=result.get("error")
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Test {test_name} failed with error: {e}")
            
            return TestResult(
                test_name=test_name,
                status=TestStatus.FAILED,
                execution_time=execution_time,
                details={},
                error_message=str(e)
            )
    
    async def _test_generation(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test basic AI text generation"""
        prompt = test_case.get("prompt", "Test prompt")
        expected_keywords = test_case.get("expected_keywords", [])
        min_length = test_case.get("min_length", 10)
        
        response = await self.ai_service.generate_text(prompt)
        content = response.get("content", "")
        
        # Validate response
        keyword_matches = sum(1 for keyword in expected_keywords if keyword.lower() in content.lower())
        keyword_score = keyword_matches / len(expected_keywords) if expected_keywords else 1.0
        
        passed = (
            len(content) >= min_length and
            keyword_score >= 0.5 and
            response.get("tokens_used", 0) > 0
        )
        
        return {
            "passed": passed,
            "content_length": len(content),
            "keyword_score": keyword_score,
            "tokens_used": response.get("tokens_used", 0),
            "response_time": response.get("response_time", 0),
            "provider_used": response.get("provider", "unknown")
        }
    
    async def _test_failover(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test provider failover behavior"""
        prompt = test_case.get("prompt", "Test failover")
        
        # Get initial provider health
        initial_health = await self.ai_service.get_provider_health()
        healthy_providers = [p for p in initial_health if p.get("is_healthy", False)]
        
        if len(healthy_providers) < 2:
            return {
                "passed": False,
                "error": "Need at least 2 healthy providers for failover testing",
                "available_providers": len(healthy_providers)
            }
        
        # Test multiple requests to ensure failover works
        responses = []
        for i in range(3):
            try:
                response = await self.ai_service.generate_text(f"{prompt} - attempt {i}")
                responses.append(response)
            except Exception as e:
                responses.append({"error": str(e)})
        
        successful_responses = [r for r in responses if "error" not in r]
        different_providers = set(r.get("provider") for r in successful_responses)
        
        passed = len(successful_responses) >= 2 and len(different_providers) >= 1
        
        return {
            "passed": passed,
            "successful_responses": len(successful_responses),
            "providers_used": list(different_providers),
            "total_attempts": len(responses)
        }
    
    async def _test_performance(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test AI service performance under load"""
        prompt = test_case.get("prompt", "Performance test")
        concurrent_requests = test_case.get("concurrent_requests", 5)
        max_response_time = test_case.get("max_response_time", 5000)  # milliseconds
        
        async def single_request():
            start = time.time()
            try:
                response = await self.ai_service.generate_text(prompt)
                return {
                    "success": True,
                    "response_time": (time.time() - start) * 1000,
                    "tokens": response.get("tokens_used", 0)
                }
            except Exception as e:
                return {
                    "success": False,
                    "response_time": (time.time() - start) * 1000,
                    "error": str(e)
                }
        
        # Run concurrent requests
        tasks = [single_request() for _ in range(concurrent_requests)]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        successful_results = [r for r in results if isinstance(r, dict) and r.get("success")]
        response_times = [r["response_time"] for r in successful_results]
        
        avg_response_time = sum(response_times) / len(response_times) if response_times else float('inf')
        max_actual_response_time = max(response_times) if response_times else float('inf')
        
        passed = (
            len(successful_results) >= concurrent_requests * 0.8 and  # 80% success rate
            avg_response_time <= max_response_time
        )
        
        return {
            "passed": passed,
            "successful_requests": len(successful_results),
            "total_requests": concurrent_requests,
            "success_rate": len(successful_results) / concurrent_requests,
            "avg_response_time": avg_response_time,
            "max_response_time": max_actual_response_time,
            "response_time_threshold": max_response_time
        }
    
    async def _test_semantic_quality(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """Test semantic quality of AI responses"""
        prompt = test_case.get("prompt", "Semantic test")
        expected_topics = test_case.get("expected_topics", [])
        min_quality_score = test_case.get("min_quality_score", 0.7)
        
        response = await self.ai_service.generate_text(prompt)
        content = response.get("content", "")
        
        # Simple semantic validation (can be enhanced with embeddings)
        topic_mentions = sum(1 for topic in expected_topics if topic.lower() in content.lower())
        topic_score = topic_mentions / len(expected_topics) if expected_topics else 1.0
        
        # Basic quality metrics
        word_count = len(content.split())
        sentence_count = content.count('.') + content.count('!') + content.count('?')
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        # Quality heuristics
        quality_score = min(1.0, (
            topic_score * 0.4 +
            min(1.0, word_count / 50) * 0.3 +  # Reasonable length
            min(1.0, avg_sentence_length / 20) * 0.3  # Reasonable sentence length
        ))
        
        passed = quality_score >= min_quality_score
        
        return {
            "passed": passed,
            "quality_score": quality_score,
            "topic_score": topic_score,
            "word_count": word_count,
            "sentence_count": sentence_count,
            "avg_sentence_length": avg_sentence_length,
            "threshold": min_quality_score
        }
