import os
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
from dotenv import load_dotenv
from loguru import logger
import sys
import time

from .services.ai_service import AIService

# Load environment variables
load_dotenv()

# Configure logging
logger.remove()
logger.add(sys.stderr, level=os.getenv("LOG_LEVEL", "INFO"))
logger.add("logs/ai_service.log", rotation="500 MB", level="INFO")

app = FastAPI(title="AI Abstraction Layer", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI service
ai_service = AIService()

# Request models
class GenerateRequest(BaseModel):
    prompt: str
    options: Optional[Dict[str, Any]] = None

class GenerateResponse(BaseModel):
    content: str
    provider: str
    model: str
    tokens_used: int
    response_time: int
    metadata: Optional[Dict[str, Any]] = None

# Mount static files
frontend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend'))
app.mount("/static", StaticFiles(directory=frontend_dir), name="static")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(frontend_dir, "index.html"))

@app.get("/health")
async def health_check():
    try:
        provider_health = await ai_service.get_provider_health()
        return {
            "status": "healthy",
            "providers": provider_health,
            "timestamp": time.time()
        }
    except Exception as error:
        logger.error(f"Health check failed: {error}")
        raise HTTPException(status_code=500, detail={
            "status": "unhealthy",
            "error": str(error)
        })

@app.post("/api/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    try:
        if not request.prompt:
            raise HTTPException(status_code=400, detail="Prompt is required")
        
        response = await ai_service.generate_text(request.prompt, request.options)
        return GenerateResponse(**response)
    except Exception as error:
        logger.error(f"Generation failed: {error}")
        raise HTTPException(status_code=500, detail={
            "error": str(error)
        })

@app.get("/api/providers")
async def get_providers():
    providers = ai_service.get_available_providers()
    return {"providers": providers}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
