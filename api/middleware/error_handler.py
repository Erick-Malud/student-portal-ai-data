"""
Global Error Handler
Provides consistent error responses across the API.
"""

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from datetime import datetime
import traceback


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        errors.append({
            "field": " -> ".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": errors
            },
            "timestamp": datetime.now().isoformat()
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    # Log the full error (in production, use proper logging)
    print(f"Error processing request: {request.url}")
    print(f"Error: {str(exc)}")
    print(traceback.format_exc())
    
    # Don't expose internal errors in production
    error_message = str(exc) if settings.API_KEY == "dev-api-key-change-in-production" else "Internal server error"
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": error_message
            },
            "timestamp": datetime.now().isoformat()
        }
    )


async def http_exception_handler(request: Request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail if isinstance(exc.detail, dict) else {
                "code": "HTTP_ERROR",
                "message": str(exc.detail)
            },
            "timestamp": datetime.now().isoformat()
        }
    )


# Import settings here to avoid circular import
from api.config import settings
