from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import re
from typing import Optional
import structlog

logger = structlog.get_logger()

class APIVersioningMiddleware:
    def __init__(self, app, default_version: str = "v1"):
        self.app = app
        self.default_version = default_version
        self.version_pattern = re.compile(r'/api/v(\d+)/')
        
    async def __call__(self, request: Request, call_next):
        # Extract version from URL path
        version = self.extract_version_from_path(request.url.path)
        
        # Fall back to header-based versioning
        if not version:
            version = self.extract_version_from_headers(request.headers)
            
        # Use default if no version specified
        if not version:
            version = self.default_version
            
        # Add version to request state
        request.state.api_version = version
        
        # Log version usage for analytics
        await self.log_version_usage(request, version)
        
        response = await call_next(request)
        
        # Add version info to response headers
        response.headers["X-API-Version"] = version
        response.headers["X-API-Deprecated"] = str(self.is_deprecated(version))
        
        return response
    
    def extract_version_from_path(self, path: str) -> Optional[str]:
        match = self.version_pattern.search(path)
        return f"v{match.group(1)}" if match else None
    
    def extract_version_from_headers(self, headers) -> Optional[str]:
        # Check Accept header: application/vnd.quiz.v2+json
        accept = headers.get("accept", "")
        if "vnd.quiz.v" in accept:
            match = re.search(r'vnd\.quiz\.v(\d+)', accept)
            return f"v{match.group(1)}" if match else None
        
        # Check custom version header
        return headers.get("x-api-version")
    
    async def log_version_usage(self, request: Request, version: str):
        await logger.ainfo(
            "api_version_usage",
            version=version,
            endpoint=request.url.path,
            user_agent=request.headers.get("user-agent", "unknown"),
            client_ip=request.client.host if request.client else "unknown"
        )
    
    def is_deprecated(self, version: str) -> bool:
        # Mark v1 as deprecated for demonstration
        return version == "v1"
