from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from app.routers import generation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = FastAPI(title="Multi-Model Quiz Generation API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generation.router, prefix="/api/generation", tags=["generation"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "multi-model-quiz-generation"}

@app.get("/")
async def root():
    return {
        "message": "Multi-Model Quiz Generation API",
        "version": "1.0.0",
        "endpoints": {
            "generate": "/api/generation/generate",
            "batch": "/api/generation/generate/batch",
            "metrics": "/api/generation/metrics/{profile_name}",
            "profiles": "/api/generation/profiles"
        }
    }
