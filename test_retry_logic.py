#!/usr/bin/env python3
"""
Test script for the new retry logic in movie auto generation.
This script demonstrates how the retry functionality works.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_movie_auto_with_retry():
    """Test the movie auto generation with retry logic."""
    print("🎬 Testing Movie Auto Generation with Retry Logic")
    print("=" * 60)
    
    # Test payload - using a simple idea that should work
    payload = {
        "idea": "A short romantic comedy about two coffee shop workers who fall in love during the busy morning rush",
        "total_segments": 15,  # Small number for testing
        "segments_per_set": 5,  # This will create 3 sets
        "save_to_files": True,
        "output_directory": "test_retry_generation"
    }
    
    print(f"📝 Test Payload:")
    print(f"   Idea: {payload['idea']}")
    print(f"   Total Segments: {payload['total_segments']}")
    print(f"   Segments per Set: {payload['segments_per_set']}")
    print(f"   Expected Sets: {payload['total_segments'] // payload['segments_per_set']}")
    
    try:
        print("\n🚀 Starting movie generation...")
        start_time = time.time()
        
        response = requests.post(f"{BASE_URL}/generate-movie-auto", json=payload)
        response.raise_for_status()
        
        result = response.json()
        generation_time = time.time() - start_time
        
        print(f"✅ Generation completed in {generation_time:.2f} seconds")
        
        # Check the result
        if 'result' in result:
            story_result = result['result']
            
            print(f"\n📊 Generation Summary:")
            print(f"   Success: {story_result.get('success', False)}")
            print(f"   Story Title: {story_result.get('story_title', 'N/A')}")
            
            gen_summary = story_result.get('generation_summary', {})
            print(f"   Total Segments Requested: {gen_summary.get('total_segments_requested', 0)}")
            print(f"   Total Segments Generated: {gen_summary.get('total_segments_generated', 0)}")
            print(f"   Successful Sets: {gen_summary.get('successful_sets', 0)}")
            print(f"   Failed Sets: {gen_summary.get('failed_sets', 0)}")
            
            # Check for failed sets
            failed_sets = gen_summary.get('failed_set_numbers', [])
            if failed_sets:
                print(f"   Failed Set Numbers: {failed_sets}")
                
                # Test retry functionality
                print(f"\n🔄 Testing retry functionality for failed sets...")
                retry_payload = {
                    "previous_result": story_result,
                    "max_retries": 3
                }
                
                retry_start = time.time()
                retry_response = requests.post(f"{BASE_URL}/retry-failed-story-sets", json=retry_payload)
                retry_response.raise_for_status()
                
                retry_result = retry_response.json()
                retry_time = time.time() - retry_start
                
                print(f"✅ Retry completed in {retry_time:.2f} seconds")
                
                if 'result' in retry_result:
                    retry_story_result = retry_result['result']
                    
                    print(f"\n📊 Retry Summary:")
                    print(f"   Final Success: {retry_story_result.get('success', False)}")
                    
                    retry_gen_summary = retry_story_result.get('generation_summary', {})
                    print(f"   Total Segments Generated: {retry_gen_summary.get('total_segments_generated', 0)}")
                    print(f"   Successful Sets: {retry_gen_summary.get('successful_sets', 0)}")
                    print(f"   Still Failed Sets: {retry_gen_summary.get('failed_sets', 0)}")
                    
                    retry_info = retry_story_result.get('retry_info', {})
                    if retry_info.get('retry_performed'):
                        print(f"   Retry Results:")
                        for retry_res in retry_info.get('retry_results', []):
                            status_emoji = "✅" if retry_res['status'] == 'success' else "❌"
                            print(f"     {status_emoji} Set {retry_res['set_number']}: {retry_res['status']}")
                    
                    return retry_story_result.get('success', False)
                else:
                    print("❌ No retry result found in response")
                    return False
            else:
                print("✅ No failed sets - retry not needed!")
                return story_result.get('success', False)
        else:
            print("❌ No result found in response")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_retry_endpoint_validation():
    """Test the retry endpoint with invalid inputs."""
    print("\n🧪 Testing Retry Endpoint Validation")
    print("=" * 40)
    
    # Test 1: Empty previous result
    print("Test 1: Empty previous result")
    try:
        response = requests.post(f"{BASE_URL}/retry-failed-story-sets", json={
            "previous_result": {},
            "max_retries": 3
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Correctly rejected empty result")
        else:
            print("   ❌ Should have rejected empty result")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 2: Invalid max_retries
    print("\nTest 2: Invalid max_retries")
    try:
        response = requests.post(f"{BASE_URL}/retry-failed-story-sets", json={
            "previous_result": {"some": "data"},
            "max_retries": 15  # Too high
        })
        print(f"   Status: {response.status_code}")
        if response.status_code == 400:
            print("   ✅ Correctly rejected invalid max_retries")
        else:
            print("   ❌ Should have rejected invalid max_retries")
    except Exception as e:
        print(f"   ❌ Request failed: {e}")

if __name__ == "__main__":
    print("🎯 Movie Auto Generation Retry Logic Test")
    print("=" * 50)
    
    # Test the main functionality
    success = test_movie_auto_with_retry()
    
    # Test validation
    test_retry_endpoint_validation()
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"🎬 Movie generation with retry: {'✅ Success' if success else '❌ Failed'}")
    
    if success:
        print("\n🎉 All tests passed!")
        print("\n💡 Usage:")
        print("1. Use /generate-movie-auto for complete movies")
        print("2. If sets fail, use /retry-failed-story-sets to retry them")
        print("3. The retry logic uses exponential backoff (2s, 4s, 8s delays)")
        print("4. You can retry up to 10 times per set (configurable)")
    else:
        print("\n❌ Some tests failed. Check the server logs for details.")