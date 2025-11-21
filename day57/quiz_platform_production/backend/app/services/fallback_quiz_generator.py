"""
Fallback quiz generator that creates quizzes without AI API
Used when AI service quota is exceeded or unavailable
"""
import random
import logging

logger = logging.getLogger(__name__)

# Template questions for common topics
QUIZ_TEMPLATES = {
    "python": [
        {
            "question": "What is the correct way to create a list in Python?",
            "options": ["list = []", "list = list()", "list = new list()", "list = array()"],
            "correct_answer": 0,
            "explanation": "In Python, you can create an empty list using square brackets [] or the list() constructor."
        },
        {
            "question": "Which keyword is used to define a function in Python?",
            "options": ["function", "def", "define", "func"],
            "correct_answer": 1,
            "explanation": "The 'def' keyword is used to define functions in Python."
        },
        {
            "question": "What does the len() function return?",
            "options": ["The length of a string", "The number of items in a collection", "The size of a file", "All of the above"],
            "correct_answer": 1,
            "explanation": "len() returns the number of items in a collection (list, string, tuple, etc.)."
        },
        {
            "question": "How do you add an item to a list in Python?",
            "options": ["list.add(item)", "list.append(item)", "list.insert(item)", "list.push(item)"],
            "correct_answer": 1,
            "explanation": "The append() method adds an item to the end of a list."
        },
        {
            "question": "What is the output of: print(2 ** 3)?",
            "options": ["6", "8", "9", "5"],
            "correct_answer": 1,
            "explanation": "The ** operator is exponentiation, so 2 ** 3 = 8."
        }
    ],
    "javascript": [
        {
            "question": "Which keyword is used to declare a variable in JavaScript?",
            "options": ["var", "let", "const", "All of the above"],
            "correct_answer": 3,
            "explanation": "JavaScript supports var, let, and const for variable declaration."
        },
        {
            "question": "What does === mean in JavaScript?",
            "options": ["Assignment", "Loose equality", "Strict equality", "Not equal"],
            "correct_answer": 2,
            "explanation": "=== is the strict equality operator that checks both value and type."
        },
        {
            "question": "How do you access an object property in JavaScript?",
            "options": ["object.property", "object['property']", "Both A and B", "object->property"],
            "correct_answer": 2,
            "explanation": "You can access properties using dot notation or bracket notation."
        }
    ],
    "general": [
        {
            "question": "What is the purpose of version control?",
            "options": ["To track changes in code", "To manage dependencies", "To compile code", "To debug code"],
            "correct_answer": 0,
            "explanation": "Version control tracks changes in code over time, allowing collaboration and history."
        },
        {
            "question": "What is an API?",
            "options": ["Application Programming Interface", "Automated Program Integration", "Advanced Programming Interface", "Application Process Integration"],
            "correct_answer": 0,
            "explanation": "API stands for Application Programming Interface - a set of protocols for building software."
        }
    ]
}

def generate_fallback_quiz(topic: str, num_questions: int = 5):
    """Generate quiz questions using fallback templates"""
    logger.info(f"Using fallback quiz generator for topic: {topic}")
    
    topic_lower = topic.lower()
    questions = []
    
    # Try to match topic to templates
    template_key = None
    if "python" in topic_lower:
        template_key = "python"
    elif "javascript" in topic_lower or "js" in topic_lower:
        template_key = "javascript"
    else:
        template_key = "general"
    
    # Get questions from template
    available_questions = QUIZ_TEMPLATES.get(template_key, QUIZ_TEMPLATES["general"])
    
    # If we need more questions than available, repeat and shuffle
    if num_questions > len(available_questions):
        # Repeat the list and shuffle
        extended = (available_questions * ((num_questions // len(available_questions)) + 1))[:num_questions]
        random.shuffle(extended)
        questions = extended
    else:
        # Select random questions
        questions = random.sample(available_questions, min(num_questions, len(available_questions)))
    
    # Customize questions with topic name
    for q in questions:
        if "{topic}" in q.get("question", ""):
            q["question"] = q["question"].replace("{topic}", topic)
        if "{topic}" in q.get("explanation", ""):
            q["explanation"] = q["explanation"].replace("{topic}", topic)
    
    return questions

