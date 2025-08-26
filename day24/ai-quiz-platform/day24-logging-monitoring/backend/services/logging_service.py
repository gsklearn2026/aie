import json
import aiofiles
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import structlog
from elasticsearch import AsyncElasticsearch
import redis.asyncio as redis

logger = structlog.get_logger()

class LoggingService:
    def __init__(self, elasticsearch_host: str = "http://localhost:9200", 
                 redis_host: str = "localhost", redis_port: int = 6379):
        self.es_client = None
        self.redis_client = None
        self.elasticsearch_host = elasticsearch_host
        self.redis_host = redis_host
        self.redis_port = redis_port
        
    async def initialize(self):
        """Initialize connections"""
        try:
            # Initialize Elasticsearch
            self.es_client = AsyncElasticsearch([self.elasticsearch_host])
            
            # Initialize Redis
            self.redis_client = redis.Redis(
                host=self.redis_host, 
                port=self.redis_port, 
                decode_responses=True
            )
            
            logger.info("Logging service initialized successfully")
            
        except Exception as e:
            logger.warning(
                "Failed to initialize external services, using file-based logging",
                error=str(e)
            )
    
    async def log_event(self, event_data: Dict[str, Any]):
        """Log an event with structured data"""
        # Add timestamp
        event_data["timestamp"] = datetime.utcnow().isoformat()
        
        # Log to file
        await self._log_to_file(event_data)
        
        # Log to Elasticsearch if available
        if self.es_client:
            await self._log_to_elasticsearch(event_data)
        
        # Cache recent logs in Redis
        if self.redis_client:
            await self._cache_log_entry(event_data)
        
        logger.debug("Event logged", event_type=event_data.get("event"))
    
    async def _log_to_file(self, event_data: Dict[str, Any]):
        """Write log entry to file"""
        log_entry = json.dumps(event_data) + "\n"
        
        async with aiofiles.open("../logs/app.log", "a") as f:
            await f.write(log_entry)
    
    async def _log_to_elasticsearch(self, event_data: Dict[str, Any]):
        """Index log entry in Elasticsearch"""
        try:
            index_name = f"quiz-platform-logs-{datetime.utcnow().strftime('%Y-%m-%d')}"
            await self.es_client.index(index=index_name, body=event_data)
        except Exception as e:
            logger.error("Failed to index to Elasticsearch", error=str(e))
    
    async def _cache_log_entry(self, event_data: Dict[str, Any]):
        """Cache recent log entry in Redis"""
        try:
            # Keep last 1000 log entries in Redis
            await self.redis_client.lpush("recent_logs", json.dumps(event_data))
            await self.redis_client.ltrim("recent_logs", 0, 999)
            await self.redis_client.expire("recent_logs", 3600)  # 1 hour expiry
        except Exception as e:
            logger.error("Failed to cache log entry", error=str(e))
    
    async def search_logs(self, query: str, start_time: Optional[datetime] = None,
                         end_time: Optional[datetime] = None, limit: int = 100) -> List[Dict]:
        """Search logs with optional time range"""
        logs = []
        
        # Try Elasticsearch first
        if self.es_client:
            try:
                es_query = {
                    "query": {
                        "bool": {
                            "must": [
                                {"query_string": {"query": query}}
                            ]
                        }
                    },
                    "size": limit,
                    "sort": [{"timestamp": {"order": "desc"}}]
                }
                
                if start_time or end_time:
                    time_range = {}
                    if start_time:
                        time_range["gte"] = start_time.isoformat()
                    if end_time:
                        time_range["lte"] = end_time.isoformat()
                    
                    es_query["query"]["bool"]["must"].append({
                        "range": {"timestamp": time_range}
                    })
                
                response = await self.es_client.search(
                    index="quiz-platform-logs-*",
                    body=es_query
                )
                
                logs = [hit["_source"] for hit in response["hits"]["hits"]]
                
            except Exception as e:
                logger.error("Elasticsearch search failed", error=str(e))
        
        # Fallback to Redis cache for recent logs
        if not logs and self.redis_client:
            try:
                cached_logs = await self.redis_client.lrange("recent_logs", 0, limit - 1)
                logs = [json.loads(log) for log in cached_logs]
                
                # Filter by query (simple text search)
                if query:
                    logs = [log for log in logs if query.lower() in json.dumps(log).lower()]
                
            except Exception as e:
                logger.error("Redis search failed", error=str(e))
        
        # Final fallback to file-based search
        if not logs:
            try:
                logs = await self._search_in_file(query, limit)
            except Exception as e:
                logger.error("File-based search failed", error=str(e))
        
        return logs
    
    async def get_metrics_summary(self) -> Dict[str, Any]:
        """Get logging metrics summary"""
        summary = {
            "total_logs_today": 0,
            "error_count_today": 0,
            "warning_count_today": 0,
            "avg_response_time": 0,
            "top_endpoints": [],
            "top_errors": []
        }
        
        if self.es_client:
            try:
                # Get today's logs
                today = datetime.utcnow().strftime('%Y-%m-%d')
                index_name = f"quiz-platform-logs-{today}"
                
                # Total logs today
                response = await self.es_client.count(index=index_name)
                summary["total_logs_today"] = response.get("count", 0)
                
                # Error and warning counts
                for level in ["error", "warning"]:
                    response = await self.es_client.count(
                        index=index_name,
                        body={"query": {"term": {"level": level}}}
                    )
                    summary[f"{level}_count_today"] = response.get("count", 0)
                
            except Exception as e:
                logger.error("Failed to get metrics summary", error=str(e))
        
        return summary
    
    async def _search_in_file(self, query: str, limit: int) -> List[Dict]:
        """Search logs in the log file"""
        logs = []
        try:
            async with aiofiles.open("../logs/app.log", "r") as f:
                content = await f.read()
                lines = content.strip().split('\n')
                
                # Parse each line as JSON and filter by query
                for line in reversed(lines):  # Start from most recent
                    if len(logs) >= limit:
                        break
                    try:
                        log_entry = json.loads(line)
                        # Simple text search in the entire log entry
                        if not query or query.lower() in json.dumps(log_entry).lower():
                            logs.append(log_entry)
                    except json.JSONDecodeError:
                        continue  # Skip invalid JSON lines
                        
        except Exception as e:
            logger.error("Failed to read log file", error=str(e))
        
        return logs

# Global logging service instance
logging_service = LoggingService()
