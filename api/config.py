"""
API Configuration
Environment variables and settings for the FastAPI application.
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Settings:
    """Application settings and configuration."""
    
    # API Info
    API_TITLE = "Student Portal AI API"
    API_DESCRIPTION = """
    Intelligent Student Portal API with AI-powered features:
    
    - 🤖 **AI Student Advisor** - Conversational chatbot
    - 🎓 **Course Recommendations** - Personalized suggestions
    - 📊 **Sentiment Analysis** - Feedback analysis
    - 🎯 **Text Classification** - Automatic categorization
    - 📈 **ML Predictions** - Performance forecasting
    
    Built with FastAPI, OpenAI, and scikit-learn.
    """
    API_VERSION = "1.0.0"
    
    # Server
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 8000))
    RELOAD = os.getenv("ENV", "development") == "development"
    
    # Environment
    ENV = os.getenv("ENV", "development")
    MOCK_MODE = os.getenv("MOCK_MODE", "false").lower() == "true"
    
    # CORS
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN")
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:8080",
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
        "http://127.0.0.1:5173",
        "http://localhost:5000", # Common frontend port
        "https://student-portal-ai-data.vercel.app",
        "https://student-portal-ai-data-p355speby-erickmaluds-projects.vercel.app"

    ]
    if FRONTEND_ORIGIN:
        CORS_ORIGINS.append(FRONTEND_ORIGIN)
    
    # Security
    API_KEY = os.getenv("API_KEY", "dev-api-key-change-in-production")
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here-change-in-production")
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE = 100
    RATE_LIMIT_PER_HOUR = 1000
    
    # OpenAI (from existing .env)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # File paths
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STUDENTS_FILE = os.path.join(BASE_DIR, "students.json")
    FEEDBACK_FILE = os.path.join(BASE_DIR, "data", "student_feedback.json")
    
    # Logging
    LOG_LEVEL = "INFO"
    
    # API Features
    ENABLE_DOCS = True  # Set to False in production if needed
    ENABLE_CHAT = True
    ENABLE_RECOMMENDATIONS = True
    ENABLE_ANALYSIS = True
    ENABLE_STUDENTS = True
    ENABLE_PREDICTIONS = True


settings = Settings()
