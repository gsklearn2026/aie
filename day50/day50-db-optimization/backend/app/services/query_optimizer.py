from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Dict, List, Any
import time

class QueryOptimizer:
    """Service for analyzing and optimizing database queries"""
    
    def __init__(self, db: Session):
        self.db = db
        self.query_log = []
    
    def analyze_query(self, query_str: str) -> Dict[str, Any]:
        """Analyze query execution plan"""
        explain_query = f"EXPLAIN ANALYZE {query_str}"
        
        try:
            result = self.db.execute(text(explain_query))
            plan = [row[0] for row in result]
            
            analysis = {
                'has_seq_scan': any('Seq Scan' in line for line in plan),
                'has_index_scan': any('Index Scan' in line for line in plan),
                'execution_time': self._extract_execution_time(plan),
                'plan': plan
            }
            
            return analysis
        except Exception as e:
            return {'error': str(e)}
    
    def _extract_execution_time(self, plan: List[str]) -> float:
        """Extract execution time from EXPLAIN ANALYZE output"""
        for line in plan:
            if 'Execution Time:' in line:
                time_str = line.split(':')[1].strip().split()[0]
                return float(time_str)
        return 0.0
    
    def get_table_indexes(self, table_name: str) -> List[Dict[str, Any]]:
        """Get all indexes for a table"""
        query = text("""
            SELECT 
                indexname,
                indexdef
            FROM pg_indexes
            WHERE tablename = :table_name
        """)
        
        result = self.db.execute(query, {'table_name': table_name})
        return [{'name': row[0], 'definition': row[1]} for row in result]
    
    def check_index_usage(self) -> List[Dict[str, Any]]:
        """Check which indexes are being used"""
        query = text("""
            SELECT 
                schemaname,
                relname as tablename,
                indexrelname as indexname,
                idx_scan,
                idx_tup_read,
                idx_tup_fetch
            FROM pg_stat_user_indexes
            ORDER BY idx_scan DESC
        """)
        
        result = self.db.execute(query)
        return [
            {
                'schema': row[0],
                'table': row[1],
                'index': row[2],
                'scans': row[3],
                'tuples_read': row[4],
                'tuples_fetched': row[5]
            }
            for row in result
        ]
    
    def get_slow_queries(self, threshold_ms: int = 100) -> List[Dict[str, Any]]:
        """Get queries slower than threshold"""
        return [
            q for q in self.query_log 
            if q['duration'] > threshold_ms / 1000.0
        ]
    
    def log_query(self, query: str, duration: float):
        """Log query for performance analysis"""
        self.query_log.append({
            'query': query[:100],
            'duration': duration,
            'timestamp': time.time()
        })
        
        # Keep only last 1000 queries
        if len(self.query_log) > 1000:
            self.query_log = self.query_log[-1000:]
