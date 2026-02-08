"""
Recommendation Routes - Course Recommendation Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request

from api.dependencies import get_data_loader
from api.models import (
    RecommendationRequest,
    RecommendationResponse,
    CourseRecommendation,
    LearningPathRequest,
)
from api.middleware.auth import verify_api_key, limiter
from ai.recommendation_engine import RecommendationEngine
from ai.course_recommender import CourseRecommender
from student import Student
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
    api_key: str = Depends(verify_api_key),
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
        # ✅ Load student via single source of truth (DB or JSON handled inside loader)
        student_data = get_data_loader().get_student_by_id(req_body.student_id)

        if student_data:
            # Ensure age is int (defensive)
            if "age" in student_data and student_data["age"] is not None:
                student_data["age"] = int(student_data["age"])
            student = Student.from_dict(student_data)
        else:
            # Fallback for unknown students
            student = Student(
                student_id=str(req_body.student_id),
                name=f"Student {req_body.student_id}",
                age=20,
                course="General",
                email=f"student{req_body.student_id}@example.com",
            )

        engine = get_engine()
        if engine is None:
            raise Exception("RecommendationEngine is not available")

        # Get recommendations
        recommendations = engine.recommend(
            student=student,
            num_recommendations=req_body.num_recommendations,
            strategy=req_body.strategy,
        )

        # Apply filters if provided
        if req_body.filters:
            if "difficulty" in req_body.filters:
                recommendations = [
                    rec
                    for rec in recommendations
                    if rec["course"].get("difficulty") in req_body.filters["difficulty"]
                ]
            if "category" in req_body.filters:
                recommendations = [
                    rec
                    for rec in recommendations
                    if rec["course"].get("category") in req_body.filters["category"]
                ]

        # Convert to response format
        course_recs = []
        for rec in recommendations:
            course = rec["course"]
            course_recs.append(
                CourseRecommendation(
                    course_name=course["name"],
                    score=rec["score"],
                    confidence=rec["confidence"],
                    reasoning=rec["reasoning"],
                    difficulty=course.get("difficulty", "intermediate"),
                    prerequisites=course.get("prerequisites", []),
                    description=course.get("description", ""),
                    category=course.get("category"),
                )
            )

        return RecommendationResponse(
            recommendations=course_recs,
            strategy_used=req_body.strategy,
            generated_at=datetime.now(),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "RECOMMENDATION_ERROR",
                "message": f"Error generating recommendations: {str(e)}",
            },
        )


@router.get("/explain/{course_name}")
@limiter.limit("30/minute")
async def explain_course(
    course_name: str,
    request: Request,
    api_key: str = Depends(verify_api_key),
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
        recommender = get_recommender()
        if recommender is None:
            raise Exception("CourseRecommender is not available")

        explanation = recommender.explain_course(course_name)

        if "couldn't find" in explanation.lower():
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "COURSE_NOT_FOUND",
                    "message": f"Course '{course_name}' not found",
                },
            )

        return {
            "course_name": course_name,
            "explanation": explanation,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "EXPLANATION_ERROR",
                "message": f"Error explaining course: {str(e)}",
            },
        )


@router.post("/learning-path")
@limiter.limit("10/minute")
async def generate_learning_path(
    req_body: LearningPathRequest,
    request: Request,
    api_key: str = Depends(verify_api_key),
):
    """
    Generate a personalized learning path to achieve a goal.

    Creates a sequence of courses that leads to the desired outcome.

    Rate limit: 10 requests per minute (computationally expensive)
    """
    try:
        # ✅ Load student via single source of truth
        student_data = get_data_loader().get_student_by_id(req_body.student_id)

        if student_data:
            if "age" in student_data and student_data["age"] is not None:
                student_data["age"] = int(student_data["age"])
            student = Student.from_dict(student_data)
        else:
            student = Student(
                student_id=str(req_body.student_id),
                name=f"Student {req_body.student_id}",
                age=20,
                course="General",
                email=f"student{req_body.student_id}@example.com",
            )

        recommender = get_recommender()
        if recommender is None:
            raise Exception("CourseRecommender is not available")

        learning_path = recommender.plan_learning_path(
            student=student,
            goal=req_body.goal,
            num_courses=req_body.num_courses,
        )

        return {
            "student_id": req_body.student_id,
            "goal": req_body.goal,
            "learning_path": learning_path,
            "generated_at": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "LEARNING_PATH_ERROR",
                "message": f"Error generating learning path: {str(e)}",
            },
        )


@router.get("/courses")
@limiter.limit("60/minute")
async def get_available_courses(
    request: Request,
    api_key: str = Depends(verify_api_key),
):
    """
    Get list of all available courses.

    Returns the complete course catalog.
    """
    engine = get_engine()
    if engine is None:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ENGINE_NOT_AVAILABLE",
                "message": "RecommendationEngine is not available",
            },
        )

    return {
        "courses": engine.courses,
        "total_courses": len(engine.courses),
        "categories": list(set(c.get("category", "general") for c in engine.courses)),
    }


@router.post("/interactive")
@limiter.limit("15/minute")
async def interactive_recommendation(
    student_id: str,
    message: str,
    request: Request,
    api_key: str = Depends(verify_api_key),
):
    """
    Get conversational course recommendations.

    Chat with the recommender AI to discuss course options.
    """
    try:
        recommender = get_recommender()
        if recommender is None:
            raise Exception("CourseRecommender is not available")

        # Keep simple defaults here (interactive mode)
        student = Student(
            student_id=student_id,
            name=f"Student {student_id}",
            age=20,
            course="General",
            email=f"student{student_id}@example.com",
        )

        response = recommender.chat(student, message)

        return {
            "student_id": student_id,
            "message": message,
            "response": response,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "INTERACTIVE_ERROR",
                "message": f"Error in interactive recommendation: {str(e)}",
            },
        )
