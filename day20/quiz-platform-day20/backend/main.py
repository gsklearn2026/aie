from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.relationship_api import router as relationship_router
from .database import create_tables
from .config.settings import settings

app = FastAPI(title=settings.PROJECT_NAME)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(relationship_router, prefix=settings.API_V1_STR)

@app.on_event("startup")
async def startup_event():
    create_tables()

@app.get("/")
async def root():
    return {"message": "Topic Relationship Mapping Service", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "topic-relationships"}
