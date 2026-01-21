import datetime
from typing import Dict, List, Any
import mysql.connector

# Use relative imports if running as module, otherwise absolute for scripts
try:
    from ai.student_data_loader import StudentDataLoader
    from db_config import get_connection
except ImportError:
    import sys
    import os
    sys.path.append(os.getcwd())
    from ai.student_data_loader import StudentDataLoader
    from db_config import get_connection

# 1) Centralized risk thresholds
THRESHOLDS = {
    "AT_RISK_ATTENDANCE": 85,
    "CRITICAL_ATTENDANCE": 70,
    "AT_RISK_AVG_GRADE": 75,
    "CRITICAL_AVG_GRADE": 60
}

def calculate_status(avg_grade: float, attendance_pct: float):
    """
    Deterministic status logic based on thresholds.
    Returns: (status_string, list_of_reasons)
    """
    reasons = []
    
    # Check for Critical Risk
    is_critical_grade = avg_grade < THRESHOLDS["CRITICAL_AVG_GRADE"]
    is_critical_attendance = attendance_pct < THRESHOLDS["CRITICAL_ATTENDANCE"]
    
    if is_critical_grade or is_critical_attendance:
        status = "Critical Risk"
    else:
        # Check for At Risk
        is_risk_grade = avg_grade < THRESHOLDS["AT_RISK_AVG_GRADE"]
        is_risk_attendance = attendance_pct < THRESHOLDS["AT_RISK_ATTENDANCE"]
        
        if is_risk_grade or is_risk_attendance:
            status = "At Risk"
        else:
            status = "Good Standing"

    # Determine reasons context (applies to both Critical and At Risk)
    if avg_grade < THRESHOLDS["AT_RISK_AVG_GRADE"]:
        reasons.append("Academic Struggle")
    if attendance_pct < THRESHOLDS["AT_RISK_ATTENDANCE"]:
        reasons.append("Attendance Warning")
        
    return status, reasons

def generate_recommendation(status: str, reasons: List[str], courses_data: List[Dict]) -> str:
    """
    Generate deterministic recommendation based on status and reasons.
    """
    if status == "Good Standing":
        return "Continue current study habits; explore advanced electives."
    
    has_academic = "Academic Struggle" in reasons
    has_attendance = "Attendance Warning" in reasons
    
    if has_academic and has_attendance:
        # Combined recommendation
        weakest_course = _find_weakest_course(courses_data)
        course_action = f"tutoring for {weakest_course}" if weakest_course else "study habit review"
        return f"Urgent: Meeting with counselor for attendance plan and {course_action}."
        
    elif has_attendance:
        return "Schedule immediate meeting with student counselor regarding attendance."
        
    elif has_academic:
        weakest_course = _find_weakest_course(courses_data)
        if weakest_course:
            return f"Enroll in tutoring for {weakest_course}."
        else:
            return "Review study habits and assignment submissions."
            
    return "General academic advising session recommended."

def _find_weakest_course(courses_data: List[Dict]) -> str:
    weakest_course = None
    min_grade = 101.0
    for c in courses_data:
        g = c.get('grade')
        if g is not None and g < min_grade:
            min_grade = g
            weakest_course = c.get('course_name', 'Course')
    return weakest_course

def run_student_audit() -> Dict[str, Any]:
    """
    Main pure function to run the student audit.
    """
    # Initialize response structure
    audit_result = {
        "generated_at": datetime.datetime.now().isoformat(),
        "thresholds": THRESHOLDS,
        "summary": {
            "total_students": 0,
            "good_standing": 0,
            "at_risk": 0,
            "critical_risk": 0
        },
        "students": [],
        "priority_interventions": []
    }
    
    loader = StudentDataLoader(use_database=True)

    students_list = loader.get_all_students()
    
    audit_result["summary"]["total_students"] = len(students_list)
    
    try:
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
    except Exception:
        # Fallback if DB connection fails - return empty/default state
        # In a real production scenario, might want to raise or log
        cursor = None
        conn = None

    for student_profile in students_list:
        # Support both 'id' (DB PK) and 'student_id' (String ID)
        # Loader normalization might vary, so checking safely
        db_pk = student_profile.get('id')
        s_id = student_profile.get('student_id')
        name = student_profile.get('name', 'Unknown')
        
        enrollments_data = []
        avg_grade = 0.0
        attendance_pct = 100.0  # Default to 100 if no records found
        
        if cursor and db_pk:
            # 2. Get Enrollments & Grades
            # Using specific query as in the original script
            cursor.execute("""
                SELECT e.grade, e.status, c.course_code, c.name as course_name
                FROM enrollments e 
                JOIN courses c ON e.course_id = c.id 
                WHERE e.student_id = %s
            """, (db_pk,))
            db_enrollments = cursor.fetchall()
            
            graded_grades = []
            for e in db_enrollments:
                enrollments_data.append({
                    "course_code": e['course_code'],
                    "course_name": e['course_name'],
                    "grade": e['grade'],
                    "status": e['status']
                })
                if e['grade'] is not None:
                    graded_grades.append(e['grade'])
            
            if graded_grades:
                avg_grade = sum(graded_grades) / len(graded_grades)
            
            # 3. Get Attendance
            cursor.execute("SELECT status FROM attendance WHERE student_id = %s", (db_pk,))
            attendance_records = cursor.fetchall()
            
            total_sessions = len(attendance_records)
            if total_sessions > 0:
                present_count = sum(1 for a in attendance_records if a['status'] in ['present', 'late'])
                attendance_pct = (present_count / total_sessions) * 100
        
        # 4. Apply Rules
        status, reasons = calculate_status(avg_grade, attendance_pct)
        recommendation = generate_recommendation(status, reasons, enrollments_data)
        
        # Update summary counts
        if status == "Good Standing":
            audit_result["summary"]["good_standing"] += 1
        elif status == "At Risk":
            audit_result["summary"]["at_risk"] += 1
        elif status == "Critical Risk":
            audit_result["summary"]["critical_risk"] += 1
            
        # Build student object
        student_obj = {
            "student_id": s_id,
            "name": name,
            "courses": enrollments_data,
            "avg_grade": round(avg_grade, 2),
            "attendance_pct": round(attendance_pct, 2),
            "status": status,
            "reasons": reasons,
            "recommendation": recommendation
        }
        audit_result["students"].append(student_obj)
        
        # Add to intervention list if needed
        if status in ["At Risk", "Critical Risk"]:
            # Determine primary reason string
            if "Academic Struggle" in reasons and "Attendance Warning" in reasons:
                p_reason = "Academic + Attendance"
            elif "Academic Struggle" in reasons:
                p_reason = "Academic Struggle"
            elif "Attendance Warning" in reasons:
                p_reason = "Attendance Warning"
            else:
                p_reason = "General Risk"

            # Priority: Critical Risk = 1, At Risk = 2 (Logic: Lower number is higher priority)
            priority_score = 1 if status == "Critical Risk" else 2
            
            intervention = {
                "priority": priority_score,
                "student_id": s_id,
                "name": name,
                "status": status,
                "primary_reason": p_reason,
                "recommendation": recommendation,
                "grade_sort_key": avg_grade # Helper for sorting, can remove later or keep
            }
            audit_result["priority_interventions"].append(intervention)

    if cursor:
        cursor.close()
    if conn:
        conn.close()

    # Sort priority interventions: 
    # 1. Critical Risk (Priority 1) before At Risk (Priority 2)
    # 2. Within same priority, lower grade first
    audit_result["priority_interventions"].sort(key=lambda x: (x["priority"], x["grade_sort_key"]))
    
    # Cleanup helper keys
    for item in audit_result["priority_interventions"]:
        item.pop("grade_sort_key", None)
        
    return audit_result
