from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
from app.services.generation_service import generation_service
from app.services.metrics_tracker import metrics_tracker
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

class GenerationRequest(BaseModel):
    question_type: str
    subject: str
    difficulty: str = "medium"
    additional_context: Optional[str] = None

class BatchGenerationRequest(BaseModel):
    requests: List[GenerationRequest]

@router.post("/generate")
async def generate_question(request: GenerationRequest, background_tasks: BackgroundTasks):
    """Generate a single question using multi-model routing"""
    
    try:
        result = await generation_service.generate_question(
            question_type=request.question_type,
            subject=request.subject,
            difficulty=request.difficulty,
            additional_context=request.additional_context
        )
        
        # Record metrics in background
        metadata = result.get("metadata", {})
        background_tasks.add_task(
            metrics_tracker.record_generation,
            profile_name=metadata.get("profile_used", "unknown"),
            question_type=request.question_type,
            latency_ms=metadata.get("latency_ms", 0),
            cost=0.001,  # Estimated cost per request
            quality_score=result.get("quality_score", 0),
            success=True
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/generate/batch")
async def generate_batch(request: BatchGenerationRequest):
    """Generate multiple questions in batch"""
    
    results = []
    for gen_request in request.requests:
        try:
            result = await generation_service.generate_question(
                question_type=gen_request.question_type,
                subject=gen_request.subject,
                difficulty=gen_request.difficulty,
                additional_context=gen_request.additional_context
            )
            results.append({"status": "success", "data": result})
        except Exception as e:
            logger.error(f"Batch item failed: {e}")
            results.append({"status": "error", "error": str(e)})
    
    return {"results": results}

@router.get("/metrics/{profile_name}")
async def get_profile_metrics(profile_name: str, days: int = 7):
    """Get performance metrics for a model profile"""
    
    try:
        metrics = metrics_tracker.get_profile_metrics(profile_name, days)
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profiles")
async def list_profiles():
    """List all available model profiles"""
    
    from app.config.settings import settings
    profiles = {}
    for name, config in settings.MODEL_PROFILES.items():
        profiles[name] = {
            "model": config["model_name"],
            "cost_tier": config["cost_tier"],
            "temperature": config["temperature"],
            "max_tokens": config["max_tokens"]
        }
    return profiles
