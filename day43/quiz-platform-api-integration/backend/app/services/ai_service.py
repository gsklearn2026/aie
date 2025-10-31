"""AI service with Gemini integration and retry logic"""
import asyncio
import httpx
import structlog
from typing import List, Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential
import google.generativeai as genai
from ..core.config import settings
from ..models.quiz import QuizQuestion

logger = structlog.get_logger()

class AIService:
    """AI service with error handling and retry logic"""
    
    def __init__(self):
        if settings.GEMINI_API_KEY:
            genai.configure(api_key=settings.GEMINI_API_KEY)
            # Use the newer model name
            self.model = genai.GenerativeModel('gemini-1.5-flash')
        else:
            logger.warning("Gemini API key not configured, using mock responses")
            self.model = None
    
    @retry(
        stop=stop_after_attempt(settings.MAX_RETRIES),
        wait=wait_exponential(multiplier=settings.RETRY_DELAY, min=1, max=10),
        reraise=True
    )
    async def generate_quiz_questions(
        self, 
        topic: str, 
        difficulty: str = "medium", 
        count: int = 5
    ) -> List[QuizQuestion]:
        """Generate quiz questions using AI"""
        logger.info("Generating quiz questions", topic=topic, difficulty=difficulty, count=count)
        
        if not self.model:
            # Return mock questions for demo
            return self._generate_mock_questions(topic, difficulty, count)
        
        try:
            prompt = f"""
            Generate {count} multiple choice quiz questions about {topic} with {difficulty} difficulty.
            
            For each question, provide:
            - Question text
            - 4 multiple choice options (A, B, C, D)
            - Correct answer letter
            
            Format as JSON array with this structure:
            [
                {{
                    "question": "Question text here?",
                    "options": ["Option A", "Option B", "Option C", "Option D"],
                    "correct_answer": "A",
                    "difficulty": "{difficulty}",
                    "category": "{topic}"
                }}
            ]
            
            Make questions educational and engaging for learners.
            """
            
            response = await asyncio.to_thread(
                self.model.generate_content, 
                prompt
            )
            
            # Parse response and create QuizQuestion objects
            import json
            questions_data = json.loads(response.text)
            
            questions = []
            for i, q_data in enumerate(questions_data):
                question = QuizQuestion(
                    id=f"q_{topic}_{i+1}",
                    question=q_data["question"],
                    options=q_data["options"],
                    correct_answer=q_data["correct_answer"],
                    difficulty=difficulty,
                    category=topic
                )
                questions.append(question)
            
            logger.info("Successfully generated quiz questions", count=len(questions))
            return questions
            
        except Exception as e:
            logger.error("Failed to generate quiz questions", error=str(e))
            # Fallback to mock questions
            return self._generate_mock_questions(topic, difficulty, count)
    
    def _generate_mock_questions(self, topic: str, difficulty: str, count: int) -> List[QuizQuestion]:
        """Generate real demo questions for different topics"""
        # Define question banks for different topics
        question_banks = {
            "javascript": {
                "easy": [
                    {
                        "question": "What is the correct way to declare a variable in JavaScript?",
                        "options": ["var name = 'John'", "variable name = 'John'", "v name = 'John'", "declare name = 'John'"],
                        "correct_answer": "A"
                    },
                    {
                        "question": "Which method is used to add an element to the end of an array?",
                        "options": ["push()", "pop()", "shift()", "unshift()"],
                        "correct_answer": "A"
                    },
                    {
                        "question": "What does '===' operator do in JavaScript?",
                        "options": ["Assigns a value", "Compares values and types", "Compares only values", "Creates a function"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "Which keyword is used to declare a constant in JavaScript?",
                        "options": ["var", "let", "const", "final"],
                        "correct_answer": "C"
                    },
                    {
                        "question": "What is the result of typeof null in JavaScript?",
                        "options": ["'null'", "'object'", "'undefined'", "'string'"],
                        "correct_answer": "B"
                    }
                ],
                "medium": [
                    {
                        "question": "What is a closure in JavaScript?",
                        "options": ["A function that returns another function", "A function that has access to variables in its outer scope", "A built-in JavaScript method", "A type of loop"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What does the 'this' keyword refer to in JavaScript?",
                        "options": ["The current function", "The global object", "The object that owns the function", "The parent element"],
                        "correct_answer": "C"
                    },
                    {
                        "question": "Which method creates a new array with all elements that pass a test?",
                        "options": ["map()", "filter()", "reduce()", "forEach()"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the difference between 'let' and 'var'?",
                        "options": ["No difference", "let has block scope, var has function scope", "var is newer than let", "let can't be reassigned"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What does JSON.stringify() do?",
                        "options": ["Parses JSON string", "Converts object to JSON string", "Validates JSON", "Creates JSON object"],
                        "correct_answer": "B"
                    }
                ],
                "hard": [
                    {
                        "question": "What is the event loop in JavaScript?",
                        "options": ["A loop that runs events", "A mechanism that handles asynchronous operations", "A type of array", "A debugging tool"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the difference between '==' and '===' operators?",
                        "options": ["No difference", "=== checks type and value, == only checks value", "== is newer", "=== is deprecated"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is a Promise in JavaScript?",
                        "options": ["A function that returns immediately", "An object representing eventual completion of an async operation", "A type of variable", "A built-in method"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What does 'hoisting' mean in JavaScript?",
                        "options": ["Moving variables to the top", "Variable and function declarations are moved to the top of their scope", "A type of loop", "A debugging technique"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the purpose of 'use strict' in JavaScript?",
                        "options": ["Makes code run faster", "Enables strict mode with error checking", "Creates a new scope", "Imports a library"],
                        "correct_answer": "B"
                    }
                ]
            },
            "python": {
                "easy": [
                    {
                        "question": "What is the correct way to print 'Hello World' in Python?",
                        "options": ["print('Hello World')", "echo 'Hello World'", "console.log('Hello World')", "printf('Hello World')"],
                        "correct_answer": "A"
                    },
                    {
                        "question": "Which keyword is used to define a function in Python?",
                        "options": ["function", "def", "func", "define"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the result of 5 // 2 in Python?",
                        "options": ["2.5", "2", "3", "2.0"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "Which data type is used to store a sequence of characters?",
                        "options": ["int", "str", "list", "bool"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What does len() function do in Python?",
                        "options": ["Returns the length of a string or list", "Creates a new list", "Sorts a list", "Reverses a string"],
                        "correct_answer": "A"
                    }
                ],
                "medium": [
                    {
                        "question": "What is a list comprehension in Python?",
                        "options": ["A way to create lists using a concise syntax", "A type of loop", "A built-in function", "A data structure"],
                        "correct_answer": "A"
                    },
                    {
                        "question": "What is the difference between a list and a tuple?",
                        "options": ["No difference", "Lists are mutable, tuples are immutable", "Tuples are faster", "Lists can't contain numbers"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What does the 'with' statement do in Python?",
                        "options": ["Creates a loop", "Manages resources and ensures proper cleanup", "Imports modules", "Defines classes"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is a decorator in Python?",
                        "options": ["A function that modifies another function", "A type of variable", "A built-in method", "A data structure"],
                        "correct_answer": "A"
                    },
                    {
                        "question": "What does 'self' refer to in Python classes?",
                        "options": ["The parent class", "The instance of the class", "A built-in keyword", "The global scope"],
                        "correct_answer": "B"
                    }
                ],
                "hard": [
                    {
                        "question": "What is the Global Interpreter Lock (GIL) in Python?",
                        "options": ["A security feature", "A mechanism that allows only one thread to execute Python bytecode at a time", "A type of loop", "A debugging tool"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the difference between 'is' and '==' in Python?",
                        "options": ["No difference", "'is' compares identity, '==' compares values", "'==' is newer", "'is' is deprecated"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is a generator in Python?",
                        "options": ["A function that returns an iterator", "A type of loop", "A built-in function", "A data structure"],
                        "correct_answer": "A"
                    },
                    {
                        "question": "What does the 'yield' keyword do in Python?",
                        "options": ["Returns a value and pauses function execution", "Creates a new variable", "Imports a module", "Defines a class"],
                        "correct_answer": "A"
                    },
                    {
                        "question": "What is duck typing in Python?",
                        "options": ["A type of bird", "If it walks like a duck and quacks like a duck, it's a duck", "A built-in type", "A debugging method"],
                        "correct_answer": "B"
                    }
                ]
            },
            "react": {
                "easy": [
                    {
                        "question": "What is React?",
                        "options": ["A database", "A JavaScript library for building user interfaces", "A programming language", "A server framework"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is JSX in React?",
                        "options": ["A JavaScript extension", "A syntax extension that allows writing HTML-like code in JavaScript", "A type of variable", "A built-in function"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is a component in React?",
                        "options": ["A function or class that returns JSX", "A variable", "A loop", "A database table"],
                        "correct_answer": "A"
                    },
                    {
                        "question": "What does 'props' stand for in React?",
                        "options": ["Properties", "Programming", "Protocols", "Procedures"],
                        "correct_answer": "A"
                    },
                    {
                        "question": "What is the virtual DOM in React?",
                        "options": ["A real DOM", "A JavaScript representation of the real DOM", "A database", "A server"],
                        "correct_answer": "B"
                    }
                ],
                "medium": [
                    {
                        "question": "What is state in React?",
                        "options": ["A variable", "Data that determines how a component renders", "A function", "A class"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the purpose of useEffect hook?",
                        "options": ["To create components", "To perform side effects in functional components", "To style components", "To handle events"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the difference between props and state?",
                        "options": ["No difference", "Props are passed down, state is managed internally", "State is passed down, props are managed internally", "Both are the same"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is a controlled component in React?",
                        "options": ["A component with no state", "A component whose value is controlled by React state", "A component with no props", "A class component"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the key prop used for in React lists?",
                        "options": ["Styling", "To help React identify which items have changed", "Event handling", "Data storage"],
                        "correct_answer": "B"
                    }
                ],
                "hard": [
                    {
                        "question": "What is the difference between useCallback and useMemo?",
                        "options": ["No difference", "useCallback returns a memoized callback, useMemo returns a memoized value", "useMemo is newer", "useCallback is deprecated"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the purpose of React.memo?",
                        "options": ["To create components", "To prevent unnecessary re-renders of functional components", "To handle state", "To manage props"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the Context API in React?",
                        "options": ["A database", "A way to pass data through the component tree without prop drilling", "A type of component", "A built-in function"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the difference between class and functional components?",
                        "options": ["No difference", "Class components use this, functional components use hooks", "Functional components are faster", "Class components are deprecated"],
                        "correct_answer": "B"
                    },
                    {
                        "question": "What is the purpose of useRef hook?",
                        "options": ["To create state", "To access DOM elements or store mutable values", "To handle events", "To create components"],
                        "correct_answer": "B"
                    }
                ]
            }
        }
        
        # Get questions for the topic and difficulty, or use a default set
        topic_questions = question_banks.get(topic.lower(), question_banks["javascript"])
        difficulty_questions = topic_questions.get(difficulty.lower(), topic_questions["easy"])
        
        # Select questions up to the requested count
        selected_questions = difficulty_questions[:count]
        
        # If we don't have enough questions, repeat some
        while len(selected_questions) < count:
            selected_questions.extend(difficulty_questions[:min(len(difficulty_questions), count - len(selected_questions))])
        
        # Convert to QuizQuestion objects
        mock_questions = []
        for i, q_data in enumerate(selected_questions[:count]):
            question = QuizQuestion(
                id=f"demo_{topic}_{difficulty}_{i+1}",
                question=q_data["question"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                difficulty=difficulty,
                category=topic
            )
            mock_questions.append(question)
        
        return mock_questions
    
    async def validate_answer(self, question: QuizQuestion, user_answer: str) -> Dict[str, Any]:
        """Validate user answer and provide feedback"""
        is_correct = question.correct_answer == user_answer
        
        feedback = {
            "correct": is_correct,
            "correct_answer": question.correct_answer,
            "explanation": f"The correct answer is {question.correct_answer}"
        }
        
        if not is_correct:
            feedback["user_answer"] = user_answer
        
        return feedback
