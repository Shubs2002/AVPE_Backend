"""
Test script for creating characters from images

This script tests the complete character creation pipeline:
1. Upload image
2. Analyze with Gemini
3. Remove background
4. Upload to Cloudinary
5. Save to MongoDB
"""

import requests
import os

# API endpoint
BASE_URL = "http://localhost:8000/api"
ENDPOINT = f"{BASE_URL}/create-character-from-image"

def test_create_character_from_image(image_path: str, character_name: str):
    """
    Test creating a character from an image
    
    Args:
        image_path: Path to the image file
        character_name: Name for the character
    """
    print(f"\n{'='*60}")
    print(f"🎭 Testing Character Creation from Image")
    print(f"{'='*60}\n")
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return
    
    print(f"📸 Image: {image_path}")
    print(f"📝 Character Name: {character_name}")
    print(f"\n🚀 Sending request to API...")
    
    try:
        # Prepare the request
        with open(image_path, 'rb') as image_file:
            files = {
                'image': (os.path.basename(image_path), image_file, 'image/png')
            }
            data = {
                'character_name': character_name,
                'remove_background': 'true',
                'upload_to_cloudinary': 'true'
            }
            
            # Send request
            response = requests.post(ENDPOINT, files=files, data=data)
        
        # Check response
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"\n✅ Character created successfully!")
                print(f"\n{'='*60}")
                print(f"📊 RESULTS")
                print(f"{'='*60}")
                print(f"🆔 Character ID: {result.get('character_id')}")
                print(f"📝 Character Name: {result.get('character_name')}")
                print(f"🖼️ Image URL: {result.get('image_url')}")
                print(f"📅 Created At: {result.get('created_at')}")
                
                # Show character data summary
                character_data = result.get('character_data', {})
                if 'characters_roster' in character_data:
                    roster = character_data['characters_roster'][0]
                    print(f"\n{'='*60}")
                    print(f"👤 CHARACTER DETAILS")
                    print(f"{'='*60}")
                    print(f"Name: {roster.get('name')}")
                    
                    physical = roster.get('physical_appearance', {})
                    print(f"Gender: {physical.get('gender')}")
                    print(f"Age: {physical.get('estimated_age')}")
                    print(f"Height: {physical.get('height')}")
                    print(f"Build: {physical.get('body_type')}")
                    
                    print(f"\nPersonality: {roster.get('personality')}")
                    print(f"Role: {roster.get('role')}")
                
                print(f"\n{'='*60}\n")
            else:
                print(f"\n❌ Failed: {result.get('error')}")
        else:
            print(f"\n❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


def test_without_cloudinary(image_path: str, character_name: str):
    """
    Test creating a character without Cloudinary upload
    (useful if Cloudinary is not configured)
    """
    print(f"\n{'='*60}")
    print(f"🎭 Testing Character Creation (No Cloudinary)")
    print(f"{'='*60}\n")
    
    if not os.path.exists(image_path):
        print(f"❌ Image file not found: {image_path}")
        return
    
    print(f"📸 Image: {image_path}")
    print(f"📝 Character Name: {character_name}")
    print(f"\n🚀 Sending request to API...")
    
    try:
        with open(image_path, 'rb') as image_file:
            files = {
                'image': (os.path.basename(image_path), image_file, 'image/png')
            }
            data = {
                'character_name': character_name,
                'remove_background': 'true',
                'upload_to_cloudinary': 'false'  # Skip Cloudinary
            }
            
            response = requests.post(ENDPOINT, files=files, data=data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get('success'):
                print(f"\n✅ Character created successfully (without Cloudinary)!")
                print(f"🆔 Character ID: {result.get('character_id')}")
                print(f"📝 Character Name: {result.get('character_name')}")
                print(f"📅 Created At: {result.get('created_at')}")
            else:
                print(f"\n❌ Failed: {result.get('error')}")
        else:
            print(f"\n❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
    
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    # Example usage - replace with your image path
    image_path = "path/to/your/character/image.png"
    character_name = "My Character"
    
    print("\n" + "="*60)
    print("🧪 CHARACTER CREATION FROM IMAGE - TEST SUITE")
    print("="*60)
    print("\nMake sure:")
    print("1. ✅ Server is running (python -m uvicorn src.main:app --reload)")
    print("2. ✅ MongoDB is connected")
    print("3. ✅ Cloudinary credentials are in .env.dev")
    print("4. ✅ Image file exists at the specified path")
    print("\n" + "="*60)
    
    # Test with Cloudinary
    # test_create_character_from_image(image_path, character_name)
    
    # Test without Cloudinary (if not configured)
    # test_without_cloudinary(image_path, character_name)
    
    print("\n💡 To run the test:")
    print("1. Update 'image_path' and 'character_name' variables above")
    print("2. Uncomment one of the test function calls")
    print("3. Run: python test_create_character_from_image.py")
