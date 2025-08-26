from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import uvicorn
import os
from dotenv import load_dotenv

from app.api.v1.endpoints import difficulty_router
from services.difficulty.classifier import DifficultyClassifier
from app.core.config import settings

load_dotenv()

app = FastAPI(
    title="Quiz Platform - Question Difficulty Classifier",
    description="AI-powered question difficulty classification service",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize difficulty classifier
classifier = DifficultyClassifier()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await classifier.initialize()
    print("🎯 Difficulty Classifier initialized successfully")

# Include routers
app.include_router(difficulty_router.router, prefix="/api/v1", tags=["difficulty"])

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head><title>Quiz Platform - Difficulty Classifier</title></head>
        <body style="font-family: Arial, sans-serif; margin: 40px;">
            <h1>🎯 Question Difficulty Classification Service</h1>
            <p>Service is running! Visit <a href="/docs">/docs</a> for API documentation.</p>
            <div style="margin-top: 20px;">
                <h3>Quick Test:</h3>
                <button onclick="testClassifier()">Test Difficulty Classification</button>
                <div id="result" style="margin-top: 10px; padding: 10px; background: #f5f5f5; border-radius: 5px;"></div>
            </div>
            <script>
                async function testClassifier() {
                    const testQuestion = "What is the capital of France?";
                    try {
                        const response = await fetch('/api/v1/classify', {
                            method: 'POST',
                            headers: {'Content-Type': 'application/json'},
                            body: JSON.stringify({
                                question_text: testQuestion,
                                subject: "geography",
                                question_type: "multiple_choice"
                            })
                        });
                        const result = await response.json();
                        document.getElementById('result').innerHTML = 
                            `<strong>Question:</strong> ${testQuestion}<br>
                             <strong>Difficulty:</strong> ${result.difficulty_level}<br>
                             <strong>Score:</strong> ${result.difficulty_score.toFixed(2)}<br>
                             <strong>Confidence:</strong> ${result.confidence.toFixed(2)}`;
                    } catch (error) {
                        document.getElementById('result').innerHTML = `Error: ${error.message}`;
                    }
                }
            </script>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "difficulty-classifier"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
