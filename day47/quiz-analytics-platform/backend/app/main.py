from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import uvicorn
import os
from dotenv import load_dotenv

from app.routes import analytics, dashboard, auth
from app.database.connection import init_db

load_dotenv()

app = FastAPI(title="Quiz Analytics API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])

@app.on_event("startup")
async def startup_event():
    try:
        await init_db()
    except Exception as e:
        print(f"Warning: Startup initialization failed: {e}")
        print("Server will continue, but some features may not work.")

@app.get("/")
async def root():
    return {"message": "Quiz Analytics API is running!", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "quiz-analytics-api"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
