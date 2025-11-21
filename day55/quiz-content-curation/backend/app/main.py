from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import curation, questions, analytics
from app.models.database import engine, Base

app = FastAPI(
    title="Quiz Content Curation API",
    description="Human-in-the-loop content curation system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(curation.router, prefix="/api/curation", tags=["curation"])
app.include_router(questions.router, prefix="/api/questions", tags=["questions"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "content-curation"}
