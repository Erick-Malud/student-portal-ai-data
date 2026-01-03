"""
AI Student Advisor - Step 3
Complete AI chatbot integrating student data, ML predictions, and OpenAI
Main chatbot for providing personalized academic advice
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

# Import OpenAI
try:
    from openai import OpenAI
except ImportError:
    print("Error: openai library not installed. Run: pip install openai")
    sys.exit(1)

# Import our modules
from ai.config import load_api_key, get_api_config
from ai.student_data_loader import StudentDataLoader
from ai.ml_predictor import MLPredictor
from ai.context_manager import ContextManager
from ai.prompt_templates import SYSTEM_PROMPTS


class AIStudentAdvisor:
    """
    AI-powered student advisor that combines:
    - Real student data from students.json
    - ML predictions for performance forecasting
    - OpenAI for natural language understanding
    - Context management for conversation memory
    """
    
    def __init__(self):
        """Initialize the AI Student Advisor"""
        print("=" * 60)
        print("Initializing AI Student Advisor...")
        print("=" * 60)
        
        # Load API key
        try:
            api_key = load_api_key()
            self.client = OpenAI(api_key=api_key)
            print("✓ OpenAI API connected")
        except Exception as e:
            print(f"✗ Error loading API: {e}")
            raise
        
        # Get API configuration
        config = get_api_config()
        self.model = config['model']
        self.max_tokens = config['max_tokens']
        self.temperature = 0.7  # Balanced for advisor role
        
        # Load student data
        try:
            self.data_loader = StudentDataLoader()
            print(f"✓ Loaded {len(self.data_loader.get_all_students())} students")
        except Exception as e:
            print(f"✗ Error loading student data: {e}")
            raise
        
        # Load ML model
        try:
            self.ml_predictor = MLPredictor()
            print("✓ ML predictor ready")
        except Exception as e:
            print(f"⚠ Warning: ML predictor not available: {e}")
            self.ml_predictor = None
        
        # Initialize context manager
        self.context = ContextManager(max_history=10)
        print("✓ Context manager initialized")
        
        # Setup output directory
        self.output_dir = Path(__file__).parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        print("\n✓ AI Student Advisor ready!")
        print("=" * 60)
    
    def chat(self, user_message: str) -> str:
        """
        Main chat function - processes user message and returns AI response
        
        Args:
            user_message: User's question or request
        
        Returns:
            AI assistant's response
        """
        # Detect if user is asking about a specific student
        all_students = self.data_loader.get_all_students()
        mentioned_student = self.context.detect_student_mention(user_message, all_students)
        
        # If student mentioned, load their context
        if mentioned_student:
            student_id = mentioned_student.get('id')
            student_stats = self.data_loader.calculate_student_stats(student_id)
            
            # Get ML prediction if available
            ml_prediction = None
            if self.ml_predictor and student_stats:
                try:
                    ml_prediction = self.ml_predictor.predict_performance(student_stats)
                except Exception as e:
                    print(f"⚠ ML prediction failed: {e}")
            
            # Set current student context
            if student_stats:
                if ml_prediction:
                    student_stats.update({'trend': self._determine_trend(student_stats, ml_prediction)})
                self.context.set_current_student(student_stats, ml_prediction)
        
        # Build context-rich prompt
        system_prompt = SYSTEM_PROMPTS.get('student_advisor', SYSTEM_PROMPTS['generic'])
        prompt_data = self.context.build_context_prompt(user_message, system_prompt)
        
        # Call OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=prompt_data['messages'],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            ai_response = response.choices[0].message.content
            
            # Add to conversation history
            self.context.add_message('user', user_message)
            self.context.add_message('assistant', ai_response)
            
            return ai_response
            
        except Exception as e:
            error_msg = f"Error communicating with OpenAI: {e}"
            print(f"✗ {error_msg}")
            return error_msg
    
    def _determine_trend(self, student_stats: Dict, ml_prediction: Dict) -> str:
        """Determine if student performance is improving, declining, or stable"""
        current = student_stats.get('avg_grade', 0)
        predicted = ml_prediction.get('predicted_grade', 0)
        
        if predicted > current + 5:
            return "improving"
        elif predicted < current - 5:
            return "declining"
        return "stable"
    
    def analyze_student(self, student_id_or_name) -> str:
        """
        Provide comprehensive analysis of a student
        
        Args:
            student_id_or_name: Student ID (int) or name (str)
        
        Returns:
            Detailed analysis text
        """
        # Get student data
        if isinstance(student_id_or_name, int):
            student = self.data_loader.get_student_by_id(student_id_or_name)
        else:
            student = self.data_loader.get_student_by_name(str(student_id_or_name))
        
        if not student:
            return f"❌ Student not found: {student_id_or_name}"
        
        student_id = student.get('id')
        student_stats = self.data_loader.calculate_student_stats(student_id)
        
        if not student_stats:
            return f"❌ Could not load statistics for student: {student_id}"
        
        # Get ML insights
        ml_insights = None
        if self.ml_predictor:
            try:
                ml_insights = self.ml_predictor.generate_insights(student_id, student_stats)
            except Exception as e:
                print(f"⚠ ML insights failed: {e}")
        
        # Build analysis prompt
        analysis_query = f"Provide a comprehensive academic analysis for {student_stats['name']}"
        
        # Set context
        self.context.set_current_student(student_stats, 
                                         ml_insights.get('prediction') if ml_insights else None)
        
        # Get AI analysis
        analysis = self.chat(analysis_query)
        
        # Add ML recommendations if available
        if ml_insights and 'recommendations' in ml_insights:
            analysis += "\n\n📋 **Recommended Actions:**\n"
            for i, rec in enumerate(ml_insights['recommendations'][:5], 1):
                analysis += f"{i}. {rec}\n"
        
        return analysis
    
    def recommend_for_student(self, student_id: int) -> str:
        """
        Generate personalized recommendations for a student
        
        Args:
            student_id: Student ID
        
        Returns:
            Recommendation text
        """
        student_stats = self.data_loader.calculate_student_stats(student_id)
        
        if not student_stats:
            return f"❌ Student not found: {student_id}"
        
        # Get ML prediction
        ml_prediction = None
        if self.ml_predictor:
            try:
                ml_prediction = self.ml_predictor.predict_performance(student_stats)
                recommendations = self.ml_predictor.recommend_actions(
                    ml_prediction['risk_level'],
                    student_stats
                )
            except Exception as e:
                print(f"⚠ ML recommendation failed: {e}")
                recommendations = []
        
        # Set context
        self.context.set_current_student(student_stats, ml_prediction)
        
        # Ask AI for personalized recommendations
        query = f"Generate personalized academic recommendations for {student_stats['name']}"
        ai_recommendations = self.chat(query)
        
        # Combine ML and AI recommendations
        result = ai_recommendations
        
        if recommendations:
            result += "\n\n📊 **Data-Driven Recommendations:**\n"
            for i, rec in enumerate(recommendations[:5], 1):
                result += f"{i}. {rec}\n"
        
        return result
    
    def compare_students(self, student_ids: List[int]) -> str:
        """
        Compare multiple students
        
        Args:
            student_ids: List of student IDs
        
        Returns:
            Comparison analysis
        """
        if len(student_ids) < 2:
            return "❌ Need at least 2 students to compare"
        
        # Load all student data
        students_data = []
        for student_id in student_ids:
            stats = self.data_loader.calculate_student_stats(student_id)
            if stats:
                students_data.append(stats)
        
        if len(students_data) < 2:
            return "❌ Could not load data for comparison"
        
        # Build comparison summary
        comparison_text = "=== STUDENT COMPARISON ===\n\n"
        for data in students_data:
            comparison_text += f"{data['name']} (ID: {data['student_id']}):\n"
            comparison_text += f"  GPA: {data['avg_grade']:.1f}\n"
            comparison_text += f"  Courses: {data['courses_completed']}\n\n"
        
        # Ask AI to analyze
        query = f"Compare these students and provide insights:\n{comparison_text}"
        return self.chat(query)
    
    def get_overall_statistics(self) -> str:
        """Get statistics about all students"""
        stats = self.data_loader.get_all_stats()
        
        summary = "=== OVERALL STATISTICS ===\n\n"
        summary += f"📊 Total Students: {stats['total_students']}\n"
        summary += f"📈 Average GPA: {stats['avg_gpa']:.1f}\n"
        summary += f"📚 Average Courses/Student: {stats['avg_courses_per_student']:.1f}\n"
        summary += f"⚠️  At Risk: {stats['at_risk_count']} students\n"
        summary += f"📊 Average: {stats['average_count']} students\n"
        summary += f"⭐ Excelling: {stats['excelling_count']} students\n"
        
        # Ask AI to provide insights
        query = f"Analyze these overall statistics and provide insights:\n{summary}"
        return self.chat(query)
    
    def save_conversation(self, filename: str = None):
        """Save current conversation to file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"advisor_conversation_{timestamp}.txt"
        
        filepath = self.output_dir / filename
        
        # Get conversation export
        conversation = self.context.export_conversation()
        session_summary = self.context.get_session_summary()
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(session_summary)
            f.write("\n\n")
            f.write(conversation)
        
        return str(filepath)
    
    def interactive_mode(self):
        """Run interactive chat session"""
        print("\n" + "=" * 60)
        print("AI STUDENT ADVISOR - Interactive Mode")
        print("=" * 60)
        print("\nCommands:")
        print("  /student <name>     - Analyze a specific student")
        print("  /analyze <id>       - Detailed analysis of student by ID")
        print("  /recommend <id>     - Get recommendations for student")
        print("  /stats              - Show overall statistics")
        print("  /history            - Show conversation history")
        print("  /reset              - Clear conversation history")
        print("  /save               - Save conversation to file")
        print("  /quit               - Exit advisor")
        print("\nOr just type your question naturally!")
        print("=" * 60)
        
        while True:
            try:
                user_input = input("\n💬 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.startswith('/'):
                    parts = user_input.split(maxsplit=1)
                    command = parts[0].lower()
                    arg = parts[1] if len(parts) > 1 else None
                    
                    if command == '/quit':
                        print("\n👋 Thanks for using AI Student Advisor!")
                        break
                    
                    elif command == '/student' and arg:
                        print(f"\n🤖 AI: Analyzing {arg}...\n")
                        response = self.analyze_student(arg)
                        print(response)
                    
                    elif command == '/analyze' and arg:
                        try:
                            student_id = int(arg)
                            print(f"\n🤖 AI: Analyzing student {student_id}...\n")
                            response = self.analyze_student(student_id)
                            print(response)
                        except ValueError:
                            print("❌ /analyze requires a numeric student ID")
                    
                    elif command == '/recommend' and arg:
                        try:
                            student_id = int(arg)
                            print(f"\n🤖 AI: Generating recommendations...\n")
                            response = self.recommend_for_student(student_id)
                            print(response)
                        except ValueError:
                            print("❌ /recommend requires a numeric student ID")
                    
                    elif command == '/stats':
                        print("\n🤖 AI: Calculating statistics...\n")
                        response = self.get_overall_statistics()
                        print(response)
                    
                    elif command == '/history':
                        print("\n" + self.context.export_conversation())
                    
                    elif command == '/reset':
                        self.context.reset_conversation()
                        print("✓ Conversation history cleared")
                    
                    elif command == '/save':
                        filepath = self.save_conversation()
                        print(f"✓ Conversation saved to: {filepath}")
                    
                    else:
                        print("❌ Unknown command or missing argument")
                
                else:
                    # Regular chat
                    print("\n🤖 AI: ", end="")
                    response = self.chat(user_input)
                    print(response)
            
            except KeyboardInterrupt:
                print("\n\n👋 Thanks for using AI Student Advisor!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")


def main():
    """Main entry point"""
    try:
        advisor = AIStudentAdvisor()
        advisor.interactive_mode()
    except Exception as e:
        print(f"❌ Failed to start AI Student Advisor: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
