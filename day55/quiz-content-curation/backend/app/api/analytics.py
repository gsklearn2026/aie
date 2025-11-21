from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.schemas import AnalyticsResponse

router = APIRouter()

@router.get("/curation", response_model=AnalyticsResponse)
async def get_curation_analytics(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
):
    """Get curation performance analytics"""
    service = AnalyticsService(db)
    return await service.get_curation_analytics(days)
