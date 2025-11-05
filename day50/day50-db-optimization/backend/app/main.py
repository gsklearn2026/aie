from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database.base import engine, Base
from .routes import quizzes, performance
from .middleware.performance_monitor import PerformanceMonitorMiddleware
import uvicorn

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Quiz Platform - Optimized")

# Shared state for performance monitoring
performance_stats = {"request_stats": []}

# Add CORS middleware first (before other middleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add performance monitoring middleware
app.add_middleware(PerformanceMonitorMiddleware, stats=performance_stats)

# Include routers
app.include_router(quizzes.router)
app.include_router(performance.router)

@app.get("/")
def root():
    return {"message": "Quiz Platform API - Optimized", "status": "running"}

@app.get("/api/stats")
def get_api_stats():
    """Get API performance statistics"""
    stats = performance_stats["request_stats"]
    if not stats:
        return {
            'total_requests': 0,
            'avg_response_time': 0.0,
            'max_response_time': 0.0,
            'min_response_time': 0.0,
            'slow_requests': 0
        }
    
    durations = [r['duration'] for r in stats]
    return {
        'total_requests': len(stats),
        'avg_response_time': sum(durations) / len(durations),
        'max_response_time': max(durations),
        'min_response_time': min(durations),
        'slow_requests': len([d for d in durations if d > 0.5])
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
