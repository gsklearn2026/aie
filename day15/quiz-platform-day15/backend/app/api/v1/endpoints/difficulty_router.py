from fastapi import APIRouter, HTTPException, Depends
from typing import List
import time

from models.schemas.difficulty import (
    QuestionRequest, DifficultyResponse, BatchRequest, BatchResponse
)
from services.difficulty.classifier import DifficultyClassifier
from services.gemini.gemini_service import GeminiService

router = APIRouter()
classifier = DifficultyClassifier()
gemini_service = GeminiService()

@router.post("/classify", response_model=DifficultyResponse)
async def classify_question(request: QuestionRequest):
    """Classify a single question's difficulty level"""
    try:
        if not classifier.feature_extractor:
            raise HTTPException(status_code=503, detail="Classifier not initialized")
        
        result = await classifier.classify_question(request)
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Classification failed: {str(e)}")

@router.post("/classify-batch", response_model=BatchResponse)
async def classify_questions_batch(request: BatchRequest):
    """Classify multiple questions in batch"""
    try:
        start_time = time.time()
        
        if len(request.questions) > 100:
            raise HTTPException(status_code=400, detail="Batch size too large (max 100)")
        
        results = await classifier.classify_batch(request.questions)
        
        total_time = (time.time() - start_time) * 1000
        avg_time = total_time / len(request.questions)
        
        return BatchResponse(
            results=results,
            total_processed=len(results),
            average_processing_time_ms=avg_time
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Batch classification failed: {str(e)}")

@router.get("/features/{question_id}")
async def get_question_features(question_text: str, question_type: str, subject: str = None):
    """Get detailed feature analysis for a question"""
    try:
        features = classifier.feature_extractor.extract_all_features(
            question_text, question_type, subject
        )
        return {"features": features, "question_text": question_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Feature extraction failed: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "classifier_ready": bool(classifier.feature_extractor),
        "cache_size": len(classifier.cache)
    }

@router.post("/classify-gemini")
async def classify_question_gemini(request: QuestionRequest):
    """Classify question difficulty using Google Gemini AI"""
    try:
        result = await gemini_service.classify_question_difficulty(
            request.question_text,
            request.subject,
            request.question_type
        )
        return {
            "difficulty": result["difficulty"],
            "confidence": result["confidence"],
            "reasoning": result["reasoning"],
            "features": result.get("features", {}),
            "model": result["model"],
            "api_provider": result["api_provider"]
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini classification failed: {str(e)}")

@router.post("/analyze-gemini")
async def analyze_question_gemini(request: QuestionRequest):
    """Get comprehensive question analysis using Google Gemini AI"""
    try:
        result = await gemini_service.get_question_analysis(
            request.question_text,
            request.subject,
            request.question_type
        )
        return result
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini analysis failed: {str(e)}")
