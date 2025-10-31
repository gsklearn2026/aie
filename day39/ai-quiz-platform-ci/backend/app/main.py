from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text
import google.generativeai as genai
import os
from . import models, database
from typing import List, Dict

# Configure Gemini AI
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = FastAPI(title="AI Quiz Platform", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
models.Base.metadata.create_all(bind=database.engine)

@app.get("/")
async def root():
    return {"message": "AI Quiz Platform API", "status": "running"}

@app.get("/health")
async def health_check():
    health_status = {
        "status": "healthy",
        "database": "disconnected",
        "ai_service": "disconnected"
    }
    
    # Check database connection
    try:
        db = database.SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        health_status["database"] = "connected"
    except Exception as e:
        health_status["database"] = f"error: {str(e)}"
    
    # Check Gemini AI connection (only if API key is provided)
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key and api_key != "your_gemini_api_key_here":
        try:
            model = genai.GenerativeModel('gemini-2.5-flash')
            response = model.generate_content("Test")
            health_status["ai_service"] = "connected"
        except Exception as e:
            health_status["ai_service"] = f"error: {str(e)}"
    else:
        health_status["ai_service"] = "not_configured"
        health_status["ai_service_note"] = "GEMINI_API_KEY not set or using placeholder value"
    
    # Return 200 if database is connected, even if AI service is not configured
    if health_status["database"] == "connected":
        return health_status
    else:
        raise HTTPException(status_code=503, detail=health_status)

@app.post("/quiz/generate")
async def generate_quiz(topic: str, difficulty: str = "medium", 
                       questions_count: int = 5, 
                       db: Session = Depends(database.get_db)):
    # Check if API key is configured
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        raise HTTPException(
            status_code=503, 
            detail="AI service not configured. Please set GEMINI_API_KEY environment variable."
        )
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        prompt = f"""Generate {questions_count} multiple choice quiz questions about {topic} 
        with {difficulty} difficulty. Format as JSON array with objects containing:
        - question: string
        - options: array of 4 strings
        - correct_answer: string (matching one of the options)
        - explanation: string
        """
        
        response = model.generate_content(prompt)
        
        # Store in database (simplified for CI demo)
        quiz_data = {
            "topic": topic,
            "difficulty": difficulty,
            "questions": response.text,
            "status": "generated"
        }
        
        return quiz_data
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(e)}")

@app.get("/quiz/list")
async def list_quizzes(db: Session = Depends(database.get_db)):
    return {"quizzes": [], "total": 0}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
