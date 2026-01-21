from fastapi import APIRouter
from fastapi.responses import JSONResponse
from ai.student_audit import run_student_audit

router = APIRouter()

@router.get("/audit/students")
async def get_student_audit_report():
    """
    Get a comprehensive AI audit of all students.
    Returns academic status, risks, and recommendations.
    """
    try:
        report = run_student_audit()
        return JSONResponse(content=report)
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "message": "Failed to run student audit"},
            status_code=500
        )
