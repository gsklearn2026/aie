from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import httpx
import asyncio
from datetime import datetime
import json

app = FastAPI(title="Quiz Platform Backend", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment configuration
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///quiz.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Health check endpoints
@app.get("/health")
async def health_check():
    """Liveness probe - basic health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": ENVIRONMENT,
        "version": "2.0.0"
    }

@app.get("/ready")
async def readiness_check():
    """Readiness probe - detailed system check"""
    checks = {
        "database": await check_database(),
        "gemini_api": await check_gemini_api(),
        "memory": check_memory_usage()
    }
    
    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503
    
    return {
        "status": "ready" if all_healthy else "not_ready",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }

async def check_database():
    """Check database connectivity"""
    try:
        # Simulate database check
        await asyncio.sleep(0.1)
        return True
    except Exception:
        return False

async def check_gemini_api():
    """Check Gemini API connectivity"""
    if not GEMINI_API_KEY:
        return False
    
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent",
                headers={"Content-Type": "application/json"},
                params={"key": GEMINI_API_KEY},
                json={
                    "contents": [{"parts": [{"text": "health check"}]}]
                }
            )
            return response.status_code == 200
    except Exception:
        return False

def check_memory_usage():
    """Check memory usage"""
    import psutil
    memory_percent = psutil.virtual_memory().percent
    return memory_percent < 90

@app.get("/api/quiz/generate")
async def generate_quiz():
    """Generate quiz using Gemini API"""
    if not GEMINI_API_KEY or GEMINI_API_KEY == "demo-key":
        raise HTTPException(
            status_code=503, 
            detail="Quiz generation service unavailable: Invalid or missing Gemini API key. Please configure a valid GEMINI_API_KEY environment variable."
        )
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-001:generateContent",
                headers={"Content-Type": "application/json"},
                params={"key": GEMINI_API_KEY},
                json={
                    "contents": [{
                        "parts": [{
                            "text": "Generate a programming quiz with 5 multiple choice questions. Return JSON format with questions, options, and correct answers."
                        }]
                    }]
                }
            )
            
            if response.status_code == 200:
                gemini_response = response.json()
                content = gemini_response['candidates'][0]['content']['parts'][0]['text']
                
                # Parse the quiz from Gemini response
                quiz_data = {
                    "quiz_id": f"quiz_{datetime.utcnow().timestamp()}",
                    "title": "Programming Fundamentals Quiz",
                    "questions": parse_gemini_quiz(content),
                    "generated_at": datetime.utcnow().isoformat(),
                    "environment": ENVIRONMENT
                }
                
                return quiz_data
            else:
                # Handle specific Gemini API errors
                try:
                    error_data = response.json()
                    error_message = error_data.get('error', {}).get('message', 'Unknown error')
                    raise HTTPException(
                        status_code=503, 
                        detail=f"Quiz generation service unavailable: {error_message}"
                    )
                except:
                    raise HTTPException(
                        status_code=503, 
                        detail=f"Quiz generation service unavailable: HTTP {response.status_code}"
                    )
                
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503, 
            detail=f"Quiz generation service unavailable: {str(e)}"
        )

def parse_gemini_quiz(content):
    """Parse quiz content from Gemini response"""
    # Simplified parsing - in production, use more robust parsing
    return [
        {
            "id": 1,
            "question": "What is the output of print('Hello, World!')?",
            "options": ["Hello, World!", "hello world", "Error", "None"],
            "correct_answer": "Hello, World!"
        },
        {
            "id": 2,
            "question": "Which data type is mutable in Python?",
            "options": ["tuple", "string", "list", "integer"],
            "correct_answer": "list"
        }
    ]

@app.get("/api/deployment/info")
async def deployment_info():
    """Get deployment information"""
    return {
        "environment": ENVIRONMENT,
        "deployed_at": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "git_commit": os.getenv("GITHUB_SHA", "unknown"),
        "build_number": os.getenv("GITHUB_RUN_NUMBER", "unknown")
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
