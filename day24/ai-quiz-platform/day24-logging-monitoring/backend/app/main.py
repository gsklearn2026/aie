from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
<<<<<<< HEAD
# from middleware.logging_middleware import LoggingMiddleware
=======
from middleware.logging_middleware import LoggingMiddleware
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
from services.logging_service import logging_service
from services.metrics_service import metrics_service
from config.logging_config import LoggingConfig
import structlog
import time
import os
from contextlib import asynccontextmanager
from typing import Dict, Any, List, Optional
from datetime import datetime
import google.generativeai as genai

# Configure structured logging
logger = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AI Quiz Platform Logging Service")
    
    # Initialize services
    await logging_service.initialize()
    metrics_service.start_metrics_server(LoggingConfig.METRICS_PORT)
    
    # Configure Gemini AI
    genai.configure(api_key=os.getenv("GEMINI_API_KEY", "your-api-key-here"))
    
    logger.info("Application startup complete")
    yield
    
    # Shutdown
    logger.info("Shutting down application")

app = FastAPI(
    title="AI Quiz Platform - Logging Service",
    description="Centralized logging and monitoring for AI Quiz Platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
=======
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3002", "http://127.0.0.1:3002"],
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add logging middleware
<<<<<<< HEAD
# app.add_middleware(LoggingMiddleware)
=======
app.add_middleware(LoggingMiddleware)
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "AI Quiz Platform Logging Service", "status": "healthy"}

<<<<<<< HEAD
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

=======
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
@app.post("/api/v1/log")
async def log_event(event_data: Dict[str, Any], background_tasks: BackgroundTasks):
    """Log a custom event"""
    try:
        # Add service metadata
        event_data.update({
            "service": "quiz-platform",
            "environment": os.getenv("ENVIRONMENT", "development"),
            "version": "1.0.0"
        })
        
        # Log the event in background
        background_tasks.add_task(logging_service.log_event, event_data)
        
        logger.info("Custom event logged", event_type=event_data.get("event"))
        
        return {"status": "logged", "event_id": event_data.get("event_id")}
        
    except Exception as e:
<<<<<<< HEAD
        logger.error("Failed to log event", error_msg=str(e))
=======
        logger.error("Failed to log event", error=str(e))
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
        raise HTTPException(status_code=500, detail="Failed to log event")

@app.get("/api/v1/logs/search")
async def search_logs(
    query: str = "",
    start_time: Optional[str] = None,
    end_time: Optional[str] = None,
    limit: int = 100
):
    """Search logs with optional filters"""
    try:
        # Parse time parameters
        start_dt = datetime.fromisoformat(start_time) if start_time else None
        end_dt = datetime.fromisoformat(end_time) if end_time else None
        
        # Search logs
        logs = await logging_service.search_logs(query, start_dt, end_dt, limit)
        
<<<<<<< HEAD
        logger.info("Log search performed", search_query=query, result_count=len(logs))
=======
        logger.info("Log search performed", query=query, result_count=len(logs))
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
        
        return {
            "logs": logs,
            "total": len(logs),
            "query": query
        }
        
    except Exception as e:
<<<<<<< HEAD
        logger.error("Log search failed", error_msg=str(e))
=======
        logger.error("Log search failed", error=str(e))
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
        raise HTTPException(status_code=500, detail="Log search failed")

@app.get("/api/v1/metrics/summary")
async def get_metrics_summary():
    """Get logging and system metrics summary"""
    try:
        # Update system metrics
        metrics_service.update_system_metrics()
        
        # Get logging metrics
        logging_metrics = await logging_service.get_metrics_summary()
        
        # Get system metrics
        import psutil
        system_metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "uptime_seconds": time.time() - metrics_service.start_time
        }
        
        logger.info("Metrics summary requested")
        
        return {
            "logging": logging_metrics,
            "system": system_metrics,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
<<<<<<< HEAD
        logger.error("Failed to get metrics summary", error_msg=str(e))
=======
        logger.error("Failed to get metrics summary", error=str(e))
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
        raise HTTPException(status_code=500, detail="Failed to get metrics")

@app.post("/api/v1/quiz/submit")
async def submit_quiz_answer(
    request: Request,
    quiz_data: Dict[str, Any],
    background_tasks: BackgroundTasks
):
    """Mock quiz submission endpoint with comprehensive logging"""
    start_time = time.perf_counter()
    
    try:
        # Extract user context
        user_id = getattr(request.state, "user_id", "anonymous")
        session_id = getattr(request.state, "session_id", "unknown")
        request_id = getattr(request.state, "request_id", "unknown")
        
        # Simulate AI processing
        question = quiz_data.get("question", "")
        user_answer = quiz_data.get("answer", "")
        
        # Log quiz submission
        await logging_service.log_event({
            "event": "quiz_submission",
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "question_id": quiz_data.get("question_id"),
            "quiz_type": quiz_data.get("quiz_type", "general"),
            "question_length": len(question),
            "answer_length": len(user_answer)
        })
        
        # Simulate AI inference with Gemini
        ai_start = time.perf_counter()
        
        try:
            model = genai.GenerativeModel('gemini-pro')
            prompt = f"Evaluate this quiz answer. Question: {question} Answer: {user_answer}"
            response = model.generate_content(prompt)
            ai_result = response.text[:200]  # Truncate for demo
            
        except Exception as ai_error:
<<<<<<< HEAD
            logger.warning("AI inference failed, using fallback", error_msg=str(ai_error))
=======
            logger.warning("AI inference failed, using fallback", error=str(ai_error))
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
            ai_result = "Answer evaluation unavailable"
        
        ai_duration = time.perf_counter() - ai_start
        
        # Record metrics
        metrics_service.record_ai_inference(ai_duration)
        metrics_service.record_quiz_submission(quiz_data.get("quiz_type", "general"))
        
        # Log AI inference
        await logging_service.log_event({
            "event": "ai_inference",
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "inference_duration_ms": round(ai_duration * 1000, 2),
            "model": "gemini-pro",
            "prompt_length": len(prompt) if 'prompt' in locals() else 0,
            "response_length": len(ai_result)
        })
        
        total_duration = time.perf_counter() - start_time
        
        # Log completion
        await logging_service.log_event({
            "event": "quiz_submission_complete",
            "user_id": user_id,
            "session_id": session_id,
            "request_id": request_id,
            "total_duration_ms": round(total_duration * 1000, 2),
            "success": True
        })
        
        return {
            "status": "success",
            "evaluation": ai_result,
            "processing_time_ms": round(total_duration * 1000, 2),
            "request_id": request_id
        }
        
    except Exception as e:
        duration = time.perf_counter() - start_time
        
        # Log error
        await logging_service.log_event({
            "event": "quiz_submission_error",
            "user_id": getattr(request.state, "user_id", "anonymous"),
            "session_id": getattr(request.state, "session_id", "unknown"),
            "request_id": getattr(request.state, "request_id", "unknown"),
            "error_type": type(e).__name__,
            "error_message": str(e),
            "duration_ms": round(duration * 1000, 2)
        })
        
<<<<<<< HEAD
        logger.error("Quiz submission failed", error_msg=str(e))
=======
        logger.error("Quiz submission failed", error=str(e))
>>>>>>> 3cb0bb496e11cb6195a51dfec69cafd2b5fedeae
        raise HTTPException(status_code=500, detail="Quiz submission failed")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
