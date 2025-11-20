from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID

from app.core.database import get_db
from app.schemas.content import MetricsResponse
from app.services.metrics_service import MetricsService

router = APIRouter()

@router.get("/{content_id}", response_model=MetricsResponse)
async def get_metrics(
    content_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = MetricsService(db)
    metrics = await service.get_metrics(content_id)
    return metrics
