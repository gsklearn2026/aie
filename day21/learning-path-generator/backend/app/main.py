from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from .api import learning_paths, topics, users
from .database.connection import init_db
from .config.settings import get_settings
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Learning Path Generator API",
    description="AI-powered personalized learning path generation",
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

# Include routers
app.include_router(learning_paths.router, prefix="/api/learning-paths", tags=["Learning Paths"])
app.include_router(topics.router, prefix="/api/topics", tags=["Topics"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])

@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    await init_db()
    logger.info("Learning Path Generator API started successfully")

@app.get("/")
async def root():
    return {"message": "Learning Path Generator API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "learning-path-generator"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
