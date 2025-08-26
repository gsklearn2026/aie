from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
import asyncio
import json
from typing import List, Dict, Any

from .database import get_db, init_db
from .models import QuizAttempt, AnalyticsEvent, PerformanceMetric
from .services.analytics_processor import AnalyticsProcessor
from .services.insight_generator import InsightGenerator
from .api.analytics_routes import router as analytics_router
from .utils.websocket_manager import WebSocketManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()
    # Start background analytics processor
    analytics_task = asyncio.create_task(start_analytics_processor())
    yield
    # Shutdown
    analytics_task.cancel()

app = FastAPI(title="Performance Analytics Engine", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket manager for real-time updates
websocket_manager = WebSocketManager()

app.include_router(analytics_router, prefix="/api/v1/analytics")

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)

async def start_analytics_processor():
    processor = AnalyticsProcessor()
    while True:
        await processor.process_events()
        await asyncio.sleep(30)  # Process every 30 seconds

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "performance-analytics-engine"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
