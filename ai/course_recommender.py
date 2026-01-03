"""
Interactive Course Recommender Chatbot
AI-powered conversational interface for personalized course recommendations.
"""

import os
from typing import Dict, List, Optional
from openai import OpenAI
from dotenv import load_dotenv

from ai.recommendation_engine import RecommendationEngine
from ai.student_data_loader import StudentDataLoader
from student import Student

# Load environment variables
load_dotenv()


class CourseRecommender:
    """
    Conversational AI assistant for course recommendations.
    
    Features:
    - Natural language interaction
    - Personalized recommendations
    - Detailed course explanations
    - Interactive Q&A about courses
    - Learning path planning
    """
    
    def __init__(self):
        """Initialize the course recommender chatbot."""
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("OPENAI_API_KEY not found in environment variables")
        
        self.client = OpenAI(api_key=api_key)
        self.recommendation_engine = RecommendationEngine()
        self.data_loader = StudentDataLoader()
        
        # Conversation history
        self.conversation_history = []
        
        # System prompt for the recommender
        self.system_prompt = """You are an intelligent course recommendation assistant for an online learning platform.

Your role:
- Help students find the best courses for their learning goals
- Provide personalized recommendations based on their history and interests
- Explain why courses are recommended
- Answer questions about courses, prerequisites, and learning paths
- Be encouraging and supportive

Guidelines:
- Be conversational and friendly
- Ask clarifying questions to understand student needs
- Reference specific courses when making recommendations
- Explain prerequisites and learning sequences clearly
- Keep responses concise (2-3 paragraphs max)
- Use emojis occasionally to be engaging 😊

When students ask for recommendations:
1. Consider their completed courses
2. Understand their goals and interests
3. Check prerequisite requirements
4. Suggest 3-5 specific courses with brief reasons
5. Offer to provide more details about any course"""
    
    def chat(
        self,
        student: Student,
        user_message: str,
        include_recommendations: bool = True
    ) -> str:
        """
        Process a chat message and return AI response.
        
        Args:
            student: Student object
            user_message: User's message
            include_recommendations: Whether to generate recommendations
        
        Returns:
            AI assistant's response
        """
        # Get recommendations if requested
        recommendations_context = ""
        if include_recommendations and any(keyword in user_message.lower() for keyword in 
                                          ['recommend', 'suggest', 'what course', 'next course', 'should i take']):
            try:
                recommendations = self.recommendation_engine.recommend(student, num_recommendations=5)
                recommendations_context = self._format_recommendations_for_context(recommendations)
            except Exception as e:
                print(f"Error getting recommendations: {e}")
                recommendations_context = ""
        
        # Build context about student
        student_context = self._build_student_context(student)
        
        # Create messages for OpenAI
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "system", "content": f"Student Context:\n{student_context}"},
        ]
        
        # Add recommendations context if available
        if recommendations_context:
            messages.append({
                "role": "system",
                "content": f"Current Recommendations:\n{recommendations_context}"
            })
        
        # Add conversation history
        messages.extend(self.conversation_history)
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        # Get AI response
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            assistant_message = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": assistant_message})
            
            # Keep only last 10 messages to manage token usage
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return assistant_message
            
        except Exception as e:
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    def get_recommendations(
        self,
        student: Student,
        num_recommendations: int = 5,
        strategy: str = 'hybrid'
    ) -> str:
        """
        Get formatted recommendations as a string.
        
        Args:
            student: Student object
            num_recommendations: Number of courses to recommend
            strategy: Recommendation strategy
        
        Returns:
            Formatted recommendations text
        """
        recommendations = self.recommendation_engine.recommend(
            student,
            num_recommendations=num_recommendations,
            strategy=strategy
        )
        
        if not recommendations:
            return "No recommendations available at this time. Please complete some courses first!"
        
        output = f"🎓 **Top {len(recommendations)} Course Recommendations for {student.name}**\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            course = rec['course']
            score = rec['score']
            confidence = rec['confidence']
            reasoning = rec['reasoning']
            
            output += f"**{i}. {course['name']}** "
            output += f"(Score: {score:.2f}, Confidence: {confidence:.0%})\n"
            output += f"   📝 {course['description']}\n"
            output += f"   💡 {reasoning}\n"
            
            # Prerequisites
            prereqs = course.get('prerequisites', [])
            if prereqs:
                output += f"   📚 Prerequisites: {', '.join(prereqs)}\n"
            
            # Difficulty
            difficulty = course.get('difficulty', 'intermediate')
            difficulty_emoji = {'beginner': '🟢', 'intermediate': '🟡', 'advanced': '🔴'}.get(difficulty, '🟡')
            output += f"   {difficulty_emoji} Difficulty: {difficulty.capitalize()}\n\n"
        
        return output
    
    def explain_course(self, course_name: str) -> str:
        """
        Provide detailed explanation of a specific course.
        
        Args:
            course_name: Name of the course
        
        Returns:
            Detailed course explanation
        """
        # Find the course
        course = None
        for c in self.recommendation_engine.courses:
            if c['name'].lower() == course_name.lower():
                course = c
                break
        
        if not course:
            return f"Sorry, I couldn't find a course named '{course_name}'. Please check the course name."
        
        # Build explanation
        explanation = f"📚 **{course['name']}**\n\n"
        
        # Description
        explanation += f"**Description:**\n{course['description']}\n\n"
        
        # Learning objectives
        objectives = course.get('learning_objectives', [])
        if objectives:
            explanation += "**What you'll learn:**\n"
            for obj in objectives:
                explanation += f"• {obj}\n"
            explanation += "\n"
        
        # Prerequisites
        prereqs = course.get('prerequisites', [])
        if prereqs:
            explanation += f"**Prerequisites:** {', '.join(prereqs)}\n"
        else:
            explanation += "**Prerequisites:** None - perfect for beginners!\n"
        explanation += "\n"
        
        # Difficulty
        difficulty = course.get('difficulty', 'intermediate')
        difficulty_emoji = {'beginner': '🟢', 'intermediate': '🟡', 'advanced': '🔴'}.get(difficulty, '🟡')
        explanation += f"**Difficulty:** {difficulty_emoji} {difficulty.capitalize()}\n\n"
        
        # Category
        category = course.get('category', 'general')
        explanation += f"**Category:** {category.replace('_', ' ').title()}\n"
        
        return explanation
    
    def plan_learning_path(
        self,
        student: Student,
        goal: str,
        num_courses: int = 8
    ) -> str:
        """
        Create a suggested learning path to achieve a goal.
        
        Args:
            student: Student object
            goal: Learning goal (e.g., "become a data scientist")
            num_courses: Number of courses in the path
        
        Returns:
            Formatted learning path
        """
        # Get recommendations
        recommendations = self.recommendation_engine.recommend(
            student,
            num_recommendations=num_courses
        )
        
        if not recommendations:
            return "Unable to create learning path. Please complete some foundational courses first."
        
        # Build learning path
        output = f"🎯 **Learning Path: {goal}**\n\n"
        output += f"Based on your current progress, here's a suggested path:\n\n"
        
        completed = student.get_completed_courses()
        if completed:
            output += f"✅ **Completed:** {', '.join(completed)}\n\n"
        
        output += "📋 **Recommended Next Steps:**\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            course = rec['course']
            output += f"**Step {i}: {course['name']}**\n"
            output += f"   {course['description']}\n"
            
            prereqs = course.get('prerequisites', [])
            if prereqs:
                output += f"   Prerequisites: {', '.join(prereqs)}\n"
            
            difficulty = course.get('difficulty', 'intermediate')
            output += f"   Difficulty: {difficulty.capitalize()}\n\n"
        
        output += "\n💡 **Tip:** Focus on one course at a time for best results!"
        
        return output
    
    def _build_student_context(self, student: Student) -> str:
        """Build context string about student for AI."""
        context = f"Student Name: {student.name}\n"
        context += f"Student ID: {student.student_id}\n"
        
        completed = student.get_completed_courses()
        if completed:
            context += f"Completed Courses: {', '.join(completed)}\n"
        else:
            context += "Completed Courses: None (new student)\n"
        
        enrolled = student.get_enrolled_courses()
        if enrolled:
            context += f"Currently Enrolled: {', '.join(enrolled)}\n"
        
        # Add performance data if available
        try:
            student_data = self.data_loader.get_student_data(student.student_id)
            if student_data and 'current_gpa' in student_data:
                context += f"GPA: {student_data['current_gpa']:.2f}\n"
        except:
            pass
        
        return context
    
    def _format_recommendations_for_context(self, recommendations: List[Dict]) -> str:
        """Format recommendations for AI context."""
        if not recommendations:
            return "No recommendations available."
        
        context = "Top recommended courses:\n"
        for i, rec in enumerate(recommendations[:5], 1):
            course = rec['course']
            score = rec['score']
            context += f"{i}. {course['name']} (score: {score:.2f}) - {course['description'][:80]}...\n"
        
        return context
    
    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
    
    def get_conversation_summary(self) -> str:
        """Get a summary of the conversation."""
        if not self.conversation_history:
            return "No conversation yet."
        
        summary = "**Conversation Summary:**\n\n"
        for msg in self.conversation_history[-6:]:  # Last 6 messages
            role = "Student" if msg['role'] == 'user' else "Assistant"
            content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
            summary += f"**{role}:** {content}\n\n"
        
        return summary


# Interactive demo
if __name__ == "__main__":
    print("🎓 Course Recommender Chatbot Demo\n")
    
    # Create a sample student
    student = Student(student_id=1, name="Alice Johnson", email="alice@example.com")
    
    # Simulate some completed courses
    student.enroll_in_course("Python Fundamentals")
    student.complete_course("Python Fundamentals", grade=88.0)
    
    # Initialize recommender
    recommender = CourseRecommender()
    
    print(f"Student: {student.name}")
    print(f"Completed: {', '.join(student.get_completed_courses())}\n")
    print("="*60)
    print()
    
    # Test 1: Get recommendations directly
    print("Test 1: Direct Recommendations")
    print("-" * 60)
    recommendations = recommender.get_recommendations(student, num_recommendations=3)
    print(recommendations)
    print()
    
    # Test 2: Conversational interaction
    print("Test 2: Conversational Interaction")
    print("-" * 60)
    
    queries = [
        "Hi! I just finished Python Fundamentals. What should I take next?",
        "I'm interested in machine learning. Can you recommend something?",
        "Tell me more about Data Structures and Algorithms"
    ]
    
    for query in queries:
        print(f"Student: {query}")
        response = recommender.chat(student, query)
        print(f"Assistant: {response}\n")
    
    # Test 3: Explain specific course
    print("Test 3: Course Explanation")
    print("-" * 60)
    explanation = recommender.explain_course("Machine Learning Fundamentals")
    print(explanation)
    print()
    
    # Test 4: Learning path
    print("Test 4: Learning Path Planning")
    print("-" * 60)
    learning_path = recommender.plan_learning_path(student, "become a machine learning engineer", num_courses=5)
    print(learning_path)
    print()
    
    print("="*60)
    print("✅ Course Recommender is working! Ready to help students find their next course.")
