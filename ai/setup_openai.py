# ai/setup_openai.py
"""
Level 5, Step 1: OpenAI Setup and First API Call
Tests OpenAI connection and makes first API call
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ai.config import validate_api_key, OPENAI_API_KEY, OPENAI_MODEL
from openai import OpenAI


def test_openai_connection():
    """
    Test OpenAI API connection with a simple call
    """
    print("╔════════════════════════════════════════════════════════════╗")
    print("║  Level 5, Step 1: OpenAI Setup Test                       ║")
    print("╚════════════════════════════════════════════════════════════╝\n")
    
    # Validate API key first
    if not validate_api_key():
        return False
    
    try:
        # Initialize OpenAI client
        print("\n🔌 Connecting to OpenAI API...")
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Make a simple test call
        print(f"🤖 Using model: {OPENAI_MODEL}")
        print("📤 Sending test message...\n")
        
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant."
                },
                {
                    "role": "user",
                    "content": "Say 'Hello! OpenAI is working!' in one sentence."
                }
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        # Extract response
        ai_message = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        print("✅ Connection successful!\n")
        print("="*60)
        print("🤖 AI Response:")
        print(f"   {ai_message}")
        print("="*60)
        print(f"\n📊 Tokens Used: {tokens_used}")
        print(f"💰 Estimated Cost: ${(tokens_used / 1000) * 0.002:.6f} USD")
        
        print("\n" + "="*60)
        print("🎉 OpenAI Setup Complete!")
        print("="*60)
        print("\n✅ What this means:")
        print("   • Your API key is working")
        print("   • You can now build AI applications")
        print("   • Ready for Step 2: Prompt Engineering")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error connecting to OpenAI: {e}")
        print("\n🔍 Troubleshooting:")
        print("   • Check your API key is correct")
        print("   • Verify you have API credits")
        print("   • Check your internet connection")
        print("   • Visit: https://platform.openai.com/account/billing")
        return False


def show_api_info():
    """
    Display helpful information about OpenAI API
    """
    print("\n📚 OpenAI API Information:")
    print("="*60)
    print("🌐 Dashboard: https://platform.openai.com/")
    print("🔑 API Keys: https://platform.openai.com/api-keys")
    print("💰 Usage: https://platform.openai.com/account/usage")
    print("📖 Docs: https://platform.openai.com/docs/")
    print("="*60)
    
    print("\n💡 Pricing (as of Dec 2025):")
    print("   • GPT-3.5-turbo: ~$0.002 per 1K tokens")
    print("   • GPT-4: ~$0.03 per 1K tokens")
    print("   • Average chat: 100-300 tokens")
    print("   • This test: ~50 tokens (~$0.0001)")
    print("="*60)


def main():
    """Main execution"""
    success = test_openai_connection()
    
    if success:
        show_api_info()
        print("\n🚀 Next Steps:")
        print("   1. Run: python ai/simple_chat.py")
        print("   2. Start building your AI chatbot!")
    else:
        print("\n❌ Setup incomplete. Please fix the issues above.")


if __name__ == "__main__":
    main()
