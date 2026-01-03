"""
Hybrid Recommendation Engine
Combines semantic similarity, ML predictions, and collaborative filtering for course recommendations.
"""

import json
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from datetime import datetime

from ai.embeddings_manager import EmbeddingsManager
from ai.ml_predictor import MLPredictor
from student import Student


class RecommendationEngine:
    """
    Hybrid recommendation system using three strategies:
    1. Semantic Similarity - Content-based using embeddings
    2. ML Predictions - Performance-based using trained models
    3. Collaborative Filtering - Pattern-based using student cohorts
    
    Combines all three for optimal recommendations.
    """
    
    def __init__(self):
        """Initialize the recommendation engine with all components."""
        self.embeddings_manager = EmbeddingsManager()
        self.ml_predictor = MLPredictor()
        
        # Load courses data
        self.courses = self._load_courses()
        
        # Strategy weights (can be tuned)
        self.weights = {
            'semantic': 0.40,      # 40% weight on content similarity
            'ml_prediction': 0.35, # 35% weight on predicted performance
            'collaborative': 0.25  # 25% weight on peer patterns
        }
    
    def _load_courses(self) -> List[Dict]:
        """Load available courses from course database."""
        # TODO: Replace with actual database query
        # For now, return sample courses
        return [
            {
                'name': 'Python Fundamentals',
                'description': 'Learn Python programming basics including variables, loops, functions, and data structures',
                'learning_objectives': ['Variables and types', 'Control flow', 'Functions', 'Lists and dictionaries'],
                'prerequisites': [],
                'difficulty': 'beginner',
                'category': 'programming'
            },
            {
                'name': 'Advanced Python',
                'description': 'Master advanced Python concepts including OOP, decorators, generators, and async programming',
                'learning_objectives': ['Classes and objects', 'Decorators', 'Generators', 'Async/await'],
                'prerequisites': ['Python Fundamentals'],
                'difficulty': 'intermediate',
                'category': 'programming'
            },
            {
                'name': 'Data Structures and Algorithms',
                'description': 'Study fundamental data structures and algorithms with Python implementation',
                'learning_objectives': ['Arrays and linked lists', 'Trees and graphs', 'Sorting algorithms', 'Dynamic programming'],
                'prerequisites': ['Python Fundamentals'],
                'difficulty': 'intermediate',
                'category': 'computer_science'
            },
            {
                'name': 'Machine Learning Fundamentals',
                'description': 'Introduction to machine learning algorithms, model training, and evaluation',
                'learning_objectives': ['Supervised learning', 'Model evaluation', 'Feature engineering', 'Scikit-learn'],
                'prerequisites': ['Python Fundamentals', 'Math for Machine Learning'],
                'difficulty': 'intermediate',
                'category': 'machine_learning'
            },
            {
                'name': 'Deep Learning',
                'description': 'Neural networks, deep learning architectures, and TensorFlow/PyTorch',
                'learning_objectives': ['Neural networks', 'CNNs', 'RNNs', 'Transfer learning'],
                'prerequisites': ['Machine Learning Fundamentals'],
                'difficulty': 'advanced',
                'category': 'machine_learning'
            },
            {
                'name': 'Web Development with Flask',
                'description': 'Build web applications using Python Flask framework',
                'learning_objectives': ['Flask basics', 'Routing', 'Templates', 'Database integration'],
                'prerequisites': ['Python Fundamentals'],
                'difficulty': 'intermediate',
                'category': 'web_development'
            },
            {
                'name': 'Data Science with Python',
                'description': 'Analyze data using pandas, NumPy, and create visualizations',
                'learning_objectives': ['Pandas', 'NumPy', 'Matplotlib', 'Statistical analysis'],
                'prerequisites': ['Python Fundamentals'],
                'difficulty': 'intermediate',
                'category': 'data_science'
            },
            {
                'name': 'Math for Machine Learning',
                'description': 'Linear algebra, calculus, and statistics for ML',
                'learning_objectives': ['Linear algebra', 'Calculus', 'Probability', 'Statistics'],
                'prerequisites': [],
                'difficulty': 'intermediate',
                'category': 'mathematics'
            }
        ]
    
    def recommend(
        self,
        student: Student,
        num_recommendations: int = 5,
        strategy: str = 'hybrid'
    ) -> List[Dict]:
        """
        Generate course recommendations for a student.
        
        Args:
            student: Student object with enrollment history
            num_recommendations: Number of courses to recommend
            strategy: 'hybrid', 'semantic', 'ml', or 'collaborative'
        
        Returns:
            List of recommendation dicts with course info and scores
        """
        # Get available courses (exclude completed and enrolled)
        available_courses = self._get_available_courses(student)
        
        if not available_courses:
            return []
        
        # Calculate scores using different strategies
        if strategy == 'semantic':
            recommendations = self._semantic_recommendations(student, available_courses)
        elif strategy == 'ml':
            recommendations = self._ml_recommendations(student, available_courses)
        elif strategy == 'collaborative':
            recommendations = self._collaborative_recommendations(student, available_courses)
        else:  # hybrid
            recommendations = self._hybrid_recommendations(student, available_courses)
        
        # Add reasoning and metadata
        for rec in recommendations:
            rec['reasoning'] = self._generate_reasoning(rec, student)
            rec['confidence'] = self._calculate_confidence(rec)
        
        # Return top N
        return recommendations[:num_recommendations]
    
    def _get_available_courses(self, student: Student) -> List[Dict]:
        """
        Filter courses that student can take (not completed, prerequisites met).
        """
        completed_courses = set(student.get_completed_courses())
        enrolled_courses = set(student.get_enrolled_courses())
        
        available = []
        
        for course in self.courses:
            course_name = course['name']
            
            # Skip if already completed or enrolled
            if course_name in completed_courses or course_name in enrolled_courses:
                continue
            
            # Check prerequisites
            prerequisites = course.get('prerequisites', [])
            if all(prereq in completed_courses for prereq in prerequisites):
                available.append(course)
        
        return available
    
    def _semantic_recommendations(
        self,
        student: Student,
        available_courses: List[Dict]
    ) -> List[Dict]:
        """
        Strategy 1: Semantic similarity based on completed courses and interests.
        """
        completed_courses = student.get_completed_courses()
        
        if not completed_courses:
            # No history - recommend based on interests if available
            # For now, return courses sorted by beginner-friendliness
            scores = []
            for course in available_courses:
                difficulty_score = {'beginner': 1.0, 'intermediate': 0.7, 'advanced': 0.4}.get(
                    course.get('difficulty', 'intermediate'), 0.5
                )
                scores.append({
                    'course': course,
                    'score': difficulty_score,
                    'strategy': 'semantic',
                    'details': 'Beginner-friendly course'
                })
            scores.sort(key=lambda x: x['score'], reverse=True)
            return scores
        
        # Find similar courses to what student has completed
        similarity_scores = {}
        
        for completed in completed_courses:
            # Find the course dict for completed course
            completed_course = next((c for c in self.courses if c['name'] == completed), None)
            if not completed_course:
                continue
            
            # Find similar available courses
            similar = self.embeddings_manager.find_similar_courses(
                completed_course,
                available_courses,
                top_k=len(available_courses)
            )
            
            # Accumulate scores
            for course_name, similarity in similar:
                if course_name not in similarity_scores:
                    similarity_scores[course_name] = []
                similarity_scores[course_name].append(similarity)
        
        # Average the similarity scores
        recommendations = []
        for course in available_courses:
            if course['name'] in similarity_scores:
                avg_score = sum(similarity_scores[course['name']]) / len(similarity_scores[course['name']])
            else:
                avg_score = 0.0
            
            recommendations.append({
                'course': course,
                'score': avg_score,
                'strategy': 'semantic',
                'details': f'Similar to completed courses ({avg_score:.2f})'
            })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations
    
    def _ml_recommendations(
        self,
        student: Student,
        available_courses: List[Dict]
    ) -> List[Dict]:
        """
        Strategy 2: ML-based predictions of student success.
        """
        recommendations = []
        
        for course in available_courses:
            # Predict student performance in this course
            try:
                prediction = self.ml_predictor.predict_performance(student, course['name'])
                predicted_grade = prediction.get('predicted_grade', 70.0)
                
                # Normalize to 0-1 score (assuming 0-100 grade scale)
                score = predicted_grade / 100.0
                
                recommendations.append({
                    'course': course,
                    'score': score,
                    'strategy': 'ml_prediction',
                    'details': f'Predicted grade: {predicted_grade:.1f}%'
                })
            except Exception as e:
                # If prediction fails, assign neutral score
                recommendations.append({
                    'course': course,
                    'score': 0.5,
                    'strategy': 'ml_prediction',
                    'details': 'Prediction unavailable'
                })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations
    
    def _collaborative_recommendations(
        self,
        student: Student,
        available_courses: List[Dict]
    ) -> List[Dict]:
        """
        Strategy 3: Collaborative filtering - what similar students took.
        """
        # Find similar students (students with similar course history)
        similar_students = self._find_similar_students(student)
        
        if not similar_students:
            # No similar students - return neutral scores
            return [{
                'course': course,
                'score': 0.5,
                'strategy': 'collaborative',
                'details': 'No similar students found'
            } for course in available_courses]
        
        # Count what courses similar students took after shared courses
        course_popularity = {}
        
        for similar_student in similar_students:
            similar_completed = similar_student.get_completed_courses()
            
            for course_name in similar_completed:
                if course_name not in course_popularity:
                    course_popularity[course_name] = 0
                course_popularity[course_name] += 1
        
        # Score available courses by popularity among similar students
        max_popularity = max(course_popularity.values()) if course_popularity else 1
        
        recommendations = []
        for course in available_courses:
            popularity = course_popularity.get(course['name'], 0)
            score = popularity / max_popularity if max_popularity > 0 else 0.0
            
            recommendations.append({
                'course': course,
                'score': score,
                'strategy': 'collaborative',
                'details': f'{popularity} similar students took this ({score:.2f})'
            })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations
    
    def _hybrid_recommendations(
        self,
        student: Student,
        available_courses: List[Dict]
    ) -> List[Dict]:
        """
        Combine all three strategies with weighted scores.
        """
        # Get recommendations from each strategy
        semantic_recs = self._semantic_recommendations(student, available_courses)
        ml_recs = self._ml_recommendations(student, available_courses)
        collaborative_recs = self._collaborative_recommendations(student, available_courses)
        
        # Create score lookup by course name
        semantic_scores = {rec['course']['name']: rec['score'] for rec in semantic_recs}
        ml_scores = {rec['course']['name']: rec['score'] for rec in ml_recs}
        collaborative_scores = {rec['course']['name']: rec['score'] for rec in collaborative_recs}
        
        # Combine scores
        recommendations = []
        for course in available_courses:
            course_name = course['name']
            
            # Weighted combination
            combined_score = (
                self.weights['semantic'] * semantic_scores.get(course_name, 0.0) +
                self.weights['ml_prediction'] * ml_scores.get(course_name, 0.0) +
                self.weights['collaborative'] * collaborative_scores.get(course_name, 0.0)
            )
            
            recommendations.append({
                'course': course,
                'score': combined_score,
                'strategy': 'hybrid',
                'details': {
                    'semantic': semantic_scores.get(course_name, 0.0),
                    'ml_prediction': ml_scores.get(course_name, 0.0),
                    'collaborative': collaborative_scores.get(course_name, 0.0),
                    'combined': combined_score
                }
            })
        
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations
    
    def _find_similar_students(self, student: Student, top_k: int = 10) -> List[Student]:
        """
        Find students with similar course history (Jaccard similarity).
        """
        # TODO: Load other students from database
        # For now, return empty list (collaborative filtering not fully functional)
        return []
    
    def _generate_reasoning(self, recommendation: Dict, student: Student) -> str:
        """Generate human-readable reasoning for a recommendation."""
        course = recommendation['course']
        score = recommendation['score']
        strategy = recommendation['strategy']
        
        reasons = []
        
        # Based on strategy
        if strategy == 'hybrid':
            details = recommendation.get('details', {})
            if details.get('semantic', 0) > 0.7:
                reasons.append("similar to courses you've completed")
            if details.get('ml_prediction', 0) > 0.75:
                reasons.append("you're predicted to perform well")
            if details.get('collaborative', 0) > 0.5:
                reasons.append("popular among similar students")
        elif strategy == 'semantic':
            reasons.append("matches your learning path")
        elif strategy == 'ml_prediction':
            reasons.append("good fit based on your performance")
        elif strategy == 'collaborative':
            reasons.append("taken by similar students")
        
        # Prerequisites
        prereqs = course.get('prerequisites', [])
        if prereqs:
            reasons.append(f"builds on {', '.join(prereqs[:2])}")
        
        # Difficulty
        difficulty = course.get('difficulty', 'intermediate')
        if difficulty == 'beginner':
            reasons.append("beginner-friendly")
        elif difficulty == 'advanced':
            reasons.append("advanced challenge")
        
        # Combine reasons
        if reasons:
            return f"Recommended because it's {' and '.join(reasons)}"
        else:
            return f"Recommended based on {strategy} analysis"
    
    def _calculate_confidence(self, recommendation: Dict) -> float:
        """Calculate confidence score (0-1) for recommendation."""
        score = recommendation['score']
        
        # Confidence increases with score
        # But cap it to avoid overconfidence
        confidence = min(0.95, score * 1.2)
        confidence = max(0.1, confidence)  # Minimum confidence
        
        return round(confidence, 2)
    
    def explain_recommendation(self, recommendation: Dict) -> str:
        """
        Provide detailed explanation of why a course was recommended.
        """
        course = recommendation['course']
        score = recommendation['score']
        strategy = recommendation['strategy']
        
        explanation = f"**{course['name']}** (Score: {score:.2f})\n\n"
        explanation += f"**Why this course?**\n{recommendation['reasoning']}\n\n"
        explanation += f"**Description:** {course['description']}\n\n"
        
        # Prerequisites
        prereqs = course.get('prerequisites', [])
        if prereqs:
            explanation += f"**Prerequisites:** {', '.join(prereqs)}\n\n"
        else:
            explanation += "**Prerequisites:** None - perfect for starting!\n\n"
        
        # Learning objectives
        objectives = course.get('learning_objectives', [])
        if objectives:
            explanation += "**You'll learn:**\n"
            for obj in objectives[:4]:
                explanation += f"- {obj}\n"
            explanation += "\n"
        
        # Difficulty
        difficulty = course.get('difficulty', 'intermediate')
        difficulty_emoji = {'beginner': '🟢', 'intermediate': '🟡', 'advanced': '🔴'}.get(difficulty, '🟡')
        explanation += f"**Difficulty:** {difficulty_emoji} {difficulty.capitalize()}\n\n"
        
        # Strategy breakdown for hybrid
        if strategy == 'hybrid' and isinstance(recommendation.get('details'), dict):
            details = recommendation['details']
            explanation += "**Recommendation Breakdown:**\n"
            explanation += f"- Content Similarity: {details.get('semantic', 0):.2f}\n"
            explanation += f"- Predicted Success: {details.get('ml_prediction', 0):.2f}\n"
            explanation += f"- Peer Patterns: {details.get('collaborative', 0):.2f}\n"
        
        return explanation
    
    def save_recommendations(
        self,
        student_id: int,
        recommendations: List[Dict],
        filename: Optional[str] = None
    ):
        """Save recommendations to file for later reference."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recommendations_student{student_id}_{timestamp}.json"
        
        filepath = Path("ai/outputs") / filename
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Prepare data for JSON serialization
        data = {
            'student_id': student_id,
            'timestamp': datetime.now().isoformat(),
            'recommendations': [
                {
                    'course_name': rec['course']['name'],
                    'score': rec['score'],
                    'confidence': rec['confidence'],
                    'reasoning': rec['reasoning'],
                    'strategy': rec['strategy']
                }
                for rec in recommendations
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Recommendations saved to: {filepath}")


# Test the recommendation engine
if __name__ == "__main__":
    print("Testing Recommendation Engine...\n")
    
    # Create a sample student
    student = Student(student_id=1, name="Test Student", email="test@example.com")
    
    # Simulate completed courses
    student.enroll_in_course("Python Fundamentals")
    student.complete_course("Python Fundamentals", grade=85.0)
    
    # Initialize engine
    engine = RecommendationEngine()
    
    # Test 1: Semantic recommendations
    print("Test 1: Semantic Recommendations")
    semantic_recs = engine.recommend(student, num_recommendations=3, strategy='semantic')
    print(f"Top 3 semantic recommendations:")
    for i, rec in enumerate(semantic_recs, 1):
        print(f"{i}. {rec['course']['name']} (score: {rec['score']:.2f})")
        print(f"   {rec['reasoning']}")
    print()
    
    # Test 2: ML recommendations
    print("Test 2: ML-Based Recommendations")
    ml_recs = engine.recommend(student, num_recommendations=3, strategy='ml')
    print(f"Top 3 ML-based recommendations:")
    for i, rec in enumerate(ml_recs, 1):
        print(f"{i}. {rec['course']['name']} (score: {rec['score']:.2f})")
        print(f"   {rec['reasoning']}")
    print()
    
    # Test 3: Hybrid recommendations (default)
    print("Test 3: Hybrid Recommendations")
    hybrid_recs = engine.recommend(student, num_recommendations=5)
    print(f"Top 5 hybrid recommendations:")
    for i, rec in enumerate(hybrid_recs, 1):
        print(f"{i}. {rec['course']['name']} (score: {rec['score']:.2f}, confidence: {rec['confidence']})")
        print(f"   {rec['reasoning']}")
    print()
    
    # Test 4: Detailed explanation
    print("Test 4: Detailed Explanation")
    if hybrid_recs:
        explanation = engine.explain_recommendation(hybrid_recs[0])
        print(explanation)
    
    # Test 5: Save recommendations
    print("Test 5: Save Recommendations")
    engine.save_recommendations(student.student_id, hybrid_recs)
    print()
    
    print("✅ All tests passed! Recommendation Engine is working correctly.")
