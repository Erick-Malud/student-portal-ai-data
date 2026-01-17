"""
FastAPI Main Application - Student Portal API
"""
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from api.config import settings
from api.middleware.auth import limiter
from api.middleware.error_handler import (
    validation_exception_handler,
    general_exception_handler,
    http_exception_handler
)
from api.routes import chat, recommendations, analysis, students, predictions
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from fastapi.exceptions import RequestValidationError, HTTPException
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app with API Key security
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    docs_url="/docs" if settings.ENABLE_DOCS else None,
    redoc_url="/redoc" if settings.ENABLE_DOCS else None,
    # Add API Key security scheme for Swagger UI
    openapi_tags=[
        {"name": "Health", "description": "Health check endpoints"},
        {"name": "Chat", "description": "AI Student Advisor chat endpoints"},
        {"name": "Recommendations", "description": "Course recommendation endpoints"},
        {"name": "Analysis", "description": "Sentiment analysis and text classification"},
        {"name": "Students", "description": "Student profile and data endpoints"},
        {"name": "Predictions", "description": "ML-based prediction endpoints"}
    ]
)

# Define security scheme for Swagger UI
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)

# Add security scheme to OpenAPI
app.openapi_schema = None  # Reset to regenerate with security

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    from fastapi.openapi.utils import get_openapi
    openapi_schema = get_openapi(
        title=settings.API_TITLE,
        version=settings.API_VERSION,
        description=settings.API_DESCRIPTION,
        routes=app.routes,
    )
    # Add security scheme
    openapi_schema["components"]["securitySchemes"] = {
        "APIKeyHeader": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-Key",
            "description": "Enter your API key. For development use: `dev-api-key-change-in-production`"
        }
    }
    # Apply security globally
    openapi_schema["security"] = [{"APIKeyHeader": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add rate limiter state
app.state.limiter = limiter

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    logger.info("Starting up Student Portal API...")
    logger.info(f"Environment: {settings.ENV}")
    logger.info(f"Mock Mode: {settings.MOCK_MODE}")
    logger.info(f"Allowed CORS Origins: {settings.CORS_ORIGINS}")
    logger.info(f"Listening on port: {settings.PORT}")

@app.get("/health", tags=["Health"])
async def health_check():
    from datetime import datetime
    return {
        "status": "ok",
        "service": "backend",
        "timestamp": datetime.now().isoformat(),
        "environment": settings.ENV,
        "mock_mode": settings.MOCK_MODE
    }

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Register routers
if settings.ENABLE_CHAT:
    app.include_router(chat.router)
    logger.info("Chat routes enabled")

if settings.ENABLE_RECOMMENDATIONS:
    app.include_router(recommendations.router)
    logger.info("Recommendation routes enabled")

if settings.ENABLE_ANALYSIS:
    app.include_router(analysis.router)
    logger.info("Analysis routes enabled")

if settings.ENABLE_STUDENTS:
    app.include_router(students.router)
    logger.info("Student routes enabled")

if settings.ENABLE_PREDICTIONS:
    app.include_router(predictions.router)
    logger.info("Prediction routes enabled")


@app.get("/", tags=["Health"])
async def root():
    """
    API health check endpoint.
    
    Returns:
    - API name and version
    - Status
    - Available features
    """
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "status": "healthy",
        "features": {
            "chat": settings.ENABLE_CHAT,
            "recommendations": settings.ENABLE_RECOMMENDATIONS,
            "analysis": settings.ENABLE_ANALYSIS,
            "students": settings.ENABLE_STUDENTS,
            "predictions": settings.ENABLE_PREDICTIONS
        },
        "docs_url": "/docs" if settings.ENABLE_DOCS else None,
        "message": "Welcome to the AI Student Portal API"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """
    Detailed health check with service status.
    """
    try:
        # Check services
        services_status = {
            "api": "healthy",
            "database": "healthy",  # Placeholder
            "ai_services": "healthy"  # Placeholder
        }
        
        return {
            "status": "healthy",
            "services": services_status,
            "version": settings.API_VERSION
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "error": str(e)
            }
        )


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    """
    logger.info(f"Starting {settings.API_TITLE} v{settings.API_VERSION}")
    logger.info(f"Server: {settings.HOST}:{settings.PORT}")
    logger.info(f"Documentation: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info("All services initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    """
    logger.info(f"Shutting down {settings.API_TITLE}")
    # Cleanup resources if needed


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server at {settings.HOST}:{settings.PORT}")
    
    uvicorn.run(
        "api.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        log_level="info"
    )
