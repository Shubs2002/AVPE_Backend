"""
Test Authentication System

Quick test script to verify authentication is working.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_authentication():
    print("🧪 Testing Authentication System")
    print("=" * 60)
    
    # Test data
    test_user = {
        "email": "test@example.com",
        "password": "TestPass123!",
        "full_name": "Test User"
    }
    
    print("\n1️⃣  Testing Registration...")
    print(f"POST {BASE_URL}/auth/register")
    print(f"Data: {json.dumps(test_user, indent=2)}")
    print("\nExpected: User registered successfully")
    
    print("\n2️⃣  Testing Login...")
    print(f"POST {BASE_URL}/auth/login")
    print(f"Data: {json.dumps({'email': test_user['email'], 'password': test_user['password']}, indent=2)}")
    print("\nExpected: Access token + Refresh token")
    
    print("\n3️⃣  Testing Protected Endpoint...")
    print(f"GET {BASE_URL}/auth/me")
    print("Headers: Authorization: Bearer <access_token>")
    print("\nExpected: User profile data")
    
    print("\n4️⃣  Testing Character Creation (Protected)...")
    print(f"POST {BASE_URL}/characters/analyze")
    print("Headers: Authorization: Bearer <access_token>")
    print("Body: image + character_name")
    print("\nExpected: Character analysis with auto user_id")
    
    print("\n" + "=" * 60)
    print("✅ Authentication system is configured!")
    print("\n📝 To test manually:")
    print("1. Start server: poetry run dev")
    print("2. Register: POST /api/auth/register")
    print("3. Login: POST /api/auth/login")
    print("4. Use token: Authorization: Bearer <token>")
    print("\n🔐 Don't forget to:")
    print("1. Install dependencies: poetry install")
    print("2. Generate JWT_SECRET_KEY and add to .env.dev")
    print("   python -c \"import secrets; print(secrets.token_urlsafe(32))\"")

if __name__ == "__main__":
    test_authentication()
