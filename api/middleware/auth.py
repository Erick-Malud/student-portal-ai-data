"""
Authentication and Rate Limiting Middleware
"""

from fastapi import Header, HTTPException, Request
from fastapi.security import APIKeyHeader
from slowapi import Limiter
from slowapi.util import get_remote_address
from api.config import settings
from typing import Optional


# Rate limiter
limiter = Limiter(key_func=get_remote_address)


# API Key header
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(x_api_key: Optional[str] = Header(None)):
    """
    Verify API key from request header.
    
    Args:
        x_api_key: API key from X-API-Key header
    
    Raises:
        HTTPException: If API key is missing or invalid
    """
    # In development, allow requests without API key
    if settings.API_KEY == "dev-api-key-change-in-production" and x_api_key is None:
        return "dev-mode"
    
    if x_api_key is None:
        raise HTTPException(
            status_code=401,
            detail={
                "code": "MISSING_API_KEY",
                "message": "API key is required. Include 'X-API-Key' header."
            }
        )
    
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=403,
            detail={
                "code": "INVALID_API_KEY",
                "message": "Invalid API key provided."
            }
        )
    
    return x_api_key


def get_rate_limit_key(request: Request) -> str:
    """
    Get unique key for rate limiting.
    Uses API key if provided, otherwise uses IP address.
    """
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key}"
    return f"ip:{get_remote_address(request)}"
