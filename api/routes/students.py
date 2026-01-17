"""
Student Routes - Student Profile and Data Endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Request
from api.models import StudentProfile, StudentPerformance, CourseGrade
from api.middleware.auth import verify_api_key, limiter
from ai.student_data_loader import StudentDataLoader
from student import Student
from typing import Union
import json
from datetime import datetime
from db_config import get_connection
import mysql.connector

router = APIRouter(prefix="/api/students", tags=["Students"])

# Services - lazy initialization
_data_loader = None

def get_data_loader():
    """Lazy initialize student data loader - loads from database"""
    global _data_loader
    if _data_loader is None:
        try:
            # Respect MOCK_MODE setting
            use_db = not settings.MOCK_MODE
            if use_db:
                try:
                    _data_loader = StudentDataLoader(use_database=True)
                except Exception as e:
                    print(f"[WARN] Database connection failed: {e}. Falling back to JSON.")
                    _data_loader = StudentDataLoader(use_database=False)
            else:
                _data_loader = StudentDataLoader(use_database=False)
                
            print(f"[INFO] Loaded student data (Source: {'Database' if _data_loader.use_database else 'JSON/Mock'})")
        except Exception as e:
            print(f"[ERROR] Could not initialize StudentDataLoader: {e}")
            _data_loader = None
    return _data_loader


@router.get("/{student_id}", response_model=StudentProfile)
@limiter.limit("60/minute")
async def get_student_profile(
    student_id: Union[int, str],  # Support both integer and string IDs (e.g., "S002")
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Get student profile information.
    
    Returns:
    - Basic info (name, email)
    - GPA
    - Completed courses
    - Currently enrolled courses
    - Join date
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
        
        return StudentProfile(
            student_id=student_data["student_id"],
            name=student_data["name"],
            email=student_data.get("email", f"student{student_id}@example.com"),
            gpa=student_data.get("current_gpa"),
            completed_courses=student_data.get("completed_courses", []),
            enrolled_courses=student_data.get("enrolled_courses", []),
            total_courses=len(student_data.get("completed_courses", [])) + len(student_data.get("enrolled_courses", [])),
            join_date=student_data.get("enrollment_date", "2025-09-01")
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "PROFILE_ERROR",
                "message": f"Error retrieving student profile: {str(e)}"
            }
        )


@router.get("/{student_id}/courses")
@limiter.limit("60/minute")
async def get_student_courses(
    student_id: Union[int, str],
    request: Request,
    status: str = "all",  # all, completed, enrolled
    api_key: str = Depends(verify_api_key)
):
    """
    Get student's courses.
    
    Args:
        student_id: Student ID
        status: Filter by status (all, completed, enrolled)
    
    Returns list of courses with details.
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
        
        completed = student_data.get("completed_courses", [])
        enrolled = student_data.get("enrolled_courses", [])
        
        courses = []
        
        if status in ["all", "completed"]:
            for course in completed:
                courses.append({
                    "course_name": course,
                    "status": "completed",
                    "grade": student_data.get("current_gpa", 85.0)  # Simplified
                })
        
        if status in ["all", "enrolled"]:
            for course in enrolled:
                courses.append({
                    "course_name": course,
                    "status": "enrolled",
                    "progress": 50.0  # Placeholder
                })
        
        return {
            "student_id": student_id,
            "courses": courses,
            "total_courses": len(courses),
            "filter": status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "COURSES_ERROR",
                "message": f"Error retrieving courses: {str(e)}"
            }
        )


@router.get("/{student_id}/performance", response_model=StudentPerformance)
@limiter.limit("60/minute")
async def get_student_performance(
    student_id: Union[int, str],
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Get detailed student performance metrics.
    
    Returns:
    - GPA
    - Course grades
    - Study time
    - Assignment completion rate
    - Predicted performance
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
        
        # Build course grades
        course_grades = []
        for course in student_data.get("completed_courses", []):
            course_grades.append(CourseGrade(
                course=course,
                grade=student_data.get("current_gpa", 85.0),
                status="completed"
            ))
        
        for course in student_data.get("enrolled_courses", []):
            course_grades.append(CourseGrade(
                course=course,
                grade=0.0,  # Not yet graded
                status="in_progress"
            ))
        
        return StudentPerformance(
            student_id=student_id,
            gpa=student_data.get("current_gpa"),
            total_credits=len(course_grades) * 3,  # Assume 3 credits per course
            course_grades=course_grades,
            study_time_per_week=student_data.get("study_time_week"),
            assignment_completion_rate=student_data.get("assignment_completion_rate"),
            predicted_next_semester_gpa=student_data.get("current_gpa", 0) + 0.1 if student_data.get("current_gpa") else None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "PERFORMANCE_ERROR",
                "message": f"Error retrieving performance data: {str(e)}"
            }
        )


@router.post("/{student_id}/enroll")
@limiter.limit("30/minute")
async def enroll_student(
    student_id: Union[int, str],
    course_name: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Enroll a student in a course.
    
    Args:
        student_id: Student ID
        course_name: Name of the course to enroll in
    
    Returns confirmation of enrollment.
    """
    try:
        # Load students data
        try:
            with open("students.json", "r") as f:
                students_data = json.load(f)
        except:
            students_data = []
        
        # Find student
        student_found = False
        for student in students_data:
            if student["student_id"] == student_id:
                student_found = True
                if "enrolled_courses" not in student:
                    student["enrolled_courses"] = []
                if course_name not in student["enrolled_courses"]:
                    student["enrolled_courses"].append(course_name)
                break
        
        if not student_found:
            raise HTTPException(
                status_code=404,
                detail={
                    "code": "STUDENT_NOT_FOUND",
                    "message": f"Student with ID {student_id} not found"
                }
            )
        
        # Save updated data
        with open("students.json", "w") as f:
            json.dump(students_data, f, indent=2)
        
        return {
            "message": "Enrollment successful",
            "student_id": student_id,
            "course": course_name,
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "ENROLLMENT_ERROR",
                "message": f"Error enrolling student: {str(e)}"
            }
        )


@router.get("")
@limiter.limit("30/minute")
async def list_students(
    request: Request,
    limit: int = 50,
    offset: int = 0,
    api_key: str = Depends(verify_api_key)
):
    """
    Get list of all students.
    
    Args:
        limit: Maximum number of students to return (default 50)
        offset: Number of students to skip (default 0)
    
    Returns paginated list of students.
    """
    try:
        # Load all students
        try:
            with open("students.json", "r") as f:
                students_data = json.load(f)
        except:
            students_data = []
        
        # Paginate
        total = len(students_data)
        students_page = students_data[offset:offset + limit]
        
        # Format response
        students_list = []
        for s in students_page:
            students_list.append({
                "student_id": s["student_id"],
                "name": s["name"],
                "email": s.get("email", f"student{s['student_id']}@example.com"),
                "gpa": s.get("current_gpa"),
                "completed_courses_count": len(s.get("completed_courses", [])),
                "enrolled_courses_count": len(s.get("enrolled_courses", []))
            })
        
        return {
            "students": students_list,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + limit < total
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "code": "LIST_ERROR",
                "message": f"Error listing students: {str(e)}"
            }
        )

@router.get("/{student_id}/stats")
@limiter.limit("60/minute")
async def get_student_stats(
    student_id: Union[int, str],
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Get expanded student stats: Attendance, Academic Record (Grades), and Chart Data.
    """
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # Resolve Student ID
        cursor.execute("SELECT id FROM students WHERE student_id = %s", (student_id,))
        s_row = cursor.fetchone()
        if not s_row:
             # Try lookup by ID PK if passed
            try:
                sid_int = int(student_id)
                cursor.execute("SELECT id FROM students WHERE id = %s", (sid_int,))
                s_row = cursor.fetchone()
            except:
                pass
                
            if not s_row:
                raise HTTPException(status_code=404, detail="Student not found")
        
        db_id = s_row['id']

        # 1. Academic Record (Grades history)
        cursor.execute("""
            SELECT c.name as course_name, c.course_code, e.grade, e.status, e.term
            FROM enrollments e
            JOIN courses c ON e.course_id = c.id
            WHERE e.student_id = %s
            ORDER BY e.term DESC, c.course_code ASC
        """, (db_id,))
        academic_record = cursor.fetchall()

        # Update GPA calculation based on DB
        total_points = 0
        total_courses = 0
        for record in academic_record:
            if record['grade'] is not None:
                # Assuming grade is 0-100, convert to 4.0 scale roughly
                # >90=4, >80=3, >70=2, >60=1
                g = record['grade']
                gp = 4.0 if g >= 90 else (3.0 if g >= 80 else (2.0 if g >= 70 else (1.0 if g >= 60 else 0)))
                total_points += gp
                total_courses += 1
        
        gpa = round(total_points / total_courses, 2) if total_courses > 0 else 0.0

        # 2. Attendance Stats
        cursor.execute("""
            SELECT date, status, c.course_code 
            FROM attendance a
            JOIN courses c ON a.course_id = c.id
            WHERE a.student_id = %s
            ORDER BY date ASC
        """, (db_id,))
        attendance_logs = cursor.fetchall()
        
        # Aggregate for Charts
        attendance_summary = {"present": 0, "absent": 0, "late": 0}
        for log in attendance_logs:
            if log['status'] in attendance_summary:
                attendance_summary[log['status']] += 1
        
        total_classes = sum(attendance_summary.values())
        attendance_rate = round((attendance_summary['present'] / total_classes) * 100, 1) if total_classes > 0 else 0

        return {
            "gpa": gpa,
            "academic_record": academic_record,
            "attendance": {
                "summary": attendance_summary,
                "rate": attendance_rate,
                "history": attendance_logs 
            }
        }

    except mysql.connector.Error as e:
         raise HTTPException(status_code=500, detail=str(e))
    finally:
        cursor.close()
        conn.close()
