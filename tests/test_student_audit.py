import pytest
from ai.student_audit import run_student_audit, calculate_status, THRESHOLDS

def test_audit_structure():
    """
    Test that run_student_audit returns the correct structure.
    Does NOT require DB connection, but relies on data loading returning something
    or handling empty gracefully.
    """
    result = run_student_audit()
    
    # Assert top-level keys
    assert "generated_at" in result
    assert "thresholds" in result
    assert "summary" in result
    assert "students" in result
    assert "priority_interventions" in result
    
    # Assert summary keys
    summary = result["summary"]
    assert "total_students" in summary
    assert "good_standing" in summary
    assert "at_risk" in summary
    assert "critical_risk" in summary
    
    # Check thresholds
    assert result["thresholds"] == THRESHOLDS

def test_status_logic():
    """
    Test deterministic status logic function.
    """
    # Good Standing
    status, reasons = calculate_status(90, 100)
    assert status == "Good Standing"
    assert len(reasons) == 0
    
    # At Risk (Grade)
    status, reasons = calculate_status(70, 100)
    assert status == "At Risk"
    assert "Academic Struggle" in reasons
    assert "Attendance Warning" not in reasons
    
    # At Risk (Attendance)
    status, reasons = calculate_status(80, 80)
    assert status == "At Risk"
    assert "Attendance Warning" in reasons
    
    # Critical Risk
    status, reasons = calculate_status(50, 100)
    assert status == "Critical Risk"
    assert "Academic Struggle" in reasons
    
    # Combined Reasons
    status, reasons = calculate_status(50, 60)
    assert status == "Critical Risk"
    assert "Academic Struggle" in reasons
    assert "Attendance Warning" in reasons
