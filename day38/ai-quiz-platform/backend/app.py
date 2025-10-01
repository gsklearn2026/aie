"""
AI Quiz Platform Backend - Docker Compose Version
Day 38: Multi-service orchestration with health checks
"""

import os
import logging
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
import redis
import google.generativeai as genai
from datetime import datetime, timedelta
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-2025')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # Initialize extensions
    db = SQLAlchemy(app)
    migrate = Migrate(app, db)
    CORS(app)
    jwt = JWTManager(app)
    
    # Redis connection
    redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379/0'))
    
    # Gemini AI setup
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    model = None
    if gemini_api_key and gemini_api_key != 'your_gemini_api_key_here' and len(gemini_api_key) > 10:
        try:
            genai.configure(api_key=gemini_api_key)
            model = genai.GenerativeModel('gemini-pro')
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini model: {str(e)}")
            model = None
    
    # Models
    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        username = db.Column(db.String(50), unique=True, nullable=False)
        email = db.Column(db.String(100), unique=True, nullable=False)
        password_hash = db.Column(db.String(255), nullable=False)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class Quiz(db.Model):
        __tablename__ = 'quizzes'
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        title = db.Column(db.String(200), nullable=False)
        description = db.Column(db.Text)
        created_by = db.Column(db.String(36), db.ForeignKey('users.id'))
        difficulty = db.Column(db.String(20), default='medium')
        category = db.Column(db.String(50))
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    class Question(db.Model):
        __tablename__ = 'questions'
        id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
        quiz_id = db.Column(db.String(36), db.ForeignKey('quizzes.id'))
        question_text = db.Column(db.Text, nullable=False)
        options = db.Column(db.JSON)
        correct_answer = db.Column(db.Text, nullable=False)
        explanation = db.Column(db.Text)
        created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Routes
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint for Docker Compose"""
        try:
            # Check database connection
            db.session.execute(db.text('SELECT 1'))
            
            # Check Redis connection
            redis_client.ping()
            
            return jsonify({
                'status': 'healthy',
                'timestamp': datetime.utcnow().isoformat(),
                'services': {
                    'database': 'connected',
                    'redis': 'connected',
                    'gemini': 'configured' if model else 'not_configured'
                }
            }), 200
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}")
            return jsonify({'status': 'unhealthy', 'error': str(e)}), 503

    @app.route('/api/quizzes', methods=['GET'])
    def get_quizzes():
        """Get all available quizzes"""
        try:
            quizzes = Quiz.query.all()
            return jsonify([{
                'id': quiz.id,
                'title': quiz.title,
                'description': quiz.description,
                'category': quiz.category,
                'difficulty': quiz.difficulty,
                'created_at': quiz.created_at.isoformat()
            } for quiz in quizzes])
        except Exception as e:
            logger.error(f"Error fetching quizzes: {str(e)}")
            return jsonify({'error': 'Failed to fetch quizzes'}), 500

    @app.route('/api/generate-question', methods=['POST'])
    def generate_question():
        """Generate AI-powered quiz question using Gemini"""
        try:
            data = request.get_json()
            topic = data.get('topic', 'General Knowledge')
            difficulty = data.get('difficulty', 'medium')
            
            # Check Redis cache first
            cache_key = f"question:{topic}:{difficulty}"
            cached_question = redis_client.get(cache_key)
            
            if cached_question:
                return jsonify(eval(cached_question))
            
            # Define sample questions
            sample_questions = {
                'Docker Containers': {
                    'question': 'What is the primary purpose of Docker containers?',
                    'options': [
                        'To run multiple operating systems on one machine',
                        'To package applications with their dependencies',
                        'To create virtual machines',
                        'To manage network traffic'
                    ],
                    'correct_answer': 'To package applications with their dependencies',
                    'explanation': 'Docker containers package applications with all their dependencies, making them portable and consistent across different environments.'
                },
                'Microservices': {
                    'question': 'What is a key advantage of microservices architecture?',
                    'options': [
                        'Simpler deployment process',
                        'Independent scaling of services',
                        'Reduced development time',
                        'Lower memory usage'
                    ],
                    'correct_answer': 'Independent scaling of services',
                    'explanation': 'Microservices allow each service to be scaled independently based on its specific needs and load.'
                },
                'General Knowledge': {
                    'question': 'What is the main benefit of using containerization?',
                    'options': [
                        'Faster hardware performance',
                        'Consistent deployment environments',
                        'Lower memory usage',
                        'Better network security'
                    ],
                    'correct_answer': 'Consistent deployment environments',
                    'explanation': 'Containerization ensures that applications run consistently across different environments by packaging all dependencies together.'
                }
            }
            
            # Try to use Gemini API if available
            if model:
                try:
                    prompt = f"""
                    Generate a {difficulty} level multiple choice question about {topic}.
                    Format the response as JSON with these fields:
                    - question: the question text
                    - options: array of 4 possible answers
                    - correct_answer: the correct answer
                    - explanation: brief explanation of why the answer is correct
                    
                    Make it educational and engaging for students.
                    """
                    
                    response = model.generate_content(prompt)
                    question_data = eval(response.text)  # In production, use proper JSON parsing
                except Exception as e:
                    logger.warning(f"Gemini API failed, using fallback: {str(e)}")
                    question_data = sample_questions.get(topic, sample_questions['General Knowledge'])
            else:
                # Use sample questions when Gemini is not available
                question_data = sample_questions.get(topic, sample_questions['General Knowledge'])
            
            # Cache for 1 hour
            redis_client.setex(cache_key, 3600, str(question_data))
            
            return jsonify(question_data)
            
        except Exception as e:
            logger.error(f"Error generating question: {str(e)}")
            return jsonify({'error': 'Failed to generate question'}), 500

    @app.route('/api/submit-answer', methods=['POST'])
    def submit_answer():
        """Submit quiz answer and get feedback"""
        try:
            data = request.get_json()
            user_answer = data.get('answer')
            correct_answer = data.get('correct_answer')
            question_id = data.get('question_id')
            
            is_correct = user_answer == correct_answer
            
            # Log response (in production, save to database)
            logger.info(f"Answer submitted - Correct: {is_correct}")
            
            return jsonify({
                'is_correct': is_correct,
                'correct_answer': correct_answer,
                'message': 'Correct! Well done.' if is_correct else 'Not quite right. Try again!',
                'timestamp': datetime.utcnow().isoformat()
            })
            
        except Exception as e:
            logger.error(f"Error submitting answer: {str(e)}")
            return jsonify({'error': 'Failed to submit answer'}), 500

    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Get platform statistics"""
        try:
            return jsonify({
                'total_quizzes': Quiz.query.count(),
                'total_users': User.query.count(),
                'total_questions': Question.query.count(),
                'uptime': 'Docker Compose Orchestrated',
                'timestamp': datetime.utcnow().isoformat()
            })
        except Exception as e:
            logger.error(f"Error fetching stats: {str(e)}")
            return jsonify({'error': 'Failed to fetch stats'}), 500

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8000, debug=True)
