#!/usr/bin/env python3
"""
Test script for the new movie auto generation parameters.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_universal_content():
    """Test Universal (U) content generation."""
    print("🎬 Test 1: Universal Content")
    print("=" * 50)
    
    payload = {
        "idea": "A heartwarming story about friendship",
        "total_segments": 10,
        "content_rating": "U",
        "no_narration": False,
        "save_to_files": True,
        "output_directory": "test_universal"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-movie-auto", json=payload)
        response.raise_for_status()
        
        result = response.json()["result"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('story_title')}")
        print(f"   Rating: U (Universal)")
        print(f"   Segments: {result['generation_summary']['total_segments_generated']}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_adult_content_with_cliffhangers():
    """Test Adult (A) content with cliffhangers."""
    print("\n🎬 Test 2: Adult Content with Cliffhangers")
    print("=" * 50)
    
    payload = {
        "idea": "A dark psychological thriller",
        "total_segments": 20,
        "content_rating": "A",
        "cliffhanger_interval": 10,
        "save_to_files": True,
        "output_directory": "test_adult"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-movie-auto", json=payload)
        response.raise_for_status()
        
        result = response.json()["result"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('story_title')}")
        print(f"   Rating: A (Adult)")
        print(f"   Cliffhangers: Every 10 segments")
        print(f"   Segments: {result['generation_summary']['total_segments_generated']}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_no_narration():
    """Test content with no narration."""
    print("\n🎬 Test 3: No Narration (Dialogue Only)")
    print("=" * 50)
    
    payload = {
        "idea": "A witty conversation between two friends",
        "total_segments": 5,
        "content_rating": "U/A",
        "no_narration": True,
        "save_to_files": True,
        "output_directory": "test_no_narration"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-movie-auto", json=payload)
        response.raise_for_status()
        
        result = response.json()["result"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('story_title')}")
        print(f"   Rating: U/A (Parental Guidance)")
        print(f"   Narration: None (dialogue only)")
        print(f"   Segments: {result['generation_summary']['total_segments_generated']}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_narration_only_first():
    """Test content with narration only in first segment."""
    print("\n🎬 Test 4: Narration Only in First Segment")
    print("=" * 50)
    
    payload = {
        "idea": "An adventure that starts with context",
        "total_segments": 8,
        "content_rating": "U",
        "narration_only_first": True,
        "save_to_files": True,
        "output_directory": "test_narration_first"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-movie-auto", json=payload)
        response.raise_for_status()
        
        result = response.json()["result"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('story_title')}")
        print(f"   Rating: U (Universal)")
        print(f"   Narration: Only in first segment")
        print(f"   Segments: {result['generation_summary']['total_segments_generated']}")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

def test_invalid_content_rating():
    """Test validation of invalid content rating."""
    print("\n🧪 Test 5: Invalid Content Rating (Validation)")
    print("=" * 50)
    
    payload = {
        "idea": "A test story",
        "total_segments": 5,
        "content_rating": "INVALID"  # Invalid rating
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-movie-auto", json=payload)
        
        if response.status_code == 400:
            error = response.json()
            print(f"✅ Validation working correctly!")
            print(f"   Error: {error.get('detail')}")
            return True
        else:
            print(f"❌ Should have rejected invalid rating")
            return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_all_parameters_combined():
    """Test all parameters combined."""
    print("\n🎬 Test 6: All Parameters Combined")
    print("=" * 50)
    
    payload = {
        "idea": "A complex multi-layered story",
        "total_segments": 30,
        "segments_per_set": 10,
        "content_rating": "U/A",
        "no_narration": False,
        "narration_only_first": False,
        "cliffhanger_interval": 15,
        "save_to_files": True,
        "output_directory": "test_combined"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/generate-movie-auto", json=payload)
        response.raise_for_status()
        
        result = response.json()["result"]
        print(f"✅ Success!")
        print(f"   Title: {result.get('story_title')}")
        print(f"   Rating: U/A (Parental Guidance)")
        print(f"   Cliffhangers: Every 15 segments")
        print(f"   Segments: {result['generation_summary']['total_segments_generated']}")
        
        # Check metadata
        gen_info = result['story_metadata']['generation_info']
        print(f"\n   Metadata Stored:")
        print(f"   - no_narration: {gen_info.get('no_narration')}")
        print(f"   - narration_only_first: {gen_info.get('narration_only_first')}")
        print(f"   - cliffhanger_interval: {gen_info.get('cliffhanger_interval')}")
        print(f"   - content_rating: {gen_info.get('content_rating')}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False

if __name__ == "__main__":
    print("🎯 Movie Auto Generation - New Parameters Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run all tests
    results.append(("Universal Content", test_universal_content()))
    results.append(("Adult with Cliffhangers", test_adult_content_with_cliffhangers()))
    results.append(("No Narration", test_no_narration()))
    results.append(("Narration Only First", test_narration_only_first()))
    results.append(("Invalid Rating Validation", test_invalid_content_rating()))
    results.append(("All Parameters Combined", test_all_parameters_combined()))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_passed = sum(1 for _, success in results if success)
    total_tests = len(results)
    
    print("\n" + "=" * 60)
    print(f"Total: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 All tests passed!")
        print("\n💡 New Parameters Available:")
        print("   - no_narration: Control narration presence")
        print("   - narration_only_first: Narration only in first segment")
        print("   - cliffhanger_interval: Add cliffhangers every N segments")
        print("   - content_rating: U, U/A, or A rating")
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed")
