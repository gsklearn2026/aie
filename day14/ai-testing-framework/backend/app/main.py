import os
import time
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
