#!/bin/bash

# AI Service Testing Framework - Complete Implementation Script
# Day 14 of 60-Days AI Engineering Series

set -e  # Exit on any error

echo "🧪 Starting AI Service Testing Framework Implementation..."
echo "======================================================"

# Create project structure
echo "📁 Creating project structure..."
mkdir -p ai-testing-framework/{backend/{app/{testing,validators,services,providers,utils},tests,golden_datasets},frontend/{src/{components,services,styles},public},docs}
cd ai-testing-framework

# Initialize Python backend
echo "🐍 Setting up Python backend with testing framework..."
cd backend

# Create requirements.txt with testing dependencies
cat > requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn[standard]==0.24.0
anthropic==0.7.8
python-dotenv==1.0.0
pydantic==2.5.0
httpx==0.25.2
pytest==7.4.3
pytest-asyncio==0.21.1
pytest-cov==4.1.0
pytest-mock==3.12.0
pytest-benchmark==4.0.0
aiofiles==23.2.1
python-multipart==0.0.6
jinja2==3.1.2
loguru==0.7.2
numpy==1.25.2
scikit-learn==1.3.2
sentence-transformers==2.2.2
nltk==3.8.1
textstat==0.7.3
concurrent-futures==3.1.1
asyncio-throttle==1.0.2
faker==20.1.0
redis==5.0.1
celery==5.3.4
EOF

# Core testing framework structure
echo "🏗️ Creating AI testing framework structure..."

# Testing framework base classes
cat > app/testing/__init__.py << 'EOF'
from .base_test_runner import BaseTestRunner
from .ai_test_suite import AITestSuite
from .validators import ContentValidator, PerformanceValidator, SemanticValidator
from .test_cases import GoldenDatasetTests, FailoverTests, PerformanceTests

__all__ = [
    'BaseTestRunner', 'AITestSuite', 'ContentValidator', 
    'PerformanceValidator', 'SemanticValidator', 'GoldenDatasetTests',
    'FailoverTests', 'PerformanceTests'
]
EOF

cat > app/testing/base_test_runner.py << 'EOF'
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
import asyncio
import time
from loguru import logger
from dataclasses import dataclass
from enum import Enum

class TestStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class TestResult:
    test_name: str
    status: TestStatus
    execution_time: float
    details: Dict[str, Any]
    error_message: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseTestRunner(ABC):
    def __init__(self, name: str):
        self.name = name
        self.results: List[TestResult] = []
        self.start_time = None
        self.end_time = None
        
    @abstractmethod
    async def setup(self) -> None:
        """Setup test environment"""
        pass
    
    @abstractmethod
    async def teardown(self) -> None:
        """Cleanup test environment"""
        pass
    
    @abstractmethod
    async def run_test(self, test_case: Dict[str, Any]) -> TestResult:
        """Execute individual test case"""
        pass
    
    async def run_suite(self, test_cases: List[Dict[str, Any]]) -> List[TestResult]:
        """Run complete test suite"""
        logger.info(f"Starting test suite: {self.name}")
        self.start_time = time.time()
        
        try:
            await self.setup()
            
            # Run tests concurrently with limited parallelism
            semaphore = asyncio.Semaphore(5)  # Limit concurrent tests
            
            async def run_single_test(test_case):
                async with semaphore:
                    return await self.run_test(test_case)
            
            tasks = [run_single_test(test_case) for test_case in test_cases]
            self.results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Handle exceptions in results
            processed_results = []
            for i, result in enumerate(self.results):
                if isinstance(result, Exception):
                    processed_results.append(TestResult(
                        test_name=f"test_{i}",
                        status=TestStatus.FAILED,
                        execution_time=0.0,
                        details={},
                        error_message=str(result)
                    ))
                else:
                    processed_results.append(result)
            
            self.results = processed_results
            
        finally:
            await self.teardown()
            self.end_time = time.time()
        
        logger.info(f"Test suite completed: {self.name}")
        return self.results
    
    def get_summary(self) -> Dict[str, Any]:
        """Get test execution summary"""
        if not self.results:
            return {"status": "no_tests", "summary": {}}
        
        passed = len([r for r in self.results if r.status == TestStatus.PASSED])
        failed = len([r for r in self.results if r.status == TestStatus.FAILED])
        skipped = len([r for r in self.results if r.status == TestStatus.SKIPPED])
        total = len(self.results)
        
        total_time = self.end_time - self.start_time if self.end_time and self.start_time else 0
        
        return {
            "status": "completed",
            "summary": {
                "total": total,
                "passed": passed,
                "failed": failed,
                "skipped": skipped,
                "success_rate": passed / total if total > 0 else 0,
                "total_execution_time": total_time,
                "average_test_time": sum(r.execution_time for r in self.results) / total if total > 0 else 0
            },
            "results": [
                {
                    "test_name": r.test_name,
                    "status": r.status.value,
                    "execution_time": r.execution_time,
                    "details": r.details,
                    "error_message": r.error_message
                }
                for r in self.results
            ]
        }
EOF

# AI-specific test suite
cat > app/testing/ai_test_suite.py << 'EOF'
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
EOF

# Content validators
cat > app/validators/__init__.py << 'EOF'
from .content_validator import ContentValidator
from .performance_validator import PerformanceValidator
from .semantic_validator import SemanticValidator

__all__ = ['ContentValidator', 'PerformanceValidator', 'SemanticValidator']
EOF

cat > app/validators/content_validator.py << 'EOF'
from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass

@dataclass
class ValidationResult:
    is_valid: bool
    score: float
    details: Dict[str, Any]
    errors: List[str]

class ContentValidator:
    def __init__(self):
        self.min_word_count = 5
        self.max_word_count = 2000
        self.required_patterns = []
        
    def validate_response(self, content: str, criteria: Optional[Dict[str, Any]] = None) -> ValidationResult:
        """Validate AI response content against criteria"""
        criteria = criteria or {}
        errors = []
        details = {}
        
        # Basic content validation
        word_count = len(content.split())
        details["word_count"] = word_count
        
        if word_count < criteria.get("min_words", self.min_word_count):
            errors.append(f"Content too short: {word_count} words")
        
        if word_count > criteria.get("max_words", self.max_word_count):
            errors.append(f"Content too long: {word_count} words")
        
        # Required keywords validation
        required_keywords = criteria.get("required_keywords", [])
        found_keywords = []
        for keyword in required_keywords:
            if keyword.lower() in content.lower():
                found_keywords.append(keyword)
        
        details["found_keywords"] = found_keywords
        details["keyword_coverage"] = len(found_keywords) / len(required_keywords) if required_keywords else 1.0
        
        if len(found_keywords) < len(required_keywords) * 0.5:  # At least 50% keyword coverage
            errors.append(f"Insufficient keyword coverage: {len(found_keywords)}/{len(required_keywords)}")
        
        # Content structure validation
        sentence_count = self._count_sentences(content)
        details["sentence_count"] = sentence_count
        
        if sentence_count == 0:
            errors.append("No complete sentences found")
        
        # Language quality checks
        details["has_profanity"] = self._check_profanity(content)
        details["coherence_score"] = self._assess_coherence(content)
        
        if details["has_profanity"]:
            errors.append("Content contains inappropriate language")
        
        # Calculate overall score
        score = self._calculate_score(details, criteria)
        details["overall_score"] = score
        
        return ValidationResult(
            is_valid=len(errors) == 0 and score >= criteria.get("min_score", 0.6),
            score=score,
            details=details,
            errors=errors
        )
    
    def _count_sentences(self, content: str) -> int:
        """Count sentences in content"""
        sentence_endings = ['.', '!', '?']
        return sum(content.count(ending) for ending in sentence_endings)
    
    def _check_profanity(self, content: str) -> bool:
        """Basic profanity check (can be enhanced with external libraries)"""
        profanity_words = ['damn', 'hell']  # Basic list, extend as needed
        return any(word in content.lower() for word in profanity_words)
    
    def _assess_coherence(self, content: str) -> float:
        """Simple coherence assessment based on text structure"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Simple heuristics for coherence
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        length_score = min(1.0, avg_sentence_length / 15)  # Optimal around 15 words
        
        # Check for repeated phrases (sign of poor coherence)
        words = content.lower().split()
        unique_words = set(words)
        uniqueness_score = len(unique_words) / len(words) if words else 0
        
        return (length_score + uniqueness_score) / 2
    
    def _calculate_score(self, details: Dict[str, Any], criteria: Dict[str, Any]) -> float:
        """Calculate overall content score"""
        score_components = []
        
        # Word count score
        word_count = details["word_count"]
        target_words = criteria.get("target_words", 100)
        word_score = max(0, 1 - abs(word_count - target_words) / target_words)
        score_components.append(word_score * 0.2)
        
        # Keyword coverage score
        score_components.append(details["keyword_coverage"] * 0.3)
        
        # Structure score
        if details["sentence_count"] > 0:
            score_components.append(0.2)
        
        # Coherence score
        score_components.append(details["coherence_score"] * 0.2)
        
        # Quality penalty for profanity
        if not details["has_profanity"]:
            score_components.append(0.1)
        
        return sum(score_components)
EOF

# Performance validator
cat > app/validators/performance_validator.py << 'EOF'
import time
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import statistics

@dataclass
class PerformanceMetrics:
    avg_response_time: float
    p95_response_time: float
    p99_response_time: float
    success_rate: float
    throughput: float
    error_count: int
    total_requests: int

class PerformanceValidator:
    def __init__(self):
        self.max_response_time = 5000  # milliseconds
        self.min_success_rate = 0.95
        self.target_throughput = 10  # requests per second
        
    async def validate_performance(self, ai_service, test_config: Dict[str, Any]) -> Dict[str, Any]:
        """Run performance validation tests"""
        concurrent_users = test_config.get("concurrent_users", 5)
        requests_per_user = test_config.get("requests_per_user", 3)
        test_prompt = test_config.get("prompt", "Performance test prompt")
        
        start_time = time.time()
        
        # Run concurrent performance test
        tasks = []
        for user in range(concurrent_users):
            tasks.append(self._run_user_simulation(ai_service, test_prompt, requests_per_user))
        
        user_results = await asyncio.gather(*tasks, return_exceptions=True)
        
        end_time = time.time()
        total_duration = end_time - start_time
        
        # Aggregate results
        all_response_times = []
        successful_requests = 0
        failed_requests = 0
        
        for user_result in user_results:
            if isinstance(user_result, Exception):
                failed_requests += requests_per_user
                continue
                
            for request_result in user_result:
                if request_result.get("success", False):
                    successful_requests += 1
                    all_response_times.append(request_result["response_time"])
                else:
                    failed_requests += 1
        
        total_requests = successful_requests + failed_requests
        
        # Calculate metrics
        if all_response_times:
            metrics = PerformanceMetrics(
                avg_response_time=statistics.mean(all_response_times),
                p95_response_time=self._percentile(all_response_times, 95),
                p99_response_time=self._percentile(all_response_times, 99),
                success_rate=successful_requests / total_requests if total_requests > 0 else 0,
                throughput=successful_requests / total_duration if total_duration > 0 else 0,
                error_count=failed_requests,
                total_requests=total_requests
            )
        else:
            metrics = PerformanceMetrics(0, 0, 0, 0, 0, failed_requests, total_requests)
        
        # Validate against thresholds
        validation_results = self._validate_metrics(metrics, test_config)
        
        return {
            "metrics": {
                "avg_response_time": metrics.avg_response_time,
                "p95_response_time": metrics.p95_response_time,
                "p99_response_time": metrics.p99_response_time,
                "success_rate": metrics.success_rate,
                "throughput": metrics.throughput,
                "error_count": metrics.error_count,
                "total_requests": metrics.total_requests,
                "test_duration": total_duration
            },
            "validation": validation_results,
            "passed": validation_results["overall_passed"]
        }
    
    async def _run_user_simulation(self, ai_service, prompt: str, request_count: int) -> List[Dict[str, Any]]:
        """Simulate requests from a single user"""
        results = []
        
        for i in range(request_count):
            start_time = time.time()
            try:
                response = await ai_service.generate_text(f"{prompt} - request {i}")
                response_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                
                results.append({
                    "success": True,
                    "response_time": response_time,
                    "tokens_used": response.get("tokens_used", 0),
                    "provider": response.get("provider", "unknown")
                })
            except Exception as e:
                response_time = (time.time() - start_time) * 1000
                results.append({
                    "success": False,
                    "response_time": response_time,
                    "error": str(e)
                })
        
        return results
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile value"""
        if not data:
            return 0.0
        sorted_data = sorted(data)
        index = (percentile / 100) * (len(sorted_data) - 1)
        if index.is_integer():
            return sorted_data[int(index)]
        else:
            lower = sorted_data[int(index)]
            upper = sorted_data[int(index) + 1]
            return lower + (upper - lower) * (index - int(index))
    
    def _validate_metrics(self, metrics: PerformanceMetrics, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate performance metrics against thresholds"""
        max_response_time = config.get("max_response_time", self.max_response_time)
        min_success_rate = config.get("min_success_rate", self.min_success_rate)
        min_throughput = config.get("min_throughput", self.target_throughput)
        
        validations = {
            "response_time_valid": metrics.p95_response_time <= max_response_time,
            "success_rate_valid": metrics.success_rate >= min_success_rate,
            "throughput_valid": metrics.throughput >= min_throughput,
            "error_count_acceptable": metrics.error_count / metrics.total_requests <= (1 - min_success_rate) if metrics.total_requests > 0 else True
        }
        
        validations["overall_passed"] = all(validations.values())
        
        return validations
EOF

# Import AI service and providers from Day 13
cat > app/services/__init__.py << 'EOF'
# Re-export AI service components from Day 13
from .ai_service import AIService
from .provider_manager import ProviderManager

__all__ = ['AIService', 'ProviderManager']
EOF

# Copy AI service structure from Day 13 (simplified version)
cat > app/services/ai_service.py << 'EOF'
import os
from typing import Dict, List, Optional, Any
from loguru import logger
from .provider_manager import ProviderManager
from ..providers.anthropic_provider import AnthropicProvider
from ..providers.mock_provider import MockProvider

class AIService:
    def __init__(self):
        self.provider_manager = ProviderManager()
        self.initialize_providers()
        
    def initialize_providers(self) -> None:
        # Add Anthropic provider if API key is available
        anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic_key and anthropic_key != "your_anthropic_key_here":
            anthropic_provider = AnthropicProvider(
                anthropic_key,
                os.getenv("ANTHROPIC_MODEL", "claude-3-sonnet-20240229")
            )
            self.provider_manager.add_provider(anthropic_provider, True)
            logger.info("Initialized Anthropic provider")
        
        # Add mock providers for testing
        self.provider_manager.add_provider(MockProvider("mock-primary"), not anthropic_key)
        self.provider_manager.add_provider(MockProvider("mock-fallback"))
        
        logger.info("AI Service initialized with providers")
    
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info(f"Generating text for prompt: \"{prompt[:50]}{'...' if len(prompt) > 50 else ''}\"")
        
        try:
            response = await self.provider_manager.generate_text(prompt, options)
            logger.info(f"Text generated successfully using {response['provider']}")
            return response
        except Exception as error:
            logger.error(f"Text generation failed: {error}")
            raise error
    
    async def get_provider_health(self) -> List[Dict[str, Any]]:
        return self.provider_manager.get_health_status()
    
    def get_available_providers(self) -> List[str]:
        return self.provider_manager.get_provider_names()
EOF

# Provider manager (simplified from Day 13)
cat > app/services/provider_manager.py << 'EOF'
from typing import Dict, List, Optional, Any
import time
from loguru import logger
from ..providers.base_provider import BaseProvider

class ProviderHealth:
    def __init__(self, provider: str, is_healthy: bool = True, error_count: int = 0):
        self.provider = provider
        self.is_healthy = is_healthy
        self.last_checked = time.time()
        self.response_time = None
        self.error_count = error_count

class ProviderManager:
    def __init__(self):
        self.providers: Dict[str, BaseProvider] = {}
        self.health_status: Dict[str, ProviderHealth] = {}
        self.primary_provider = None
        
    def add_provider(self, provider: BaseProvider, is_primary: bool = False) -> None:
        name = provider.get_provider_name()
        self.providers[name] = provider
        self.health_status[name] = ProviderHealth(name)
        
        if is_primary or not self.primary_provider:
            self.primary_provider = name
            
        logger.info(f"Added provider: {name} (primary: {is_primary})")
    
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        available_providers = await self.get_healthy_providers()
        
        if not available_providers:
            raise Exception("No healthy providers available")
        
        # Try primary provider first if healthy
        if self.primary_provider and self.primary_provider in available_providers:
            try:
                response = await self.call_provider(self.primary_provider, prompt, options)
                logger.info(f"Successfully used primary provider: {self.primary_provider}")
                return response
            except Exception as error:
                logger.warning(f"Primary provider {self.primary_provider} failed, trying fallback")
                await self.update_health_status(self.primary_provider, False)
        
        # Try fallback providers
        for provider_name in available_providers:
            if provider_name == self.primary_provider:
                continue
                
            try:
                response = await self.call_provider(provider_name, prompt, options)
                logger.info(f"Successfully used fallback provider: {provider_name}")
                return response
            except Exception as error:
                logger.warning(f"Provider {provider_name} failed: {error}")
                await self.update_health_status(provider_name, False)
        
        raise Exception("All providers failed")
    
    async def call_provider(self, provider_name: str, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        provider = self.providers.get(provider_name)
        if not provider:
            raise Exception(f"Provider {provider_name} not found")
        
        response = await provider.generate_text(prompt, options)
        await self.update_health_status(provider_name, True, response["response_time"])
        return response
    
    async def get_healthy_providers(self) -> List[str]:
        healthy_providers = []
        
        for name, provider in self.providers.items():
            try:
                is_healthy = await provider.is_healthy()
                await self.update_health_status(name, is_healthy)
                
                if is_healthy:
                    healthy_providers.append(name)
            except Exception as error:
                logger.error(f"Health check failed for {name}: {error}")
                await self.update_health_status(name, False)
        
        return healthy_providers
    
    async def update_health_status(self, provider_name: str, is_healthy: bool, response_time: Optional[int] = None) -> None:
        current_status = self.health_status.get(provider_name)
        if not current_status:
            return
        
        current_status.is_healthy = is_healthy
        current_status.last_checked = time.time()
        current_status.response_time = response_time
        current_status.error_count = 0 if is_healthy else current_status.error_count + 1
    
    def get_health_status(self) -> List[Dict[str, Any]]:
        return [
            {
                "provider": status.provider,
                "is_healthy": status.is_healthy,
                "last_checked": status.last_checked,
                "response_time": status.response_time,
                "error_count": status.error_count
            }
            for status in self.health_status.values()
        ]
    
    def get_provider_names(self) -> List[str]:
        return list(self.providers.keys())
EOF

# Copy providers from Day 13
cat > app/providers/__init__.py << 'EOF'
from .base_provider import BaseProvider
from .anthropic_provider import AnthropicProvider
from .mock_provider import MockProvider

__all__ = ['BaseProvider', 'AnthropicProvider', 'MockProvider']
EOF

cat > app/providers/base_provider.py << 'EOF'
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import time
from loguru import logger

class BaseProvider(ABC):
    def __init__(self, name: str):
        self.name = name
        self.error_count = 0
        self.last_health_check = None
        
    @abstractmethod
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        pass
    
    @abstractmethod
    async def is_healthy(self) -> bool:
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        pass
    
    def get_provider_name(self) -> str:
        return self.name
    
    def increment_error_count(self) -> None:
        self.error_count += 1
        
    def reset_error_count(self) -> None:
        self.error_count = 0
        
    def get_error_count(self) -> int:
        return self.error_count
EOF

cat > app/providers/anthropic_provider.py << 'EOF'
import anthropic
from typing import Dict, Any, Optional
import time
from loguru import logger
from .base_provider import BaseProvider

class AnthropicProvider(BaseProvider):
    def __init__(self, api_key: str, model: str = "claude-3-sonnet-20240229"):
        super().__init__("anthropic")
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            options = options or {}
            
            response = self.client.messages.create(
                model=options.get('model', self.model),
                max_tokens=options.get('max_tokens', 1000),
                temperature=options.get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            response_time = int((time.time() - start_time) * 1000)
            self.reset_error_count()
            
            return {
                "content": response.content[0].text if response.content else "",
                "provider": self.get_provider_name(),
                "model": self.model,
                "tokens_used": response.usage.output_tokens,
                "response_time": response_time,
                "metadata": {
                    "input_tokens": response.usage.input_tokens,
                    "stop_reason": response.stop_reason
                }
            }
            
        except Exception as error:
            self.increment_error_count()
            logger.error(f"Anthropic provider error: {error}")
            raise error
    
    async def is_healthy(self) -> bool:
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=10,
                messages=[{"role": "user", "content": "health check"}]
            )
            self.last_health_check = time.time()
            return True
        except Exception as error:
            logger.error(f"Anthropic health check failed: {error}")
            return False
    
    def get_model_name(self) -> str:
        return self.model
EOF

cat > app/providers/mock_provider.py << 'EOF'
import asyncio
import random
import time
from typing import Dict, Any, Optional
from .base_provider import BaseProvider

class MockProvider(BaseProvider):
    def __init__(self, name: str = "mock", should_fail: bool = False):
        super().__init__(name)
        self.should_fail = should_fail
        self.response_delay = 0.1
        
    async def generate_text(self, prompt: str, options: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        start_time = time.time()
        
        if self.should_fail:
            self.increment_error_count()
            raise Exception("Mock provider intentionally failed")
        
        await asyncio.sleep(self.response_delay)
        
        response_time = int((time.time() - start_time) * 1000)
        self.reset_error_count()
        
        return {
            "content": f"Mock response to: \"{prompt[:50]}{'...' if len(prompt) > 50 else ''}\"",
            "provider": self.get_provider_name(),
            "model": "mock-model-v1",
            "tokens_used": random.randint(50, 150),
            "response_time": response_time,
            "metadata": {"mock_response": True}
        }
    
    async def is_healthy(self) -> bool:
        return not self.should_fail
    
    def get_model_name(self) -> str:
        return "mock-model-v1"
    
    def set_should_fail(self, should_fail: bool) -> None:
        self.should_fail = should_fail
        
    def set_response_delay(self, delay: float) -> None:
        self.response_delay = delay
EOF

# FastAPI main application with testing endpoints
cat > app/main.py << 'EOF'
import os
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
from loguru import logger
import sys

from .services.ai_service import AIService
from .testing.ai_test_suite import AITestSuite
from .validators.content_validator import ContentValidator
from .validators.performance_validator import PerformanceValidator

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))
logger.add("logs/ai_testing.log", rotation="500 MB", level="INFO")

app = FastAPI(title="AI Testing Framework", version="1.0.0")

# Initialize services
ai_service = AIService()
ai_test_suite = AITestSuite(ai_service)
content_validator = ContentValidator()
performance_validator = PerformanceValidator()

# Global test state
test_results = {}

# Request models
class GenerateRequest(BaseModel):
    prompt: str
    options: Optional[Dict[str, Any]] = None

class TestSuiteRequest(BaseModel):
    test_cases: List[Dict[str, Any]]
    suite_name: Optional[str] = "custom_suite"

class ValidateContentRequest(BaseModel):
    content: str
    criteria: Optional[Dict[str, Any]] = None

# Mount static files for React frontend
app.mount("/static", StaticFiles(directory="../frontend/build"), name="static")

@app.get("/")
async def read_root():
    return FileResponse("../frontend/build/index.html")

# AI Service endpoints
@app.post("/api/generate")
async def generate_text(request: GenerateRequest):
    try:
        response = await ai_service.generate_text(request.prompt, request.options)
        return response
    except Exception as error:
        logger.error(f"Generation failed: {error}")
        raise HTTPException(status_code=500, detail=str(error))

@app.get("/api/providers")
async def get_providers():
    providers = ai_service.get_available_providers()
    health = await ai_service.get_provider_health()
    return {"providers": providers, "health": health}

# Testing endpoints
@app.post("/api/test/run-suite")
async def run_test_suite(request: TestSuiteRequest, background_tasks: BackgroundTasks):
    """Run a test suite asynchronously"""
    suite_name = request.suite_name
    test_id = f"test_{int(time.time())}"
    
    # Initialize test state
    test_results[test_id] = {
        "status": "running",
        "suite_name": suite_name,
        "start_time": time.time(),
        "results": None
    }
    
    # Run tests in background
    background_tasks.add_task(run_test_suite_background, test_id, request.test_cases)
    
    return {"test_id": test_id, "status": "started"}

async def run_test_suite_background(test_id: str, test_cases: List[Dict[str, Any]]):
    """Background task to run test suite"""
    try:
        results = await ai_test_suite.run_suite(test_cases)
        summary = ai_test_suite.get_summary()
        
        test_results[test_id].update({
            "status": "completed",
            "results": summary,
            "end_time": time.time()
        })
    except Exception as e:
        test_results[test_id].update({
            "status": "failed",
            "error": str(e),
            "end_time": time.time()
        })

@app.get("/api/test/status/{test_id}")
async def get_test_status(test_id: str):
    """Get test execution status"""
    if test_id not in test_results:
        raise HTTPException(status_code=404, detail="Test not found")
    
    return test_results[test_id]

@app.get("/api/test/predefined-suites")
async def get_predefined_test_suites():
    """Get predefined test suites"""
    return {
        "basic_generation": [
            {
                "name": "simple_generation",
                "type": "generation",
                "prompt": "Explain artificial intelligence in simple terms",
                "expected_keywords": ["artificial", "intelligence", "computer", "learn"],
                "min_length": 50
            },
            {
                "name": "technical_generation",
                "type": "generation", 
                "prompt": "Describe machine learning algorithms",
                "expected_keywords": ["machine", "learning", "algorithm", "data"],
                "min_length": 100
            }
        ],
        "failover_tests": [
            {
                "name": "provider_failover",
                "type": "failover",
                "prompt": "Test failover mechanism"
            }
        ],
        "performance_tests": [
            {
                "name": "load_test",
                "type": "performance",
                "prompt": "Performance test prompt",
                "concurrent_requests": 5,
                "max_response_time": 3000
            }
        ],
        "semantic_tests": [
            {
                "name": "semantic_quality",
                "type": "semantic",
                "prompt": "Explain quantum computing",
                "expected_topics": ["quantum", "computing", "physics"],
                "min_quality_score": 0.7
            }
        ]
    }

@app.post("/api/validate/content")
async def validate_content(request: ValidateContentRequest):
    """Validate content quality"""
    try:
        result = content_validator.validate_response(request.content, request.criteria)
        return {
            "is_valid": result.is_valid,
            "score": result.score,
            "details": result.details,
            "errors": result.errors
        }
    except Exception as error:
        logger.error(f"Content validation failed: {error}")
        raise HTTPException(status_code=500, detail=str(error))

@app.post("/api/validate/performance")
async def validate_performance(test_config: Dict[str, Any]):
    """Run performance validation"""
    try:
        result = await performance_validator.validate_performance(ai_service, test_config)
        return result
    except Exception as error:
        logger.error(f"Performance validation failed: {error}")
        raise HTTPException(status_code=500, detail=str(error))

@app.get("/health")
async def health_check():
    try:
        provider_health = await ai_service.get_provider_health()
        return {
            "status": "healthy",
            "providers": provider_health,
            "testing_framework": "ready"
        }
    except Exception as error:
        raise HTTPException(status_code=500, detail=str(error))

if __name__ == "__main__":
    import uvicorn
    import time
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
EOF

# Create comprehensive test files
echo "🧪 Creating comprehensive test files..."

cat > tests/test_ai_test_suite.py << 'EOF'
import pytest
import asyncio
from app.testing.ai_test_suite import AITestSuite
from app.services.ai_service import AIService
from app.providers.mock_provider import MockProvider

@pytest.mark.asyncio
async def test_ai_test_suite_basic_generation():
    # Setup
    ai_service = AIService()
    test_suite = AITestSuite(ai_service)
    
    test_cases = [
        {
            "name": "basic_test",
            "type": "generation",
            "prompt": "Test prompt",
            "expected_keywords": ["test"],
            "min_length": 10
        }
    ]
    
    # Execute
    results = await test_suite.run_suite(test_cases)
    summary = test_suite.get_summary()
    
    # Verify
    assert len(results) == 1
    assert summary["summary"]["total"] == 1
    assert summary["summary"]["passed"] >= 0

@pytest.mark.asyncio
async def test_ai_test_suite_performance():
    ai_service = AIService()
    test_suite = AITestSuite(ai_service)
    
    test_cases = [
        {
            "name": "performance_test",
            "type": "performance", 
            "prompt": "Performance test",
            "concurrent_requests": 3,
            "max_response_time": 5000
        }
    ]
    
    results = await test_suite.run_suite(test_cases)
    assert len(results) == 1
    assert results[0].test_name == "performance_test"

@pytest.mark.asyncio
async def test_ai_test_suite_semantic_quality():
    ai_service = AIService()
    test_suite = AITestSuite(ai_service)
    
    test_cases = [
        {
            "name": "semantic_test",
            "type": "semantic",
            "prompt": "Explain machine learning",
            "expected_topics": ["machine", "learning"],
            "min_quality_score": 0.5
        }
    ]
    
    results = await test_suite.run_suite(test_cases)
    assert len(results) == 1
    assert results[0].details.get("quality_score") is not None
EOF

cat > tests/test_validators.py << 'EOF'
import pytest
from app.validators.content_validator import ContentValidator
from app.validators.performance_validator import PerformanceValidator

def test_content_validator_basic():
    validator = ContentValidator()
    
    content = "This is a test response with artificial intelligence concepts explained clearly."
    criteria = {
        "required_keywords": ["test", "intelligence"],
        "min_words": 5,
        "max_words": 100
    }
    
    result = validator.validate_response(content, criteria)
    
    assert result.score > 0
    assert result.details["word_count"] > 0
    assert result.details["keyword_coverage"] > 0

def test_content_validator_short_content():
    validator = ContentValidator()
    
    content = "Short"
    criteria = {"min_words": 10}
    
    result = validator.validate_response(content, criteria)
    
    assert not result.is_valid
    assert len(result.errors) > 0

@pytest.mark.asyncio
async def test_performance_validator():
    from app.services.ai_service import AIService
    
    validator = PerformanceValidator()
    ai_service = AIService()
    
    test_config = {
        "concurrent_users": 2,
        "requests_per_user": 2,
        "prompt": "Test performance",
        "max_response_time": 10000,
        "min_success_rate": 0.5
    }
    
    result = await validator.validate_performance(ai_service, test_config)
    
    assert "metrics" in result
    assert "validation" in result
    assert result["metrics"]["total_requests"] > 0
EOF

# Environment configuration
cat > .env.example << 'EOF'
# AI Provider API Keys
ANTHROPIC_API_KEY=your_anthropic_key_here

# Application Configuration
LOG_LEVEL=INFO
ANTHROPIC_MODEL=claude-3-sonnet-20240229

# Testing Configuration
MAX_TEST_CONCURRENCY=10
TEST_TIMEOUT_SECONDS=30
PERFORMANCE_TEST_DURATION=60
EOF

cp .env.example .env

# Golden datasets for testing
echo "📚 Creating golden datasets..."
mkdir -p golden_datasets

cat > golden_datasets/basic_prompts.json << 'EOF'
{
  "dataset_name": "basic_prompts",
  "version": "1.0",
  "test_cases": [
    {
      "prompt": "Explain artificial intelligence in simple terms",
      "expected_keywords": ["artificial", "intelligence", "computer", "machine", "learn"],
      "min_words": 30,
      "max_words": 200,
      "expected_topics": ["AI", "technology", "automation"]
    },
    {
      "prompt": "What is machine learning?",
      "expected_keywords": ["machine", "learning", "data", "algorithm", "pattern"],
      "min_words": 25,
      "max_words": 150,
      "expected_topics": ["ML", "data science", "algorithms"]
    },
    {
      "prompt": "Describe the benefits of cloud computing",
      "expected_keywords": ["cloud", "computing", "scalability", "cost", "access"],
      "min_words": 40,
      "max_words": 250,
      "expected_topics": ["cloud", "infrastructure", "benefits"]
    }
  ]
}
EOF

# Move to frontend directory
cd ../frontend

echo "⚛️ Creating React frontend with testing dashboard..."

# Initialize React app structure
mkdir -p src/{components,services,styles,utils}
mkdir -p public

# Package.json for React
cat > package.json << 'EOF'
{
  "name": "ai-testing-dashboard",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "recharts": "^2.8.0",
    "react-router-dom": "^6.8.0",
    "@heroicons/react": "^2.0.18"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  },
  "proxy": "http://localhost:8000"
}
EOF

# React main app component
cat > src/App.js << 'EOF'
import React, { useState, useEffect } from 'react';
import TestDashboard from './components/TestDashboard';
import AIGenerator from './components/AIGenerator';
import PerformanceMonitor from './components/PerformanceMonitor';
import './styles/App.css';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [systemHealth, setSystemHealth] = useState(null);

  useEffect(() => {
    checkSystemHealth();
    const interval = setInterval(checkSystemHealth, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkSystemHealth = async () => {
    try {
      const response = await fetch('/health');
      const data = await response.json();
      setSystemHealth(data);
    } catch (error) {
      console.error('Health check failed:', error);
      setSystemHealth({ status: 'unhealthy', error: error.message });
    }
  };

  const renderActiveComponent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <TestDashboard systemHealth={systemHealth} />;
      case 'generator':
        return <AIGenerator />;
      case 'performance':
        return <PerformanceMonitor />;
      default:
        return <TestDashboard systemHealth={systemHealth} />;
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>AI Testing Framework</h1>
          <div className="system-status">
            <span className={`status-indicator ${systemHealth?.status || 'unknown'}`}>
              {systemHealth?.status === 'healthy' ? '🟢' : '🔴'}
            </span>
            <span className="status-text">
              {systemHealth?.status === 'healthy' ? 'System Online' : 'System Issues'}
            </span>
          </div>
        </div>
        
        <nav className="navigation">
          <button 
            className={`nav-button ${activeTab === 'dashboard' ? 'active' : ''}`}
            onClick={() => setActiveTab('dashboard')}
          >
            Test Dashboard
          </button>
          <button 
            className={`nav-button ${activeTab === 'generator' ? 'active' : ''}`}
            onClick={() => setActiveTab('generator')}
          >
            AI Generator
          </button>
          <button 
            className={`nav-button ${activeTab === 'performance' ? 'active' : ''}`}
            onClick={() => setActiveTab('performance')}
          >
            Performance Monitor
          </button>
        </nav>
      </header>

      <main className="app-main">
        {renderActiveComponent()}
      </main>
    </div>
  );
}

export default App;
EOF

# Test Dashboard Component
cat > src/components/TestDashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import TestSuiteRunner from './TestSuiteRunner';
import TestResults from './TestResults';
import ProviderStatus from './ProviderStatus';

const TestDashboard = ({ systemHealth }) => {
  const [testSuites, setTestSuites] = useState({});
  const [activeTests, setActiveTests] = useState([]);
  const [testHistory, setTestHistory] = useState([]);

  useEffect(() => {
    loadPredefinedSuites();
    loadTestHistory();
  }, []);

  const loadPredefinedSuites = async () => {
    try {
      const response = await fetch('/api/test/predefined-suites');
      const data = await response.json();
      setTestSuites(data);
    } catch (error) {
      console.error('Failed to load test suites:', error);
    }
  };

  const loadTestHistory = () => {
    const history = JSON.parse(localStorage.getItem('testHistory') || '[]');
    setTestHistory(history.slice(-10)); // Keep last 10 test runs
  };

  const handleTestStart = (testId, suiteName) => {
    setActiveTests(prev => [...prev, { testId, suiteName, startTime: new Date() }]);
  };

  const handleTestComplete = (testId, results) => {
    setActiveTests(prev => prev.filter(test => test.testId !== testId));
    
    const testRecord = {
      testId,
      timestamp: new Date().toISOString(),
      results,
      summary: results.summary
    };
    
    const updatedHistory = [...testHistory, testRecord].slice(-10);
    setTestHistory(updatedHistory);
    localStorage.setItem('testHistory', JSON.stringify(updatedHistory));
  };

  return (
    <div className="test-dashboard">
      <div className="dashboard-grid">
        <div className="dashboard-section">
          <h2>System Status</h2>
          <ProviderStatus providers={systemHealth?.providers || []} />
        </div>

        <div className="dashboard-section">
          <h2>Test Suite Runner</h2>
          <TestSuiteRunner 
            testSuites={testSuites}
            onTestStart={handleTestStart}
            onTestComplete={handleTestComplete}
          />
        </div>

        <div className="dashboard-section full-width">
          <h2>Active Tests</h2>
          {activeTests.length === 0 ? (
            <p className="no-data">No active tests</p>
          ) : (
            <div className="active-tests">
              {activeTests.map(test => (
                <div key={test.testId} className="active-test">
                  <span className="test-name">{test.suiteName}</span>
                  <span className="test-status">Running...</span>
                  <span className="test-duration">
                    {Math.floor((new Date() - test.startTime) / 1000)}s
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="dashboard-section full-width">
          <h2>Test History</h2>
          <TestResults testHistory={testHistory} />
        </div>
      </div>
    </div>
  );
};

export default TestDashboard;
EOF

# Test Suite Runner Component
cat > src/components/TestSuiteRunner.js << 'EOF'
import React, { useState } from 'react';

const TestSuiteRunner = ({ testSuites, onTestStart, onTestComplete }) => {
  const [selectedSuite, setSelectedSuite] = useState('');
  const [isRunning, setIsRunning] = useState(false);
  const [customTestCases, setCustomTestCases] = useState('');

  const runTestSuite = async (suiteName, testCases) => {
    setIsRunning(true);
    
    try {
      // Start test suite
      const response = await fetch('/api/test/run-suite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          test_cases: testCases,
          suite_name: suiteName
        })
      });
      
      const { test_id } = await response.json();
      onTestStart(test_id, suiteName);
      
      // Poll for results
      const pollResults = async () => {
        try {
          const statusResponse = await fetch(`/api/test/status/${test_id}`);
          const status = await statusResponse.json();
          
          if (status.status === 'completed' || status.status === 'failed') {
            onTestComplete(test_id, status.results || { error: status.error });
            setIsRunning(false);
          } else {
            setTimeout(pollResults, 2000); // Poll every 2 seconds
          }
        } catch (error) {
          console.error('Error polling test status:', error);
          setIsRunning(false);
        }
      };
      
      pollResults();
      
    } catch (error) {
      console.error('Failed to start test suite:', error);
      setIsRunning(false);
    }
  };

  const handleRunPredefinedSuite = () => {
    if (!selectedSuite || !testSuites[selectedSuite]) return;
    
    const testCases = testSuites[selectedSuite];
    runTestSuite(selectedSuite, testCases);
  };

  const handleRunCustomSuite = () => {
    try {
      const testCases = JSON.parse(customTestCases);
      runTestSuite('custom_suite', testCases);
    } catch (error) {
      alert('Invalid JSON format for test cases');
    }
  };

  return (
    <div className="test-suite-runner">
      <div className="predefined-suites">
        <h3>Predefined Test Suites</h3>
        <select 
          value={selectedSuite} 
          onChange={(e) => setSelectedSuite(e.target.value)}
          disabled={isRunning}
        >
          <option value="">Select a test suite</option>
          {Object.keys(testSuites).map(suiteName => (
            <option key={suiteName} value={suiteName}>
              {suiteName.replace('_', ' ').toUpperCase()}
            </option>
          ))}
        </select>
        
        <button 
          onClick={handleRunPredefinedSuite}
          disabled={!selectedSuite || isRunning}
          className="run-button"
        >
          {isRunning ? 'Running...' : 'Run Suite'}
        </button>
      </div>

      <div className="custom-suite">
        <h3>Custom Test Cases</h3>
        <textarea
          value={customTestCases}
          onChange={(e) => setCustomTestCases(e.target.value)}
          placeholder='[{"name": "test1", "type": "generation", "prompt": "test prompt"}]'
          rows={6}
          disabled={isRunning}
        />
        
        <button 
          onClick={handleRunCustomSuite}
          disabled={!customTestCases.trim() || isRunning}
          className="run-button"
        >
          Run Custom Suite
        </button>
      </div>
    </div>
  );
};

export default TestSuiteRunner;
EOF

# Test Results Component
cat > src/components/TestResults.js << 'EOF'
import React, { useState } from 'react';

const TestResults = ({ testHistory }) => {
  const [selectedTest, setSelectedTest] = useState(null);

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return '#4caf50';
      case 'failed': return '#f44336';
      case 'running': return '#ff9800';
      default: return '#757575';
    }
  };

  const formatDuration = (seconds) => {
    if (seconds < 60) return `${Math.round(seconds)}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = Math.round(seconds % 60);
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div className="test-results">
      {testHistory.length === 0 ? (
        <p className="no-data">No test history available</p>
      ) : (
        <>
          <div className="results-list">
            {testHistory.map((test, index) => (
              <div 
                key={test.testId} 
                className={`result-item ${selectedTest?.testId === test.testId ? 'selected' : ''}`}
                onClick={() => setSelectedTest(test)}
              >
                <div className="result-header">
                  <span className="test-name">{test.testId}</span>
                  <span 
                    className="test-status"
                    style={{ color: getStatusColor(test.results?.status) }}
                  >
                    {test.results?.status || 'unknown'}
                  </span>
                </div>
                
                <div className="result-summary">
                  <span className="timestamp">
                    {new Date(test.timestamp).toLocaleString()}
                  </span>
                  
                  {test.summary && (
                    <div className="summary-stats">
                      <span className="stat passed">✓ {test.summary.passed}</span>
                      <span className="stat failed">✗ {test.summary.failed}</span>
                      <span className="stat duration">
                        ⏱ {formatDuration(test.summary.total_execution_time)}
                      </span>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {selectedTest && (
            <div className="result-details">
              <h3>Test Details: {selectedTest.testId}</h3>
              
              {selectedTest.summary && (
                <div className="summary-section">
                  <h4>Summary</h4>
                  <div className="summary-grid">
                    <div className="summary-item">
                      <span className="label">Total Tests:</span>
                      <span className="value">{selectedTest.summary.total}</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Passed:</span>
                      <span className="value passed">{selectedTest.summary.passed}</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Failed:</span>
                      <span className="value failed">{selectedTest.summary.failed}</span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Success Rate:</span>
                      <span className="value">
                        {Math.round(selectedTest.summary.success_rate * 100)}%
                      </span>
                    </div>
                    <div className="summary-item">
                      <span className="label">Avg Time:</span>
                      <span className="value">
                        {Math.round(selectedTest.summary.average_test_time * 1000)}ms
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {selectedTest.results?.results && (
                <div className="individual-results">
                  <h4>Individual Test Results</h4>
                  {selectedTest.results.results.map((result, index) => (
                    <div key={index} className="individual-result">
                      <div className="result-name">
                        <span className={`status-dot ${result.status}`}></span>
                        {result.test_name}
                      </div>
                      <div className="result-details-content">
                        <div className="detail-item">
                          <span className="label">Execution Time:</span>
                          <span className="value">{Math.round(result.execution_time * 1000)}ms</span>
                        </div>
                        
                        {result.details && Object.keys(result.details).length > 0 && (
                          <div className="detail-item">
                            <span className="label">Details:</span>
                            <pre className="details-json">
                              {JSON.stringify(result.details, null, 2)}
                            </pre>
                          </div>
                        )}
                        
                        {result.error_message && (
                          <div className="detail-item error">
                            <span className="label">Error:</span>
                            <span className="value">{result.error_message}</span>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default TestResults;
EOF

# Provider Status Component
cat > src/components/ProviderStatus.js << 'EOF'
import React from 'react';

const ProviderStatus = ({ providers }) => {
  const formatTimestamp = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleTimeString();
  };

  return (
    <div className="provider-status">
      {providers.length === 0 ? (
        <p className="no-data">No provider information available</p>
      ) : (
        <div className="providers-grid">
          {providers.map((provider, index) => (
            <div key={index} className={`provider-card ${provider.is_healthy ? 'healthy' : 'unhealthy'}`}>
              <div className="provider-header">
                <h4 className="provider-name">{provider.provider}</h4>
                <span className={`status-badge ${provider.is_healthy ? 'healthy' : 'unhealthy'}`}>
                  {provider.is_healthy ? '🟢 Healthy' : '🔴 Unhealthy'}
                </span>
              </div>
              
              <div className="provider-details">
                <div className="detail-row">
                  <span className="label">Last Checked:</span>
                  <span className="value">{formatTimestamp(provider.last_checked)}</span>
                </div>
                
                {provider.response_time && (
                  <div className="detail-row">
                    <span className="label">Response Time:</span>
                    <span className="value">{provider.response_time}ms</span>
                  </div>
                )}
                
                <div className="detail-row">
                  <span className="label">Error Count:</span>
                  <span className={`value ${provider.error_count > 0 ? 'error' : ''}`}>
                    {provider.error_count}
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ProviderStatus;
EOF

# AI Generator Component
cat > src/components/AIGenerator.js << 'EOF'
import React, { useState } from 'react';

const AIGenerator = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [validationResult, setValidationResult] = useState(null);

  const generateText = async () => {
    if (!prompt.trim()) return;
    
    setIsLoading(true);
    setResponse(null);
    setValidationResult(null);
    
    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt })
      });
      
      const data = await response.json();
      setResponse(data);
      
      // Auto-validate the response
      await validateContent(data.content);
      
    } catch (error) {
      console.error('Generation failed:', error);
      setResponse({ error: error.message });
    } finally {
      setIsLoading(false);
    }
  };

  const validateContent = async (content) => {
    try {
      const response = await fetch('/api/validate/content', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          content,
          criteria: {
            min_words: 10,
            max_words: 500,
            required_keywords: prompt.split(' ').slice(0, 3), // Use first 3 words as keywords
            min_score: 0.6
          }
        })
      });
      
      const validation = await response.json();
      setValidationResult(validation);
      
    } catch (error) {
      console.error('Validation failed:', error);
    }
  };

  return (
    <div className="ai-generator">
      <div className="generator-form">
        <h2>AI Text Generator</h2>
        
        <div className="form-group">
          <label htmlFor="prompt">Enter your prompt:</label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="Ask the AI to generate content..."
            rows={4}
            disabled={isLoading}
          />
        </div>
        
        <button 
          onClick={generateText}
          disabled={!prompt.trim() || isLoading}
          className="generate-button"
        >
          {isLoading ? 'Generating...' : 'Generate Text'}
        </button>
      </div>

      {response && (
        <div className="response-section">
          <h3>Generated Response</h3>
          
          {response.error ? (
            <div className="error-message">
              Error: {response.error}
            </div>
          ) : (
            <>
              <div className="response-content">
                {response.content}
              </div>
              
              <div className="response-metadata">
                <div className="metadata-grid">
                  <div className="metadata-item">
                    <span className="label">Provider:</span>
                    <span className="value">{response.provider}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="label">Model:</span>
                    <span className="value">{response.model}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="label">Tokens Used:</span>
                    <span className="value">{response.tokens_used}</span>
                  </div>
                  <div className="metadata-item">
                    <span className="label">Response Time:</span>
                    <span className="value">{response.response_time}ms</span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      )}

      {validationResult && (
        <div className="validation-section">
          <h3>Content Validation</h3>
          
          <div className={`validation-status ${validationResult.is_valid ? 'valid' : 'invalid'}`}>
            <span className="status-icon">
              {validationResult.is_valid ? '✅' : '❌'}
            </span>
            <span className="status-text">
              {validationResult.is_valid ? 'Content is valid' : 'Content validation failed'}
            </span>
            <span className="score">
              Score: {Math.round(validationResult.score * 100)}%
            </span>
          </div>
          
          <div className="validation-details">
            <div className="details-grid">
              <div className="detail-item">
                <span className="label">Word Count:</span>
                <span className="value">{validationResult.details.word_count}</span>
              </div>
              <div className="detail-item">
                <span className="label">Keyword Coverage:</span>
                <span className="value">
                  {Math.round(validationResult.details.keyword_coverage * 100)}%
                </span>
              </div>
              <div className="detail-item">
                <span className="label">Coherence Score:</span>
                <span className="value">
                  {Math.round(validationResult.details.coherence_score * 100)}%
                </span>
              </div>
            </div>
            
            {validationResult.errors && validationResult.errors.length > 0 && (
              <div className="validation-errors">
                <h4>Validation Errors:</h4>
                <ul>
                  {validationResult.errors.map((error, index) => (
                    <li key={index}>{error}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AIGenerator;
EOF

# Performance Monitor Component
cat > src/components/PerformanceMonitor.js << 'EOF'
import React, { useState } from 'react';

const PerformanceMonitor = () => {
  const [testConfig, setTestConfig] = useState({
    concurrent_users: 5,
    requests_per_user: 3,
    prompt: 'Performance test prompt for load testing',
    max_response_time: 3000,
    min_success_rate: 0.9
  });
  
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);

  const runPerformanceTest = async () => {
    setIsRunning(true);
    setResults(null);
    
    try {
      const response = await fetch('/api/validate/performance', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(testConfig)
      });
      
      const data = await response.json();
      setResults(data);
      
    } catch (error) {
      console.error('Performance test failed:', error);
      setResults({ error: error.message });
    } finally {
      setIsRunning(false);
    }
  };

  const updateConfig = (field, value) => {
    setTestConfig(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <div className="performance-monitor">
      <div className="test-configuration">
        <h2>Performance Test Configuration</h2>
        
        <div className="config-grid">
          <div className="config-item">
            <label>Concurrent Users:</label>
            <input
              type="number"
              value={testConfig.concurrent_users}
              onChange={(e) => updateConfig('concurrent_users', parseInt(e.target.value))}
              min="1"
              max="20"
              disabled={isRunning}
            />
          </div>
          
          <div className="config-item">
            <label>Requests per User:</label>
            <input
              type="number"
              value={testConfig.requests_per_user}
              onChange={(e) => updateConfig('requests_per_user', parseInt(e.target.value))}
              min="1"
              max="10"
              disabled={isRunning}
            />
          </div>
          
          <div className="config-item">
            <label>Max Response Time (ms):</label>
            <input
              type="number"
              value={testConfig.max_response_time}
              onChange={(e) => updateConfig('max_response_time', parseInt(e.target.value))}
              min="100"
              max="10000"
              step="100"
              disabled={isRunning}
            />
          </div>
          
          <div className="config-item">
            <label>Min Success Rate:</label>
            <input
              type="number"
              value={testConfig.min_success_rate}
              onChange={(e) => updateConfig('min_success_rate', parseFloat(e.target.value))}
              min="0"
              max="1"
              step="0.1"
              disabled={isRunning}
            />
          </div>
        </div>
        
        <div className="config-item full-width">
          <label>Test Prompt:</label>
          <textarea
            value={testConfig.prompt}
            onChange={(e) => updateConfig('prompt', e.target.value)}
            rows={3}
            disabled={isRunning}
          />
        </div>
        
        <button 
          onClick={runPerformanceTest}
          disabled={isRunning}
          className="run-test-button"
        >
          {isRunning ? 'Running Performance Test...' : 'Run Performance Test'}
        </button>
      </div>

      {results && (
        <div className="test-results">
          <h2>Performance Test Results</h2>
          
          {results.error ? (
            <div className="error-message">
              Error: {results.error}
            </div>
          ) : (
            <>
              <div className={`overall-status ${results.passed ? 'passed' : 'failed'}`}>
                <span className="status-icon">
                  {results.passed ? '✅' : '❌'}
                </span>
                <span className="status-text">
                  {results.passed ? 'Performance test passed' : 'Performance test failed'}
                </span>
              </div>
              
              <div className="metrics-grid">
                <div className="metric-card">
                  <div className="metric-value">
                    {Math.round(results.metrics.avg_response_time)}ms
                  </div>
                  <div className="metric-label">Average Response Time</div>
                </div>
                
                <div className="metric-card">
                  <div className="metric-value">
                    {Math.round(results.metrics.p95_response_time)}ms
                  </div>
                  <div className="metric-label">95th Percentile</div>
                </div>
                
                <div className="metric-card">
                  <div className="metric-value">
                    {Math.round(results.metrics.success_rate * 100)}%
                  </div>
                  <div className="metric-label">Success Rate</div>
                </div>
                
                <div className="metric-card">
                  <div className="metric-value">
                    {Math.round(results.metrics.throughput * 10) / 10}
                  </div>
                  <div className="metric-label">Requests/Second</div>
                </div>
                
                <div className="metric-card">
                  <div className="metric-value">
                    {results.metrics.total_requests}
                  </div>
                  <div className="metric-label">Total Requests</div>
                </div>
                
                <div className="metric-card">
                  <div className="metric-value">
                    {results.metrics.error_count}
                  </div>
                  <div className="metric-label">Errors</div>
                </div>
              </div>
              
              <div className="validation-results">
                <h3>Validation Results</h3>
                <div className="validation-grid">
                  {Object.entries(results.validation).map(([key, value]) => {
                    if (key === 'overall_passed') return null;
                    
                    return (
                      <div key={key} className={`validation-item ${value ? 'passed' : 'failed'}`}>
                        <span className="validation-icon">
                          {value ? '✅' : '❌'}
                        </span>
                        <span className="validation-name">
                          {key.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                        </span>
                      </div>
                    );
                  })}
                </div>
              </div>
            </>
          )}
        </div>
      )}
    </div>
  );
};

export default PerformanceMonitor;
EOF

# App.css styles with Google Cloud Skills Boost theme
cat > src/styles/App.css << 'EOF'
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: 'Google Sans', 'Roboto', sans-serif;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  min-height: 100vh;
  color: #333;
}

.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header Styles */
.app-header {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 1rem 2rem;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.header-content h1 {
  color: #1a73e8;
  font-size: 2rem;
  font-weight: 400;
}

.system-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 20px;
}

.status-indicator {
  font-size: 0.8rem;
}

.status-text {
  font-size: 0.9rem;
  font-weight: 500;
  color: #5f6368;
}

.navigation {
  display: flex;
  gap: 1rem;
}

.nav-button {
  background: transparent;
  border: 2px solid #e8eaed;
  color: #5f6368;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: all 0.2s ease;
}

.nav-button:hover {
  border-color: #1a73e8;
  color: #1a73e8;
}

.nav-button.active {
  background: #1a73e8;
  border-color: #1a73e8;
  color: white;
}

/* Main Content */
.app-main {
  flex: 1;
  padding: 2rem;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

/* Dashboard Styles */
.test-dashboard {
  height: 100%;
}

.dashboard-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  height: 100%;
}

.dashboard-section {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 2rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.dashboard-section.full-width {
  grid-column: 1 / -1;
}

.dashboard-section h2 {
  color: #1a73e8;
  font-size: 1.5rem;
  font-weight: 400;
  margin-bottom: 1.5rem;
}

/* Provider Status */
.providers-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.provider-card {
  background: #f8f9fa;
  border: 2px solid #e8eaed;
  border-radius: 12px;
  padding: 1rem;
  transition: all 0.2s ease;
}

.provider-card.healthy {
  border-color: #4caf50;
  background: #e8f5e8;
}

.provider-card.unhealthy {
  border-color: #f44336;
  background: #ffebee;
}

.provider-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.provider-name {
  font-size: 1.1rem;
  font-weight: 600;
  color: #333;
}

.status-badge {
  font-size: 0.8rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-weight: 500;
}

.status-badge.healthy {
  background: #e8f5e8;
  color: #2e7d32;
}

.status-badge.unhealthy {
  background: #ffebee;
  color: #c62828;
}

.provider-details .detail-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.detail-row .label {
  color: #5f6368;
  font-size: 0.9rem;
}

.detail-row .value {
  font-weight: 500;
  color: #333;
}

.detail-row .value.error {
  color: #f44336;
}

/* Test Suite Runner */
.test-suite-runner {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.predefined-suites, .custom-suite {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.predefined-suites h3, .custom-suite h3 {
  color: #333;
  font-size: 1.1rem;
  margin-bottom: 0.5rem;
}

.predefined-suites select, .custom-suite textarea {
  width: 100%;
  padding: 0.75rem;
  border: 2px solid #e8eaed;
  border-radius: 8px;
  font-size: 0.9rem;
  font-family: inherit;
}

.predefined-suites select:focus, .custom-suite textarea:focus {
  outline: none;
  border-color: #1a73e8;
}

.run-button {
  background: #1a73e8;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background-color 0.2s;
}

.run-button:hover:not(:disabled) {
  background: #1557b0;
}

.run-button:disabled {
  background: #e8eaed;
  color: #9aa0a6;
  cursor: not-allowed;
}

/* Test Results */
.test-results {
  display: flex;
  gap: 2rem;
  height: 400px;
}

.results