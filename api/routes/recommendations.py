"""
Recommendation Routes - Course Recommendation Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from api.models import (
    RecommendationRequest, RecommendationResponse, CourseRecommendation,
    LearningPathRequest
)
from api.middleware.auth import verify_api_key, limiter
from ai.recommendation_engine import RecommendationEngine
from ai.course_recommender import CourseRecommender
from ai.student_data_loader import StudentDataLoader
from api.config import settings
from student import Student
import json
from datetime import datetime

router = APIRouter(prefix="/api/recommend", tags=["Recommendations"])

# Services - lazy initialization
_engine = None
_recommender = None

def get_engine():
    """Lazy initialize recommendation engine"""
    global _engine
    if _engine is None:
        try:
            _engine = RecommendationEngine()
        except Exception as e:
            print(f"Warning: Could not initialize RecommendationEngine: {e}")
            _engine = None
    return _engine

def get_recommender():
    """Lazy initialize course recommender"""
    global _recommender
    if _recommender is None:
        try:
            _recommender = CourseRecommender()
        except Exception as e:
            print(f"Warning: Could not initialize CourseRecommender: {e}")
            _recommender = None
    return _recommender


@router.post("", response_model=RecommendationResponse)
@limiter.limit("20/minute")
async def get_recommendations(
    req_body: RecommendationRequest,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Get personalized course recommendations.
    
    Uses hybrid approach combining:
    - Semantic similarity (content-based)
    - ML predictions (performance-based)
    - Collaborative filtering (pattern-based)
    
    Rate limit: 20 requests per minute
    """
    try:
        # Load student using data loader
        loader = StudentDataLoader(use_database=not settings.MOCK_MODE)
        student_data = loader.get_student_by_id(req_body.student_id)
        
        if student_data:
            # Ensure age is int
            if "age" in student_data:
                student_data["age"] = int(student_data["age"])
            student = Student.from_dict(student_data)
        else:
            # Fallback for unknown students
            student = Student(
                student_id=str(req_body.student_id),
                name=f"Student {req_body.student_id}",
                age=20,
                course="General",
                email=f"student{req_body.student_id}@example.com"
            )
        
        # Get recommendations
        recommendations = get_engine().recommend(
            student=student,
            num_recommendations=req_body.num_recommendations,
            strategy=req_body.strategy
        )
        
        # Apply filters if provided
        if req_body.filters:
            if "difficulty" in req_body.filters:
                recommendations = [
                    rec for rec in recommendations
                    if rec["course"].get("difficulty") in req_body.filters["difficulty"]
                ]
            if "category" in req_body.filters:
                recommendations = [
                    rec for rec in recommendations
                    if rec["course"].get("category") in req_body.filters["category"]
                ]
        
        # Convert to response format
        course_recs = []
        for rec in recommendations:
            course = rec["course"]
            course_recs.append(CourseRecommendation(
                course_name=course["name"],
                score=rec["score"],
                confidence=rec["confidence"],
                reasoning=rec["reasoning"],
                difficulty=course.get("difficulty", "intermediate"),
                prerequisites=course.get("prerequisites", []),
                description=course.get("description", ""),
                category=course.get("category")
            ))
        
        return RecommendationResponse(
            recommendations=course_recs,
            strategy_used=req_body.strategy,
            generated_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "RECOMMENDATION_ERROR",
                "message": f"Error generating recommendations: {str(e)}"
            }
        )


@router.get("/explain/{course_name}")
@limiter.limit("30/minute")
async def explain_course(
    course_name: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Get detailed explanation of a specific course.
    
    Provides:
    - Course description
    - Learning objectives
    - Prerequisites
    - Difficulty level
    - Category
    """
    try:
        explanation = get_recommender().explain_course(course_name)
        
        if "couldn't find" in explanation.lower():
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "COURSE_NOT_FOUND",
                    "message": f"Course '{course_name}' not found"
                }
            )
        
        return {
            "course_name": course_name,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "EXPLANATION_ERROR",
                "message": f"Error explaining course: {str(e)}"
            }
        )


@router.post("/learning-path")
@limiter.limit("10/minute")
async def generate_learning_path(
    req_body: LearningPathRequest,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Generate a personalized learning path to achieve a goal.
    
    Creates a sequence of courses that leads to the desired outcome.
    
    Rate limit: 10 requests per minute (computationally expensive)
    """
    try:
        # Load student using data loader
        loader = StudentDataLoader(use_database=not settings.MOCK_MODE)
        student_data = loader.get_student_by_id(req_body.student_id)
        
        if student_data:
            # Ensure age is int
            if "age" in student_data:
                student_data["age"] = int(student_data["age"])
            student = Student.from_dict(student_data)
        else:
            student = Student(
                student_id=str(req_body.student_id),
                name=f"Student {req_body.student_id}",
                age=20,
                course="General",
                email=f"student{req_body.student_id}@example.com"
            )
        
        # Generate learning path
        learning_path = get_recommender().plan_learning_path(
            student=student,
            goal=req_body.goal,
            num_courses=req_body.num_courses
        )
        
        return {
            "student_id": req_body.student_id,
            "goal": req_body.goal,
            "learning_path": learning_path,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "LEARNING_PATH_ERROR",
                "message": f"Error generating learning path: {str(e)}"
            }
        )


@router.get("/courses")
@limiter.limit("60/minute")
async def get_available_courses(
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Get list of all available courses.
    
    Returns the complete course catalog.
    """
    return {
        "courses": get_engine().courses,
        "total_courses": len(get_engine().courses),
        "categories": list(set(c.get("category", "general") for c in get_engine().courses))
    }


@router.post("/interactive")
@limiter.limit("15/minute")
async def interactive_recommendation(
    student_id: str,
    message: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Get conversational course recommendations.
    
    Chat with the recommender AI to discuss course options.
    """
    try:
        # Create student with temporary defaults for missing fields
        student = Student(
            student_id=student_id,
            name=f"Student {student_id}",
            age=20,  # Default age
            course="General", # Default course program
            email=f"student{student_id}@example.com"
        )
        
        # Get conversational response
        response = get_recommender().chat(student, message)
        
        return {
            "student_id": student_id,
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERACTIVE_ERROR",
                "message": f"Error in interactive recommendation: {str(e)}"
            }
        )
