from dotenv import load_dotenv
load_dotenv()

import json
import os
from pathlib import Path
from ai.student_audit import run_student_audit

def audit_students():
    print("=" * 80)
    print("🎓 COMPREHENSIVE STUDENT ACADEMIC AUDIT (Refactored)")
    print("=" * 80)

    # 1. Run the audit logic
    print("\nRunning audit logic...")
    result = run_student_audit()
    
    summary = result["summary"]
    print(f"\nProcessing {summary['total_students']} student records...\n")

    # 2. Print Students
    for s in result["students"]:
        print(f"👤 {s['name']} ({s['student_id']})")
        print(f"   📚 Courses: {len(s['courses'])} enrolled")
        
        for c in s['courses']:
            grade_display = c['grade'] if c['grade'] is not None else "N/A"
            print(f"      - {c['course_code']} {c['course_name']}: {grade_display} ({c['status']})")
            
        print(f"   📊 Avg Grade: {s['avg_grade']} | 📅 Attendance: {s['attendance_pct']}%")
        
        # Format status string
        reason_str = ", ".join(s['reasons']) if s['reasons'] else "On Track"
        print(f"   🏷️  Status: {s['status']} ({reason_str})")
        print("-" * 40)

    # 3. Print Intervention Summary
    print("\n" + "=" * 80)
    print("🚨 INTERVENTION REQUIRED")
    print("=" * 80)
    
    interventions = result["priority_interventions"]
    
    if not interventions:
        print("✅ No students currently require intervention.")
    else:
        # Format table header
        print(f"{'PRIORITY':<10} {'STATUS':<15} {'STUDENT':<20} {'REASON':<20} {'RECOMMENDATION'}")
        print("-" * 100)
        
        for item in interventions:
            p_label = str(item['priority'])
            print(f"{p_label:<10} {item['status']:<15} {item['name']:<20} {item['primary_reason']:<20} {item['recommendation']}")

    # 4. Save Output
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)
    file_path = output_dir / "audit_report.json"
    
    with open(file_path, "w", encoding='utf-8') as f:
        json.dump(result, f, indent=2)
        
    print(f"\n✅ Audit report saved to {file_path}")

if __name__ == "__main__":
    audit_students()
