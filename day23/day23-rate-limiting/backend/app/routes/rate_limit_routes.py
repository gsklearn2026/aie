from flask import Blueprint, request, jsonify, current_app
from middleware.rate_limiter import RateLimiter, rate_limit
import structlog

logger = structlog.get_logger()

rate_limit_bp = Blueprint('rate_limit', __name__)

@rate_limit_bp.route('/status', methods=['GET'])
@rate_limit('status')
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
