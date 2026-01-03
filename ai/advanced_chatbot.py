# ai/advanced_chatbot.py
"""
Level 5, Step 2: Advanced Student Portal Chatbot
Improved chatbot using prompt engineering techniques
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ai.config import validate_api_key, OPENAI_API_KEY
from ai.prompt_templates import SYSTEM_PROMPTS, build_prompt
from openai import OpenAI


class AdvancedStudentBot:
    """
    Enhanced chatbot with prompt engineering techniques
    """
    
    def __init__(self, temperature=0.7, use_few_shot=False):
        """
        Initialize the advanced chatbot
        
        Args:
            temperature (float): Creativity setting (0.0-2.0)
            use_few_shot (bool): Use few-shot examples
        """
        if not validate_api_key():
            raise ValueError("API key not configured")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.temperature = temperature
        self.use_few_shot = use_few_shot
        self.conversation_history = []
        self.total_tokens = 0
        
        # Use expert system prompt
        self.system_prompt = SYSTEM_PROMPTS["student_advisor"]
    
    def chat(self, user_message, constraints=None):
        """
        Enhanced chat with prompt engineering
        
        Args:
            user_message (str): User's message
            constraints (list, optional): Constraints to apply
            
        Returns:
            tuple: (response, tokens_used)
        """
        # Build enhanced prompt
        if self.use_few_shot and "recommend" in user_message.lower():
            system_prompt, enhanced_message = build_prompt(
                "student_advisor",
                user_message,
                few_shot="course_recommendation",
                constraints=constraints
            )
        else:
            system_prompt = self.system_prompt
            enhanced_message = user_message
            
            if constraints:
                constraint_text = "\n".join([
                    f"Constraint: {c}" for c in constraints
                ])
                enhanced_message = f"{constraint_text}\n\n{user_message}"
        
        # Add to history
        self.conversation_history.append({
            "role": "user",
            "content": enhanced_message
        })
        
        # Prepare messages
        messages = [
            {"role": "system", "content": system_prompt}
        ] + self.conversation_history
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
                temperature=self.temperature,
                max_tokens=250
            )
            
            ai_message = response.choices[0].message.content
            tokens = response.usage.total_tokens
            self.total_tokens += tokens
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": ai_message
            })
            
            return ai_message, tokens
            
        except Exception as e:
            return f"Error: {str(e)}", 0
    
    def reset(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_stats(self):
        """Get conversation statistics"""
        return {
            "messages": len(self.conversation_history) // 2,
            "total_tokens": self.total_tokens,
            "cost": (self.total_tokens / 1000) * 0.002,
            "temperature": self.temperature,
            "few_shot_enabled": self.use_few_shot
        }


def interactive_chat():
    """Run interactive advanced chatbot"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║     🚀 Advanced Student Portal AI Assistant                ║")
    print("║     Level 5, Step 2: Prompt Engineering Enhanced          ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    print("🎛️ Configuration Options:")
    print("1. Standard mode (Temperature: 0.7)")
    print("2. Factual mode (Temperature: 0.0)")
    print("3. Creative mode (Temperature: 1.2)")
    print("4. Expert mode (With few-shot learning)\n")
    
    choice = input("Choose mode (1-4) [default: 1]: ").strip() or "1"
    
    config = {
        "1": (0.7, False, "Standard"),
        "2": (0.0, False, "Factual"),
        "3": (1.2, False, "Creative"),
        "4": (0.7, True, "Expert")
    }
    
    temperature, few_shot, mode_name = config.get(choice, (0.7, False, "Standard"))
    
    try:
        bot = AdvancedStudentBot(temperature=temperature, use_few_shot=few_shot)
        
        print(f"\n✅ {mode_name} mode activated!")
        print(f"   Temperature: {temperature}")
        print(f"   Few-shot learning: {'Enabled' if few_shot else 'Disabled'}")
        print("\n💬 Start chatting! (Commands: 'quit', 'reset', 'stats')\n")
        print("="*60)
        
        while True:
            user_input = input("\n😊 You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() == 'quit':
                stats = bot.get_stats()
                print("\n" + "="*60)
                print("📊 Session Statistics:")
                print(f"   Messages exchanged: {stats['messages']}")
                print(f"   Total tokens: {stats['total_tokens']}")
                print(f"   Total cost: ${stats['cost']:.6f}")
                print(f"   Mode: {mode_name} (T={stats['temperature']})")
                print("="*60)
                print("\n👋 Thanks for chatting! Goodbye!")
                break
            
            if user_input.lower() == 'reset':
                bot.reset()
                print("🔄 Conversation reset!")
                continue
            
            if user_input.lower() == 'stats':
                stats = bot.get_stats()
                print(f"\n📊 Current stats:")
                print(f"   Messages: {stats['messages']}")
                print(f"   Tokens: {stats['total_tokens']}")
                print(f"   Cost: ${stats['cost']:.6f}")
                continue
            
            # Get response
            print("\n🤖 AI: ", end="", flush=True)
            response, tokens = bot.chat(user_input)
            print(response)
            print(f"   [Tokens: {tokens} | Mode: {mode_name}]")
            print("-"*60)
    
    except ValueError as e:
        print(f"\n❌ Setup error: {e}")
    except KeyboardInterrupt:
        print("\n\n👋 Chat interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")


def demo_comparison():
    """Demo showing improvement from Step 1 to Step 2"""
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  🎬 Demo: Step 1 vs Step 2 Comparison                     ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    test_questions = [
        "What should I study?",
        "I'm 22 and interested in AI and data",
        "Which course has best job prospects?"
    ]
    
    try:
        print("📊 Testing with same questions...\n")
        
        for question in test_questions:
            print("="*60)
            print(f"❓ Question: {question}\n")
            
            # Basic bot (Step 1 style)
            print("🔵 Basic Bot (Step 1):")
            basic_bot = AdvancedStudentBot(temperature=0.7, use_few_shot=False)
            basic_bot.system_prompt = SYSTEM_PROMPTS["generic"]
            response1, _ = basic_bot.chat(question)
            print(f"   {response1}\n")
            
            # Advanced bot (Step 2 style)
            print("🚀 Advanced Bot (Step 2 - Expert Mode):")
            advanced_bot = AdvancedStudentBot(temperature=0.7, use_few_shot=True)
            response2, _ = advanced_bot.chat(question)
            print(f"   {response2}\n")
        
        print("="*60)
        print("\n💡 Notice the difference:")
        print("   • Basic: Generic, less helpful")
        print("   • Advanced: Specific, expert, actionable")
        print("\n🎯 This is the power of prompt engineering!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")


def main():
    """Main execution"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        demo_comparison()
    else:
        interactive_chat()


if __name__ == "__main__":
    main()
