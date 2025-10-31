from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from .config.manager import config
from .config.database import db
from .services.gemini_service import gemini_service
import logging
import uvicorn

# Setup logging
logging.basicConfig(
    level=getattr(logging, config.get('logging.level', 'INFO')),
    format=config.get('logging.format', '%(asctime)s - %(levelname)s - %(message)s')
)

logger = logging.getLogger(__name__)

# Create FastAPI app with environment-specific settings
app = FastAPI(
    title=config.get('app.name', 'Quiz Platform'),
    version=config.get('app.version', '1.0.0'),
    debug=config.get('app.debug', False)
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.get('security.cors_origins', ["*"]),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize application"""
    logger.info(f"Starting {config.get('app.name')} in {config.env} environment")
    
    # Create database tables
    db.create_tables()
    
    logger.info("Application startup complete")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": f"Welcome to {config.get('app.name')}",
        "environment": config.env,
        "version": config.get('app.version'),
        "features": config.get('features', {})
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    db_healthy = db.health_check()
    ai_healthy = gemini_service.health_check()
    
    status = "healthy" if db_healthy and ai_healthy else "unhealthy"
    
    return JSONResponse(
        status_code=200 if status == "healthy" else 503,
        content={
            "status": status,
            "environment": config.env,
            "services": {
                "database": "healthy" if db_healthy else "unhealthy",
                "gemini_ai": "healthy" if ai_healthy else "unhealthy"
            }
        }
    )

@app.get("/config")
async def get_config():
    """Get safe configuration (non-sensitive values only)"""
    if not config.is_development():
        raise HTTPException(status_code=404, detail="Endpoint not available in production")
    
    return {
        "environment": config.env,
        "configuration": config.get_safe_config()
    }

@app.post("/quiz/generate")
async def generate_quiz(topic: str, difficulty: str = "medium"):
    """Generate quiz question"""
    try:
        question = await gemini_service.generate_quiz_question(topic, difficulty)
        
        if not question:
            raise HTTPException(status_code=503, detail="Quiz generation service unavailable")
        
        return question
        
    except Exception as e:
        logger.error(f"Error generating quiz: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=config.get('app.host', '0.0.0.0'),
        port=config.get('app.port', 8000),
        reload=config.get('app.hot_reload', False),
        workers=config.get('app.workers', 1) if not config.get('app.hot_reload') else 1
    )
