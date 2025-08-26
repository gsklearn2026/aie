#!/bin/bash

# Day 25: Error Handling Framework Implementation Script
# AI Quiz Platform - Error Handling Framework

set -e

echo "🚀 Setting up Day 25: Error Handling Framework for AI Quiz Platform"

# Create project structure
mkdir -p ai-quiz-platform/backend/{src/{api,core,middleware,models,services,tests},logs,config}
mkdir -p ai-quiz-platform/frontend/{src/{components,hooks,services,utils,tests},public}
mkdir -p ai-quiz-platform/docker
mkdir -p ai-quiz-platform/scripts

cd ai-quiz-platform

# Backend Implementation
echo "📦 Creating Backend Error Handling Framework..."

# Requirements file
cat > backend/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
python-dotenv==1.0.0
redis==5.0.1
google-generativeai==0.3.2
pydantic==2.5.0
httpx==0.25.2
structlog==23.2.0
pytest==7.4.3
pytest-asyncio==0.21.1
watchdog==3.0.0
aiofiles==23.2.1
websockets==12.0
pydantic-settings==2.1.0
tenacity==8.2.3
EOF

# Environment configuration
cat > backend/.env << 'EOF'
# AI Quiz Platform Configuration
APP_NAME=ai-quiz-platform
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO

# API Keys
GEMINI_API_KEY=your_gemini_api_key_here

# Database
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Error Handling
MAX_RETRY_ATTEMPTS=3
CIRCUIT_BREAKER_FAILURE_THRESHOLD=5
CIRCUIT_BREAKER_RECOVERY_TIMEOUT=60
EOF

# Core error handling models
cat > backend/src/models/errors.py << 'EOF'
from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel
from datetime import datetime
import uuid

class ErrorType(str, Enum):
    CLIENT_ERROR = "client_error"
    SERVER_ERROR = "server_error"
    AI_SERVICE_ERROR = "ai_service_error"
    BUSINESS_LOGIC_ERROR = "business_logic_error"
    AUTHENTICATION_ERROR = "authentication_error"
    VALIDATION_ERROR = "validation_error"
    RATE_LIMIT_ERROR = "rate_limit_error"
    NETWORK_ERROR = "network_error"

class ErrorSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class CircuitBreakerState(str, Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class ErrorContext(BaseModel):
    error_id: str
    timestamp: datetime
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    details: Optional[Dict[str, Any]] = None
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    request_path: Optional[str] = None
    correlation_id: Optional[str] = None
    retry_count: int = 0
    recoverable: bool = True
    user_facing_message: Optional[str] = None

    @classmethod
    def create(cls, error_type: ErrorType, message: str, **kwargs):
        return cls(
            error_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            error_type=error_type,
            message=message,
            **kwargs
        )

class ErrorResponse(BaseModel):
    success: bool = False
    error_id: str
    message: str
    details: Optional[Dict[str, Any]] = None
    retry_after: Optional[int] = None
EOF

# Circuit breaker implementation
cat > backend/src/core/circuit_breaker.py << 'EOF'
import asyncio
import time
from typing import Callable, Any
from datetime import datetime, timedelta
from src.models.errors import CircuitBreakerState
import structlog

logger = structlog.get_logger()

class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: tuple = (Exception,)
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitBreakerState.CLOSED
        
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        if self.state == CircuitBreakerState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitBreakerState.HALF_OPEN
                logger.info("Circuit breaker moving to HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self) -> bool:
        return (
            self.last_failure_time and
            time.time() - self.last_failure_time >= self.recovery_timeout
        )
    
    def _on_success(self):
        self.failure_count = 0
        self.state = CircuitBreakerState.CLOSED
        logger.info("Circuit breaker reset to CLOSED state")
    
    def _on_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitBreakerState.OPEN
            logger.warning(f"Circuit breaker OPENED after {self.failure_count} failures")
    
    def get_state(self) -> dict:
        return {
            "state": self.state,
            "failure_count": self.failure_count,
            "last_failure_time": self.last_failure_time,
            "failure_threshold": self.failure_threshold
        }
EOF

# Error classification service
cat > backend/src/services/error_classifier.py << 'EOF'
import re
from typing import Dict, Any
from src.models.errors import ErrorType, ErrorSeverity, ErrorContext
import structlog

logger = structlog.get_logger()

class ErrorClassifier:
    def __init__(self):
        self.classification_rules = {
            # AI Service Errors
            r"rate.?limit|quota.?exceeded|too.?many.?requests": {
                "type": ErrorType.RATE_LIMIT_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": True,
                "user_message": "AI service is busy. Please try again in a moment."
            },
            r"gemini|openai|anthropic.*unavailable|service.?unavailable": {
                "type": ErrorType.AI_SERVICE_ERROR,
                "severity": ErrorSeverity.HIGH,
                "recoverable": True,
                "user_message": "AI service is temporarily unavailable. Trying alternative approach."
            },
            
            # Authentication Errors
            r"unauthorized|invalid.?token|authentication.?failed": {
                "type": ErrorType.AUTHENTICATION_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": False,
                "user_message": "Please log in again to continue."
            },
            
            # Validation Errors
            r"validation.?error|invalid.?input|bad.?request": {
                "type": ErrorType.VALIDATION_ERROR,
                "severity": ErrorSeverity.LOW,
                "recoverable": False,
                "user_message": "Please check your input and try again."
            },
            
            # Network Errors
            r"connection.?timeout|network.?error|dns.?resolution": {
                "type": ErrorType.NETWORK_ERROR,
                "severity": ErrorSeverity.MEDIUM,
                "recoverable": True,
                "user_message": "Network issue detected. Retrying automatically."
            }
        }
    
    def classify_error(self, error: Exception, context: Dict[str, Any] = None) -> ErrorContext:
        error_message = str(error).lower()
        
        # Default classification
        error_type = ErrorType.SERVER_ERROR
        severity = ErrorSeverity.HIGH
        recoverable = False
        user_message = "An unexpected error occurred. Our team has been notified."
        
        # Apply classification rules
        for pattern, rules in self.classification_rules.items():
            if re.search(pattern, error_message):
                error_type = rules["type"]
                severity = rules["severity"]
                recoverable = rules["recoverable"]
                user_message = rules["user_message"]
                break
        
        # HTTP status code based classification
        if hasattr(error, 'status_code'):
            if 400 <= error.status_code < 500:
                error_type = ErrorType.CLIENT_ERROR
                severity = ErrorSeverity.LOW
            elif error.status_code >= 500:
                error_type = ErrorType.SERVER_ERROR
                severity = ErrorSeverity.HIGH
        
        return ErrorContext.create(
            error_type=error_type,
            message=str(error),
            severity=severity,
            recoverable=recoverable,
            user_facing_message=user_message,
            details=context or {}
        )
EOF

# Retry mechanism
cat > backend/src/core/retry_handler.py << 'EOF'
import asyncio
import random
from typing import Callable, Any, Type
from tenacity import (
    retry, stop_after_attempt, wait_exponential_jitter,
    retry_if_exception_type, before_sleep_log
)
from src.models.errors import ErrorType
import structlog

logger = structlog.get_logger()

class RetryHandler:
    @staticmethod
    def get_retry_decorator(error_type: ErrorType, max_attempts: int = 3):
        """Get appropriate retry decorator based on error type"""
        
        if error_type == ErrorType.RATE_LIMIT_ERROR:
            return retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential_jitter(initial=1, max=60, jitter=10),
                retry=retry_if_exception_type((Exception,)),
                before_sleep=before_sleep_log(logger, "warning")
            )
        
        elif error_type == ErrorType.NETWORK_ERROR:
            return retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential_jitter(initial=0.5, max=10),
                retry=retry_if_exception_type((Exception,)),
                before_sleep=before_sleep_log(logger, "info")
            )
        
        elif error_type == ErrorType.AI_SERVICE_ERROR:
            return retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential_jitter(initial=2, max=30),
                retry=retry_if_exception_type((Exception,)),
                before_sleep=before_sleep_log(logger, "warning")
            )
        
        else:
            # No retry for client errors, auth errors, etc.
            return lambda func: func

    @staticmethod
    async def execute_with_retry(
        func: Callable,
        error_type: ErrorType,
        max_attempts: int = 3,
        *args,
        **kwargs
    ) -> Any:
        """Execute function with appropriate retry logic"""
        
        if error_type in [ErrorType.CLIENT_ERROR, ErrorType.AUTHENTICATION_ERROR, ErrorType.VALIDATION_ERROR]:
            # No retry for these error types
            return await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
        
        retry_decorator = RetryHandler.get_retry_decorator(error_type, max_attempts)
        
        if asyncio.iscoroutinefunction(func):
            @retry_decorator
            async def wrapped():
                return await func(*args, **kwargs)
            return await wrapped()
        else:
            @retry_decorator
            def wrapped():
                return func(*args, **kwargs)
            return wrapped()
EOF

# Global error handler
cat > backend/src/middleware/error_handler.py << 'EOF'
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.middleware.base import BaseHTTPMiddleware
from src.models.errors import ErrorResponse, ErrorType, ErrorSeverity
from src.services.error_classifier import ErrorClassifier
from src.core.circuit_breaker import CircuitBreaker
import structlog
import traceback
import time

logger = structlog.get_logger()

class GlobalErrorHandler(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.error_classifier = ErrorClassifier()
        self.circuit_breakers = {}
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        try:
            response = await call_next(request)
            return response
            
        except Exception as error:
            # Log the error with context
            correlation_id = request.headers.get("x-correlation-id", "unknown")
            user_id = getattr(request.state, "user_id", None)
            
            error_context = self.error_classifier.classify_error(
                error,
                context={
                    "request_path": str(request.url),
                    "method": request.method,
                    "user_id": user_id,
                    "correlation_id": correlation_id,
                    "processing_time": time.time() - start_time
                }
            )
            
            # Log structured error
            logger.error(
                "Request failed",
                error_id=error_context.error_id,
                error_type=error_context.error_type,
                message=error_context.message,
                path=str(request.url),
                user_id=user_id,
                correlation_id=correlation_id,
                stack_trace=traceback.format_exc()
            )
            
            # Determine appropriate HTTP status code
            status_code = self._get_status_code(error_context.error_type)
            
            # Create user-friendly response
            error_response = ErrorResponse(
                error_id=error_context.error_id,
                message=error_context.user_facing_message or "An error occurred",
                details={
                    "type": error_context.error_type,
                    "recoverable": error_context.recoverable
                } if error_context.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL] else None
            )
            
            return JSONResponse(
                status_code=status_code,
                content=error_response.dict()
            )
    
    def _get_status_code(self, error_type: ErrorType) -> int:
        status_map = {
            ErrorType.CLIENT_ERROR: 400,
            ErrorType.AUTHENTICATION_ERROR: 401,
            ErrorType.VALIDATION_ERROR: 400,
            ErrorType.RATE_LIMIT_ERROR: 429,
            ErrorType.AI_SERVICE_ERROR: 503,
            ErrorType.NETWORK_ERROR: 503,
            ErrorType.SERVER_ERROR: 500,
            ErrorType.BUSINESS_LOGIC_ERROR: 422
        }
        return status_map.get(error_type, 500)

# Custom exception handlers
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            error_id="validation_error",
            message="Invalid input data",
            details={"validation_errors": exc.errors()}
        ).dict()
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error_id="http_error",
            message=exc.detail,
            details={"status_code": exc.status_code}
        ).dict()
    )
EOF

# AI service with error handling
cat > backend/src/services/ai_service.py << 'EOF'
import google.generativeai as genai
from typing import Dict, List, Any
from src.core.circuit_breaker import CircuitBreaker
from src.core.retry_handler import RetryHandler
from src.models.errors import ErrorType
import structlog
import os

logger = structlog.get_logger()

class AIService:
    def __init__(self):
        self.api_key = os.getenv("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        
        # Circuit breaker for AI service
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60
        )
        
        # Fallback questions for when AI fails
        self.fallback_questions = [
            {
                "question": "What is the primary goal of machine learning?",
                "options": ["To replace humans", "To find patterns in data", "To create robots", "To build websites"],
                "correct_answer": "To find patterns in data",
                "explanation": "Machine learning focuses on finding patterns and making predictions from data."
            },
            {
                "question": "Which algorithm is commonly used for classification?",
                "options": ["Linear Regression", "Decision Tree", "K-means", "PCA"],
                "correct_answer": "Decision Tree",
                "explanation": "Decision trees are popular classification algorithms that create decision rules."
            }
        ]
    
    async def generate_quiz_questions(self, topic: str, difficulty: str, count: int = 5) -> List[Dict[str, Any]]:
        """Generate quiz questions with error handling and fallback"""
        
        try:
            # Use circuit breaker
            questions = await self.circuit_breaker.call(
                self._generate_questions_with_ai, topic, difficulty, count
            )
            return questions
            
        except Exception as e:
            logger.warning(
                "AI service failed, using fallback questions",
                error=str(e),
                topic=topic,
                difficulty=difficulty
            )
            # Return fallback questions
            return self.fallback_questions[:count]
    
    async def _generate_questions_with_ai(self, topic: str, difficulty: str, count: int) -> List[Dict[str, Any]]:
        """Generate questions using AI with retry logic"""
        
        if not self.api_key:
            raise Exception("Gemini API key not configured")
        
        prompt = f"""
        Generate {count} multiple choice questions about {topic} with {difficulty} difficulty level.
        
        Return as JSON array with this format:
        [
            {{
                "question": "Question text",
                "options": ["Option A", "Option B", "Option C", "Option D"],
                "correct_answer": "Correct option text",
                "explanation": "Brief explanation"
            }}
        ]
        """
        
        try:
            # Execute with retry logic for AI service errors
            response = await RetryHandler.execute_with_retry(
                self._call_gemini_api,
                ErrorType.AI_SERVICE_ERROR,
                max_attempts=3,
                prompt=prompt
            )
            
            # Parse response (simplified for demo)
            questions = self._parse_ai_response(response.text)
            
            if not questions:
                raise Exception("AI returned empty response")
                
            return questions
            
        except Exception as e:
            logger.error("Failed to generate questions with AI", error=str(e))
            raise
    
    def _call_gemini_api(self, prompt: str):
        """Call Gemini API"""
        return self.model.generate_content(prompt)
    
    def _parse_ai_response(self, response_text: str) -> List[Dict[str, Any]]:
        """Parse AI response into question format"""
        # Simplified parsing - in production, use proper JSON parsing
        try:
            import json
            # Extract JSON from response
            start = response_text.find('[')
            end = response_text.rfind(']') + 1
            if start != -1 and end != 0:
                return json.loads(response_text[start:end])
        except:
            pass
        
        # Return fallback if parsing fails
        return self.fallback_questions
    
    def get_circuit_breaker_status(self) -> Dict[str, Any]:
        """Get circuit breaker status for monitoring"""
        return self.circuit_breaker.get_state()
EOF

# API endpoints
cat > backend/src/api/quiz_routes.py << 'EOF'
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from src.services.ai_service import AIService
from src.models.errors import ErrorType, ErrorContext
import structlog

logger = structlog.get_logger()
router = APIRouter(prefix="/api/quiz", tags=["quiz"])

# Dependency injection
def get_ai_service():
    return AIService()

@router.post("/generate")
async def generate_quiz(
    topic: str,
    difficulty: str = "medium",
    count: int = 5,
    ai_service: AIService = Depends(get_ai_service)
) -> Dict[str, Any]:
    """Generate quiz questions with error handling"""
    
    try:
        # Validate inputs
        if not topic or len(topic.strip()) == 0:
            raise HTTPException(status_code=400, detail="Topic is required")
        
        if count < 1 or count > 20:
            raise HTTPException(status_code=400, detail="Question count must be between 1 and 20")
        
        # Generate questions
        questions = await ai_service.generate_quiz_questions(topic, difficulty, count)
        
        return {
            "success": True,
            "data": {
                "questions": questions,
                "topic": topic,
                "difficulty": difficulty,
                "generated_count": len(questions)
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to generate quiz", error=str(e), topic=topic)
        raise HTTPException(status_code=500, detail="Failed to generate quiz questions")

@router.get("/health")
async def health_check(ai_service: AIService = Depends(get_ai_service)):
    """Health check endpoint with service status"""
    
    circuit_breaker_status = ai_service.get_circuit_breaker_status()
    
    return {
        "status": "healthy",
        "timestamp": "2025-08-14T10:30:00Z",
        "services": {
            "ai_service": {
                "status": "up" if circuit_breaker_status["state"] == "closed" else "degraded",
                "circuit_breaker": circuit_breaker_status
            }
        }
    }

@router.post("/submit")
async def submit_quiz(
    quiz_id: str,
    answers: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Submit quiz answers with validation"""
    
    try:
        if not quiz_id:
            raise HTTPException(status_code=400, detail="Quiz ID is required")
        
        if not answers:
            raise HTTPException(status_code=400, detail="Answers are required")
        
        # Simulate scoring logic
        score = len(answers) * 0.8  # 80% for demo
        
        return {
            "success": True,
            "data": {
                "quiz_id": quiz_id,
                "score": score,
                "total_questions": len(answers),
                "percentage": (score / len(answers)) * 100
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to submit quiz", error=str(e), quiz_id=quiz_id)
        raise HTTPException(status_code=500, detail="Failed to process quiz submission")
EOF

# Main application
cat > backend/src/main.py << 'EOF'
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from src.middleware.error_handler import (
    GlobalErrorHandler,
    validation_exception_handler,
    http_exception_handler
)
from src.api.quiz_routes import router as quiz_router
import structlog
import uvicorn

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

app = FastAPI(
    title="AI Quiz Platform",
    description="Error Handling Framework Demo",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global error handling middleware
app.add_middleware(GlobalErrorHandler)

# Exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, http_exception_handler)

# Routes
app.include_router(quiz_router)

@app.get("/")
async def root():
    return {"message": "AI Quiz Platform - Error Handling Framework", "status": "running"}

if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)
EOF

# Frontend Implementation
echo "🎨 Creating Frontend Error Handling Components..."

# Package.json
cat > frontend/package.json << 'EOF'
{
  "name": "ai-quiz-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1",
    "axios": "^1.6.0",
    "react-query": "^3.39.0",
    "react-router-dom": "^6.8.0",
    "react-hot-toast": "^2.4.1",
    "@heroicons/react": "^2.0.18",
    "tailwindcss": "^3.3.0",
    "autoprefixer": "^10.4.14",
    "postcss": "^8.4.24"
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
  }
}
EOF

# Error boundary component
cat > frontend/src/components/ErrorBoundary.js << 'EOF'
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error: error,
      errorInfo: errorInfo
    });
    
    // Log error to monitoring service
    console.error('Error Boundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
          <div className="sm:mx-auto sm:w-full sm:max-w-md">
            <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10">
              <div className="text-center">
                <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                  <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
                <h3 className="mt-4 text-lg font-medium text-gray-900">
                  Oops! Something went wrong
                </h3>
                <p className="mt-2 text-sm text-gray-500">
                  {this.props.fallbackMessage || "We're working to fix this issue. Please try refreshing the page."}
                </p>
                <div className="mt-6">
                  <button
                    onClick={() => window.location.reload()}
                    className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Refresh Page
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
EOF

# Error handling service
cat > frontend/src/services/errorHandler.js << 'EOF'
import toast from 'react-hot-toast';

class ErrorHandler {
  static handleError(error, context = {}) {
    console.error('Error occurred:', error, context);
    
    let userMessage = 'An unexpected error occurred';
    let shouldRetry = false;
    
    if (error.response) {
      // Server responded with error status
      const { status, data } = error.response;
      
      if (data && data.message) {
        userMessage = data.message;
      }
      
      if (data && data.details && data.details.recoverable) {
        shouldRetry = true;
      }
      
      // Handle specific status codes
      switch (status) {
        case 401:
          userMessage = 'Please log in again to continue';
          // Redirect to login
          setTimeout(() => {
            window.location.href = '/login';
          }, 2000);
          break;
        case 429:
          userMessage = 'Too many requests. Please wait a moment.';
          shouldRetry = true;
          break;
        case 503:
          userMessage = 'Service temporarily unavailable. Retrying...';
          shouldRetry = true;
          break;
      }
    } else if (error.request) {
      // Network error
      userMessage = 'Network connection issue. Please check your internet.';
      shouldRetry = true;
    }
    
    // Show user-friendly toast
    toast.error(userMessage, {
      duration: shouldRetry ? 5000 : 4000,
      position: 'top-right',
    });
    
    return { userMessage, shouldRetry };
  }
  
  static async withRetry(apiCall, maxRetries = 3, delay = 1000) {
    for (let attempt = 1; attempt <= maxRetries; attempt++) {
      try {
        return await apiCall();
      } catch (error) {
        if (attempt === maxRetries) {
          throw error;
        }
        
        const { shouldRetry } = this.handleError(error, { attempt });
        
        if (!shouldRetry) {
          throw error;
        }
        
        // Exponential backoff
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, attempt - 1)));
      }
    }
  }
}

export default ErrorHandler;
EOF

# API service with error handling
cat > frontend/src/services/api.js << 'EOF'
import axios from 'axios';
import ErrorHandler from './errorHandler';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

class ApiService {
  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    this.setupInterceptors();
  }
  
  setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add correlation ID for tracking
        config.headers['x-correlation-id'] = this.generateCorrelationId();
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        ErrorHandler.handleError(error);
        return Promise.reject(error);
      }
    );
  }
  
  generateCorrelationId() {
    return 'req_' + Math.random().toString(36).substr(2, 9);
  }
  
  async generateQuiz(topic, difficulty = 'medium', count = 5) {
    return ErrorHandler.withRetry(async () => {
      const response = await this.client.post('/api/quiz/generate', {
        topic,
        difficulty,
        count
      });
      return response.data;
    });
  }
  
  async submitQuiz(quizId, answers) {
    return ErrorHandler.withRetry(async () => {
      const response = await this.client.post('/api/quiz/submit', {
        quiz_id: quizId,
        answers
      });
      return response.data;
    });
  }
  
  async getHealthStatus() {
    const response = await this.client.get('/api/quiz/health');
    return response.data;
  }
}

export default new ApiService();
EOF

# Quiz dashboard component
cat > frontend/src/components/QuizDashboard.js << 'EOF'
import React, { useState, useEffect } from 'react';
import ErrorBoundary from './ErrorBoundary';
import ApiService from '../services/api';
import toast from 'react-hot-toast';

const QuizDashboard = () => {
  const [loading, setLoading] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [healthStatus, setHealthStatus] = useState(null);
  const [topic, setTopic] = useState('');
  const [difficulty, setDifficulty] = useState('medium');

  useEffect(() => {
    checkHealthStatus();
    const interval = setInterval(checkHealthStatus, 30000); // Check every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const checkHealthStatus = async () => {
    try {
      const status = await ApiService.getHealthStatus();
      setHealthStatus(status);
    } catch (error) {
      console.error('Health check failed:', error);
    }
  };

  const generateQuiz = async () => {
    if (!topic.trim()) {
      toast.error('Please enter a topic for your quiz');
      return;
    }

    setLoading(true);
    try {
      const result = await ApiService.generateQuiz(topic, difficulty, 5);
      if (result.success) {
        setQuestions(result.data.questions);
        setCurrentQuestion(0);
        setAnswers({});
        toast.success('Quiz generated successfully!');
      }
    } catch (error) {
      console.error('Failed to generate quiz:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerSelect = (questionIndex, answer) => {
    setAnswers(prev => ({
      ...prev,
      [questionIndex]: answer
    }));
  };

  const submitQuiz = async () => {
    try {
      const quizAnswers = Object.entries(answers).map(([index, answer]) => ({
        question_index: parseInt(index),
        selected_answer: answer
      }));

      const result = await ApiService.submitQuiz('quiz_123', quizAnswers);
      if (result.success) {
        toast.success(`Quiz completed! Score: ${result.data.percentage.toFixed(1)}%`);
      }
    } catch (error) {
      console.error('Failed to submit quiz:', error);
    }
  };

  const getServiceStatusColor = (status) => {
    switch (status) {
      case 'up': return 'text-green-600 bg-green-100';
      case 'degraded': return 'text-yellow-600 bg-yellow-100';
      default: return 'text-red-600 bg-red-100';
    }
  };

  return (
    <ErrorBoundary fallbackMessage="The quiz component encountered an error. Please try refreshing.">
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Header */}
          <div className="bg-white shadow rounded-lg p-6 mb-6">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold text-gray-900">AI Quiz Platform</h1>
              
              {/* Service Status */}
              {healthStatus && (
                <div className="flex items-center space-x-4">
                  <div className="text-sm">
                    <span className="text-gray-500">AI Service: </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getServiceStatusColor(healthStatus.services.ai_service.status)}`}>
                      {healthStatus.services.ai_service.status}
                    </span>
                  </div>
                  <div className="text-sm">
                    <span className="text-gray-500">Circuit Breaker: </span>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      healthStatus.services.ai_service.circuit_breaker.state === 'closed' 
                        ? 'text-green-600 bg-green-100' 
                        : 'text-red-600 bg-red-100'
                    }`}>
                      {healthStatus.services.ai_service.circuit_breaker.state}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Quiz Generation */}
          {questions.length === 0 && (
            <div className="bg-white shadow rounded-lg p-6 mb-6">
              <h2 className="text-lg font-medium text-gray-900 mb-4">Generate New Quiz</h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Topic</label>
                  <input
                    type="text"
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    placeholder="e.g., Machine Learning, Python, Data Science"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Difficulty</label>
                  <select
                    value={difficulty}
                    onChange={(e) => setDifficulty(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="easy">Easy</option>
                    <option value="medium">Medium</option>
                    <option value="hard">Hard</option>
                  </select>
                </div>
                
                <div className="flex items-end">
                  <button
                    onClick={generateQuiz}
                    disabled={loading}
                    className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-medium py-2 px-4 rounded-md transition-colors"
                  >
                    {loading ? 'Generating...' : 'Generate Quiz'}
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Quiz Questions */}
          {questions.length > 0 && (
            <div className="bg-white shadow rounded-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-lg font-medium text-gray-900">
                  Question {currentQuestion + 1} of {questions.length}
                </h2>
                <button
                  onClick={() => {
                    setQuestions([]);
                    setAnswers({});
                    setCurrentQuestion(0);
                  }}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Start New Quiz
                </button>
              </div>

              {questions[currentQuestion] && (
                <div className="space-y-4">
                  <h3 className="text-xl font-medium text-gray-800">
                    {questions[currentQuestion].question}
                  </h3>
                  
                  <div className="space-y-2">
                    {questions[currentQuestion].options.map((option, index) => (
                      <label key={index} className="flex items-center p-3 border rounded-lg hover:bg-gray-50 cursor-pointer">
                        <input
                          type="radio"
                          name={`question-${currentQuestion}`}
                          value={option}
                          checked={answers[currentQuestion] === option}
                          onChange={() => handleAnswerSelect(currentQuestion, option)}
                          className="mr-3"
                        />
                        <span className="text-gray-700">{option}</span>
                      </label>
                    ))}
                  </div>

                  <div className="flex justify-between pt-4">
                    <button
                      onClick={() => setCurrentQuestion(Math.max(0, currentQuestion - 1))}
                      disabled={currentQuestion === 0}
                      className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50 disabled:opacity-50"
                    >
                      Previous
                    </button>
                    
                    {currentQuestion < questions.length - 1 ? (
                      <button
                        onClick={() => setCurrentQuestion(currentQuestion + 1)}
                        className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        Next
                      </button>
                    ) : (
                      <button
                        onClick={submitQuiz}
                        className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
                      >
                        Submit Quiz
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
};

export default QuizDashboard;
EOF

# Main App component
cat > frontend/src/App.js << 'EOF'
import React from 'react';
import { Toaster } from 'react-hot-toast';
import QuizDashboard from './components/QuizDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

function App() {
  return (
    <ErrorBoundary>
      <div className="App">
        <QuizDashboard />
        <Toaster position="top-right" />
      </div>
    </ErrorBoundary>
  );
}

export default App;
EOF

# Main index file
cat > frontend/src/index.js << 'EOF'
import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
EOF

# CSS files
cat > frontend/src/index.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}
EOF

cat > frontend/src/App.css << 'EOF'
.App {
  text-align: left;
}
EOF

# HTML template
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="AI Quiz Platform with Error Handling Framework" />
    <title>AI Quiz Platform</title>
  </head>
  <body>
    <noscript>You need to enable JavaScript to run this app.</noscript>
    <div id="root"></div>
  </body>
</html>
EOF

# Tailwind config
cat > frontend/tailwind.config.js << 'EOF'
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
EOF

cat > frontend/postcss.config.js << 'EOF'
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}
EOF

# Tests
echo "🧪 Creating Test Files..."

cat > backend/src/tests/test_error_handling.py << 'EOF'
import pytest
import asyncio
from unittest.mock import Mock, patch
from src.services.error_classifier import ErrorClassifier
from src.core.circuit_breaker import CircuitBreaker
from src.core.retry_handler import RetryHandler
from src.models.errors import ErrorType, ErrorSeverity

class TestErrorClassifier:
    def setup_method(self):
        self.classifier = ErrorClassifier()
    
    def test_rate_limit_classification(self):
        error = Exception("Rate limit exceeded")
        context = self.classifier.classify_error(error)
        
        assert context.error_type == ErrorType.RATE_LIMIT_ERROR
        assert context.severity == ErrorSeverity.MEDIUM
        assert context.recoverable == True
        assert "AI service is busy" in context.user_facing_message
    
    def test_authentication_error_classification(self):
        error = Exception("Authentication failed")
        context = self.classifier.classify_error(error)
        
        assert context.error_type == ErrorType.AUTHENTICATION_ERROR
        assert context.recoverable == False
        assert "log in again" in context.user_facing_message

class TestCircuitBreaker:
    def setup_method(self):
        self.circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_opens_after_failures(self):
        async def failing_function():
            raise Exception("Service unavailable")
        
        # Trigger failures to open circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await self.circuit_breaker.call(failing_function)
        
        # Circuit should be open now
        assert self.circuit_breaker.state.value == "open"
        
        # Should raise exception without calling function
        with pytest.raises(Exception, match="Circuit breaker is OPEN"):
            await self.circuit_breaker.call(failing_function)
    
    @pytest.mark.asyncio
    async def test_circuit_breaker_recovers(self):
        async def sometimes_failing_function():
            if hasattr(sometimes_failing_function, 'call_count'):
                sometimes_failing_function.call_count += 1
            else:
                sometimes_failing_function.call_count = 1
            
            if sometimes_failing_function.call_count <= 3:
                raise Exception("Service unavailable")
            return "success"
        
        # Trigger failures to open circuit
        for _ in range(3):
            with pytest.raises(Exception):
                await self.circuit_breaker.call(sometimes_failing_function)
        
        # Wait for recovery timeout
        await asyncio.sleep(1.1)
        
        # Should succeed and close circuit
        result = await self.circuit_breaker.call(sometimes_failing_function)
        assert result == "success"
        assert self.circuit_breaker.state.value == "closed"

class TestRetryHandler:
    @pytest.mark.asyncio
    async def test_retry_for_rate_limit_errors(self):
        call_count = 0
        
        async def rate_limited_function():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Rate limit exceeded")
            return "success"
        
        result = await RetryHandler.execute_with_retry(
            rate_limited_function,
            ErrorType.RATE_LIMIT_ERROR,
            max_attempts=3
        )
        
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.asyncio
    async def test_no_retry_for_client_errors(self):
        call_count = 0
        
        async def client_error_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Bad request")
        
        with pytest.raises(Exception):
            await RetryHandler.execute_with_retry(
                client_error_function,
                ErrorType.CLIENT_ERROR,
                max_attempts=3
            )
        
        # Should only be called once (no retry)
        assert call_count == 1

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
EOF

# Frontend tests
mkdir -p frontend/src/components/__tests__
cat > frontend/src/components/__tests__/ErrorBoundary.test.js << 'EOF'
import React from 'react';
import { render, screen } from '@testing-library/react';
import ErrorBoundary from '../ErrorBoundary';

// Mock component that throws an error
const ThrowError = ({ shouldThrow }) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

describe('ErrorBoundary', () => {
  // Suppress console.error for these tests
  const originalError = console.error;
  beforeAll(() => {
    console.error = jest.fn();
  });
  
  afterAll(() => {
    console.error = originalError;
  });

  test('renders children when there is no error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('No error')).toBeInTheDocument();
  });

  test('renders error UI when there is an error', () => {
    render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Oops! Something went wrong')).toBeInTheDocument();
    expect(screen.getByText('Refresh Page')).toBeInTheDocument();
  });

  test('renders custom fallback message', () => {
    render(
      <ErrorBoundary fallbackMessage="Custom error message">
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    );
    
    expect(screen.getByText('Custom error message')).toBeInTheDocument();
  });
});
EOF

# Docker files
echo "🐳 Creating Docker Configuration..."

cat > docker/Dockerfile.backend << 'EOF'
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

# Create logs directory
RUN mkdir -p logs

EXPOSE 8000

CMD ["python", "-m", "src.main"]
EOF

cat > docker/Dockerfile.frontend << 'EOF'
FROM node:18-alpine as build

WORKDIR /app

COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
COPY docker/nginx.conf /etc/nginx/nginx.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
EOF

cat > docker/nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;
    
    upstream backend {
        server backend:8000;
    }
    
    server {
        listen 80;
        server_name localhost;
        
        location / {
            root /usr/share/nginx/html;
            index index.html index.htm;
            try_files $uri $uri/ /index.html;
        }
        
        location /api {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
EOF

cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  backend:
    build:
      context: .
      dockerfile: docker/Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - REDIS_URL=redis://redis:6379
      - ENVIRONMENT=development
    depends_on:
      - redis
    volumes:
      - ./backend/logs:/app/logs

  frontend:
    build:
      context: .
      dockerfile: docker/Dockerfile.frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

volumes:
  redis_data:
EOF

# Start/Stop scripts
echo "📜 Creating Start/Stop Scripts..."

cat > scripts/start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting AI Quiz Platform - Error Handling Framework"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start services
echo "🏃 Starting services..."

# Start backend in background
cd backend
export PYTHONPATH=.
python -m src.main &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend in background
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Services started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"

# Save PIDs for stop script
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "Press Ctrl+C to stop all services"
wait
EOF

cat > scripts/stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping AI Quiz Platform services..."

# Kill backend process
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo "✅ Backend stopped"
    fi
    rm .backend.pid
fi

# Kill frontend process
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo "✅ Frontend stopped"
    fi
    rm .frontend.pid
fi

# Kill any remaining processes
pkill -f "python -m src.main"
pkill -f "npm start"

echo "🏁 All services stopped"
EOF

chmod +x scripts/start.sh scripts/stop.sh

# Test runner script
cat > scripts/test.sh << 'EOF'
#!/bin/bash

echo "🧪 Running Error Handling Framework Tests"

# Backend tests
echo "🐍 Running Backend Tests..."
cd backend
source ../venv/bin/activate
export PYTHONPATH=.
python -m pytest src/tests/ -v
cd ..

# Frontend tests
echo "⚛️  Running Frontend Tests..."
cd frontend
npm test -- --watchAll=false
cd ..

echo "✅ All tests completed!"
EOF

chmod +x scripts/test.sh

# Demo script
cat > scripts/demo.sh << 'EOF'
#!/bin/bash

echo "🎬 Running Error Handling Framework Demo"

# Wait for services to be ready
echo "⏳ Waiting for services to start..."
sleep 10

echo "🔍 Testing API endpoints..."

# Test health endpoint
echo "Testing health endpoint..."
curl -s http://localhost:8000/api/quiz/health | jq .

# Test quiz generation with valid input
echo "Testing quiz generation (valid)..."
curl -s -X POST http://localhost:8000/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "Python", "difficulty": "medium", "count": 3}' | jq .

# Test quiz generation with invalid input (should trigger validation error)
echo "Testing validation error handling..."
curl -s -X POST http://localhost:8000/api/quiz/generate \
  -H "Content-Type: application/json" \
  -d '{"topic": "", "difficulty": "medium", "count": 25}' | jq .

# Test non-existent endpoint (should trigger 404 handling)
echo "Testing 404 error handling..."
curl -s http://localhost:8000/api/nonexistent | jq .

echo "✅ Demo completed! Check the responses above to see error handling in action."
echo "🌐 Visit http://localhost:3000 to see the full UI"
EOF

chmod +x scripts/demo.sh

echo "✅ AI Quiz Platform Error Handling Framework implementation completed!"
echo ""
echo "📁 Project structure created:"
echo "   - Backend: Python FastAPI with comprehensive error handling"
echo "   - Frontend: React with error boundaries and user-friendly error display"
echo "   - Error Classification: Automatic categorization and appropriate responses"
echo "   - Circuit Breaker: Protects against cascading failures"
echo "   - Retry Logic: Smart retry mechanisms for different error types"
echo "   - Tests: Comprehensive test suite for error handling components"
echo ""
echo "🚀 To start the application:"
echo "   ./scripts/start.sh"
echo ""
echo "🧪 To run tests:"
echo "   ./scripts/test.sh"
echo ""
echo "🎬 To run demo:"
echo "   ./scripts/demo.sh"
echo ""
echo "🛑 To stop all services:"
echo "   ./scripts/stop.sh"
echo ""
echo "🐳 To run with Docker:"
echo "   docker-compose up --build"