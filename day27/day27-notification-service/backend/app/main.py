from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import redis
import json
import asyncio
from typing import Dict, List
import logging
from .events.event_processor import EventProcessor
from .api import notifications, preferences, events
from .services.websocket_manager import WebSocketManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Notification Service", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
websocket_manager = WebSocketManager()
event_processor = EventProcessor(redis_client, websocket_manager)

# Include routers
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])
app.include_router(preferences.router, prefix="/api/preferences", tags=["preferences"])
app.include_router(events.router, prefix="/api/events", tags=["events"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting notification service...")
    # Start event processor
    asyncio.create_task(event_processor.start_processing())

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket_manager.connect(websocket, user_id)
    try:
        while True:
            data = await websocket.receive_text()
            # Echo back for testing
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, user_id)

@app.get("/")
async def root():
    return {"message": "Notification Service API", "status": "running"}

@app.get("/health")
async def health_check():
    try:
        redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
