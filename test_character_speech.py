"""
Test Character Speech Feature

Tests the complete workflow:
1. Analyze character (AI detects can_speak)
2. Create character (with can_speak field)
3. Generate story (auto-detects speech from character)
"""

import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.dev')

BASE_URL = "http://localhost:8000/api"

def get_auth_token():
    """Get authentication token"""
    # Replace with your actual credentials
    response = requests.post(
        f"{BASE_URL}/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword"
        }
    )
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.text}")
        return None

def test_analyze_character(token, image_path, character_name):
    """Test Step 1: Analyze character"""
    print(f"\n🔍 Step 1: Analyzing character '{character_name}'...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {'character_name': character_name}
        
        response = requests.post(
            f"{BASE_URL}/characters/analyze",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Analysis complete!")
        print(f"   Character ID: {result['character_id']}")
        print(f"   Gender: {result['gender']}")
        print(f"   Can Speak: {result['can_speak']}")
        print(f"   Voice: {result['voice_description'][:80]}...")
        print(f"   Keywords: {result['keywords'][:80]}...")
        return result
    else:
        print(f"❌ Analysis failed: {response.text}")
        return None

def test_create_character(token, image_path, analysis_result):
    """Test Step 2: Create character"""
    print(f"\n💾 Step 2: Creating character...")
    
    headers = {"Authorization": f"Bearer {token}"}
    
    with open(image_path, 'rb') as f:
        files = {'image': f}
        data = {
            'character_id': analysis_result['character_id'],
            'character_name': analysis_result['character_name'],
            'gender': analysis_result['gender'],
            'voice_description': analysis_result['voice_description'],
            'keywords': analysis_result['keywords'],
            'is_private': 'true',
            'can_speak': str(analysis_result['can_speak']).lower()
        }
        
        response = requests.post(
            f"{BASE_URL}/characters/create",
            headers=headers,
            files=files,
            data=data
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Character created!")
        print(f"   Character ID: {result['character_id']}")
        print(f"   Can Speak: {result['can_speak']}")
        print(f"   Cloudinary URL: {result['cloudinary_url'][:60]}...")
        return result
    else:
        print(f"❌ Creation failed: {response.text}")
        return None

def test_generate_story(token, character_id, idea):
    """Test Step 3: Generate story"""
    print(f"\n📝 Step 3: Generating story...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "idea": idea,
        "character_id": character_id,
        "num_segments": 3  # Small number for testing
    }
    
    response = requests.post(
        f"{BASE_URL}/v2/generate-daily-character",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Story generated!")
        print(f"   Title: {result['title']}")
        print(f"   Segments: {len(result['segments'])}")
        
        # Check character metadata
        metadata = result.get('character_metadata', {})
        characters = metadata.get('characters', [])
        if characters:
            char = characters[0]
            print(f"   Character: {char['character_name']}")
            print(f"   Can Speak: {char['can_speak']}")
            print(f"   Voice: {char['voice_description'][:60]}...")
        
        # Check if story has dialogue or creature sounds
        first_segment = result['segments'][0]
        if 'dialogue' in first_segment:
            print(f"   ✅ Story includes dialogue (character can speak)")
        elif 'creature_sounds' in first_segment:
            print(f"   ✅ Story uses creature sounds (character cannot speak)")
        
        return result
    else:
        print(f"❌ Story generation failed: {response.text}")
        return None

def test_multi_character_story(token, character_ids, idea):
    """Test multi-character story with mixed speech capabilities"""
    print(f"\n👥 Testing multi-character story...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "idea": idea,
        "character_ids": character_ids,
        "num_segments": 3
    }
    
    response = requests.post(
        f"{BASE_URL}/v2/generate-daily-character",
        headers=headers,
        json=payload
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Multi-character story generated!")
        print(f"   Title: {result['title']}")
        
        # Check each character's speech capability
        metadata = result.get('character_metadata', {})
        characters = metadata.get('characters', [])
        
        print(f"\n   Characters:")
        for char in characters:
            print(f"   - {char['character_name']}: can_speak={char['can_speak']}")
        
        # Check if any character can speak
        any_can_speak = any(char['can_speak'] for char in characters)
        print(f"\n   Speech enabled: {any_can_speak}")
        
        return result
    else:
        print(f"❌ Multi-character story failed: {response.text}")
        return None

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 Testing Character Speech Feature")
    print("=" * 60)
    
    # Get auth token
    token = get_auth_token()
    if not token:
        print("❌ Cannot proceed without authentication")
        return
    
    # Test with a sample image (replace with your actual image path)
    image_path = "test_character.jpg"
    
    if not os.path.exists(image_path):
        print(f"\n⚠️  Image file not found: {image_path}")
        print("Please provide a test image and update the path in the script.")
        return
    
    # Test 1: Non-speaking character (creature)
    print("\n" + "=" * 60)
    print("Test 1: Non-Speaking Character (Creature)")
    print("=" * 60)
    
    analysis = test_analyze_character(token, image_path, "Floof")
    if analysis:
        character = test_create_character(token, image_path, analysis)
        if character:
            story = test_generate_story(
                token,
                character['character_id'],
                "Character discovers a magical glowing object"
            )
    
    # Test 2: Speaking character (human)
    # You would need a different image for this test
    # print("\n" + "=" * 60)
    # print("Test 2: Speaking Character (Human)")
    # print("=" * 60)
    # 
    # analysis2 = test_analyze_character(token, "human_character.jpg", "Hero")
    # if analysis2:
    #     character2 = test_create_character(token, "human_character.jpg", analysis2)
    #     if character2:
    #         story2 = test_generate_story(
    #             token,
    #             character2['character_id'],
    #             "Character gives a motivational speech"
    #         )
    
    print("\n" + "=" * 60)
    print("✅ Testing Complete!")
    print("=" * 60)

if __name__ == "__main__":
    main()
