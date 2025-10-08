#!/usr/bin/env python3
"""
Test script for the new video download endpoint.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_download_video_endpoint():
    """Test the new download video endpoint."""
    print("📥 Testing Video Download Endpoint")
    print("=" * 50)
    
    # Test payload
    payload = {
        "video_url": "https://generativelanguage.googleapis.com/v1beta/files/lk8kxsr49b3j:download?alt=media",
        "filename": "test_download_video",
        "download_dir": "downloads"
    }
    
    print(f"📝 Test Payload:")
    print(f"   Video URL: {payload['video_url'][:60]}...")
    print(f"   Filename: {payload['filename']}")
    print(f"   Download Dir: {payload['download_dir']}")
    
    try:
        print("\n🚀 Starting download...")
        
        response = requests.post(f"{BASE_URL}/api/download-video", json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"✅ Download completed!")
        print(f"📊 Result:")
        print(f"   Success: {result.get('success', False)}")
        print(f"   File Path: {result.get('filepath', 'N/A')}")
        print(f"   Error: {result.get('error', 'None')}")
        
        return result.get('success', False)
        
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_download_with_custom_options():
    """Test download with different options."""
    print("\n🧪 Testing Download with Custom Options")
    print("=" * 45)
    
    # Test with different filename and directory
    payload = {
        "video_url": "https://generativelanguage.googleapis.com/v1beta/files/lk8kxsr49b3j:download?alt=media",
        "filename": "custom_harvest_moon_video",
        "download_dir": "downloads/custom"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/download-video", json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        print(f"✅ Custom download completed!")
        print(f"   File Path: {result.get('filepath', 'N/A')}")
        
        return result.get('success', False)
        
    except Exception as e:
        print(f"❌ Custom download failed: {e}")
        return False

def test_download_validation():
    """Test download endpoint validation."""
    print("\n🔍 Testing Download Validation")
    print("=" * 35)
    
    # Test 1: Missing video_url
    print("Test 1: Missing video_url")
    try:
        response = requests.post(f"{BASE_URL}/api/download-video", json={
            "filename": "test"
        })
        result = response.json()
        if not result.get('success') and 'video_url is required' in result.get('error', ''):
            print("   ✅ Correctly rejected missing video_url")
        else:
            print("   ❌ Should have rejected missing video_url")
    except Exception as e:
        print(f"   ❌ Validation test failed: {e}")
    
    # Test 2: Invalid URL
    print("\nTest 2: Invalid URL")
    try:
        response = requests.post(f"{BASE_URL}/api/download-video", json={
            "video_url": "https://invalid-url-that-does-not-exist.com/video.mp4",
            "filename": "test_invalid"
        })
        result = response.json()
        if not result.get('success'):
            print("   ✅ Correctly handled invalid URL")
        else:
            print("   ❌ Should have failed with invalid URL")
    except Exception as e:
        print(f"   ❌ Invalid URL test failed: {e}")

if __name__ == "__main__":
    print("🎯 Video Download Endpoint Test Suite")
    print("=" * 40)
    
    # Test the main functionality
    success1 = test_download_video_endpoint()
    
    # Test custom options
    success2 = test_download_with_custom_options()
    
    # Test validation
    test_download_validation()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"📥 Basic download: {'✅ Success' if success1 else '❌ Failed'}")
    print(f"🎨 Custom options: {'✅ Success' if success2 else '❌ Failed'}")
    
    if success1 and success2:
        print("\n🎉 All download tests passed!")
        print("\n💡 Usage Examples:")
        print("# Basic download")
        print('curl -X POST "http://localhost:8000/api/download-video" \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"video_url": "YOUR_VIDEO_URL", "filename": "my_video"}\'')
        print("\n# Custom directory")
        print('curl -X POST "http://localhost:8000/api/download-video" \\')
        print('  -H "Content-Type: application/json" \\')
        print('  -d \'{"video_url": "YOUR_VIDEO_URL", "filename": "my_video", "download_dir": "custom_folder"}\'')
    else:
        print("\n❌ Some tests failed. Check the server logs for details.")