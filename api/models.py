"""
Pydantic Models for Request/Response Validation
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, validator
from datetime import datetime


# ============= Chat Models =============

class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    student_id: Union[int, str] = Field(..., description="Student ID (e.g., 'S002' or 2)")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    session_id: Optional[str] = Field(None, description="Optional session ID for conversation continuity")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": 1,
                "message": "What courses should I take next?",
                "session_id": "abc-123-def"
            }
        }


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    response: str = Field(..., description="AI assistant's response")
    recommendations: Optional[List[str]] = Field(None, description="Course recommendations if applicable")
    suggested_courses: Optional[List[Dict[str, Any]]] = Field(None, description="Detailed suggested courses (Mock/Advanced mode)")
    student_summary: Optional[Dict[str, Any]] = Field(None, description="Summary of student data (Mock/Advanced mode)")
    mode: Optional[str] = Field(None, description="Mode (mock/real)")
    session_id: str = Field(..., description="Session ID for conversation")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    class Config:
        json_schema_extra = {
            "example": {
                "response": "Based on your progress, I recommend...",
                "recommendations": ["Advanced Python", "Data Structures"],
                "session_id": "abc-123-def",
                "timestamp": "2026-01-03T14:30:00Z"
            }
        }


# ============= Recommendation Models =============

class RecommendationRequest(BaseModel):
    """Request model for course recommendations."""
    student_id: Union[int, str] = Field(..., description="Student ID")
    num_recommendations: int = Field(5, ge=1, le=20, description="Number of recommendations (1-20)")
    strategy: str = Field("hybrid", pattern="^(hybrid|semantic|ml|collaborative)$")
    filters: Optional[Dict[str, List[str]]] = Field(None, description="Optional filters for difficulty/category")
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": 1,
                "num_recommendations": 5,
                "strategy": "hybrid",
                "filters": {
                    "difficulty": ["beginner", "intermediate"],
                    "category": ["programming", "data_science"]
                }
            }
        }


class CourseRecommendation(BaseModel):
    """Single course recommendation."""
    course_name: str
    score: float = Field(..., ge=0.0, le=1.0)
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: str
    difficulty: str
    prerequisites: List[str]
    description: str
    category: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Response model for recommendations."""
    recommendations: List[CourseRecommendation]
    strategy_used: str
    generated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "recommendations": [
                    {
                        "course_name": "Advanced Python",
                        "score": 0.89,
                        "confidence": 0.92,
                        "reasoning": "Similar to courses you've completed",
                        "difficulty": "intermediate",
                        "prerequisites": ["Python Fundamentals"],
                        "description": "Master advanced Python concepts",
                        "category": "programming"
                    }
                ],
                "strategy_used": "hybrid",
                "generated_at": "2026-01-03T14:30:00Z"
            }
        }


class LearningPathRequest(BaseModel):
    """Request for learning path generation."""
    student_id: Union[int, str] = Field(..., description="Student ID")
    goal: str = Field(..., min_length=5, max_length=200)
    num_courses: int = Field(8, ge=3, le=15)


# ============= Analysis Models =============

class SentimentRequest(BaseModel):
    """Request for sentiment analysis."""
    text: str = Field(..., min_length=1, max_length=5000)
    include_emotion: bool = Field(True)
    include_reasoning: bool = Field(True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "text": "I love this course! The instructor is amazing.",
                "include_emotion": True,
                "include_reasoning": True
            }
        }


class SentimentResponse(BaseModel):
    """Response for sentiment analysis."""
    sentiment: str = Field(..., pattern="^(positive|negative|neutral)$")
    score: float = Field(..., ge=-1.0, le=1.0)
    emotion: Optional[str] = None
    confidence: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None


class FeedbackItem(BaseModel):
    """Single feedback item."""
    student_id: Union[int, str] = Field(..., description="Student ID")
    text: str = Field(..., min_length=1)
    course: Optional[str] = None
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


class FeedbackAnalysisRequest(BaseModel):
    """Request for full feedback analysis."""
    feedback: List[FeedbackItem] = Field(..., min_items=1, max_items=1000)
    generate_report: bool = Field(True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "feedback": [
                    {
                        "student_id": 1,
                        "text": "Great course!",
                        "course": "Python Fundamentals",
                        "timestamp": "2026-01-03T10:00:00Z"
                    }
                ],
                "generate_report": True
            }
        }


class FeedbackAnalysisResponse(BaseModel):
    """Response for feedback analysis."""
    summary: Dict[str, Any]
    alerts: List[Dict[str, Any]]
    topics: List[Dict[str, Any]]
    report_id: Optional[str] = None
    report_url: Optional[str] = None


class TextClassificationRequest(BaseModel):
    """Request for text classification."""
    text: str = Field(..., min_length=1, max_length=5000)


class TextClassificationResponse(BaseModel):
    """Response for text classification."""
    category: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    priority: str = Field(..., pattern="^(critical|high|medium|low)$")
    requires_action: bool
    suggested_response_time: str
    reasoning: str


# ============= Student Models =============

class StudentProfile(BaseModel):
    """Student profile information."""
    student_id: Union[int, str]  # Support both integer and string IDs (e.g., "S001")
    name: str
    email: str
    gpa: Optional[float] = None
    completed_courses: List[str]
    enrolled_courses: List[str]
    total_courses: int
    join_date: Optional[str] = None


class CourseGrade(BaseModel):
    """Course grade information."""
    course: str
    grade: float
    status: str


class StudentPerformance(BaseModel):
    """Student performance metrics."""
    student_id: Union[int, str]
    gpa: Optional[float] = None
    total_credits: int
    course_grades: List[CourseGrade]
    study_time_per_week: Optional[float] = None
    assignment_completion_rate: Optional[float] = None
    predicted_next_semester_gpa: Optional[float] = None


# ============= Prediction Models =============

class PerformancePredictionRequest(BaseModel):
    """Request for performance prediction."""
    student_id: Union[int, str] = Field(..., description="Student ID")
    course: str = Field(..., min_length=1)
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": 1,
                "course": "Machine Learning Fundamentals"
            }
        }


class PerformancePredictionResponse(BaseModel):
    """Response for performance prediction."""
    student_id: Union[int, str]
    course: str
    predicted_grade: float
    confidence: float = Field(..., ge=0.0, le=1.0)
    risk_level: str = Field(..., pattern="^(low|medium|high|critical)$")
    recommendations: List[str]


# ============= Error Models =============

class ErrorDetail(BaseModel):
    """Error detail information."""
    field: Optional[str] = None
    issue: str


class ErrorResponse(BaseModel):
    """Standard error response."""
    error: Dict[str, Any] = Field(..., description="Error information")
    timestamp: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Invalid student_id",
                    "details": {
                        "field": "student_id",
                        "issue": "Must be positive integer"
                    }
                },
                "timestamp": "2026-01-03T14:30:00Z"
            }
        }


# ============= Health Check =============

class HealthResponse(BaseModel):
    """Health check response."""
    status: str = Field(..., pattern="^(healthy|unhealthy)$")
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)
    services: Dict[str, str] = Field(..., description="Status of dependent services")
