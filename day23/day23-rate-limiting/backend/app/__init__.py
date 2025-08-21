from flask import Flask
from flask_cors import CORS
import redis
import os
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    CORS(app)
    
    # Redis configuration
    app.config['REDIS_URL'] = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    app.config['GEMINI_API_KEY'] = os.getenv('GEMINI_API_KEY')
    
    # Initialize Redis
    redis_client = redis.from_url(app.config['REDIS_URL'])
    app.redis = redis_client
    
    # Register blueprints
    from .routes.quiz_routes import quiz_bp
    from .routes.rate_limit_routes import rate_limit_bp
    
    app.register_blueprint(quiz_bp, url_prefix='/api/quiz')
    app.register_blueprint(rate_limit_bp, url_prefix='/api/rate-limit')
    
    return app
