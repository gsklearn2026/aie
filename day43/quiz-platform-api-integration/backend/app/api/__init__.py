"""API routes"""
from fastapi import APIRouter
from .quiz_routes import router as quiz_router
from .integration_routes import router as integration_router

router = APIRouter()

router.include_router(quiz_router, prefix="/quiz", tags=["quiz"])
router.include_router(integration_router, prefix="/integration", tags=["integration"])
