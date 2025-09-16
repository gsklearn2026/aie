"""Security Testing Platform Main Application"""
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from .api.security_api import router as security_router
from .models.database import create_tables

# Create FastAPI app
app = FastAPI(
    title="Quiz Platform Security Testing",
    description="Comprehensive security testing platform for AI-powered quiz system",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(security_router)

# Serve static files if they exist
if os.path.exists("../frontend/build"):
    app.mount("/", StaticFiles(directory="../frontend/build", html=True), name="static")

@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("🚀 Starting Security Testing Platform...")
    create_tables()
    print("✅ Database tables created")

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Security Testing Platform is running"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
