import psycopg2
from psycopg2 import pool
import time
import threading
from typing import Optional, Any, Iterable
import logging
import sqlite3
import queue
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnectionPool:
    def __init__(self, minconn: int, maxconn: int, **kwargs):
        self.minconn = minconn
        self.maxconn = maxconn
        self.kwargs = kwargs
        self._pool: Optional[pool.ThreadedConnectionPool] = None
        self._lock = threading.Lock()
        self._use_fallback = False
        self._fallback_pool: Optional[queue.LifoQueue] = None
        self._fallback_total_connections = 0
        
        # Metrics
        self.total_checkouts = 0
        self.total_returns = 0
        self.total_failures = 0
        self.peak_usage = 0
        self.creation_time = time.time()
        
        self._initialize_pool()
    
    def _initialize_pool(self):
        try:
            self._pool = pool.ThreadedConnectionPool(
                self.minconn,
                self.maxconn,
                **self.kwargs
            )
            logger.info(f"✅ Database pool initialized: min={self.minconn}, max={self.maxconn}")
        except Exception as e:
            logger.warning(f"⚠️  Falling back to in-memory SQLite pool due to initialization error: {e}")
            self._use_fallback = True
            self._fallback_pool = queue.LifoQueue(maxsize=self.maxconn)
            for _ in range(self.minconn):
                conn = self._create_fallback_connection()
                self._fallback_pool.put(conn)
                self._fallback_total_connections += 1
            logger.info(f"✅ SQLite fallback pool initialized: min={self.minconn}, max={self.maxconn}")
    
    def get_connection(self, timeout: int = 30):
        start_time = time.time()
        try:
            if self._use_fallback:
                conn = self._get_fallback_connection(timeout)
            else:
                conn = self._pool.getconn()
                
                # Validate connection
                try:
                    cursor = conn.cursor()
                    cursor.execute("SELECT 1")
                    cursor.close()
                except Exception:
                    # Connection is dead, try to get a new one
                    self._pool.putconn(conn, close=True)
                    conn = self._pool.getconn()
            
            with self._lock:
                self.total_checkouts += 1
                current_usage = self.total_checkouts - self.total_returns
                self.peak_usage = max(self.peak_usage, current_usage)
            
            wait_time = time.time() - start_time
            if wait_time > 1:
                logger.warning(f"⏱️  Connection checkout took {wait_time:.2f}s")
            
            return conn
        except pool.PoolError as e:
            with self._lock:
                self.total_failures += 1
            logger.error(f"❌ Pool exhausted or error: {e}")
            raise
    
    def return_connection(self, conn):
        try:
            if self._use_fallback:
                if self._fallback_pool is None:
                    raise RuntimeError("Fallback pool not initialized")
                self._fallback_pool.put(conn, block=False)
            else:
                self._pool.putconn(conn)
            with self._lock:
                self.total_returns += 1
        except Exception as e:
            logger.error(f"❌ Error returning connection: {e}")
    
    def get_metrics(self):
        current_usage = self.total_checkouts - self.total_returns
        uptime = time.time() - self.creation_time
        
        return {
            "pool_type": "database",
            "min_connections": self.minconn,
            "max_connections": self.maxconn,
            "current_usage": current_usage,
            "available": self.maxconn - current_usage,
            "total_checkouts": self.total_checkouts,
            "total_returns": self.total_returns,
            "total_failures": self.total_failures,
            "peak_usage": self.peak_usage,
            "reuse_rate": (self.total_checkouts - self.minconn) / max(1, self.total_checkouts) * 100,
            "uptime_seconds": uptime
        }
    
    def close_all(self):
        if self._use_fallback:
            if self._fallback_pool:
                while True:
                    try:
                        conn = self._fallback_pool.get_nowait()
                    except queue.Empty:
                        break
                    try:
                        conn.close()
                    except Exception:
                        pass
            logger.info("🔒 All fallback database connections closed")
        elif self._pool:
            self._pool.closeall()
            logger.info("🔒 All database connections closed")

    def _create_fallback_connection(self):
        raw_conn = sqlite3.connect(":memory:", check_same_thread=False)
        raw_conn.row_factory = sqlite3.Row
        self._configure_sqlite_connection(raw_conn)
        self._ensure_fallback_schema(raw_conn)
        return SQLiteCompatConnection(raw_conn)

    def _get_fallback_connection(self, timeout: int):
        if self._fallback_pool is None:
            raise RuntimeError("Fallback pool not initialized")
        try:
            conn = self._fallback_pool.get(timeout=timeout)
            return conn
        except queue.Empty:
            with self._lock:
                if self._fallback_total_connections < self.maxconn:
                    conn = self._create_fallback_connection()
                    self._fallback_total_connections += 1
                    return conn
            raise pool.PoolError("SQLite fallback pool exhausted")

    @staticmethod
    def _configure_sqlite_connection(conn: sqlite3.Connection):
        try:
            conn.execute("PRAGMA foreign_keys = ON;")
            conn.execute("PRAGMA journal_mode = WAL;")
            conn.execute("PRAGMA synchronous = NORMAL;")
        except Exception as pragma_err:
            logger.debug(f"ℹ️ SQLite pragma setup skipped: {pragma_err}")

    @staticmethod
    def _ensure_fallback_schema(conn: sqlite3.Connection):
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS quizzes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    topic TEXT,
                    difficulty TEXT,
                    question TEXT,
                    options TEXT,
                    correct_answer TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
                """
            )
            conn.commit()
        finally:
            cursor.close()

# Global pool instance
db_pool: Optional[DatabaseConnectionPool] = None

def initialize_db_pool(database_url: str, minconn: int = 5, maxconn: int = 50):
    global db_pool
    
    # Parse connection string
    import urllib.parse as urlparse
    url = urlparse.urlparse(database_url)
    
    db_pool = DatabaseConnectionPool(
        minconn=minconn,
        maxconn=maxconn,
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port,
        database=url.path[1:]
    )
    return db_pool

def get_db_pool() -> DatabaseConnectionPool:
    if db_pool is None:
        raise RuntimeError("Database pool not initialized")
    return db_pool


class SQLiteCompatConnection:
    """Wrap sqlite3 connection to emulate psycopg2 interface used in the project."""

    def __init__(self, connection: sqlite3.Connection):
        self._connection = connection

    def cursor(self):
        return SQLiteCompatCursor(self._connection.cursor())

    def commit(self):
        return self._connection.commit()

    def rollback(self):
        return self._connection.rollback()

    def close(self):
        return self._connection.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc:
            self.rollback()
        else:
            self.commit()
        self.close()


class SQLiteCompatCursor:
    placeholder_pattern = re.compile(r"%s")

    def __init__(self, cursor: sqlite3.Cursor):
        self._cursor = cursor

    def execute(self, query: str, params: Optional[Iterable[Any]] = None):
        sql, normalized_params = self._normalize(query, params)
        if normalized_params is None:
            return self._cursor.execute(sql)
        return self._cursor.execute(sql, normalized_params)

    def executemany(self, query: str, seq_of_params: Iterable[Iterable[Any]]):
        sql = self.placeholder_pattern.sub("?", query)
        normalized = [tuple(params) for params in seq_of_params]
        return self._cursor.executemany(sql, normalized)

    def fetchone(self):
        return self._cursor.fetchone()

    def fetchall(self):
        return self._cursor.fetchall()

    def close(self):
        return self._cursor.close()

    @property
    def description(self):
        return self._cursor.description

    def _normalize(self, query: str, params: Optional[Iterable[Any]]):
        sql = self.placeholder_pattern.sub("?", query)
        if params is None:
            return sql, None
        if isinstance(params, tuple):
            return sql, params
        if isinstance(params, list):
            return sql, tuple(params)
        # Fall back to tuple conversion for other iterables
        return sql, tuple(params)
