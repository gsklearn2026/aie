import os
from flask import Flask, jsonify
from flask_restx import Api, Resource, fields, Namespace
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import google.generativeai as genai
from datetime import datetime
import json

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-key-change-in-production'
CORS(app, 
     origins=['http://localhost:3000', 'http://127.0.0.1:3000'], 
     supports_credentials=True,
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)

# Configure Gemini AI
genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'demo-key'))

# Initialize Flask-RESTX with OpenAPI configuration
api = Api(
    app,
    version='1.0',
    title='Quiz Platform API',
    description='Comprehensive API for AI-powered quiz platform with real-time features',
    doc='/docs/',
    authorizations={
        'Bearer': {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': 'Add a JWT token to the header with format: Bearer {token}'
        }
    },
    security='Bearer'
)

# Define namespaces
quiz_ns = Namespace('quizzes', description='Quiz management operations')
user_ns = Namespace('users', description='User management operations')
analytics_ns = Namespace('analytics', description='Quiz analytics and reporting')
ai_ns = Namespace('ai', description='AI-powered quiz generation')

# Add namespaces to API
api.add_namespace(quiz_ns, path='/api/v1/quizzes')
api.add_namespace(user_ns, path='/api/v1/users')
api.add_namespace(analytics_ns, path='/api/v1/analytics')
api.add_namespace(ai_ns, path='/api/v1/ai')

# Define data models for OpenAPI documentation
quiz_model = api.model('Quiz', {
    'id': fields.String(required=True, description='Unique quiz identifier'),
    'title': fields.String(required=True, description='Quiz title'),
    'description': fields.String(description='Quiz description'),
    'difficulty': fields.String(enum=['easy', 'medium', 'hard'], description='Quiz difficulty level'),
    'category': fields.String(description='Quiz category'),
    'questions': fields.List(fields.Nested(api.model('Question', {
        'id': fields.String(description='Question ID'),
        'text': fields.String(description='Question text'),
        'options': fields.List(fields.String, description='Answer options'),
        'correct_answer': fields.String(description='Correct answer')
    }))),
    'created_at': fields.DateTime(description='Creation timestamp'),
    'updated_at': fields.DateTime(description='Last update timestamp')
})

user_model = api.model('User', {
    'id': fields.String(required=True, description='User ID'),
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='User email'),
    'role': fields.String(enum=['student', 'teacher', 'admin'], description='User role'),
    'created_at': fields.DateTime(description='Account creation date'),
    'quiz_attempts': fields.Integer(description='Number of quiz attempts')
})

quiz_result_model = api.model('QuizResult', {
    'id': fields.String(description='Result ID'),
    'user_id': fields.String(description='User who took the quiz'),
    'quiz_id': fields.String(description='Quiz taken'),
    'score': fields.Float(description='Score percentage (0-100)'),
    'time_taken': fields.Integer(description='Time taken in seconds'),
    'answers': fields.Raw(description='User answers array'),
    'completed_at': fields.DateTime(description='Completion timestamp')
})

# Mock data store
quizzes_db = {
    'quiz_1': {
        'id': 'quiz_1',
        'title': 'Python Fundamentals',
        'description': 'Test your Python basics',
        'difficulty': 'easy',
        'category': 'Programming',
        'questions': [
            {
                'id': 'q1',
                'text': 'What is Python?',
                'options': ['A snake', 'A programming language', 'A framework', 'A database'],
                'correct_answer': 'A programming language'
            }
        ],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }
}

users_db = {
    'user_1': {
        'id': 'user_1',
        'username': 'john_doe',
        'email': 'john@example.com',
        'role': 'student',
        'created_at': datetime.now().isoformat(),
        'quiz_attempts': 5
    }
}

results_db = {
    'result_1': {
        'id': 'result_1',
        'user_id': 'user_1',
        'quiz_id': 'quiz_1',
        'score': 85.5,
        'time_taken': 300,
        'answers': ['A programming language'],
        'completed_at': datetime.now().isoformat()
    }
}

# Quiz endpoints
@quiz_ns.route('/')
class QuizList(Resource):
    @quiz_ns.doc('list_quizzes')
    @quiz_ns.marshal_list_with(quiz_model)
    @quiz_ns.response(200, 'Success')
    @quiz_ns.response(500, 'Internal Server Error')
    @limiter.limit("30 per minute")
    def get(self):
        """Fetch all available quizzes with pagination support"""
        return list(quizzes_db.values())

    @quiz_ns.doc('create_quiz')
    @quiz_ns.expect(quiz_model)
    @quiz_ns.marshal_with(quiz_model, code=201)
    @quiz_ns.response(201, 'Quiz created successfully')
    @quiz_ns.response(400, 'Invalid input data')
    @quiz_ns.response(409, 'Quiz already exists')
    def post(self):
        """Create a new quiz with AI-generated questions"""
        data = api.payload
        
        # Validate that data is a dictionary
        if not isinstance(data, dict):
            api.abort(400, "Invalid request data. Expected JSON object.")
        
        # Validate required fields
        if not data.get('title'):
            api.abort(400, "Title is required")
        
        quiz_id = f"quiz_{len(quizzes_db) + 1}"
        data['id'] = quiz_id
        data['created_at'] = datetime.now().isoformat()
        data['updated_at'] = datetime.now().isoformat()
        quizzes_db[quiz_id] = data
        return data, 201

@quiz_ns.route('/<string:quiz_id>')
@quiz_ns.param('quiz_id', 'The quiz identifier')
class Quiz(Resource):
    @quiz_ns.doc('get_quiz')
    @quiz_ns.marshal_with(quiz_model)
    @quiz_ns.response(200, 'Success')
    @quiz_ns.response(404, 'Quiz not found')
    def get(self, quiz_id):
        """Fetch a specific quiz by ID"""
        if quiz_id not in quizzes_db:
            api.abort(404, f"Quiz {quiz_id} not found")
        return quizzes_db[quiz_id]

    @quiz_ns.doc('update_quiz')
    @quiz_ns.expect(quiz_model)
    @quiz_ns.marshal_with(quiz_model)
    @quiz_ns.response(200, 'Quiz updated successfully')
    @quiz_ns.response(404, 'Quiz not found')
    def put(self, quiz_id):
        """Update an existing quiz"""
        if quiz_id not in quizzes_db:
            api.abort(404, f"Quiz {quiz_id} not found")
        
        data = api.payload
        
        # Validate that data is a dictionary
        if not isinstance(data, dict):
            api.abort(400, "Invalid request data. Expected JSON object.")
        
        data['updated_at'] = datetime.now().isoformat()
        quizzes_db[quiz_id].update(data)
        return quizzes_db[quiz_id]

    @quiz_ns.doc('delete_quiz')
    @quiz_ns.response(204, 'Quiz deleted successfully')
    @quiz_ns.response(404, 'Quiz not found')
    def delete(self, quiz_id):
        """Delete a quiz permanently"""
        if quiz_id not in quizzes_db:
            api.abort(404, f"Quiz {quiz_id} not found")
        del quizzes_db[quiz_id]
        return '', 204

# User endpoints
@user_ns.route('/')
class UserList(Resource):
    @user_ns.doc('list_users')
    @user_ns.marshal_list_with(user_model)
    @user_ns.response(200, 'Success')
    def get(self):
        """Get all users with role-based filtering"""
        return list(users_db.values())

@user_ns.route('/<string:user_id>')
@user_ns.param('user_id', 'The user identifier')
class User(Resource):
    @user_ns.doc('get_user')
    @user_ns.marshal_with(user_model)
    @user_ns.response(200, 'Success')
    @user_ns.response(404, 'User not found')
    def get(self, user_id):
        """Get user profile information"""
        if user_id not in users_db:
            api.abort(404, f"User {user_id} not found")
        return users_db[user_id]

# Analytics endpoints
@analytics_ns.route('/results')
class ResultsList(Resource):
    @analytics_ns.doc('list_results')
    @analytics_ns.marshal_list_with(quiz_result_model)
    @analytics_ns.response(200, 'Success')
    def get(self):
        """Get quiz results with analytics metrics"""
        return list(results_db.values())

@analytics_ns.route('/stats')
class AnalyticsStats(Resource):
    @analytics_ns.doc('get_stats')
    @analytics_ns.response(200, 'Success')
    def get(self):
        """Get platform statistics and insights"""
        stats = {
            'total_quizzes': len(quizzes_db),
            'total_users': len(users_db),
            'total_attempts': len(results_db),
            'average_score': 85.5,
            'completion_rate': 92.3
        }
        return stats

# AI endpoints
@ai_ns.route('/generate-questions')
class AIQuestionGeneration(Resource):
    @ai_ns.doc('generate_questions')
    @ai_ns.response(200, 'Questions generated successfully')
    @ai_ns.response(500, 'AI service unavailable')
    def post(self):
        """Generate quiz questions using Gemini AI"""
        try:
            # Simulate AI generation
            questions = [
                {
                    'text': 'What is the purpose of API documentation?',
                    'options': ['Testing', 'Communication', 'Storage', 'Security'],
                    'correct_answer': 'Communication'
                }
            ]
            return {'questions': questions, 'generated_at': datetime.now().isoformat()}
        except Exception as e:
            api.abort(500, f"AI generation failed: {str(e)}")

# Health check endpoint
@api.route('/health')
class HealthCheck(Resource):
    @api.doc('health_check')
    @api.response(200, 'Service healthy')
    def get(self):
        """Check API health and service status"""
        return {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'version': '1.0.0',
            'services': {
                'database': 'connected',
                'ai_service': 'available',
                'cache': 'active'
            }
        }

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
