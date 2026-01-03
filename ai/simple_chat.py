# ai/simple_chat.py
"""
Level 5, Step 1: Simple Student Portal AI Chatbot
Your first AI chatbot with context about the student portal
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ai.config import validate_api_key, OPENAI_API_KEY, OPENAI_MODEL
from openai import OpenAI


class StudentPortalBot:
    """
    Simple chatbot for Student Portal with context
    """
    
    def __init__(self):
        """Initialize the chatbot"""
        if not validate_api_key():
            raise ValueError("API key not configured properly")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.model = OPENAI_MODEL
        self.conversation_history = []
        
        # System prompt - gives the AI context about your portal
        self.system_prompt = """You are a helpful AI assistant for a Student Portal system.

Portal Information:
- We have 26 students enrolled
- Available courses: Data Science, IT (Information Technology), Management, and English
- Students can enroll in multiple courses
- We track enrollment data and student activity
- We use machine learning to predict student enrollment patterns

Your role:
- Answer questions about the portal
- Help students understand course offerings
- Provide guidance on enrollments
- Be friendly and professional
- Keep responses concise (2-3 sentences)

Remember: You're helping students succeed in their education!"""
    
    def chat(self, user_message):
        """
        Send a message and get AI response
        
        Args:
            user_message (str): The user's message
            
        Returns:
            str: AI's response
        """
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Prepare messages (system prompt + history)
        messages = [
            {"role": "system", "content": self.system_prompt}
        ] + self.conversation_history
        
        try:
            # Call OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=150,
                temperature=0.7
            )
            
            # Extract AI response
            ai_message = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            # Add AI response to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_message
            })
            
            return ai_message, tokens_used
            
        except Exception as e:
            return f"Error: {str(e)}", 0
    
    def reset(self):
        """Clear conversation history"""
        self.conversation_history = []


def interactive_chat():
    """
    Run an interactive chat session
    """
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     🤖 Student Portal AI Assistant                        ║")
    print("║     Level 5, Step 1: Your First Chatbot                   ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    try:
        bot = StudentPortalBot()
        print("✅ Chatbot initialized successfully!")
        print("\n💬 Start chatting! (Type 'quit' to exit, 'reset' to clear history)\n")
        print("="*60)
        
        total_tokens = 0
        
        while True:
            # Get user input
            user_input = input("\n😊 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() == 'quit':
                print("\n👋 Goodbye! Thanks for chatting!")
                print(f"\n📊 Session Stats:")
                print(f"   Total tokens used: {total_tokens}")
                print(f"   Estimated cost: ${(total_tokens / 1000) * 0.002:.6f} USD")
                break
            
            if user_input.lower() == 'reset':
                bot.reset()
                print("🔄 Conversation history cleared!")
                continue
            
            # Get AI response
            print("\n🤖 AI: ", end="", flush=True)
            response, tokens = bot.chat(user_input)
            print(response)
            
            total_tokens += tokens
            print(f"   [Tokens: {tokens}]")
            print("-"*60)
    
    except ValueError as e:
        print(f"\n❌ Setup Error: {e}")
        print("\n📝 Please run: python ai/setup_openai.py")
    except KeyboardInterrupt:
        print("\n\n👋 Chat interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")


def demo_chat():
    """
    Run a demo conversation
    """
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     🎬 Demo: Student Portal AI in Action                  ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    try:
        bot = StudentPortalBot()
        
        demo_questions = [
            "Hello! What is this portal about?",
            "What courses do you offer?",
            "How many students are enrolled?",
            "I'm interested in technology. What should I study?"
        ]
        
        total_tokens = 0
        
        for question in demo_questions:
            print(f"\n😊 Student: {question}")
            print("🤖 AI: ", end="", flush=True)
            response, tokens = bot.chat(question)
            print(response)
            total_tokens += tokens
            print(f"   [Tokens: {tokens}]")
            print("-"*60)
        
        print(f"\n📊 Demo Stats:")
        print(f"   Questions asked: {len(demo_questions)}")
        print(f"   Total tokens: {total_tokens}")
        print(f"   Estimated cost: ${(total_tokens / 1000) * 0.002:.6f} USD")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_chat()
    else:
        interactive_chat()


if __name__ == "__main__":
    main()
