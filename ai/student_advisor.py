"""
AI Student Advisor - Step 3
Complete AI chatbot integrating student data, ML predictions, and OpenAI
Main chatbot for providing personalized academic advice
"""

import os
import sys
import random
from pathlib import Path
from typing import Optional, Dict, List, Union, Any
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
            if api_key == "MOCK":
                self.is_mock = True
                self.client = None
                print("✓ Mock mode enabled - OpenAI API bypassed")
            else:
                self.is_mock = False
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
        self.context_manager = ContextManager(max_history=10)
        self.context = self.context_manager  # keep old name working in other methods
        print("✓ Context manager initialized")

        
        # Setup output directory
        self.output_dir = Path(__file__).parent / "outputs"
        self.output_dir.mkdir(exist_ok=True)
        
        print("\n✓ AI Student Advisor ready!")
        print("=" * 60)
    
    def chat(self, student_id_or_message, user_message: str = None) -> Union[str, Dict[str, Any]]:
        """
        API-compatible chat function.

        Supports BOTH:
          1) chat("hello") -> old usage
          2) chat(student_id, "hello") -> API usage
        """
        # ---- Compatibility handling ----
        if user_message is None:
            # old style: chat("hello")
            student_id = None
            user_message = str(student_id_or_message)
        else:
            # new style: chat(student_id, "hello")
            student_id = student_id_or_message

        # ---- Load student context if student_id provided ----
        if student_id is not None:
            student_stats = self.data_loader.calculate_student_stats(student_id)

            if student_stats:
                ml_prediction = None
                if self.ml_predictor:
                    try:
                        ml_prediction = self.ml_predictor.predict_performance(student_stats)
                    except Exception as e:
                        print(f"⚠ ML prediction failed: {e}")

                if ml_prediction:
                    student_stats.update({
                        "trend": self._determine_trend(student_stats, ml_prediction)
                    })

                self.context_manager.set_current_student(student_stats, ml_prediction)
            else:
                self.context_manager.clear_current_student()

        # ---- Build context-rich prompt ----
        system_prompt = SYSTEM_PROMPTS.get(
            "student_advisor",
            SYSTEM_PROMPTS["generic"]
        )

        prompt_data = self.context_manager.build_context_prompt(
            user_message,
            system_prompt
        )

        # ---- Call OpenAI ----
        try:
            if self.is_mock:
                # Use smart mock response
                ai_response = self._generate_mock_response(student_id, user_message)
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=prompt_data["messages"],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )

                ai_response = response.choices[0].message.content

            # Save conversation
            self.context_manager.add_message("user", user_message)
            
            # Extract text for history if structured
            if isinstance(ai_response, dict):
                history_content = ai_response.get("response", str(ai_response))
            else:
                history_content = ai_response
                
            self.context_manager.add_message("assistant", history_content)

            return ai_response

        except Exception as e:
            error_msg = f"Error communicating with OpenAI: {e}"
            print(f"✗ {error_msg}")
            return error_msg




    def _detect_intent(self, message: str) -> str:
        """Detect intent from user message using simple keyword matching."""
        if not message:
            return "UNKNOWN"
        msg = message.lower()
        
        if any(w in msg for w in ["next", "take next", "what courses", "recommend course", "recommendation", "semester"]):
            if "plan" in msg or "schedule" in msg or "timetable" in msg or "load" in msg:
                return "SEMESTER_PLAN"
            return "NEXT_COURSES"
        
        if any(w in msg for w in ["plan", "semester plan", "timetable", "schedule", "workload"]):
            return "SEMESTER_PLAN"
            
        if any(w in msg for w in ["career", "job", "future", "internship", "employability", "skills", "work"]):
            return "CAREER"
            
        if any(w in msg for w in ["challenging", "hard", "easy", "advanced", "difficulty", "struggle", "fail"]):
            return "DIFFICULTY"
            
        if any(w in msg for w in ["progress", "performance", "improve", "grades", "study", "analysis"]):
            return "PROGRESS"
            
        return "UNKNOWN"

    def _generate_mock_response(self, student_id: Optional[str], user_message: str) -> Dict[str, Any]:
        """
        Generate a smart, rule-based response in Mock Mode.
        Uses local database/loaders instead of OpenAI.
        """
        import json
        from datetime import datetime
        
        # 1. Normalize Student ID
        clean_student_id = str(student_id).strip().upper() if student_id else None
        
        # 2. Handle missing student ID (Generic greeting)
        if not clean_student_id:
            return {
                "response": "Hello! I am your AI Student Advisor (Mock Mode). Please provide your Student ID so I can look up your records and give personalized advice.",
                "recommendations": [],
                "suggested_courses": [],
                "student_summary": None,
                "mode": "mock",
                "timestamp": datetime.now().isoformat()
            }

        # 3. Load Student & Enrollments
        # Try finding student with normalized ID (and original as fallback)
        student = self.data_loader.get_student_by_id(clean_student_id)
        if not student and clean_student_id != str(student_id):
             # Try original just in case
             student = self.data_loader.get_student_by_id(student_id)
        
        # Handle Not Found - Return 200 Friendly JSON as requested
        if not student:
             return {
                "response": f"I couldn't find a student with ID {clean_student_id} in our records. Please verify the ID and try again, or ask your administrator.",
                "recommendations": [],
                "suggested_courses": [],
                "student_summary": {
                    "student_id": clean_student_id,
                    "name": "Unknown",
                    "major": "Unknown",
                    "enrolled_course_count": 0,
                    "performance_level": "unknown",
                    "intent": "unknown"
                },
                "mode": "mock",
                "timestamp": datetime.now().isoformat()
             }

        # Extract details
        name = student.get('name', 'Student')
        major = student.get('course', 'Generic Major')
        enrolled_courses = student.get('enrolled_courses', [])
        # Ensure it's a list
        if not isinstance(enrolled_courses, list):
            enrolled_courses = []
            
        count = len(enrolled_courses)
        
        # 4. Determine Performance Status
        if count <= 2:
            status = "at_risk"
        elif count >= 5:
            status = "excelling"
        else:
            status = "average"

        # 5. Detect Intent
        intent = self._detect_intent(user_message or "")
        
        # 6. Intent-Specific Logic
        response_msg = ""
        recommendations = []
        course_catalog = {
            "Data": [
                {"code": "DS101", "name": "Intro to Data Science", "dept": "Data"},
                {"code": "DS201", "name": "Machine Learning I", "dept": "Data"},
                {"code": "DS301", "name": "Big Data Analytics", "dept": "Data"},
                {"code": "IT105", "name": "Database Systems", "dept": "IT"},
                {"code": "STAT201", "name": "Applied Statistics", "dept": "Math"}
            ],
            "IT": [
                {"code": "IT101", "name": "Intro to Programming", "dept": "IT"},
                {"code": "IT105", "name": "Database Systems", "dept": "IT"},
                {"code": "IT201", "name": "Web Development", "dept": "IT"},
                {"code": "SEC101", "name": "Cybersecurity Basics", "dept": "Security"},
                {"code": "NET101", "name": "Networking Fundamentals", "dept": "IT"}
            ],
            "Business": [
                {"code": "BUS101", "name": "Management 101", "dept": "Business"},
                {"code": "MKT101", "name": "Marketing Principles", "dept": "Business"},
                {"code": "ACC101", "name": "Accounting I", "dept": "Business"},
                {"code": "ECO101", "name": "Microeconomics", "dept": "Economics"},
                {"code": "COM101", "name": "Business Communication", "dept": "Communication"}
            ]
        }
        
        # Randomized Phrases
        openers = [f"Hi {name}!", f"Hello {name}.", f"Welcome back, {name}!", f"Good to see you, {name}."]
        opener = random.choice(openers)
        
        potential_courses = course_catalog.get(major, course_catalog["IT"])
        
        # Filter Logic Helper
        def get_suggestions(count_needed):
            # Sort by dept match first (simple heuristic)
            candidates = sorted(potential_courses, key=lambda x: 0 if x['dept'] in major else 1)
            found = []
            for c in candidates:
                # Check not enrolled (fuzzy match strings)
                is_enrolled = any(c['name'] in str(ec) or c['code'] in str(ec) for ec in enrolled_courses)
                if not is_enrolled and c not in found:
                    found.append(c)
            return found[:count_needed]

        suggested = []
        
        # --- BRANCHES ---
        
        if intent == "NEXT_COURSES":
            sugg = get_suggestions(3)
            # Reformat for consistent output
            suggested = [{
                "course_code": c['code'],
                "course_name": c['name'],
                "department": c['dept']
            } for c in sugg]
            
            response_msg = f"{opener} Based on your major in {major}, I recommend focusing on core technical skills."
            if suggested:
                 response_msg += f" {suggested[0]['course_name']} would be a great next step."
            
            recommendations = [
                "Prioritize core major requirements first",
                "Consider one cross-disciplinary elective",
                "Check prerequisites before registering"
            ]

        elif intent == "SEMESTER_PLAN":
            response_msg = f"{opener} Let's look at your semester plan. You are currently taking {count} courses."
            if count <= 2:
                response_msg += " This is a light load. I recommend adding 1-2 foundational courses to stay on track."
                recommendations = ["Add 1 Core Course", "Add 1 Elective", "Review Graduation Timeline"]
            elif count >= 5:
                response_msg += " This is a heavy load! Consider dropping one course or ensuring you have strong time management."
                recommendations = ["Prioritize hardest subjects", "Form study groups", "Consider auditing an elective"]
            else:
                response_msg += " This is a balanced workload. You are on a good path."
                recommendations = ["Maintain current pace", "Start projects early", "Balance study/life"]
                
            sugg = get_suggestions(3)
            suggested = [{"course_code": c['code'], "course_name": c['name'], "department": c['dept']} for c in sugg]

        elif intent == "CAREER":
            skills = {
                "IT": "software development, databases, and secure coding",
                "Data": "statistical analysis, machine learning, and data visualization",
                "Business": "strategic management, financial analysis, and communication"
            }
            career_focus = skills.get(major, "professional skills")
            
            response_msg = f"{opener} To build a career in {major}, you should focus on {career_focus}."
            recommendations = [
                "Build a portfolio of projects",
                "Look for summer internships",
                "Attend industry networking events"
            ]
            
            sugg = get_suggestions(3) 
            suggested = [{"course_code": c['code'], "course_name": c['name'], "department": c['dept']} for c in sugg]


        elif intent == "DIFFICULTY":
            if status == "excelling":
                response_msg = f"{opener} Since you are excelling, you might enjoy more challenging project-based courses."
                recommendations = ["Take an Advanced level course", "Join a research lab", "Compete in hackathons"]
            else:
                 response_msg = f"{opener} If you are finding things difficult, focus on mastering the basics before moving on."
                 recommendations = ["Attend office hours", "Use the tutoring center", "Review foundational material"]
            
            sugg = get_suggestions(2)
            suggested = [{"course_code": c['code'], "course_name": c['name'], "department": c['dept']} for c in sugg]

        elif intent == "PROGRESS":
            response_msg = f"{opener} You have {count} active enrollments. "
            if status == "at_risk":
                 response_msg += "We need to improve your engagement. What subject are you struggling with most?"
            elif status == "excelling":
                 response_msg += "Your performance is excellent! Keep up the great work."
            else:
                 response_msg += "You are making steady progress."
            
            recommendations = ["Review weekly goals", "Track your study hours", "Meet with your academic advisor"]
            suggested = []

        else: # UNKNOWN
            response_msg = f"{opener} I'm your AI advisor. I can help with course selection, semester planning, or career advice. Currently you have {count} courses."
            recommendations = ["Ask about 'next semester courses'", "Ask for a 'study plan'", "Ask about 'career skills'"]
            sugg = get_suggestions(2)
            suggested = [{"course_code": c['code'], "course_name": c['name'], "department": c['dept']} for c in sugg]

        # 7. Construct Final Response
        result = {
            "response": response_msg,
            "recommendations": recommendations,
            "suggested_courses": suggested,
            "student_summary": {
                "student_id": clean_student_id,
                "name": name,
                "major": major,
                "enrolled_course_count": count,
                "performance_level": status,
                "intent": intent
            },
            "mode": "mock",
            "timestamp": datetime.now().isoformat()
        }
        
        return result

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
