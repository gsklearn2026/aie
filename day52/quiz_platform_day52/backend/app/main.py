from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
from app.middleware.memory_profiler import MemoryProfilerMiddleware
from app.routes import quiz_routes, memory_routes
from app.services.memory_monitor import MemoryMonitor
from app.services.cleanup_scheduler import CleanupScheduler

memory_monitor = None
cleanup_scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global memory_monitor, cleanup_scheduler
    
    # Startup
    memory_monitor = MemoryMonitor()
    cleanup_scheduler = CleanupScheduler()
    
    await memory_monitor.start()
    await cleanup_scheduler.start()
    
    yield
    
    # Shutdown
    await memory_monitor.stop()
    await cleanup_scheduler.stop()

app = FastAPI(title="Quiz Platform - Memory Optimized", lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Memory Profiler Middleware
app.add_middleware(MemoryProfilerMiddleware)

# Routes
app.include_router(quiz_routes.router, prefix="/api/quiz", tags=["quiz"])
app.include_router(memory_routes.router, prefix="/api/memory", tags=["memory"])

@app.get("/")
async def root():
    return {"message": "Quiz Platform API - Memory Optimized", "status": "running"}

@app.websocket("/ws/memory")
async def memory_websocket(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            metrics = memory_monitor.get_current_metrics()
            await websocket.send_json(metrics)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass
