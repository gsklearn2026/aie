from prometheus_client import Counter, Histogram, Gauge
import time
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from backend.models.quiz import PerformanceMetric, Base
from backend.config.settings import settings

# Prometheus metrics
request_count = Counter('api_requests_total', 'Total API requests', ['method', 'endpoint', 'status'])
request_duration = Histogram('api_request_duration_seconds', 'Request duration', ['method', 'endpoint'])
response_size = Histogram('api_response_size_bytes', 'Response size', ['endpoint'])
cache_hits = Counter('cache_hits_total', 'Cache hits', ['endpoint'])
cache_misses = Counter('cache_misses_total', 'Cache misses', ['endpoint'])
compression_ratio = Gauge('compression_ratio_percent', 'Compression ratio', ['endpoint'])

engine = create_async_engine(settings.DATABASE_URL)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def record_metric(
    endpoint: str,
    method: str,
    response_time_ms: float,
    response_size_bytes: int,
    compressed_size_bytes: int,
    cache_hit: bool
):
    async with async_session() as session:
        metric = PerformanceMetric(
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time_ms,
            response_size_bytes=response_size_bytes,
            compressed_size_bytes=compressed_size_bytes,
            cache_hit=1 if cache_hit else 0
        )
        session.add(metric)
        await session.commit()
        
async def get_performance_stats(limit: int = 100):
    async with async_session() as session:
        from sqlalchemy import select, func
        
        # Average response time by endpoint
        stmt = select(
            PerformanceMetric.endpoint,
            func.avg(PerformanceMetric.response_time_ms).label('avg_response_time'),
            func.avg(PerformanceMetric.response_size_bytes).label('avg_size'),
            func.avg(PerformanceMetric.compressed_size_bytes).label('avg_compressed'),
            func.sum(PerformanceMetric.cache_hit).label('cache_hits'),
            func.count(PerformanceMetric.id).label('total_requests')
        ).group_by(PerformanceMetric.endpoint).limit(limit)
        
        result = await session.execute(stmt)
        stats = []
        
        for row in result:
            compression_saving = 0
            if row.avg_size and row.avg_compressed:
                compression_saving = round((1 - row.avg_compressed / row.avg_size) * 100, 2)
                
            stats.append({
                'endpoint': row.endpoint,
                'avg_response_time_ms': round(row.avg_response_time, 2),
                'avg_size_kb': round(row.avg_size / 1024, 2),
                'avg_compressed_kb': round(row.avg_compressed / 1024, 2),
                'compression_saving_percent': compression_saving,
                'cache_hit_rate': round((row.cache_hits / row.total_requests * 100), 2),
                'total_requests': row.total_requests
            })
            
        return stats
