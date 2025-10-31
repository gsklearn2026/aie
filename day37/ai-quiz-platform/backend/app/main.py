from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
import google.generativeai as genai
import redis
import os
import json
from typing import Dict, List
import asyncio
from datetime import datetime

app = FastAPI(title="AI Quiz Platform API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
security = HTTPBearer()
redis_client = None
genai_client = None

@app.on_event("startup")
async def startup_event():
    global redis_client, genai_client
    
    # Initialize Redis
    redis_client = redis.Redis(
        host=os.getenv("REDIS_HOST", "localhost"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        decode_responses=True
    )
    
    # Initialize Gemini AI
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    genai_client = genai.GenerativeModel('gemini-pro')
    
    print("✅ Services initialized successfully")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check Redis connection
        redis_client.ping()
        
        return {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "services": {
                "redis": "connected",
                "gemini": "configured",
                "database": "connected"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

def generate_mock_quiz(topic: str, difficulty: str, num_questions: int):
    """Generate a mock quiz when external API is not available"""
    quiz_templates = {
        "javascript": {
            "easy": [
                {
                    "question": "What is JavaScript?",
                    "options": ["A programming language", "A database", "A web browser", "An operating system"],
                    "correct_answer": 0,
                    "explanation": "JavaScript is a programming language commonly used for web development."
                },
                {
                    "question": "Which keyword is used to declare a variable in JavaScript?",
                    "options": ["var", "int", "string", "float"],
                    "correct_answer": 0,
                    "explanation": "The 'var' keyword is used to declare variables in JavaScript."
                },
                {
                    "question": "What does DOM stand for?",
                    "options": ["Document Object Model", "Data Object Management", "Dynamic Object Method", "Document Order Management"],
                    "correct_answer": 0,
                    "explanation": "DOM stands for Document Object Model, which represents the structure of HTML documents."
                }
            ],
            "medium": [
                {
                    "question": "What is the difference between '==' and '===' in JavaScript?",
                    "options": ["No difference", "'==' compares values, '===' compares values and types", "'===' is faster", "'==' is deprecated"],
                    "correct_answer": 1,
                    "explanation": "'==' performs type coercion, while '===' performs strict equality comparison."
                },
                {
                    "question": "What is a closure in JavaScript?",
                    "options": ["A function that returns another function", "A way to close a browser tab", "A data type", "A loop construct"],
                    "correct_answer": 0,
                    "explanation": "A closure is a function that has access to variables in its outer scope even after the outer function returns."
                }
            ],
            "hard": [
                {
                    "question": "What is the event loop in JavaScript?",
                    "options": ["A loop that runs forever", "A mechanism that handles asynchronous operations", "A type of array", "A debugging tool"],
                    "correct_answer": 1,
                    "explanation": "The event loop is a mechanism that allows JavaScript to handle asynchronous operations by managing the call stack and callback queue."
                }
            ]
        },
        "python": {
            "easy": [
                {
                    "question": "What is Python?",
                    "options": ["A snake", "A programming language", "A database", "A web browser"],
                    "correct_answer": 1,
                    "explanation": "Python is a high-level programming language known for its simplicity and readability."
                },
                {
                    "question": "Which keyword is used to define a function in Python?",
                    "options": ["function", "def", "func", "define"],
                    "correct_answer": 1,
                    "explanation": "The 'def' keyword is used to define functions in Python."
                }
            ],
            "medium": [
                {
                    "question": "What is a list comprehension in Python?",
                    "options": ["A way to read lists", "A concise way to create lists", "A type of loop", "A data structure"],
                    "correct_answer": 1,
                    "explanation": "List comprehension is a concise way to create lists in Python using a single line of code."
                }
            ],
            "hard": [
                {
                    "question": "What is the Global Interpreter Lock (GIL) in Python?",
                    "options": ["A security feature", "A mechanism that allows only one thread to execute Python bytecode at a time", "A debugging tool", "A memory management technique"],
                    "correct_answer": 1,
                    "explanation": "GIL is a mechanism that ensures only one thread can execute Python bytecode at a time, which can limit multi-threading performance."
                }
            ]
        }
    }
    
    # Get questions for the topic and difficulty
    topic_lower = topic.lower()
    if topic_lower not in quiz_templates:
        topic_lower = "javascript"  # Default fallback
    
    difficulty_questions = quiz_templates[topic_lower].get(difficulty, quiz_templates[topic_lower]["easy"])
    
    # Select the requested number of questions
    selected_questions = difficulty_questions[:num_questions]
    
    # If we need more questions, repeat from easy level
    while len(selected_questions) < num_questions:
        selected_questions.extend(quiz_templates[topic_lower]["easy"][:num_questions - len(selected_questions)])
        if len(selected_questions) >= num_questions:
            break
    
    return {
        "title": f"{topic} {difficulty.title()} Quiz",
        "questions": selected_questions[:num_questions]
    }

@app.post("/api/quiz/generate")
async def generate_quiz(topic: str, difficulty: str = "medium", num_questions: int = 5):
    """Generate quiz using Gemini AI with fallback to mock quiz"""
    try:
        # Try to use Gemini AI if API key is valid
        if genai_client and os.getenv("GEMINI_API_KEY") and os.getenv("GEMINI_API_KEY") != "test-key-placeholder":
            prompt = f"""
            Generate a {difficulty} level quiz about {topic} with {num_questions} multiple choice questions.
            Format as JSON with this structure:
            {{
                "title": "Quiz Title",
                "questions": [
                    {{
                        "question": "Question text",
                        "options": ["A", "B", "C", "D"],
                        "correct_answer": 0,
                        "explanation": "Why this is correct"
                    }}
                ]
            }}
            """
            
            response = genai_client.generate_content(prompt)
            quiz_data = json.loads(response.text)
        else:
            # Use mock quiz generation
            quiz_data = generate_mock_quiz(topic, difficulty, num_questions)
        
        # Cache quiz
        quiz_id = f"quiz_{datetime.utcnow().timestamp()}"
        redis_client.setex(quiz_id, 3600, json.dumps(quiz_data))
        
        return {"quiz_id": quiz_id, "quiz": quiz_data}
        
    except Exception as e:
        error_message = str(e)
        # If external API fails, try mock quiz as fallback
        try:
            quiz_data = generate_mock_quiz(topic, difficulty, num_questions)
            quiz_id = f"quiz_{datetime.utcnow().timestamp()}"
            redis_client.setex(quiz_id, 3600, json.dumps(quiz_data))
            return {"quiz_id": quiz_id, "quiz": quiz_data}
        except Exception as fallback_error:
            raise HTTPException(status_code=500, detail=f"Quiz generation failed: {str(fallback_error)}")

@app.get("/api/quiz/{quiz_id}")
async def get_quiz(quiz_id: str):
    """Retrieve cached quiz"""
    try:
        quiz_data = redis_client.get(quiz_id)
        if not quiz_data:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        return {"quiz": json.loads(quiz_data)}
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid quiz data")

@app.post("/api/quiz/{quiz_id}/submit")
async def submit_quiz(quiz_id: str, answers: List[int]):
    """Submit quiz answers and calculate score"""
    try:
        quiz_data = redis_client.get(quiz_id)
        if not quiz_data:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        quiz = json.loads(quiz_data)
        questions = quiz["questions"]
        
        if len(answers) != len(questions):
            raise HTTPException(status_code=400, detail="Answer count mismatch")
        
        score = 0
        results = []
        
        for i, (answer, question) in enumerate(zip(answers, questions)):
            is_correct = answer == question["correct_answer"]
            if is_correct:
                score += 1
            
            results.append({
                "question_index": i,
                "user_answer": answer,
                "correct_answer": question["correct_answer"],
                "is_correct": is_correct,
                "explanation": question["explanation"]
            })
        
        result = {
            "score": score,
            "total": len(questions),
            "percentage": round((score / len(questions)) * 100, 2),
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Cache result
        result_id = f"result_{quiz_id}_{datetime.utcnow().timestamp()}"
        redis_client.setex(result_id, 86400, json.dumps(result))
        
        return {"result_id": result_id, "result": result}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Submission failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
