import google.generativeai as genai
import time
import threading
from collections import deque
from typing import Optional, Dict, Any
import logging
import os
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiConnection:
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp", offline_mode: Optional[bool] = None):
        self.api_key = api_key
        self.model_name = model_name
        self.creation_time = time.time()
        self.last_used = time.time()
        self.usage_count = 0
        self.is_healthy = True
        self.offline_mode = offline_mode if offline_mode is not None else self._should_use_offline_mode(api_key)
        
        self.model = None
        if not self.offline_mode:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(model_name)
            except Exception as exc:
                logger.warning(f"⚠️  Falling back to offline Gemini mode: {exc}")
                self.offline_mode = True
    
    def generate(self, prompt: str, **kwargs) -> str:
        self.last_used = time.time()
        self.usage_count += 1
        
        try:
            if self.offline_mode or self.model is None:
                return self._mock_response(prompt)
            
            response = self.model.generate_content(prompt, **kwargs)
            self.is_healthy = True
            return getattr(response, "text", str(response))
        except Exception as e:
            logger.error(f"❌ Generation error: {e}")
            self.is_healthy = False
            if not self.offline_mode:
                logger.info("🔁 Switching Gemini connection to offline mode")
                self.offline_mode = True
                return self._mock_response(prompt)
            raise
    
    def health_check(self) -> bool:
        if self.offline_mode or self.model is None:
            self.is_healthy = True
            return True
        try:
            response = self.model.generate_content("Hi")
            self.is_healthy = True
            return bool(response)
        except Exception:
            self.is_healthy = False
            return False

    def _mock_response(self, prompt: str) -> str:
        # Deterministic offline payload with five unique questions
        topic_match = re.search(r"quiz (?:question|about) (?:about )?(.+?)(?:\.|\n)", prompt, re.IGNORECASE)
        difficulty_match = re.search(r"Create a (.+?) multiple-choice", prompt, re.IGNORECASE)
        topic = topic_match.group(1).strip() if topic_match else "general knowledge"
        difficulty = difficulty_match.group(1).strip() if difficulty_match else "medium"
        question_templates = [
            f"Which statement best describes the fundamentals of {topic}?",
            f"What is a practical application of {topic} in everyday scenarios?",
            f"Which option highlights an historical milestone related to {topic}?",
            f"How does {topic} influence modern innovation or research?",
            f"Which concept would be considered an advanced idea within {topic}?"
        ]
        option_sets = [
            [
                f"Core principles of {topic}",
                f"Unrelated trivia about {topic}",
                f"Misconception about {topic}",
                f"Rare exception within {topic}"
            ],
            [
                f"Example of {topic} in daily use",
                f"Fictional account of {topic}",
                f"Obsolete practice from {topic}",
                f"Unverified myth about {topic}"
            ],
            [
                f"Major breakthrough in {topic}",
                f"Minor detail from {topic}",
                f"Unrelated global event",
                f"Speculative rumor in {topic}"
            ],
            [
                f"Contribution of {topic} to technology",
                f"Impact of {topic} on art",
                f"Irrelevant cultural reference",
                f"Myth about {topic}"
            ],
            [
                f"Advanced theory in {topic}",
                f"Introductory overview of {topic}",
                f"Outdated model in {topic}",
                f"Incorrect assumption about {topic}"
            ]
        ]
        questions = []
        for idx, template in enumerate(question_templates):
            options = option_sets[idx]
            questions.append({
                "question": template,
                "options": options,
                "correct_answer": options[0]
            })
        mock_payload = {
            "questions": questions,
            "metadata": {
                "difficulty": difficulty,
                "mode": "offline-mock",
                "model": self.model_name
            }
        }
        return json.dumps(mock_payload)

    @staticmethod
    def _should_use_offline_mode(api_key: Optional[str] = None) -> bool:
        env_flag = os.getenv("GEMINI_OFFLINE", "").lower()
        if env_flag in {"1", "true", "yes"}:
            return True
        # Default placeholder keys or missing keys should use offline mode
        default_prefixes = ("AIzaSyD", "test-", "mock-")
        key_to_check = api_key or os.getenv("GEMINI_API_KEY", "")
        if not key_to_check:
            return True
        return any(key_to_check.startswith(prefix) for prefix in default_prefixes)

class GeminiConnectionPool:
    def __init__(self, api_key: str, pool_size: int = 10, rate_limit_per_min: int = 50):
        self.api_key = api_key
        self.pool_size = pool_size
        self.rate_limit_per_min = rate_limit_per_min
        self.offline_mode = GeminiConnection._should_use_offline_mode(api_key)
        
        self._pool: deque[GeminiConnection] = deque()
        self._in_use: Dict[int, GeminiConnection] = {}
        self._lock = threading.Lock()
        self._rate_limiter = RateLimiter(rate_limit_per_min)
        
        # Metrics
        self.total_requests = 0
        self.total_rate_limited = 0
        self.total_errors = 0
        self.creation_time = time.time()
        
        self._initialize_pool()
    
    def _initialize_pool(self):
        for _ in range(self.pool_size):
            conn = GeminiConnection(self.api_key, offline_mode=self.offline_mode)
            self._pool.append(conn)
        logger.info(f"✅ Gemini AI pool initialized: size={self.pool_size}, rate_limit={self.rate_limit_per_min}/min")
    
    def get_connection(self, timeout: int = 30) -> GeminiConnection:
        start_time = time.time()
        
        # Rate limit check
        if not self._rate_limiter.allow_request():
            with self._lock:
                self.total_rate_limited += 1
            wait_time = self._rate_limiter.time_until_next_slot()
            logger.warning(f"⏱️  Rate limited, waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        # Get connection from pool
        while True:
            with self._lock:
                if self._pool:
                    conn = self._pool.popleft()
                    self._in_use[id(conn)] = conn
                    self.total_requests += 1
                    return conn
            
            # Pool exhausted, wait
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError("No available Gemini connections")
            
            time.sleep(0.1)
    
    def return_connection(self, conn: GeminiConnection):
        with self._lock:
            if id(conn) in self._in_use:
                del self._in_use[id(conn)]
                
                # Health check before returning
                if conn.is_healthy and (time.time() - conn.creation_time) < 3600:
                    self._pool.append(conn)
                else:
                    # Replace unhealthy or old connection
                    new_conn = GeminiConnection(self.api_key, offline_mode=self.offline_mode)
                    self._pool.append(new_conn)
                    logger.info("🔄 Replaced unhealthy/old connection")
    
    def get_metrics(self):
        with self._lock:
            current_usage = len(self._in_use)
            available = len(self._pool)
        
        return {
            "pool_type": "gemini_ai",
            "pool_size": self.pool_size,
            "current_usage": current_usage,
            "available": available,
            "total_requests": self.total_requests,
            "total_rate_limited": self.total_rate_limited,
            "total_errors": self.total_errors,
            "rate_limit_per_min": self.rate_limit_per_min,
            "current_rate": self._rate_limiter.get_current_rate(),
            "uptime_seconds": time.time() - self.creation_time
        }

class RateLimiter:
    def __init__(self, max_per_minute: int):
        self.max_per_minute = max_per_minute
        self.window_seconds = 60
        self.requests = deque()
        self._lock = threading.Lock()
    
    def allow_request(self) -> bool:
        with self._lock:
            now = time.time()
            
            # Remove old requests outside window
            while self.requests and self.requests[0] < now - self.window_seconds:
                self.requests.popleft()
            
            if len(self.requests) < self.max_per_minute:
                self.requests.append(now)
                return True
            
            return False
    
    def time_until_next_slot(self) -> float:
        with self._lock:
            if not self.requests:
                return 0.0
            
            oldest = self.requests[0]
            wait_time = max(0, self.window_seconds - (time.time() - oldest))
            return wait_time
    
    def get_current_rate(self) -> int:
        with self._lock:
            now = time.time()
            while self.requests and self.requests[0] < now - self.window_seconds:
                self.requests.popleft()
            return len(self.requests)

# Global pool instance
gemini_pool: Optional[GeminiConnectionPool] = None

def initialize_gemini_pool(api_key: str, pool_size: int = 10, rate_limit_per_min: int = 50):
    global gemini_pool
    gemini_pool = GeminiConnectionPool(api_key, pool_size, rate_limit_per_min)
    return gemini_pool

def get_gemini_pool() -> GeminiConnectionPool:
    if gemini_pool is None:
        raise RuntimeError("Gemini pool not initialized")
    return gemini_pool
