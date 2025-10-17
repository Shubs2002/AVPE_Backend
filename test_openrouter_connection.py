"""
Test OpenRouter API Connection

This script tests the connection to OpenRouter API to diagnose issues.
"""

import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv(".env.dev")

# Get configuration
OPENAI_API_KEY = os.getenv("OpenAI_API_KEY")
OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL")
SCRIPT_MODEL = os.getenv("SCRIPT_MODEL")

print("🔍 Testing OpenRouter API Connection")
print("=" * 60)
print(f"Base URL: {OPENROUTER_BASE_URL}")
print(f"Model: {SCRIPT_MODEL}")
print(f"API Key: {OPENAI_API_KEY[:20]}..." if OPENAI_API_KEY else "API Key: NOT SET")
print("=" * 60)

if not OPENAI_API_KEY:
    print("❌ ERROR: OpenAI_API_KEY not set in .env.dev")
    exit(1)

if not OPENROUTER_BASE_URL:
    print("❌ ERROR: OPENROUTER_BASE_URL not set in .env.dev")
    exit(1)

if not SCRIPT_MODEL:
    print("❌ ERROR: SCRIPT_MODEL not set in .env.dev")
    exit(1)

try:
    print("\n🚀 Creating OpenAI client...")
    client = OpenAI(
        base_url=OPENROUTER_BASE_URL,
        api_key=OPENAI_API_KEY
    )
    print("✅ Client created successfully")
    
    print("\n📤 Sending test request...")
    response = client.chat.completions.create(
        model=SCRIPT_MODEL,
        messages=[
            {
                "role": "user",
                "content": "Say 'Hello, World!' in JSON format: {\"message\": \"Hello, World!\"}"
            }
        ],
        max_tokens=100
    )
    
    print("✅ Request successful!")
    print("\n📥 Response:")
    print(f"Model: {response.model}")
    print(f"Content: {response.choices[0].message.content}")
    print("\n✅ OpenRouter connection is working!")
    
except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    print(f"\nError type: {type(e).__name__}")
    
    # Check for common issues
    if "Connection" in str(e) or "connection" in str(e):
        print("\n💡 Possible causes:")
        print("  1. No internet connection")
        print("  2. OpenRouter API is down")
        print("  3. Firewall blocking the connection")
        print("  4. Invalid base URL")
    elif "401" in str(e) or "Unauthorized" in str(e):
        print("\n💡 Possible causes:")
        print("  1. Invalid API key")
        print("  2. API key expired")
        print("  3. API key not activated")
    elif "429" in str(e) or "rate limit" in str(e).lower():
        print("\n💡 Possible causes:")
        print("  1. Rate limit exceeded")
        print("  2. Free tier quota exhausted")
        print("  3. Too many requests")
    elif "404" in str(e):
        print("\n💡 Possible causes:")
        print("  1. Invalid model name")
        print("  2. Model not available")
        print("  3. Wrong base URL")
    
    print("\n🔧 Troubleshooting steps:")
    print("  1. Check your internet connection")
    print("  2. Verify API key at: https://openrouter.ai/keys")
    print("  3. Check model availability at: https://openrouter.ai/models")
    print("  4. Try a different model (e.g., 'openai/gpt-3.5-turbo')")
    print("  5. Check OpenRouter status: https://status.openrouter.ai/")
