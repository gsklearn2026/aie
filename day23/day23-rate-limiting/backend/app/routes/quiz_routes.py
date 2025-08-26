from flask import Blueprint, request, jsonify, current_app
from middleware.rate_limiter import rate_limit
import json
import structlog

logger = structlog.get_logger()

quiz_bp = Blueprint('quiz', __name__)

@quiz_bp.route('/generate', methods=['POST'])
@rate_limit('ai_generate')
def generate_quiz():
    """Generate quiz using Gemini AI with rate limiting"""
    try:
        data = request.get_json()
        topic = data.get('topic', 'General Knowledge')
        difficulty = data.get('difficulty', 'medium')
        num_questions = min(int(data.get('num_questions', 5)), 10)  # Max 10 questions
        
        # If running tests or no API key, return a stub quiz to avoid external dependency
        if current_app.config.get('TESTING') or not current_app.config.get('GEMINI_API_KEY') or current_app.config.get('GEMINI_API_KEY') == '':
            quiz_data = {
                'quiz_id': 'test_quiz',
                'title': f'{topic} Quiz',
                'difficulty': difficulty,
                'questions': [
                    {
                        'id': i + 1,
                        'question': f'Sample question {i + 1} about {topic}?',
                        'options': ['A', 'B', 'C', 'D'],
                        'correct_answer': 0,
                        'explanation': 'Sample explanation'
                    } for i in range(num_questions)
                ]
            }
        else:
            try:
                # Import Gemini only when needed
                import google.generativeai as genai
                
                # Configure Gemini
                genai.configure(api_key=current_app.config['GEMINI_API_KEY'])
                model = genai.GenerativeModel('gemini-pro')
                
                # Generate quiz
                prompt = f"""
                Create a {difficulty} difficulty quiz about {topic} with {num_questions} multiple choice questions.
                Return ONLY a valid JSON object with this structure:
                {{
                    "quiz_id": "unique_id",
                    "title": "{topic} Quiz",
                    "difficulty": "{difficulty}",
                    "questions": [
                        {{
                            "id": 1,
                            "question": "Question text",
                            "options": ["A", "B", "C", "D"],
                            "correct_answer": 0,
                            "explanation": "Why this is correct"
                        }}
                    ]
                }}
                """
                
                response = model.generate_content(prompt)
                quiz_data = json.loads(response.text)
            except Exception as ai_error:
                logger.warning("AI quiz generation failed, falling back to stub quiz", error=str(ai_error))
                # Fallback to stub quiz if AI generation fails
                quiz_data = {
                    'quiz_id': 'fallback_quiz',
                    'title': f'{topic} Quiz (Fallback)',
                    'difficulty': difficulty,
                    'questions': [
                        {
                            'id': i + 1,
                            'question': f'Fallback question {i + 1} about {topic}?',
                            'options': ['A', 'B', 'C', 'D'],
                            'correct_answer': 0,
                            'explanation': 'Fallback explanation'
                        } for i in range(num_questions)
                    ]
                }
        
        # Cache quiz in Redis
        quiz_key = f"quiz:{quiz_data['quiz_id']}"
        current_app.redis.setex(quiz_key, 3600, json.dumps(quiz_data))  # 1 hour TTL
        
        logger.info("Quiz generated successfully", quiz_id=quiz_data['quiz_id'])
        
        return jsonify({
            'success': True,
            'quiz': quiz_data
        })
        
    except Exception as e:
        logger.error("Quiz generation failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to generate quiz'
        }), 500

@quiz_bp.route('/submit', methods=['POST'])
@rate_limit('quiz_submit')
def submit_quiz():
    """Submit quiz answers with rate limiting"""
    try:
        data = request.get_json()
        quiz_id = data.get('quiz_id')
        answers = data.get('answers', [])
        
        # Get quiz from cache
        quiz_key = f"quiz:{quiz_id}"
        quiz_data = current_app.redis.get(quiz_key)
        
        if not quiz_data:
            return jsonify({
                'success': False,
                'error': 'Quiz not found or expired'
            }), 404
            
        quiz = json.loads(quiz_data)
        
        # Calculate score
        correct_answers = 0
        total_questions = len(quiz['questions'])
        
        for i, answer in enumerate(answers):
            if i < total_questions and answer == quiz['questions'][i]['correct_answer']:
                correct_answers += 1
        
        score = (correct_answers / total_questions) * 100 if total_questions > 0 else 0
        
        result = {
            'quiz_id': quiz_id,
            'score': score,
            'correct_answers': correct_answers,
            'total_questions': total_questions,
            'percentage': f"{score:.1f}%"
        }
        
        # Store result
        result_key = f"result:{quiz_id}:{request.headers.get('X-User-ID', 'anonymous')}"
        current_app.redis.setex(result_key, 86400, json.dumps(result))  # 24 hours TTL
        
        logger.info("Quiz submitted", quiz_id=quiz_id, score=score)
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        logger.error("Quiz submission failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to submit quiz'
        }), 500

@quiz_bp.route('/list', methods=['GET'])
@rate_limit('quiz_list')
def list_quizzes():
    """List available quizzes with rate limiting"""
    try:
        # Get all quiz keys from Redis
        quiz_keys = current_app.redis.keys('quiz:*')
        quizzes = []
        
        for key in quiz_keys[:20]:  # Limit to 20 most recent
            quiz_data = current_app.redis.get(key)
            if quiz_data:
                quiz = json.loads(quiz_data)
                quizzes.append({
                    'quiz_id': quiz['quiz_id'],
                    'title': quiz['title'],
                    'difficulty': quiz['difficulty'],
                    'num_questions': len(quiz.get('questions', []))
                })
        
        return jsonify({
            'success': True,
            'quizzes': quizzes
        })
        
    except Exception as e:
        logger.error("Quiz listing failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to list quizzes'
        }), 500
