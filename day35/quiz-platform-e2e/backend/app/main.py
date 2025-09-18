"""Main FastAPI application for Quiz Platform"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from .api import auth, quiz, health
from .middleware.logging import LoggingMiddleware
import os

app = FastAPI(
    title="Quiz Platform API",
    description="AI-powered quiz platform with E2E testing",
    version="1.0.0"
)

# Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend-e2e:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(LoggingMiddleware)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(quiz.router, prefix="/api/quiz", tags=["quiz"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "Quiz Platform API is running", "version": "1.0.0"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
