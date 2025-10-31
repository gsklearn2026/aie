#!/bin/bash

# Day 23: Rate Limiting and Request Throttling Implementation Script
# AI Engineering Quiz Platform - 60 Days Hands-On Series

set -e

echo "🚀 Day 23: Implementing Rate Limiting and Request Throttling"
echo "============================================================"

# Create project structure
echo "📁 Creating project structure..."
mkdir -p day23-rate-limiting/{backend,frontend,tests,config,scripts}
cd day23-rate-limiting

# Backend structure
mkdir -p backend/{app,middleware,models,routes,services,utils}
mkdir -p backend/app/rate_limiter

# Frontend structure  
mkdir -p frontend/{src,public}
mkdir -p frontend/src/{components,services,hooks,styles}

# Tests structure
mkdir -p tests/{unit,integration,e2e}

# Create backend requirements
cat > backend/requirements.txt << 'EOF'
flask==3.0.3
flask-cors==4.0.1
redis==5.0.4
python-dotenv==1.0.1
pydantic==2.7.1
google-generativeai==0.5.4
pytest==8.2.0
pytest-asyncio==0.23.6
requests==2.31.0
gunicorn==22.0.0
flask-limiter==3.7.0
werkzeug==3.0.3
dataclasses-json==0.6.6
structlog==24.1.0
EOF

# Create backend main application
cat > backend/app/__init__.py << 'EOF'
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
EOF

# Create rate limiter middleware
cat > backend/middleware/rate_limiter.py << 'EOF'
import time
import json
from functools import wraps
from flask import request, jsonify, current_app, g
from typing import Dict, Tuple, Optional
import redis
import structlog

logger = structlog.get_logger()

class RateLimitConfig:
    """Rate limit configuration for different user tiers and endpoints"""
    
    TIERS = {
        'free': {'requests': 100, 'window': 3600},  # 100 requests per hour
        'premium': {'requests': 1000, 'window': 3600},  # 1000 requests per hour
        'admin': {'requests': 10, 'window': 60}  # 10 requests per minute for admin endpoints
    }
    
    ENDPOINT_LIMITS = {
        'ai_generate': {'requests': 5, 'window': 60},  # 5 AI generations per minute
        'quiz_submit': {'requests': 30, 'window': 300},  # 30 submissions per 5 minutes
        'quiz_list': {'requests': 200, 'window': 3600}  # 200 list requests per hour
    }

class TokenBucket:
    """Token bucket algorithm implementation"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    def is_allowed(self, key: str, max_tokens: int, refill_rate: float, window: int) -> Tuple[bool, Dict]:
        """
        Check if request is allowed using token bucket algorithm
        
        Args:
            key: Unique identifier for the bucket
            max_tokens: Maximum tokens in bucket
            refill_rate: Tokens added per second
            window: Time window in seconds
            
        Returns:
            Tuple of (is_allowed, info_dict)
        """
        now = time.time()
        bucket_key = f"bucket:{key}"
        
        # Get current bucket state
        pipe = self.redis.pipeline()
        pipe.hmget(bucket_key, 'tokens', 'last_refill')
        pipe.ttl(bucket_key)
        bucket_data, ttl = pipe.execute()
        
        tokens = float(bucket_data[0] or max_tokens)
        last_refill = float(bucket_data[1] or now)
        
        # Calculate tokens to add based on time elapsed
        time_elapsed = now - last_refill
        tokens_to_add = time_elapsed * refill_rate
        tokens = min(max_tokens, tokens + tokens_to_add)
        
        # Check if request can be served
        if tokens >= 1:
            tokens -= 1
            allowed = True
        else:
            allowed = False
            
        # Update bucket state
        pipe = self.redis.pipeline()
        pipe.hmset(bucket_key, {
            'tokens': tokens,
            'last_refill': now
        })
        pipe.expire(bucket_key, window * 2)  # Keep bucket for 2x window
        pipe.execute()
        
        return allowed, {
            'allowed': allowed,
            'tokens_remaining': int(tokens),
            'reset_time': int(now + (max_tokens - tokens) / refill_rate),
            'retry_after': int((1 - tokens) / refill_rate) if not allowed else 0
        }

class RateLimiter:
    """Main rate limiter class"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.bucket = TokenBucket(redis_client)
        
    def get_user_tier(self, user_id: str) -> str:
        """Get user tier from Redis or default to free"""
        tier = self.redis.get(f"user_tier:{user_id}")
        return tier.decode() if tier else 'free'
    
    def get_rate_limit_key(self, user_id: str, endpoint: str = None) -> str:
        """Generate rate limit key"""
        if endpoint:
            return f"rate_limit:{user_id}:{endpoint}"
        return f"rate_limit:{user_id}"
    
    def check_rate_limit(self, user_id: str, endpoint: str = None) -> Tuple[bool, Dict]:
        """Check if request is within rate limits"""
        
        # Get user tier
        tier = self.get_user_tier(user_id)
        
        # Check endpoint-specific limits first
        if endpoint and endpoint in RateLimitConfig.ENDPOINT_LIMITS:
            config = RateLimitConfig.ENDPOINT_LIMITS[endpoint]
            key = self.get_rate_limit_key(user_id, endpoint)
            
            refill_rate = config['requests'] / config['window']
            allowed, info = self.bucket.is_allowed(
                key, config['requests'], refill_rate, config['window']
            )
            
            if not allowed:
                return False, info
        
        # Check general tier limits
        if tier in RateLimitConfig.TIERS:
            config = RateLimitConfig.TIERS[tier]
            key = self.get_rate_limit_key(user_id)
            
            refill_rate = config['requests'] / config['window']
            allowed, info = self.bucket.is_allowed(
                key, config['requests'], refill_rate, config['window']
            )
            
            # Add tier information
            info['tier'] = tier
            info['tier_limit'] = config['requests']
            info['window'] = config['window']
            
            return allowed, info
        
        # Default: allow request
        return True, {'allowed': True, 'tier': 'unknown'}

def rate_limit(endpoint: str = None):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get user ID from request
            user_id = request.headers.get('X-User-ID', request.remote_addr)
            
            # Initialize rate limiter
            rate_limiter = RateLimiter(current_app.redis)
            
            # Check rate limit
            allowed, info = rate_limiter.check_rate_limit(user_id, endpoint)
            
            if not allowed:
                logger.warning(
                    "Rate limit exceeded",
                    user_id=user_id,
                    endpoint=endpoint,
                    info=info
                )
                
                response = jsonify({
                    'error': 'Rate limit exceeded',
                    'message': f'Too many requests. Try again in {info.get("retry_after", 60)} seconds.',
                    'rate_limit_info': info
                })
                response.status_code = 429
                response.headers['X-RateLimit-Limit'] = str(info.get('tier_limit', 'unknown'))
                response.headers['X-RateLimit-Remaining'] = str(info.get('tokens_remaining', 0))
                response.headers['X-RateLimit-Reset'] = str(info.get('reset_time', 0))
                response.headers['Retry-After'] = str(info.get('retry_after', 60))
                
                return response
            
            # Store rate limit info in g for use in response headers
            g.rate_limit_info = info
            
            # Execute the original function
            result = f(*args, **kwargs)
            
            # Add rate limit headers to successful responses
            if hasattr(result, 'headers'):
                result.headers['X-RateLimit-Limit'] = str(info.get('tier_limit', 'unknown'))
                result.headers['X-RateLimit-Remaining'] = str(info.get('tokens_remaining', 0))
                result.headers['X-RateLimit-Reset'] = str(info.get('reset_time', 0))
            
            return result
        return decorated_function
    return decorator
EOF

# Create quiz routes with rate limiting
cat > backend/routes/quiz_routes.py << 'EOF'
from flask import Blueprint, request, jsonify, current_app
from middleware.rate_limiter import rate_limit
import google.generativeai as genai
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
EOF

# Create rate limit routes for monitoring
cat > backend/routes/rate_limit_routes.py << 'EOF'
from flask import Blueprint, request, jsonify, current_app
from middleware.rate_limiter import RateLimiter
import structlog

logger = structlog.get_logger()

rate_limit_bp = Blueprint('rate_limit', __name__)

@rate_limit_bp.route('/status', methods=['GET'])
def get_rate_limit_status():
    """Get current rate limit status for user"""
    try:
        user_id = request.headers.get('X-User-ID', request.remote_addr)
        
        rate_limiter = RateLimiter(current_app.redis)
        
        # Check status for different endpoints
        status = {}
        
        # General tier status
        allowed, info = rate_limiter.check_rate_limit(user_id)
        status['general'] = info
        
        # Endpoint-specific status
        endpoints = ['ai_generate', 'quiz_submit', 'quiz_list']
        for endpoint in endpoints:
            allowed, info = rate_limiter.check_rate_limit(user_id, endpoint)
            status[endpoint] = info
        
        return jsonify({
            'success': True,
            'user_id': user_id,
            'rate_limits': status
        })
        
    except Exception as e:
        logger.error("Rate limit status check failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to get rate limit status'
        }), 500

@rate_limit_bp.route('/upgrade-tier', methods=['POST'])
def upgrade_user_tier():
    """Upgrade user tier (for demo purposes)"""
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        tier = data.get('tier', 'premium')
        
        if tier not in ['free', 'premium', 'admin']:
            return jsonify({
                'success': False,
                'error': 'Invalid tier'
            }), 400
        
        # Set user tier in Redis
        current_app.redis.setex(f"user_tier:{user_id}", 86400, tier)  # 24 hours
        
        logger.info("User tier upgraded", user_id=user_id, tier=tier)
        
        return jsonify({
            'success': True,
            'message': f'User {user_id} upgraded to {tier} tier'
        })
        
    except Exception as e:
        logger.error("Tier upgrade failed", error=str(e))
        return jsonify({
            'success': False,
            'error': 'Failed to upgrade tier'
        }), 500
EOF

# Create main Flask app
cat > backend/main.py << 'EOF'
from app import create_app
import structlog
import logging

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
EOF

# Create environment file
cat > backend/.env << 'EOF'
REDIS_URL=redis://localhost:6379/0
GEMINI_API_KEY=your_gemini_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
EOF

# Create frontend package.json
cat > frontend/package.json << 'EOF'
{
  "name": "quiz-platform-frontend",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-scripts": "5.0.1",
    "axios": "^1.7.2",
    "react-router-dom": "^6.23.1",
    "tailwindcss": "^3.4.3",
    "autoprefixer": "^10.4.19",
    "postcss": "^8.4.38",
    "@heroicons/react": "^2.1.3",
    "recharts": "^2.12.7",
    "react-hot-toast": "^2.4.1"
  },
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test",
    "eject": "react-scripts eject"
  },
  "eslintConfig": {
    "extends": [
      "react-app",
      "react-app/jest"
    ]
  },
  "browserslist": {
    "production": [
      ">0.2%",
      "not dead",
      "not op_mini all"
    ],
    "development": [
      "last 1 chrome version",
      "last 1 firefox version",
      "last 1 safari version"
    ]
  }
}
EOF

# Create React components
cat > frontend/src/App.js << 'EOF'
import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import Header from './components/Header';
import Dashboard from './components/Dashboard';
import QuizGenerator from './components/QuizGenerator';
import RateLimitMonitor from './components/RateLimitMonitor';
import './styles/App.css';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/quiz" element={<QuizGenerator />} />
            <Route path="/rate-limits" element={<RateLimitMonitor />} />
          </Routes>
        </main>
        <Toaster position="top-right" />
      </div>
    </Router>
  );
}

export default App;
EOF

# Create Header component
cat > frontend/src/components/Header.js << 'EOF'
import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { 
  HomeIcon, 
  PuzzlePieceIcon, 
  ChartBarIcon 
} from '@heroicons/react/24/outline';

const Header = () => {
  const location = useLocation();
  
  const navigation = [
    { name: 'Dashboard', href: '/', icon: HomeIcon },
    { name: 'Quiz Generator', href: '/quiz', icon: PuzzlePieceIcon },
    { name: 'Rate Limits', href: '/rate-limits', icon: ChartBarIcon },
  ];

  return (
    <header className="bg-white shadow-sm border-b border-gray-200">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <h1 className="text-xl font-bold text-gray-900">
                AI Quiz Platform
              </h1>
            </div>
            <nav className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navigation.map((item) => {
                const Icon = item.icon;
                return (
                  <Link
                    key={item.name}
                    to={item.href}
                    className={`${
                      location.pathname === item.href
                        ? 'border-indigo-500 text-gray-900'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    } inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium`}
                  >
                    <Icon className="h-4 w-4 mr-2" />
                    {item.name}
                  </Link>
                );
              })}
            </nav>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
EOF

# Create Rate Limit Monitor component
cat > frontend/src/components/RateLimitMonitor.js << 'EOF'
import React, { useState, useEffect } from 'react';
import { 
  ClockIcon, 
  ExclamationTriangleIcon,
  CheckCircleIcon 
} from '@heroicons/react/24/outline';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell } from 'recharts';
import toast from 'react-hot-toast';
import { getRateLimitStatus, upgradeTier } from '../services/api';

const RateLimitMonitor = () => {
  const [rateLimits, setRateLimits] = useState(null);
  const [loading, setLoading] = useState(true);
  const [userId, setUserId] = useState('user123');

  useEffect(() => {
    fetchRateLimitStatus();
    const interval = setInterval(fetchRateLimitStatus, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchRateLimitStatus = async () => {
    try {
      const data = await getRateLimitStatus(userId);
      setRateLimits(data.rate_limits);
    } catch (error) {
      console.error('Failed to fetch rate limit status:', error);
      toast.error('Failed to fetch rate limit status');
    } finally {
      setLoading(false);
    }
  };

  const handleUpgradeTier = async (tier) => {
    try {
      await upgradeTier(userId, tier);
      toast.success(`Upgraded to ${tier} tier!`);
      fetchRateLimitStatus();
    } catch (error) {
      console.error('Failed to upgrade tier:', error);
      toast.error('Failed to upgrade tier');
    }
  };

  const formatChartData = () => {
    if (!rateLimits) return [];
    
    return Object.entries(rateLimits).map(([endpoint, data]) => ({
      endpoint: endpoint.replace('_', ' ').toUpperCase(),
      remaining: data.tokens_remaining || 0,
      limit: data.tier_limit || 100,
      usage: (data.tier_limit || 100) - (data.tokens_remaining || 0)
    }));
  };

  const getStatusColor = (remaining, limit) => {
    const percentage = (remaining / limit) * 100;
    if (percentage > 50) return 'text-green-600';
    if (percentage > 20) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getStatusIcon = (remaining, limit) => {
    const percentage = (remaining / limit) * 100;
    if (percentage > 50) return CheckCircleIcon;
    if (percentage > 20) return ExclamationTriangleIcon;
    return ClockIcon;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  const chartData = formatChartData();

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Rate Limit Monitor</h1>
        <div className="flex space-x-2">
          <button
            onClick={() => handleUpgradeTier('premium')}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
          >
            Upgrade to Premium
          </button>
          <button
            onClick={() => handleUpgradeTier('admin')}
            className="px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700"
          >
            Admin Access
          </button>
        </div>
      </div>

      {/* User Info */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">User Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">User ID</label>
            <input
              type="text"
              value={userId}
              onChange={(e) => setUserId(e.target.value)}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm px-3 py-2"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Current Tier</label>
            <p className="mt-1 text-lg font-semibold text-indigo-600">
              {rateLimits?.general?.tier || 'Free'}
            </p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Window</label>
            <p className="mt-1 text-sm text-gray-600">
              {rateLimits?.general?.window ? `${rateLimits.general.window}s` : 'N/A'}
            </p>
          </div>
        </div>
      </div>

      {/* Rate Limit Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {rateLimits && Object.entries(rateLimits).map(([endpoint, data]) => {
          const StatusIcon = getStatusIcon(data.tokens_remaining || 0, data.tier_limit || 100);
          return (
            <div key={endpoint} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-gray-600 capitalize">
                    {endpoint.replace('_', ' ')}
                  </p>
                  <p className="text-2xl font-bold text-gray-900">
                    {data.tokens_remaining || 0}
                  </p>
                  <p className="text-sm text-gray-500">
                    of {data.tier_limit || 100} remaining
                  </p>
                </div>
                <StatusIcon 
                  className={`h-8 w-8 ${getStatusColor(
                    data.tokens_remaining || 0, 
                    data.tier_limit || 100
                  )}`} 
                />
              </div>
              {data.reset_time && (
                <div className="mt-4 text-xs text-gray-500">
                  Resets: {new Date(data.reset_time * 1000).toLocaleTimeString()}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Usage Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">API Usage Overview</h2>
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="endpoint" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="usage" name="Used">
                {chartData.map((entry, index) => (
                  <Cell 
                    key={`cell-${index}`} 
                    fill={entry.usage / entry.limit > 0.8 ? '#EF4444' : 
                         entry.usage / entry.limit > 0.5 ? '#F59E0B' : '#10B981'} 
                  />
                ))}
              </Bar>
              <Bar dataKey="remaining" name="Remaining" fill="#E5E7EB" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default RateLimitMonitor;
EOF

# Create API service
cat > frontend/src/services/api.js << 'EOF'
import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include user ID
api.interceptors.request.use((config) => {
  const userId = localStorage.getItem('userId') || 'user123';
  config.headers['X-User-ID'] = userId;
  return config;
});

// Add response interceptor to handle rate limiting
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers['retry-after'];
      throw new Error(`Rate limit exceeded. Try again in ${retryAfter} seconds.`);
    }
    throw error;
  }
);

export const generateQuiz = async (topic, difficulty, numQuestions) => {
  const response = await api.post('/quiz/generate', {
    topic,
    difficulty,
    num_questions: numQuestions,
  });
  return response.data;
};

export const submitQuiz = async (quizId, answers) => {
  const response = await api.post('/quiz/submit', {
    quiz_id: quizId,
    answers,
  });
  return response.data;
};

export const listQuizzes = async () => {
  const response = await api.get('/quiz/list');
  return response.data;
};

export const getRateLimitStatus = async (userId) => {
  const response = await api.get('/rate-limit/status', {
    headers: { 'X-User-ID': userId }
  });
  return response.data;
};

export const upgradeTier = async (userId, tier) => {
  const response = await api.post('/rate-limit/upgrade-tier', {
    user_id: userId,
    tier,
  });
  return response.data;
};

export default api;
EOF

# Create remaining components
cat > frontend/src/components/Dashboard.js << 'EOF'
import React from 'react';
import { Link } from 'react-router-dom';
import { 
  PuzzlePieceIcon, 
  ChartBarIcon,
  ShieldCheckIcon,
  ClockIcon 
} from '@heroicons/react/24/outline';

const Dashboard = () => {
  const features = [
    {
      title: 'AI Quiz Generator',
      description: 'Generate custom quizzes using AI with rate limiting protection',
      icon: PuzzlePieceIcon,
      link: '/quiz',
      color: 'bg-blue-500'
    },
    {
      title: 'Rate Limit Monitor',
      description: 'Monitor API usage and rate limit status in real-time',
      icon: ChartBarIcon,
      link: '/rate-limits',
      color: 'bg-green-500'
    },
    {
      title: 'API Protection',
      description: 'Secure endpoints with tiered rate limiting',
      icon: ShieldCheckIcon,
      link: '/rate-limits',
      color: 'bg-purple-500'
    },
    {
      title: 'Request Throttling',
      description: 'Intelligent request management and throttling',
      icon: ClockIcon,
      link: '/rate-limits',
      color: 'bg-orange-500'
    }
  ];

  return (
    <div className="space-y-8">
      <div className="text-center">
        <h1 className="text-3xl font-bold text-gray-900">
          Day 23: Rate Limiting & Request Throttling
        </h1>
        <p className="mt-4 text-lg text-gray-600">
          Learn how to protect your APIs and manage resources with intelligent rate limiting
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {features.map((feature) => {
          const Icon = feature.icon;
          return (
            <Link
              key={feature.title}
              to={feature.link}
              className="block bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
            >
              <div className="flex items-center space-x-4">
                <div className={`${feature.color} p-3 rounded-lg`}>
                  <Icon className="h-8 w-8 text-white" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">
                    {feature.title}
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {feature.description}
                  </p>
                </div>
              </div>
            </Link>
          );
        })}
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Today's Learning Objectives
        </h2>
        <ul className="space-y-3 text-gray-600">
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            Implement token bucket algorithm for rate limiting
          </li>
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            Create tiered rate limits for different user types
          </li>
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            Build real-time rate limit monitoring dashboard
          </li>
          <li className="flex items-start">
            <span className="text-green-500 mr-2">✓</span>
            Integrate with Redis for distributed rate limiting
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard;
EOF

# Create Quiz Generator component
cat > frontend/src/components/QuizGenerator.js << 'EOF'
import React, { useState } from 'react';
import { generateQuiz, submitQuiz } from '../services/api';
import toast from 'react-hot-toast';

const QuizGenerator = () => {
  const [quiz, setQuiz] = useState(null);
  const [loading, setLoading] = useState(false);
  const [answers, setAnswers] = useState([]);
  const [result, setResult] = useState(null);
  const [formData, setFormData] = useState({
    topic: 'JavaScript',
    difficulty: 'medium',
    numQuestions: 5
  });

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const response = await generateQuiz(
        formData.topic,
        formData.difficulty,
        formData.numQuestions
      );
      
      if (response.success) {
        setQuiz(response.quiz);
        setAnswers(new Array(response.quiz.questions.length).fill(null));
        setResult(null);
        toast.success('Quiz generated successfully!');
      }
    } catch (error) {
      console.error('Quiz generation failed:', error);
      toast.error(error.message || 'Failed to generate quiz');
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionIndex, answerIndex) => {
    const newAnswers = [...answers];
    newAnswers[questionIndex] = answerIndex;
    setAnswers(newAnswers);
  };

  const handleSubmit = async () => {
    if (answers.some(answer => answer === null)) {
      toast.error('Please answer all questions');
      return;
    }

    try {
      const response = await submitQuiz(quiz.quiz_id, answers);
      if (response.success) {
        setResult(response.result);
        toast.success(`Quiz completed! Score: ${response.result.percentage}`);
      }
    } catch (error) {
      console.error('Quiz submission failed:', error);
      toast.error(error.message || 'Failed to submit quiz');
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-gray-900">AI Quiz Generator</h1>
      
      {/* Quiz Generation Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-medium text-gray-900 mb-4">Generate New Quiz</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">Topic</label>
            <input
              type="text"
              value={formData.topic}
              onChange={(e) => setFormData({...formData, topic: e.target.value})}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm px-3 py-2"
              placeholder="e.g., JavaScript, Python, React"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Difficulty</label>
            <select
              value={formData.difficulty}
              onChange={(e) => setFormData({...formData, difficulty: e.target.value})}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm px-3 py-2"
            >
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700">Questions</label>
            <select
              value={formData.numQuestions}
              onChange={(e) => setFormData({...formData, numQuestions: parseInt(e.target.value)})}
              className="mt-1 block w-full border-gray-300 rounded-md shadow-sm px-3 py-2"
            >
              <option value={3}>3 Questions</option>
              <option value={5}>5 Questions</option>
              <option value={10}>10 Questions</option>
            </select>
          </div>
        </div>
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Quiz'}
        </button>
      </div>

      {/* Quiz Display */}
      {quiz && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">{quiz.title}</h2>
          <p className="text-sm text-gray-600 mb-6">
            Difficulty: {quiz.difficulty} | Questions: {quiz.questions.length}
          </p>
          
          <div className="space-y-6">
            {quiz.questions.map((question, qIndex) => (
              <div key={question.id} className="border-b border-gray-200 pb-6">
                <h3 className="text-lg font-medium text-gray-900 mb-3">
                  {qIndex + 1}. {question.question}
                </h3>
                <div className="space-y-2">
                  {question.options.map((option, oIndex) => (
                    <label key={oIndex} className="flex items-center">
                      <input
                        type="radio"
                        name={`question-${qIndex}`}
                        value={oIndex}
                        checked={answers[qIndex] === oIndex}
                        onChange={() => handleAnswerChange(qIndex, oIndex)}
                        className="mr-3"
                      />
                      <span>{option}</span>
                    </label>
                  ))}
                </div>
              </div>
            ))}
          </div>
          
          <button
            onClick={handleSubmit}
            className="mt-6 px-6 py-2 bg-green-600 text-white rounded-md hover:bg-green-700"
          >
            Submit Quiz
          </button>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quiz Results</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="text-center">
              <p className="text-3xl font-bold text-green-600">{result.percentage}</p>
              <p className="text-sm text-gray-600">Final Score</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-blue-600">{result.correct_answers}</p>
              <p className="text-sm text-gray-600">Correct Answers</p>
            </div>
            <div className="text-center">
              <p className="text-3xl font-bold text-gray-600">{result.total_questions}</p>
              <p className="text-sm text-gray-600">Total Questions</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default QuizGenerator;
EOF

# Create CSS styles
cat > frontend/src/styles/App.css << 'EOF'
@tailwind base;
@tailwind components;
@tailwind utilities;

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
EOF

# Create index.js
cat > frontend/src/index.js << 'EOF'
import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

const container = document.getElementById('root');
const root = createRoot(container);

root.render(<App />);
EOF

# Create public HTML
cat > frontend/public/index.html << 'EOF'
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <meta name="theme-color" content="#000000" />
    <meta name="description" content="AI Quiz Platform with Rate Limiting" />
    <title>AI Quiz Platform - Rate Limiting Demo</title>
    <script src="https://cdn.tailwindcss.com"></script>
  </head>
  <body>
    <div id="root"></div>
  </body>
</html>
EOF

# Create tests
cat > tests/test_rate_limiter.py << 'EOF'
import pytest
import time
from unittest.mock import Mock, patch
from backend.middleware.rate_limiter import RateLimiter, TokenBucket, RateLimitConfig

class TestTokenBucket:
    def test_token_bucket_allows_requests_within_limit(self):
        # Mock Redis
        redis_mock = Mock()
        redis_mock.pipeline.return_value.hmget.return_value = [None, None]
        redis_mock.pipeline.return_value.ttl.return_value = -1
        redis_mock.pipeline.return_value.execute.return_value = [[None, None], -1]
        
        bucket = TokenBucket(redis_mock)
        
        allowed, info = bucket.is_allowed('test_key', 10, 1.0, 60)
        
        assert allowed == True
        assert info['tokens_remaining'] >= 0
    
    def test_token_bucket_denies_when_no_tokens(self):
        # Mock Redis with no tokens
        redis_mock = Mock()
        redis_mock.pipeline.return_value.hmget.return_value = [0, time.time()]
        redis_mock.pipeline.return_value.ttl.return_value = 30
        redis_mock.pipeline.return_value.execute.return_value = [[0, time.time()], 30]
        
        bucket = TokenBucket(redis_mock)
        
        allowed, info = bucket.is_allowed('test_key', 10, 1.0, 60)
        
        assert allowed == False
        assert info['retry_after'] > 0

class TestRateLimiter:
    def test_rate_limiter_checks_user_tier(self):
        redis_mock = Mock()
        redis_mock.get.return_value = b'premium'
        
        rate_limiter = RateLimiter(redis_mock)
        tier = rate_limiter.get_user_tier('user123')
        
        assert tier == 'premium'
    
    def test_rate_limiter_defaults_to_free_tier(self):
        redis_mock = Mock()
        redis_mock.get.return_value = None
        
        rate_limiter = RateLimiter(redis_mock)
        tier = rate_limiter.get_user_tier('user123')
        
        assert tier == 'free'

class TestRateLimitConfig:
    def test_tier_configurations(self):
        assert 'free' in RateLimitConfig.TIERS
        assert 'premium' in RateLimitConfig.TIERS
        assert 'admin' in RateLimitConfig.TIERS
        
        assert RateLimitConfig.TIERS['free']['requests'] == 100
        assert RateLimitConfig.TIERS['premium']['requests'] == 1000
    
    def test_endpoint_configurations(self):
        assert 'ai_generate' in RateLimitConfig.ENDPOINT_LIMITS
        assert 'quiz_submit' in RateLimitConfig.ENDPOINT_LIMITS
        
        assert RateLimitConfig.ENDPOINT_LIMITS['ai_generate']['requests'] == 5
EOF

# Create integration tests
cat > tests/test_integration.py << 'EOF'
import pytest
import json
import time
from backend.app import create_app

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['REDIS_URL'] = 'redis://localhost:6379/1'  # Use test database
    return app

@pytest.fixture
def client(app):
    return app.test_client()

def test_rate_limit_endpoint_protection(client):
    """Test that endpoints are protected by rate limiting"""
    
    # Make multiple requests quickly
    responses = []
    for i in range(12):  # Exceed admin limit of 10/minute
        response = client.get('/api/rate-limit/status', headers={'X-User-ID': 'test_user'})
        responses.append(response)
        
    # Check that some requests were rate limited
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes  # Rate limit exceeded

def test_quiz_generation_rate_limit(client):
    """Test AI generation endpoint rate limiting"""
    
    # Mock Gemini API key
    with client.application.app_context():
        client.application.config['GEMINI_API_KEY'] = 'test_key'
    
    # Make requests to AI generation endpoint
    quiz_data = {
        'topic': 'Test Topic',
        'difficulty': 'easy',
        'num_questions': 3
    }
    
    responses = []
    for i in range(7):  # Exceed AI generation limit of 5/minute
        response = client.post('/api/quiz/generate', 
                              json=quiz_data,
                              headers={'X-User-ID': 'test_user'})
        responses.append(response)
        time.sleep(0.1)  # Small delay between requests
    
    # Check rate limiting kicks in
    status_codes = [r.status_code for r in responses]
    assert 429 in status_codes

def test_tier_upgrade_functionality(client):
    """Test user tier upgrade functionality"""
    
    # Upgrade user tier
    upgrade_data = {
        'user_id': 'test_user',
        'tier': 'premium'
    }
    
    response = client.post('/api/rate-limit/upgrade-tier', json=upgrade_data)
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['success'] == True
    assert 'premium' in data['message']

def test_rate_limit_headers(client):
    """Test that rate limit headers are included in responses"""
    
    response = client.get('/api/rate-limit/status', headers={'X-User-ID': 'test_user'})
    
    # Check for rate limit headers
    assert 'X-RateLimit-Limit' in response.headers
    assert 'X-RateLimit-Remaining' in response.headers
    assert 'X-RateLimit-Reset' in response.headers

def test_redis_integration(client):
    """Test Redis integration for rate limiting"""
    
    # Make a request
    response = client.get('/api/rate-limit/status', headers={'X-User-ID': 'redis_test_user'})
    assert response.status_code == 200
    
    # Check that data is stored in Redis
    with client.application.app_context():
        redis_client = client.application.redis
        
        # Check for rate limit keys
        keys = redis_client.keys('bucket:*redis_test_user*')
        assert len(keys) > 0
EOF

# Create Docker configuration
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data

  backend:
    build: ./backend
    ports:
      - "5000:5000"
    environment:
      - REDIS_URL=redis://redis:6379/0
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    depends_on:
      - redis
    volumes:
      - ./backend:/app
    command: python main.py

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:5000/api
    volumes:
      - ./frontend:/app
      - /app/node_modules

volumes:
  redis_data:
EOF

# Create backend Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["python", "main.py"]
EOF

# Create frontend Dockerfile
cat > frontend/Dockerfile << 'EOF'
FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
EOF

# Create startup script
cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting AI Quiz Platform with Rate Limiting..."

# Check if Redis is running
if ! pgrep -x "redis-server" > /dev/null; then
    echo "Starting Redis server..."
    redis-server --daemonize yes --port 6379
    sleep 2
fi

# Setup Python virtual environment
echo "Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Run tests
echo "Running tests..."
source venv/bin/activate
python -m pytest tests/ -v

# Start backend
echo "Starting backend server..."
cd backend
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Start frontend
echo "Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ Setup complete!"
echo "📊 Dashboard: http://localhost:3000"
echo "🔧 API: http://localhost:5000"
echo "📈 Rate Limits Monitor: http://localhost:3000/rate-limits"

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "Press Ctrl+C to stop all services"
wait
EOF

# Create stop script
cat > stop.sh << 'EOF'
#!/bin/bash

echo "🛑 Stopping AI Quiz Platform..."

# Kill backend
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
fi

# Kill frontend
if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null
    rm frontend.pid
fi

# Stop Redis
redis-cli shutdown 2>/dev/null

echo "✅ All services stopped"
EOF

# Make scripts executable
chmod +x start.sh stop.sh

echo "✅ Day 23 Implementation Complete!"
echo ""
echo "📁 Project Structure Created:"
echo "   ├── backend/ (Flask API with rate limiting)"
echo "   ├── frontend/ (React dashboard)"
echo "   ├── tests/ (Unit and integration tests)"
echo "   ├── docker-compose.yml (Docker setup)"
echo "   ├── start.sh (Development startup)"
echo "   └── stop.sh (Cleanup script)"
echo ""
echo "🚀 Next Steps:"
echo "1. Set your Gemini API key in backend/.env"
echo "2. Run: ./start.sh"
echo "3. Visit: http://localhost:3000"
echo ""
echo "🔧 Manual Setup (without script):"
echo "1. Start Redis: redis-server"
echo "2. Backend: cd backend && pip install -r requirements.txt && python main.py"
echo "3. Frontend: cd frontend && npm install && npm start"
echo ""
echo "📊 Test the rate limiting:"
echo "   - Generate multiple quizzes quickly"
echo "   - Monitor usage in Rate Limits dashboard"
echo "   - Try upgrading user tiers"