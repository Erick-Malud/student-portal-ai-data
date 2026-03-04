"""
Student Routes - Student Profile and Academic Data (JSON-based)
Clean Portfolio Version
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Union, List
from datetime import datetime

from api.dependencies import get_data_loader
from api.middleware.auth import verify_api_key, limiter
from api.models import StudentProfile, StudentPerformance, CourseGrade

router = APIRouter(prefix="/api/students", tags=["Students"])


# ------------------------------------------------------------------
# Student Profile
# ------------------------------------------------------------------
@router.get("/{student_id}", response_model=StudentProfile)
@limiter.limit("60/minute")
async def get_student_profile(
    student_id: Union[str, int],
    request: Request,
    api_key: str = None
):
    loader = get_data_loader()
    student = loader.get_student_by_id(student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    completed = student.get("completed_courses", [])
    enrolled = student.get("courses", [])

    return StudentProfile(
        student_id=student["student_id"],
        name=student["name"],
        email=student.get("email"),
        gpa=round(sum(student.get("grades", {}).values()) / len(student.get("grades", {})), 2)
            if student.get("grades") else None,
        completed_courses=completed,
        enrolled_courses=enrolled,
        total_courses=len(completed) + len(enrolled),
        join_date="2025-09-01"
    )


# ------------------------------------------------------------------
# Student Courses
# ------------------------------------------------------------------
@router.get("/{student_id}/courses")
@limiter.limit("60/minute")
async def get_student_courses(
    student_id: Union[str, int],
    request: Request,
    status: str = "all",
    api_key: str = None
):
    loader = get_data_loader()
    student = loader.get_student_by_id(student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    grades = student.get("grades", {})
    courses = student.get("courses", [])

    results = []

    for course in courses:
        results.append({
            "course": course,
            "status": "completed" if course in grades else "enrolled",
            "grade": grades.get(course)
        })

    if status != "all":
        results = [c for c in results if c["status"] == status]

    return {
        "student_id": student_id,
        "courses": results,
        "total_courses": len(results)
    }


# ------------------------------------------------------------------
# Student Performance (Grades + GPA)
# ------------------------------------------------------------------
@router.get("/{student_id}/performance", response_model=StudentPerformance)
@limiter.limit("60/minute")
async def get_student_performance(
    student_id: Union[str, int],
    request: Request,
    api_key: str = None
):
    loader = get_data_loader()
    student = loader.get_student_by_id(student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    grades = student.get("grades", {})
    course_grades: List[CourseGrade] = []

    for course, grade in grades.items():
        course_grades.append(
            CourseGrade(course=course, grade=grade, status="completed")
        )

    for course in student.get("courses", []):
        if course not in grades:
            course_grades.append(
                CourseGrade(course=course, grade=0.0, status="in_progress")
            )

    gpa = round(sum(grades.values()) / len(grades), 2) if grades else None

    return StudentPerformance(
        student_id=student_id,
        gpa=gpa,
        total_credits=len(course_grades) * 3,
        course_grades=course_grades,
        study_time_per_week=student.get("study_time_week"),
        assignment_completion_rate=student.get("assignment_completion_rate"),
        predicted_next_semester_gpa=round(gpa + 0.1, 2) if gpa else None
    )


# ------------------------------------------------------------------
# Student Attendance
# ------------------------------------------------------------------
@router.get("/{student_id}/attendance")
@limiter.limit("60/minute")
async def get_student_attendance(
    student_id: Union[str, int],
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    loader = get_data_loader()
    student = loader.get_student_by_id(student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    attendance = student.get("attendance", {})
    total = attendance.get("total_classes", 0)
    attended = attendance.get("attended", 0)

    rate = round((attended / total) * 100, 1) if total > 0 else 0

    return {
        "student_id": student_id,
        "attendance": attendance,
        "attendance_rate": rate
    }


@router.get("/{student_id}/stats")
@limiter.limit("60/minute")
async def get_student_stats(
    student_id: Union[str, int],
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    loader = get_data_loader()
    student = loader.get_student_by_id(student_id)

    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    grades = student.get("grades", {})
    enrolled = student.get("enrolled_courses") or student.get("courses", [])
    completed = student.get("completed_courses", [])
    if not completed and grades:
        completed = list(grades.keys())
    if enrolled and completed:
        enrolled = [c for c in enrolled if c not in completed]
    attendance = student.get("attendance", {})
    academic_record = student.get("academic_record")

    if not academic_record:
        academic_record = []
        course_codes = list(dict.fromkeys(completed + enrolled))
        for code in course_codes:
            grade = grades.get(code)
            status = "completed" if grade is not None or code in completed else "enrolled"
            academic_record.append({
                "course_code": code,
                "course_name": code,
                "term": "Fall 2025",
                "status": status,
                "grade": grade,
            })

    if "summary" not in attendance:
        total = attendance.get("total_classes", 0)
        attended = attendance.get("attended", 0)
        late = attendance.get("late", 0)
        absent = attendance.get("absent", 0)
        present = attendance.get("present")
        if present is None:
            present = max(attended - late, 0)
        if total == 0 and (present or late or absent):
            total = present + late + absent
        if attended == 0 and (present or late):
            attended = present + late
        attendance.update({
            "total_classes": total,
            "attended": attended,
            "present": present,
            "summary": {
                "present": present,
                "absent": absent,
                "late": late,
            },
        })

    # GPA
    gpa = round(sum(grades.values()) / len(grades), 2) if grades else None

    # Attendance rate
    total = attendance.get("total_classes", 0)
    attended = attendance.get("attended", 0)
    attendance_rate = round((attended / total) * 100, 1) if total > 0 else 0

    return {
        "student_id": student.get("student_id", str(student_id)),
        "name": student.get("name"),
        "email": student.get("email"),
        "gpa": gpa,
        "total_courses": len(enrolled) + len(completed),
        "completed_courses": completed,
        "enrolled_courses": enrolled,
        "academic_record": academic_record,
        "attendance_rate": attendance_rate,
        "attendance": attendance,
    }


# ------------------------------------------------------------------
# List Students
# ------------------------------------------------------------------
@router.get("")
@limiter.limit("30/minute")
async def list_students(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    api_key: str = Depends(verify_api_key)
):
    loader = get_data_loader()
    students = loader.get_all_students()

    total = len(students)
    page = students[offset: offset + limit]

    return {
        "students": [
            {
                "student_id": s["student_id"],
                "name": s["name"],
                "email": s.get("email"),
                "course": s.get("course")
            } for s in page
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": offset + limit < total
    }
