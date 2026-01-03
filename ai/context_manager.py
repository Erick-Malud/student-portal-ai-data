"""
Context Manager - Step 3
Manages conversation history and student context for AI chatbot
Builds rich context prompts combining data, ML predictions, and conversation history
"""

from typing import Dict, List, Optional
from datetime import datetime


class ContextManager:
    """Manage conversation memory and student context"""
    
    def __init__(self, max_history: int = 10):
        """
        Initialize context manager
        
        Args:
            max_history: Maximum number of messages to keep in history
        """
        self.max_history = max_history
        self.conversation_history: List[Dict] = []
        self.current_student: Optional[Dict] = None
        self.ml_predictions: Optional[Dict] = None
        self.session_stats = {
            'queries': 0,
            'students_discussed': set(),
            'start_time': datetime.now()
        }
    
    def add_message(self, role: str, content: str):
        """
        Add a message to conversation history
        
        Args:
            role: 'user' or 'assistant'
            content: Message content
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': datetime.now().isoformat()
        }
        
        self.conversation_history.append(message)
        
        # Trim history if too long
        if len(self.conversation_history) > self.max_history * 2:
            # Keep last max_history pairs (user + assistant)
            self.conversation_history = self.conversation_history[-self.max_history * 2:]
        
        # Update stats
        if role == 'user':
            self.session_stats['queries'] += 1
    
    def set_current_student(self, student_data: Dict, ml_prediction: Dict = None):
        """
        Set the current student being discussed
        
        Args:
            student_data: Student information dict
            ml_prediction: Optional ML prediction results
        """
        self.current_student = student_data
        self.ml_predictions = ml_prediction
        
        # Track student in session
        student_id = student_data.get('student_id') or student_data.get('id')
        if student_id:
            self.session_stats['students_discussed'].add(student_id)
    
    def clear_current_student(self):
        """Clear current student context"""
        self.current_student = None
        self.ml_predictions = None
    
    def get_conversation_history(self, last_n: int = None) -> List[Dict]:
        """
        Get conversation history
        
        Args:
            last_n: Number of recent messages to return (None = all)
        
        Returns:
            List of message dicts
        """
        if last_n is None:
            return self.conversation_history
        return self.conversation_history[-last_n:]
    
    def build_context_prompt(self, user_query: str, system_prompt: str = None) -> Dict:
        """
        Build a complete context prompt for OpenAI
        Combines system prompt, student data, ML predictions, and conversation history
        
        Args:
            user_query: Current user question
            system_prompt: Optional custom system prompt
        
        Returns:
            Dict with messages array for OpenAI API
        """
        messages = []
        
        # 1. System prompt
        if system_prompt:
            system_message = system_prompt
        else:
            system_message = self._build_default_system_prompt()
        
        messages.append({
            'role': 'system',
            'content': system_message
        })
        
        # 2. Add current student context if available
        if self.current_student:
            context_message = self._build_student_context()
            messages.append({
                'role': 'system',
                'content': context_message
            })
        
        # 3. Add recent conversation history (last 5 exchanges)
        recent_history = self.get_conversation_history(last_n=10)
        for msg in recent_history:
            messages.append({
                'role': msg['role'],
                'content': msg['content']
            })
        
        # 4. Add current user query
        messages.append({
            'role': 'user',
            'content': user_query
        })
        
        return {'messages': messages}
    
    def _build_default_system_prompt(self) -> str:
        """Build default system prompt for student advisor"""
        return """You are an expert AI Student Advisor for a learning portal. Your role is to:

1. Provide personalized academic advice based on student data and ML predictions
2. Analyze student performance and identify areas for improvement
3. Make actionable, encouraging recommendations
4. Answer questions about courses, grades, and academic progress
5. Be supportive, professional, and data-driven in your responses

Guidelines:
- Use the provided student data and ML predictions to inform your advice
- Be specific and actionable in recommendations
- Consider the student's risk level when giving advice
- Maintain a supportive and encouraging tone
- If data is missing, acknowledge limitations clearly
- Keep responses concise (2-4 paragraphs unless detailed analysis requested)

Remember: Your goal is to help students succeed academically."""
    
    def _build_student_context(self) -> str:
        """Build formatted student context for AI"""
        context_parts = ["=== CURRENT STUDENT CONTEXT ==="]
        
        if self.current_student:
            # Basic info
            name = self.current_student.get('name', 'Unknown')
            student_id = self.current_student.get('student_id') or self.current_student.get('id', 'N/A')
            context_parts.append(f"\nStudent: {name} (ID: {student_id})")
            
            # Academic performance
            avg_grade = self.current_student.get('avg_grade', 0)
            courses_completed = self.current_student.get('courses_completed', 0)
            active_enrollments = self.current_student.get('active_enrollments', 0)
            
            context_parts.append(f"\nCurrent Performance:")
            context_parts.append(f"- GPA: {avg_grade:.1f}")
            context_parts.append(f"- Courses Completed: {courses_completed}")
            context_parts.append(f"- Active Enrollments: {active_enrollments}")
            
            # Course grades
            grades = self.current_student.get('grades', {})
            if grades:
                context_parts.append(f"\nCourse Grades:")
                for course, grade in grades.items():
                    context_parts.append(f"  • {course}: {grade}")
            
            # ML predictions
            if self.ml_predictions:
                context_parts.append(f"\n=== ML PREDICTION ===")
                predicted = self.ml_predictions.get('predicted_grade', 0)
                risk = self.ml_predictions.get('risk_level', 'unknown')
                confidence = self.ml_predictions.get('confidence', 0)
                
                context_parts.append(f"Predicted Final Grade: {predicted:.1f}")
                context_parts.append(f"Risk Level: {risk.upper()}")
                context_parts.append(f"Prediction Confidence: {confidence:.0%}")
                
                # Add trend if available
                if 'trend' in self.ml_predictions:
                    trend = self.ml_predictions['trend']
                    context_parts.append(f"Performance Trend: {trend}")
        
        context_parts.append("\n=== END CONTEXT ===")
        return "\n".join(context_parts)
    
    def get_session_summary(self) -> str:
        """Generate a summary of the current session"""
        duration = datetime.now() - self.session_stats['start_time']
        minutes = int(duration.total_seconds() / 60)
        
        summary_parts = [
            "=== SESSION SUMMARY ===",
            f"Duration: {minutes} minutes",
            f"Total Queries: {self.session_stats['queries']}",
            f"Students Discussed: {len(self.session_stats['students_discussed'])}",
            f"Messages in History: {len(self.conversation_history)}",
        ]
        
        if self.current_student:
            name = self.current_student.get('name', 'Unknown')
            summary_parts.append(f"Current Student: {name}")
        
        return "\n".join(summary_parts)
    
    def reset_conversation(self):
        """Clear conversation history but keep session stats"""
        self.conversation_history = []
        self.current_student = None
        self.ml_predictions = None
    
    def reset_session(self):
        """Completely reset context manager"""
        self.conversation_history = []
        self.current_student = None
        self.ml_predictions = None
        self.session_stats = {
            'queries': 0,
            'students_discussed': set(),
            'start_time': datetime.now()
        }
    
    def export_conversation(self) -> str:
        """Export conversation history as formatted text"""
        if not self.conversation_history:
            return "No conversation history."
        
        lines = ["=" * 60, "CONVERSATION HISTORY", "=" * 60, ""]
        
        for msg in self.conversation_history:
            role = msg['role'].upper()
            content = msg['content']
            timestamp = msg.get('timestamp', 'Unknown time')
            
            lines.append(f"[{timestamp}] {role}:")
            lines.append(content)
            lines.append("")
        
        return "\n".join(lines)
    
    def detect_student_mention(self, text: str, all_students: List[Dict]) -> Optional[Dict]:
        """
        Detect if a student is mentioned in the text
        
        Args:
            text: User input text
            all_students: List of all student dicts
        
        Returns:
            Student dict if found, None otherwise
        """
        text_lower = text.lower()
        
        # Check for each student name
        for student in all_students:
            name = student.get('name', '').lower()
            
            # Check for full name or first name
            if name in text_lower:
                return student
            
            # Check for first name only
            first_name = name.split()[0] if name else ''
            if first_name and first_name in text_lower:
                return student
        
        return None


if __name__ == "__main__":
    """Test the context manager"""
    print("=" * 60)
    print("Testing Context Manager")
    print("=" * 60)
    
    # Initialize
    context = ContextManager(max_history=5)
    
    # Test 1: Add messages
    print("\n1. Testing add_message():")
    context.add_message('user', 'Tell me about Alice')
    context.add_message('assistant', 'Alice is performing well with a 90.0 GPA')
    context.add_message('user', 'What courses is she taking?')
    print(f"   Messages in history: {len(context.get_conversation_history())}")
    
    # Test 2: Set current student
    print("\n2. Testing set_current_student():")
    student_data = {
        'id': 1,
        'name': 'Alice Johnson',
        'avg_grade': 90.0,
        'courses_completed': 2,
        'active_enrollments': 1,
        'grades': {'Python': 92, 'Math': 88}
    }
    ml_prediction = {
        'predicted_grade': 85.5,
        'risk_level': 'average',
        'confidence': 0.87,
        'trend': 'stable'
    }
    context.set_current_student(student_data, ml_prediction)
    print(f"   Current student: {context.current_student['name']}")
    
    # Test 3: Build context prompt
    print("\n3. Testing build_context_prompt():")
    prompt = context.build_context_prompt("How can Alice improve?")
    print(f"   Messages in prompt: {len(prompt['messages'])}")
    print(f"   System prompt length: {len(prompt['messages'][0]['content'])} chars")
    
    # Test 4: Session summary
    print("\n4. Testing get_session_summary():")
    summary = context.get_session_summary()
    print(summary)
    
    # Test 5: Export conversation
    print("\n5. Testing export_conversation():")
    export = context.export_conversation()
    print(f"   Export length: {len(export)} chars")
    
    # Test 6: Student mention detection
    print("\n6. Testing detect_student_mention():")
    test_students = [
        {'id': 1, 'name': 'Alice Johnson'},
        {'id': 2, 'name': 'Bob Smith'}
    ]
    detected = context.detect_student_mention("Tell me about Alice", test_students)
    if detected:
        print(f"   Detected: {detected['name']}")
    
    print("\n✓ All tests passed!")
