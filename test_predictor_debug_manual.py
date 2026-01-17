
import sys
import os
from pathlib import Path

# Add current directory to path
sys.path.append(os.getcwd())

try:
    from ai.ml_predictor import MLPredictor
    from student import Student

    print("Initializing MLPredictor...")
    predictor = MLPredictor()
    print("MLPredictor initialized.")

    # Test with S004 data (empty)
    student = Student(
        student_id="S004",
        name="Emily Davis",
        age=21,
        course="IT",
        email="emily.davis@example.com",
        enrolled_courses=[],
        completed_courses=[],
        grades={}
    )
    
    print(f"Testing prediction for student {student.student_id}...")
    result = predictor.predict_performance(student, "Machine Learning Fundamentals")
    print("Prediction result:", result)

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
