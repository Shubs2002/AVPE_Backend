"""
Test Character Privacy Feature

Tests the complete 2-step character creation with privacy controls:
1. Analyze character image (Step 1)
2. Create character with is_private flag (Step 2)
3. List characters with privacy filtering (Step 4 - COMPLETED)

Privacy Rules:
- Private characters (is_private=true): Only visible to creator
- Public characters (is_private=false): Visible to everyone
"""

import requests
import json
from pathlib import Path

# API Configuration
BASE_URL = "http://localhost:8000/api"

# Test users (you need to register these first)
USER1_EMAIL = "user1@example.com"
USER1_PASSWORD = "password123"

USER2_EMAIL = "user2@example.com"
USER2_PASSWORD = "password123"


def register_and_login(email: str, password: str, full_name: str) -> dict:
    """Register and login a user, return tokens"""
    
    # Step 1: Send OTP
    print(f"\n📧 Sending OTP to {email}...")
    response = requests.post(f"{BASE_URL}/auth/send-otp", json={"email": email})
    print(f"Response: {response.json()}")
    
    # Step 2: Get OTP from user
    otp = input(f"Enter OTP sent to {email}: ")
    
    # Step 3: Register with OTP
    print(f"\n🔐 Registering user...")
    response = requests.post(f"{BASE_URL}/auth/register", json={
        "email": email,
        "password": password,
        "full_name": full_name,
        "otp": otp
    })
    
    if response.status_code != 200:
        print(f"❌ Registration failed: {response.json()}")
        # Try to login instead
        print(f"🔑 Trying to login...")
        response = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
    
    result = response.json()
    print(f"✅ User authenticated: {result.get('user', {}).get('user_id')}")
    
    return {
        "access_token": result["access_token"],
        "refresh_token": result["refresh_token"],
        "user": result["user"]
    }


def create_character(image_path: str, character_name: str, is_private: bool, access_token: str) -> dict:
    """Create a character with privacy setting"""
    
    print(f"\n🎭 Creating character: {character_name} (Private: {is_private})")
    
    # Step 1: Analyze character image
    print(f"🔍 Step 1: Analyzing character image...")
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {"character_name": character_name}
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.post(
            f"{BASE_URL}/characters/analyze",
            files=files,
            data=data,
            headers=headers
        )
    
    if response.status_code != 200:
        print(f"❌ Analysis failed: {response.json()}")
        return None
    
    analysis = response.json()
    print(f"✅ Analysis complete:")
    print(f"   Character ID: {analysis['character_id']}")
    print(f"   Gender: {analysis['gender']}")
    print(f"   Voice: {analysis['voice_description'][:50]}...")
    print(f"   Keywords: {analysis['keywords'][:80]}...")
    
    # Step 2: Create character with privacy setting
    print(f"\n💾 Step 2: Creating character with is_private={is_private}...")
    with open(image_path, "rb") as f:
        files = {"image": f}
        data = {
            "character_id": analysis["character_id"],
            "character_name": analysis["character_name"],
            "gender": analysis["gender"],
            "voice_description": analysis["voice_description"],
            "keywords": analysis["keywords"],
            "is_private": str(is_private).lower()  # Convert to string for form data
        }
        headers = {"Authorization": f"Bearer {access_token}"}
        
        response = requests.post(
            f"{BASE_URL}/characters/create",
            files=files,
            data=data,
            headers=headers
        )
    
    if response.status_code != 200:
        print(f"❌ Creation failed: {response.json()}")
        return None
    
    character = response.json()
    print(f"✅ Character created successfully!")
    print(f"   Character ID: {character['character_id']}")
    print(f"   Cloudinary URL: {character['cloudinary_url']}")
    
    return character


def list_characters(access_token: str = None) -> dict:
    """List characters with optional authentication"""
    
    if access_token:
        print(f"\n📋 Listing characters (authenticated)...")
        headers = {"Authorization": f"Bearer {access_token}"}
    else:
        print(f"\n📋 Listing characters (unauthenticated)...")
        headers = {}
    
    response = requests.get(f"{BASE_URL}/characters", headers=headers)
    
    if response.status_code != 200:
        print(f"❌ Failed to list characters: {response.json()}")
        return None
    
    result = response.json()
    print(f"✅ Found {result['total']} characters:")
    
    for char in result["characters"]:
        privacy = "🔒 Private" if char.get("is_private") else "🌍 Public"
        print(f"   {privacy} - {char['character_name']} (ID: {char['character_id'][:15]}...)")
        print(f"      User: {char.get('user_id', 'N/A')}")
    
    return result


def test_privacy_feature():
    """Test the complete privacy feature"""
    
    print("=" * 80)
    print("🧪 TESTING CHARACTER PRIVACY FEATURE")
    print("=" * 80)
    
    # Check if test image exists
    test_image = "test_character.jpg"
    if not Path(test_image).exists():
        print(f"\n⚠️  Test image not found: {test_image}")
        print(f"Please provide a character image file named '{test_image}'")
        return
    
    # Register/Login User 1
    print("\n" + "=" * 80)
    print("👤 USER 1 SETUP")
    print("=" * 80)
    user1 = register_and_login(USER1_EMAIL, USER1_PASSWORD, "Test User 1")
    
    # Register/Login User 2
    print("\n" + "=" * 80)
    print("👤 USER 2 SETUP")
    print("=" * 80)
    user2 = register_and_login(USER2_EMAIL, USER2_PASSWORD, "Test User 2")
    
    # User 1 creates a PRIVATE character
    print("\n" + "=" * 80)
    print("🔒 USER 1: CREATE PRIVATE CHARACTER")
    print("=" * 80)
    char1_private = create_character(
        test_image,
        "Private Hero",
        is_private=True,
        access_token=user1["access_token"]
    )
    
    # User 1 creates a PUBLIC character
    print("\n" + "=" * 80)
    print("🌍 USER 1: CREATE PUBLIC CHARACTER")
    print("=" * 80)
    char1_public = create_character(
        test_image,
        "Public Hero",
        is_private=False,
        access_token=user1["access_token"]
    )
    
    # User 2 creates a PUBLIC character
    print("\n" + "=" * 80)
    print("🌍 USER 2: CREATE PUBLIC CHARACTER")
    print("=" * 80)
    char2_public = create_character(
        test_image,
        "Another Public Hero",
        is_private=False,
        access_token=user2["access_token"]
    )
    
    # Test 1: User 1 lists characters (should see their private + public + other public)
    print("\n" + "=" * 80)
    print("🧪 TEST 1: USER 1 LISTS CHARACTERS")
    print("Expected: Private Hero (own), Public Hero (own), Another Public Hero (other)")
    print("=" * 80)
    user1_list = list_characters(user1["access_token"])
    
    # Test 2: User 2 lists characters (should NOT see User 1's private character)
    print("\n" + "=" * 80)
    print("🧪 TEST 2: USER 2 LISTS CHARACTERS")
    print("Expected: Another Public Hero (own), Public Hero (other)")
    print("Should NOT see: Private Hero (User 1's private)")
    print("=" * 80)
    user2_list = list_characters(user2["access_token"])
    
    # Test 3: Unauthenticated user lists characters (should only see public)
    print("\n" + "=" * 80)
    print("🧪 TEST 3: UNAUTHENTICATED USER LISTS CHARACTERS")
    print("Expected: Public Hero, Another Public Hero")
    print("Should NOT see: Private Hero")
    print("=" * 80)
    public_list = list_characters()
    
    # Summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    
    if user1_list and user2_list and public_list:
        user1_count = user1_list["total"]
        user2_count = user2_list["total"]
        public_count = public_list["total"]
        
        print(f"✅ User 1 sees: {user1_count} characters (should be 3)")
        print(f"✅ User 2 sees: {user2_count} characters (should be 2)")
        print(f"✅ Public sees: {public_count} characters (should be 2)")
        
        # Verify privacy logic
        user1_names = [c["character_name"] for c in user1_list["characters"]]
        user2_names = [c["character_name"] for c in user2_list["characters"]]
        public_names = [c["character_name"] for c in public_list["characters"]]
        
        print(f"\n🔍 Privacy Verification:")
        print(f"   User 1 can see 'Private Hero': {'✅' if 'Private Hero' in user1_names else '❌'}")
        print(f"   User 2 CANNOT see 'Private Hero': {'✅' if 'Private Hero' not in user2_names else '❌'}")
        print(f"   Public CANNOT see 'Private Hero': {'✅' if 'Private Hero' not in public_names else '❌'}")
        print(f"   Everyone can see 'Public Hero': {'✅' if 'Public Hero' in public_names else '❌'}")
        
        if (user1_count == 3 and user2_count == 2 and public_count == 2 and
            'Private Hero' in user1_names and 
            'Private Hero' not in user2_names and
            'Private Hero' not in public_names):
            print(f"\n🎉 ALL TESTS PASSED! Privacy feature working correctly!")
        else:
            print(f"\n⚠️  Some tests failed. Please review the results above.")
    else:
        print(f"❌ Tests failed - could not retrieve character lists")


if __name__ == "__main__":
    test_privacy_feature()
