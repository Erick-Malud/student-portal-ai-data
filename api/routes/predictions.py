"""
Prediction Routes - ML-Based Prediction Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from api.models import PerformancePredictionRequest, PerformancePredictionResponse
from api.middleware.auth import verify_api_key, limiter
from ai.ml_predictor import MLPredictor
from ai.student_data_loader import StudentDataLoader
from api.config import settings
from student import Student

router = APIRouter(prefix="/api/predict", tags=["Predictions"])

# Services - lazy initialization
_ml_predictor = None
_data_loader = None

def get_ml_predictor():
    """Lazy initialize ML predictor"""
    global _ml_predictor
    if _ml_predictor is None:
        try:
            _ml_predictor = MLPredictor()
        except Exception as e:
            print(f"Warning: Could not initialize MLPredictor: {e}")
            _ml_predictor = None
    return _ml_predictor

def get_data_loader():
    """Lazy initialize student data loader"""
    global _data_loader
    if _data_loader is None:
        if not settings.MOCK_MODE:
            try:
                _data_loader = StudentDataLoader(use_database=True)
            except Exception as e:
                print(f"[WARN] Could not load from database: {e}, using JSON fallback")
                _data_loader = StudentDataLoader(use_database=False)
        else:
             _data_loader = StudentDataLoader(use_database=False)

    return _data_loader


@router.post("/performance", response_model=PerformancePredictionResponse)
@limiter.limit("30/minute")
async def predict_performance(
    req_body: PerformancePredictionRequest,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Predict student performance in a course using ML models.
    
    Uses trained regression models from Month 4 to predict:
    - Expected grade
    - Risk level
    - Recommendations
    
    Rate limit: 30 requests per minute
    """
    try:
        # Load student data
        student_data = get_data_loader().get_student_by_id(req_body.student_id)
        
        if not student_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Student with ID {req_body.student_id} not found"
                }
            )
        
        # Create student object
        student = Student(
            student_id=req_body.student_id,
            name=student_data["name"],
            age=student_data.get("age", 20),
            course=student_data.get("course", "Unknown"),
            email=student_data.get("email", f"student{req_body.student_id}@example.com"),
            enrolled_courses=student_data.get("enrolled_courses", []),
            completed_courses=student_data.get("completed_courses", []),
            grades=student_data.get("grades", {})
        )
        
        # Get predictor instance
        predictor = get_ml_predictor()
        if not predictor:
            raise HTTPException(
                status_code=503,
                detail="ML Predictor service is not available (Model not loaded)"
            )

        # Make prediction
        prediction = predictor.predict_performance(student, req_body.course)
        
        # Determine risk level
        predicted_grade = prediction.get("predicted_grade", 70.0)
        if predicted_grade >= 85:
            risk_level = "low"
        elif predicted_grade >= 75:
            risk_level = "medium"
        elif predicted_grade >= 60:
            risk_level = "high"
        else:
            risk_level = "critical"
        
        # Generate recommendations
        recommendations = []
        if risk_level in ["high", "critical"]:
            recommendations.append("Consider tutoring or study group")
            recommendations.append("Review prerequisites carefully")
        elif risk_level == "medium":
            recommendations.append("Dedicate extra study time")
            recommendations.append("Attend office hours if struggling")
        else:
            recommendations.append("Course matches your skill level")
            recommendations.append("Prerequisites completed successfully")
        
        # Calculate confidence
        confidence = prediction.get("confidence", 0.75)
        
        return PerformancePredictionResponse(
            student_id=req_body.student_id,
            course=req_body.course,
            predicted_grade=predicted_grade,
            confidence=confidence,
            risk_level=risk_level,
            recommendations=recommendations
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "PREDICTION_ERROR",
                "message": f"Error predicting performance: {str(e)}"
            }
        )


@router.post("/risk")
@limiter.limit("30/minute")
async def predict_at_risk(
    student_id: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Predict if a student is at risk of dropping out or failing.
    
    Analyzes multiple factors:
    - Current GPA
    - Assignment completion rate
    - Study time
    - Engagement metrics
    
    Returns risk assessment and interventions.
    """
    try:
        student_data = get_data_loader().get_student_by_id(student_id)
        
        if not student_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Student with ID {student_id} not found"
                }
            )
        
        # Calculate risk score based on multiple factors
        risk_score = 0.0
        factors = []
        
        # GPA factor
        gpa = student_data.get("current_gpa", 80.0)
        if gpa < 60:
            risk_score += 0.4
            factors.append("Low GPA (< 60%)")
        elif gpa < 70:
            risk_score += 0.2
            factors.append("Below average GPA")
        
        # Completion rate factor
        completion_rate = student_data.get("assignment_completion_rate", 1.0)
        if completion_rate < 0.6:
            risk_score += 0.3
            factors.append("Low assignment completion rate")
        elif completion_rate < 0.8:
            risk_score += 0.1
            factors.append("Moderate assignment completion")
        
        # Study time factor
        study_time = student_data.get("study_time_week", 10.0)
        if study_time < 5:
            risk_score += 0.2
            factors.append("Insufficient study time")
        
        # Engagement factor
        engagement = student_data.get("engagement_score", 0.8)
        if engagement < 0.5:
            risk_score += 0.1
            factors.append("Low engagement")
        
        # Determine risk level
        if risk_score >= 0.7:
            risk_level = "critical"
            interventions = [
                "Immediate advisor meeting required",
                "Consider course load reduction",
                "Arrange emergency tutoring",
                "Mental health support assessment"
            ]
        elif risk_score >= 0.4:
            risk_level = "high"
            interventions = [
                "Schedule advisor check-in",
                "Recommend tutoring services",
                "Monitor progress weekly",
                "Consider study skills workshop"
            ]
        elif risk_score >= 0.2:
            risk_level = "medium"
            interventions = [
                "Provide additional resources",
                "Encourage study groups",
                "Regular progress monitoring"
            ]
        else:
            risk_level = "low"
            interventions = [
                "Continue current approach",
                "Maintain regular check-ins"
            ]
        
        return {
            "student_id": student_id,
            "risk_level": risk_level,
            "risk_score": round(risk_score, 2),
            "risk_factors": factors if factors else ["No significant risk factors identified"],
            "recommended_interventions": interventions,
            "confidence": 0.85,
            "requires_immediate_action": risk_level in ["critical", "high"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "RISK_PREDICTION_ERROR",
                "message": f"Error predicting at-risk status: {str(e)}"
            }
        )


@router.get("/features")
@limiter.limit("60/minute")
async def get_feature_importance(
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Get feature importance from ML models.
    
    Shows which factors most influence predictions:
    - GPA
    - Study time
    - Assignment completion
    - Prior course performance
    - etc.
    
    Useful for understanding what drives student success.
    """
    try:
        # Get feature importance from ML predictor
        features = get_ml_predictor().get_feature_importance()
        
        return {
            "features": features,
            "model_type": "Random Forest Regressor",
            "note": "Higher values indicate stronger influence on predictions"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "FEATURES_ERROR",
                "message": f"Error retrieving feature importance: {str(e)}"
            }
        )


@router.post("/batch")
@limiter.limit("10/minute")
async def batch_predictions(
    student_id: str,
    courses: list[str],
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Predict performance for multiple courses at once.
    
    Useful for comparing options or planning course load.
    
    Rate limit: 10 requests per minute (computationally expensive)
    Max courses: 20
    """
    try:
        if len(courses) > 20:
            raise HTTPException(
                status_code=400,
                detail={
                    "code": "TOO_MANY_COURSES",
                    "message": "Maximum 20 courses per batch request"
                }
            )
        
        # Load student
        student_data = get_data_loader().get_student_data(student_id)
        if not student_data:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Student with ID {student_id} not found"
                }
            )
        
        student = Student(
            student_id=student_id,
            name=student_data["name"],
            email=student_data.get("email", f"student{student_id}@example.com")
        )
        
        # Make predictions for all courses
        predictions = []
        for course in courses:
            try:
                pred = get_ml_predictor().predict_performance(student, course)
                predicted_grade = pred.get("predicted_grade", 70.0)
                
                predictions.append({
                    "course": course,
                    "predicted_grade": predicted_grade,
                    "confidence": pred.get("confidence", 0.75),
                    "risk_level": "low" if predicted_grade >= 85 else "medium" if predicted_grade >= 75 else "high"
                })
            except:
                predictions.append({
                    "course": course,
                    "error": "Prediction not available"
                })
        
        # Sort by predicted grade (descending)
        predictions.sort(key=lambda x: x.get("predicted_grade", 0), reverse=True)
        
        return {
            "student_id": student_id,
            "predictions": predictions,
            "total_courses": len(courses),
            "best_fit": predictions[0]["course"] if predictions else None,
            "average_predicted_grade": sum(p.get("predicted_grade", 0) for p in predictions) / len(predictions) if predictions else 0
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "BATCH_PREDICTION_ERROR",
                "message": f"Error in batch predictions: {str(e)}"
            }
        )
