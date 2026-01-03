# ai/config.py
"""
Configuration module for OpenAI API
Loads API key securely from environment variables
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
BASE_DIR = Path(__file__).resolve().parent.parent
env_path = BASE_DIR / ".env"
load_dotenv(dotenv_path=env_path)

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
OPENAI_MAX_TOKENS = int(os.getenv("OPENAI_MAX_TOKENS", "500"))
OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))


def validate_api_key():
    """
    Validate that API key is configured
    Returns True if valid, False otherwise
    """
    if not OPENAI_API_KEY:
        print("❌ Error: OPENAI_API_KEY not found!")
        print("\n📝 Setup Instructions:")
        print("1. Copy .env.example to .env")
        print("2. Add your OpenAI API key to .env")
        print("3. Get API key from: https://platform.openai.com/api-keys")
        return False
    
    if OPENAI_API_KEY == "your_openai_api_key_here":
        print("❌ Error: Please replace the placeholder API key!")
        print("Update .env file with your real OpenAI API key")
        return False
    
    if not OPENAI_API_KEY.startswith("sk-"):
        print("⚠️ Warning: API key format looks incorrect")
        print("OpenAI keys usually start with 'sk-'")
        return False
    
    print("✅ API key loaded successfully!")
    return True


def get_api_config():
    """
    Get current API configuration
    """
    return {
        "model": OPENAI_MODEL,
        "max_tokens": OPENAI_MAX_TOKENS,
        "temperature": OPENAI_TEMPERATURE
    }


if __name__ == "__main__":
    print("🔧 Testing Configuration...")
    print(f"Model: {OPENAI_MODEL}")
    print(f"Max Tokens: {OPENAI_MAX_TOKENS}")
    print(f"Temperature: {OPENAI_TEMPERATURE}")
    validate_api_key()
