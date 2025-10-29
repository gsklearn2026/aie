from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import json
import uuid
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import asyncio
import os
from pydantic import BaseModel

# Configure Gemini AI
genai.configure(api_key="AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8")
model = genai.GenerativeModel('gemini-pro')

app = FastAPI(title="Quiz Taking Interface API", version="1.0.0")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory storage (use Redis in production)
quiz_sessions: Dict[str, dict] = {}
active_connections: Dict[str, WebSocket] = {}

# Data Models
class QuizQuestion(BaseModel):
    id: str
    question: str
    options: List[str]
    correct_answer: str
    explanation: str
    difficulty: str = "medium"

class QuizSession(BaseModel):
    session_id: str
    quiz_id: str
    user_id: str
    questions: List[QuizQuestion]
    current_question: int = 0
    answers: Dict[str, str] = {}
    start_time: datetime
    end_time: Optional[datetime] = None
    time_limit: int = 1800  # 30 minutes
    status: str = "active"

class AnswerSubmission(BaseModel):
    question_id: str
    answer: str
    time_taken: float

class QuizStart(BaseModel):
    quiz_id: str
    user_id: str
    quiz_title: str = "AI Engineering Quiz"

# Helper Functions
async def generate_ai_questions(topic: str, count: int = 5) -> List[QuizQuestion]:
    """Generate quiz questions using Gemini AI"""
    prompt = f"""Generate {count} multiple choice questions about {topic} for AI Engineering students.
    
    Format each question as JSON with this structure:
    {{
        "question": "The question text",
        "options": ["Option A", "Option B", "Option C", "Option D"],
        "correct_answer": "Option A",
        "explanation": "Brief explanation of why this is correct",
        "difficulty": "easy|medium|hard"
    }}
    
    Make questions practical and relevant to real-world AI engineering applications.
    Return only a JSON array of questions, no other text."""
    
    try:
        response = model.generate_content(prompt)
        questions_data = json.loads(response.text)
        
        questions = []
        for i, q_data in enumerate(questions_data):
            questions.append(QuizQuestion(
                id=str(uuid.uuid4()),
                question=q_data["question"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                explanation=q_data["explanation"],
                difficulty=q_data.get("difficulty", "medium")
            ))
        return questions
    except Exception as e:
        # Fallback questions if AI generation fails
        fallback_questions = [
            QuizQuestion(
                id=str(uuid.uuid4()),
                question="What is the primary purpose of state management in React applications?",
                options=[
                    "To manage component lifecycle",
                    "To handle component re-renders efficiently",
                    "To share data between components",
                    "To optimize performance"
                ],
                correct_answer="To share data between components",
                explanation="State management primarily helps share and synchronize data across components",
                difficulty="medium"
            ),
            QuizQuestion(
                id=str(uuid.uuid4()),
                question="Which HTTP status code indicates successful quiz submission?",
                options=["200", "201", "204", "400"],
                correct_answer="201",
                explanation="201 Created indicates successful resource creation",
                difficulty="easy"
            )
        ]
        return fallback_questions[:count]

def calculate_score(session: dict) -> dict:
    """Calculate quiz score and statistics"""
    total_questions = len(session["questions"])
    correct_answers = 0
    
    for question in session["questions"]:
        user_answer = session["answers"].get(question["id"])
        if user_answer == question["correct_answer"]:
            correct_answers += 1
    
    score_percentage = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
    
    return {
        "total_questions": total_questions,
        "correct_answers": correct_answers,
        "score_percentage": round(score_percentage, 2),
        "time_taken": (datetime.now() - datetime.fromisoformat(session["start_time"])).total_seconds()
    }

# API Endpoints
@app.post("/api/quiz/start")
async def start_quiz(quiz_data: QuizStart):
    """Start a new quiz session"""
    session_id = str(uuid.uuid4())
    
    # Generate AI questions
    questions = await generate_ai_questions(quiz_data.quiz_title)
    
    session = {
        "session_id": session_id,
        "quiz_id": quiz_data.quiz_id,
        "user_id": quiz_data.user_id,
        "questions": [q.dict() for q in questions],
        "current_question": 0,
        "answers": {},
        "start_time": datetime.now().isoformat(),
        "end_time": None,
        "time_limit": 1800,
        "status": "active"
    }
    
    quiz_sessions[session_id] = session
    
    return {
        "session_id": session_id,
        "total_questions": len(questions),
        "time_limit": 1800,
        "first_question": questions[0].dict() if questions else None
    }

@app.get("/api/quiz/session/{session_id}")
async def get_session(session_id: str):
    """Get current quiz session state"""
    if session_id not in quiz_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = quiz_sessions[session_id]
    current_idx = session["current_question"]
    
    return {
        "session_id": session_id,
        "current_question_index": current_idx,
        "total_questions": len(session["questions"]),
        "current_question": session["questions"][current_idx] if current_idx < len(session["questions"]) else None,
        "progress": (current_idx / len(session["questions"])) * 100,
        "time_remaining": max(0, session["time_limit"] - (datetime.now() - datetime.fromisoformat(session["start_time"])).total_seconds()),
        "status": session["status"]
    }

@app.post("/api/quiz/session/{session_id}/answer")
async def submit_answer(session_id: str, answer: AnswerSubmission):
    """Submit answer for current question"""
    if session_id not in quiz_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = quiz_sessions[session_id]
    
    if session["status"] != "active":
        raise HTTPException(status_code=400, detail="Session is not active")
    
    # Store answer
    session["answers"][answer.question_id] = answer.answer
    
    # Move to next question
    session["current_question"] += 1
    
    # Check if quiz is complete
    if session["current_question"] >= len(session["questions"]):
        session["status"] = "completed"
        session["end_time"] = datetime.now().isoformat()
    
    # Send update via WebSocket if connected
    if session_id in active_connections:
        try:
            await active_connections[session_id].send_text(json.dumps({
                "type": "answer_submitted",
                "current_question": session["current_question"],
                "is_complete": session["status"] == "completed"
            }))
        except:
            pass
    
    return {
        "success": True,
        "next_question_index": session["current_question"],
        "is_complete": session["status"] == "completed"
    }

@app.get("/api/quiz/session/{session_id}/results")
async def get_results(session_id: str):
    """Get quiz results"""
    if session_id not in quiz_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    session = quiz_sessions[session_id]
    
    if session["status"] != "completed":
        raise HTTPException(status_code=400, detail="Quiz not completed yet")
    
    results = calculate_score(session)
    
    # Generate AI feedback
    try:
        feedback_prompt = f"""Provide encouraging feedback for a quiz with {results['score_percentage']}% score.
        Student answered {results['correct_answers']} out of {results['total_questions']} questions correctly.
        Give 2-3 sentences of constructive feedback."""
        
        feedback_response = model.generate_content(feedback_prompt)
        ai_feedback = feedback_response.text.strip()
    except:
        ai_feedback = "Great effort! Keep practicing to improve your AI engineering skills."
    
    return {
        "session_id": session_id,
        "score": results,
        "feedback": ai_feedback,
        "detailed_answers": [
            {
                "question": q["question"],
                "user_answer": session["answers"].get(q["id"], "Not answered"),
                "correct_answer": q["correct_answer"],
                "explanation": q["explanation"],
                "is_correct": session["answers"].get(q["id"]) == q["correct_answer"]
            }
            for q in session["questions"]
        ]
    }

@app.websocket("/ws/quiz/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket for real-time quiz updates"""
    await websocket.accept()
    active_connections[session_id] = websocket
    
    try:
        while True:
            data = await websocket.receive_text()
            # Handle incoming WebSocket messages if needed
            await websocket.send_text(json.dumps({"type": "heartbeat", "timestamp": datetime.now().isoformat()}))
    except WebSocketDisconnect:
        if session_id in active_connections:
            del active_connections[session_id]

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
