from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn

from .middleware.versioning import APIVersioningMiddleware
from .api.v1.routes import quiz as quiz_v1
from .api.v2.routes import quiz as quiz_v2
from .services.version_analytics import analytics_service

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 API Versioning System Starting...")
    yield
    # Shutdown
    print("🛑 API Versioning System Shutting down...")

app = FastAPI(
    title="Quiz Platform API",
    description="Multi-version API with backward compatibility",
    version="2.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add version detection middleware
versioning_middleware = APIVersioningMiddleware(app)
app.middleware("http")(versioning_middleware)

# Include version-specific routes
app.include_router(quiz_v1.router, prefix="/api/v1")
app.include_router(quiz_v2.router, prefix="/api/v2")

@app.get("/")
async def root():
    return {
        "message": "Quiz Platform API with Versioning",
        "versions": {
            "v1": {
                "status": "deprecated",
                "endpoints": ["/api/v1/quiz/create", "/api/v1/quiz/list", "/api/v1/quiz/{id}"]
            },
            "v2": {
                "status": "current", 
                "endpoints": ["/api/v2/quiz/create", "/api/v2/quiz/list", "/api/v2/quiz/{id}", "/api/v2/quiz/{id}/analytics"]
            }
        }
    }

@app.get("/api/version/analytics")
async def get_version_analytics(request: Request):
    """Get API version usage analytics"""
    return {
        "version_distribution": analytics_service.get_version_distribution(),
        "daily_stats": analytics_service.get_daily_stats(),
        "endpoint_popularity": analytics_service.get_endpoint_popularity(),
        "client_breakdown": analytics_service.get_client_breakdown(),
        "deprecation_impact": analytics_service.get_deprecation_impact()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": "2025-01-15T10:00:00Z"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
