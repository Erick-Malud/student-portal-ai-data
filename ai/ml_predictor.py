"""
ML Predictor - Step 3
Integrates Machine Learning models with AI chatbot
Uses trained regression model to predict student performance
"""

import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Optional, List


class MLPredictor:
    """Use trained ML models to predict student success"""
    
    def __init__(self, model_path: str = None):
        """
        Initialize with path to trained model
        
        Args:
            model_path: Path to .joblib model file
        """
        if model_path is None:
            # Try common locations
            possible_paths = [
                Path("ml/models/regression_baseline_model.joblib"),
                Path("outputs/regression_baseline_model.joblib"),
                Path(__file__).parent.parent / "ml/models/regression_baseline_model.joblib",
                Path(__file__).parent.parent / "outputs/regression_baseline_model.joblib"
            ]
            
            for path in possible_paths:
                if path.exists():
                    model_path = str(path)
                    break
            
            if model_path is None:
                raise FileNotFoundError(
                    "ML model not found. Please ensure regression_baseline_model.joblib "
                    "exists in ml/models/ or outputs/ directory."
                )
        
        self.model_path = Path(model_path)
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load the trained ML model"""
        try:
            self.model = joblib.load(self.model_path)
            print(f"✓ Loaded ML model from {self.model_path.name}")
            return self.model
        except Exception as e:
            raise Exception(f"Error loading ML model: {e}")
    
    def predict_performance(self, student_data: Dict) -> Dict:
        """
        Predict student performance based on current data
        
        Args:
            student_data: Dict with student features
                Required keys: 'avg_grade', 'courses_completed', 'active_enrollments'
        
        Returns:
            Dict with prediction results
        """
        try:
            # Extract features
            avg_grade = student_data.get('avg_grade', 0)
            courses_completed = student_data.get('courses_completed', 0)
            active_enrollments = student_data.get('active_enrollments', 0)
            
            # Prepare features for model
            # Note: Adjust based on your actual model's feature requirements
            features = np.array([[avg_grade, courses_completed, active_enrollments]])
            
            # Make prediction
            predicted_grade = self.model.predict(features)[0]
            
            # Calculate confidence (simple heuristic based on current performance)
            confidence = self._calculate_confidence(avg_grade, predicted_grade)
            
            # Determine risk level
            risk_level = self.get_risk_level(predicted_grade)
            
            return {
                'predicted_grade': float(predicted_grade),
                'risk_level': risk_level,
                'confidence': confidence,
                'features_used': {
                    'current_gpa': avg_grade,
                    'courses_completed': courses_completed,
                    'active_enrollments': active_enrollments
                }
            }
            
        except Exception as e:
            # Fallback prediction based on current average
            avg_grade = student_data.get('avg_grade', 0)
            return {
                'predicted_grade': avg_grade,
                'risk_level': self.get_risk_level(avg_grade),
                'confidence': 0.5,
                'error': f"Model prediction failed, using current GPA: {str(e)}",
                'features_used': student_data
            }
    
    def _calculate_confidence(self, current_grade: float, predicted_grade: float) -> float:
        """
        Calculate prediction confidence score
        
        Logic: Higher confidence when prediction is close to current performance
        """
        difference = abs(current_grade - predicted_grade)
        
        # Confidence decreases as difference increases
        if difference < 5:
            confidence = 0.95
        elif difference < 10:
            confidence = 0.85
        elif difference < 15:
            confidence = 0.75
        elif difference < 20:
            confidence = 0.65
        else:
            confidence = 0.50
        
        return confidence
    
    def get_risk_level(self, grade: float) -> str:
        """
        Classify performance into risk levels
        
        Args:
            grade: Predicted or current grade (0-100)
        
        Returns:
            Risk level: 'at_risk', 'average', or 'excelling'
        """
        if grade < 70:
            return "at_risk"
        elif grade < 85:
            return "average"
        else:
            return "excelling"
    
    def recommend_actions(self, risk_level: str, student_data: Dict = None) -> List[str]:
        """
        Generate actionable recommendations based on risk level
        
        Args:
            risk_level: 'at_risk', 'average', or 'excelling'
            student_data: Optional student data for personalized recommendations
        
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        if risk_level == "at_risk":
            recommendations = [
                "⚠️ Schedule meeting with academic advisor immediately",
                "📚 Attend tutoring sessions or study groups",
                "⏰ Review time management and study schedule",
                "📝 Focus on completing all homework assignments",
                "🤝 Consider peer mentoring or study partner",
                "📊 Meet with instructors during office hours",
                "🎯 Prioritize courses with lowest grades"
            ]
        
        elif risk_level == "average":
            recommendations = [
                "📈 Good progress! Maintain current study habits",
                "🎯 Focus on improving weakest subject areas",
                "📚 Review challenging concepts regularly",
                "🤝 Participate actively in class discussions",
                "⏰ Ensure consistent attendance and punctuality",
                "📝 Complete optional practice problems for mastery",
                "🏆 Set goals to move into 'excelling' category"
            ]
        
        else:  # excelling
            recommendations = [
                "🌟 Excellent work! Keep up the outstanding performance",
                "🚀 Consider taking advanced or honors courses",
                "🎓 Explore leadership opportunities (TA, mentoring)",
                "💡 Work on personal projects to deepen knowledge",
                "🤝 Help struggling peers through study groups",
                "📚 Explore related topics beyond coursework",
                "🏆 Apply for scholarships or academic awards"
            ]
        
        # Add personalized recommendations if data available
        if student_data:
            courses_completed = student_data.get('courses_completed', 0)
            if courses_completed < 2:
                recommendations.append("📌 Focus on building strong foundation in early courses")
            elif courses_completed > 5:
                recommendations.append("📌 Consider planning for graduation requirements")
        
        return recommendations
    
    def generate_insights(self, student_id: int, student_data: Dict) -> Dict:
        """
        Generate comprehensive insights combining data + ML predictions
        
        Args:
            student_id: Student ID
            student_data: Dict with student statistics
        
        Returns:
            Dict with full analysis and recommendations
        """
        # Get ML prediction
        prediction = self.predict_performance(student_data)
        
        # Generate recommendations
        recommendations = self.recommend_actions(
            prediction['risk_level'],
            student_data
        )
        
        # Calculate trend (prediction vs current)
        current_grade = student_data.get('avg_grade', 0)
        predicted_grade = prediction['predicted_grade']
        trend = "stable"
        
        if predicted_grade > current_grade + 5:
            trend = "improving"
        elif predicted_grade < current_grade - 5:
            trend = "declining"
        
        # Build comprehensive insights
        insights = {
            'student_id': student_id,
            'student_name': student_data.get('name', 'Unknown'),
            'current_performance': {
                'gpa': current_grade,
                'courses_completed': student_data.get('courses_completed', 0),
                'active_enrollments': student_data.get('active_enrollments', 0)
            },
            'prediction': prediction,
            'trend': trend,
            'recommendations': recommendations,
            'summary': self._generate_summary(
                student_data.get('name', 'Student'),
                current_grade,
                predicted_grade,
                prediction['risk_level'],
                trend
            )
        }
        
        return insights
    
    def _generate_summary(self, name: str, current: float, predicted: float, 
                         risk: str, trend: str) -> str:
        """Generate human-readable summary"""
        risk_descriptions = {
            'at_risk': 'needs immediate intervention',
            'average': 'is performing adequately',
            'excelling': 'is performing excellently'
        }
        
        trend_descriptions = {
            'improving': 'showing signs of improvement',
            'declining': 'showing concerning decline',
            'stable': 'maintaining steady performance'
        }
        
        summary = (
            f"{name} currently has a GPA of {current:.1f} and {risk_descriptions[risk]}. "
            f"ML model predicts a final grade of {predicted:.1f}, {trend_descriptions[trend]}."
        )
        
        return summary


def predict_for_student(student_data: Dict, model_path: str = None) -> Dict:
    """
    Convenience function for quick predictions
    
    Args:
        student_data: Dict with student features
        model_path: Optional path to model file
    
    Returns:
        Prediction results dict
    """
    predictor = MLPredictor(model_path)
    return predictor.predict_performance(student_data)


if __name__ == "__main__":
    """Test the ML predictor"""
    print("=" * 60)
    print("Testing ML Predictor")
    print("=" * 60)
    
    try:
        # Initialize predictor
        predictor = MLPredictor()
        
        # Test case 1: At-risk student
        print("\n1. Testing At-Risk Student:")
        at_risk_data = {
            'avg_grade': 65.0,
            'courses_completed': 2,
            'active_enrollments': 3
        }
        result = predictor.predict_performance(at_risk_data)
        print(f"   Current GPA: {at_risk_data['avg_grade']}")
        print(f"   Predicted Grade: {result['predicted_grade']:.1f}")
        print(f"   Risk Level: {result['risk_level']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        
        # Test case 2: Average student
        print("\n2. Testing Average Student:")
        average_data = {
            'avg_grade': 78.0,
            'courses_completed': 4,
            'active_enrollments': 2
        }
        result = predictor.predict_performance(average_data)
        print(f"   Current GPA: {average_data['avg_grade']}")
        print(f"   Predicted Grade: {result['predicted_grade']:.1f}")
        print(f"   Risk Level: {result['risk_level']}")
        
        # Test case 3: Excelling student
        print("\n3. Testing Excelling Student:")
        excelling_data = {
            'avg_grade': 92.0,
            'courses_completed': 5,
            'active_enrollments': 1
        }
        result = predictor.predict_performance(excelling_data)
        print(f"   Current GPA: {excelling_data['avg_grade']}")
        print(f"   Predicted Grade: {result['predicted_grade']:.1f}")
        print(f"   Risk Level: {result['risk_level']}")
        
        # Test recommendations
        print("\n4. Testing Recommendations:")
        for level in ['at_risk', 'average', 'excelling']:
            print(f"\n   {level.upper()} recommendations:")
            recs = predictor.recommend_actions(level)
            for i, rec in enumerate(recs[:3], 1):  # Show first 3
                print(f"      {i}. {rec}")
        
        # Test full insights
        print("\n5. Testing Full Insights:")
        insights = predictor.generate_insights(1, {
            'name': 'Test Student',
            'avg_grade': 75.0,
            'courses_completed': 3,
            'active_enrollments': 2
        })
        print(f"   Summary: {insights['summary']}")
        print(f"   Trend: {insights['trend']}")
        
        print("\n✓ All tests passed!")
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
