from ai.ml_predictor import MLPredictor
from student import Student
import traceback

try:
    print("Initializing MLPredictor...")
    predictor = MLPredictor()
    print("MLPredictor initialized successfully.")
    
    student = Student(student_id="S002", name="Test Student", email="test@test.com")
    print("Predicting for S002...")
    result = predictor.predict_performance(student, "Database Systems II")
    print("Prediction result:", result)

except Exception as e:
    print("FAILED")
    traceback.print_exc()
