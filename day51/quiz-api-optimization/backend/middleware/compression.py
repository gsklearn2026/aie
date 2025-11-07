import gzip
import brotli
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from backend.config.settings import settings
import time

class CompressionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = time.time()
        response = await call_next(request)
        
        if not settings.ENABLE_COMPRESSION:
            return response
            
        # Skip compression for small responses or non-text content
        if (not hasattr(response, 'body') or 
            len(response.body) < settings.COMPRESSION_MIN_SIZE):
            return response
            
        content_type = response.headers.get('content-type', '')
        if not any(ct in content_type for ct in ['json', 'text', 'javascript', 'xml']):
            return response
            
        accept_encoding = request.headers.get('accept-encoding', '').lower()
        
        original_size = len(response.body)
        compressed_body = response.body
        encoding_used = 'identity'
        
        # Try brotli first (better compression)
        if 'br' in accept_encoding:
            compressed_body = brotli.compress(response.body, quality=4)
            encoding_used = 'br'
        # Fallback to gzip
        elif 'gzip' in accept_encoding:
            compressed_body = gzip.compress(response.body)
            encoding_used = 'gzip'
            
        compressed_size = len(compressed_body)
        compression_ratio = round((1 - compressed_size / original_size) * 100, 2)
        
        # Update response
        response.headers['Content-Encoding'] = encoding_used
        response.headers['Content-Length'] = str(compressed_size)
        response.headers['X-Original-Size'] = str(original_size)
        response.headers['X-Compressed-Size'] = str(compressed_size)
        response.headers['X-Compression-Ratio'] = f"{compression_ratio}%"
        response.headers['X-Response-Time'] = f"{int((time.time() - start_time) * 1000)}ms"
        
        return Response(
            content=compressed_body,
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
