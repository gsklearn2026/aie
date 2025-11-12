import pytest
import time
import threading
from pools.database_pool import DatabaseConnectionPool
from pools.gemini_pool import GeminiConnectionPool
import os

def test_database_pool_basic():
    """Test basic database pool operations"""
    pool = DatabaseConnectionPool(
        minconn=2,
        maxconn=5,
        user="quizuser",
        password="quizpass",
        host="localhost",
        port=5432,
        database="quizdb"
    )
    
    conn = pool.get_connection()
    assert conn is not None
    
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    result = cursor.fetchone()
    assert result[0] == 1
    cursor.close()
    
    pool.return_connection(conn)
    
    metrics = pool.get_metrics()
    assert metrics["total_checkouts"] >= 1
    assert metrics["total_returns"] >= 1
    
    pool.close_all()

def test_database_pool_concurrent():
    """Test concurrent connection usage"""
    pool = DatabaseConnectionPool(
        minconn=2,
        maxconn=10,
        user="quizuser",
        password="quizpass",
        host="localhost",
        port=5432,
        database="quizdb"
    )
    
    results = []
    
    def worker():
        try:
            conn = pool.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            pool.return_connection(conn)
            results.append(True)
        except Exception as e:
            results.append(False)
    
    threads = [threading.Thread(target=worker) for _ in range(20)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    
    assert all(results), "Some threads failed"
    
    metrics = pool.get_metrics()
    assert metrics["total_checkouts"] == 20
    assert metrics["total_returns"] == 20
    
    pool.close_all()

def test_gemini_pool_rate_limiting():
    """Test Gemini pool rate limiting"""
    api_key = os.getenv("GEMINI_API_KEY", "AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8")
    pool = GeminiConnectionPool(
        api_key=api_key,
        pool_size=3,
        rate_limit_per_min=10
    )
    
    start_time = time.time()
    requests_made = 0
    
    for i in range(15):
        try:
            conn = pool.get_connection(timeout=5)
            response = conn.generate("Say hi")
            pool.return_connection(conn)
            requests_made += 1
        except TimeoutError:
            break
    
    elapsed = time.time() - start_time
    
    # Should hit rate limit
    metrics = pool.get_metrics()
    assert metrics["total_rate_limited"] > 0, "Rate limiter should have triggered"

def test_pool_metrics_accuracy():
    """Test pool metrics accuracy"""
    pool = DatabaseConnectionPool(
        minconn=2,
        maxconn=5,
        user="quizuser",
        password="quizpass",
        host="localhost",
        port=5432,
        database="quizdb"
    )
    
    # Checkout 3 connections
    conns = []
    for _ in range(3):
        conns.append(pool.get_connection())
    
    metrics = pool.get_metrics()
    assert metrics["current_usage"] == 3
    assert metrics["available"] == 2
    
    # Return all
    for conn in conns:
        pool.return_connection(conn)
    
    metrics = pool.get_metrics()
    assert metrics["current_usage"] == 0
    assert metrics["available"] == 5
    
    pool.close_all()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
