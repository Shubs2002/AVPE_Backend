"""
Test script for Image Editing & Generation API

Run this after starting the server to test the new endpoints.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000/api"


def test_generate_single_image():
    """Test single image generation"""
    print("\n" + "="*60)
    print("TEST 1: Generate Single Image")
    print("="*60)
    
    payload = {
        "prompt": "A cute fluffy pink creature with big curious eyes playing in a sunny park with green grass and blue sky",
        "aspect_ratio": "16:9",
        "resolution": "2K",
        "use_google_search": False
    }
    
    print(f"📤 Sending request...")
    print(f"Prompt: {payload['prompt'][:80]}...")
    
    response = requests.post(f"{BASE_URL}/images/generate", json=payload)
    result = response.json()
    
    if result.get("success"):
        print(f"✅ SUCCESS!")
        print(f"   Image saved to: {result['image_path']}")
        if result.get('text_response'):
            print(f"   Text response: {result['text_response'][:100]}...")
    else:
        print(f"❌ FAILED: {result.get('error')}")
    
    return result


def test_generate_bulk_images():
    """Test bulk image generation"""
    print("\n" + "="*60)
    print("TEST 2: Generate Bulk Images (3 images)")
    print("="*60)
    
    payload = {
        "prompts": [
            "A sunny beach with palm trees and blue ocean waves",
            "A snowy mountain peak at golden hour with pink sky",
            "A bustling city street at night with neon lights"
        ],
        "aspect_ratio": "16:9",
        "resolution": "2K",
        "delay_between_requests": 2.0,
        "output_dir": "test_generated_images"
    }
    
    print(f"📤 Generating {len(payload['prompts'])} images...")
    print(f"⏱️  Delay between requests: {payload['delay_between_requests']}s")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/images/generate-bulk", json=payload)
    result = response.json()
    elapsed = time.time() - start_time
    
    if result.get("success"):
        print(f"✅ SUCCESS!")
        print(f"   Total time: {elapsed:.1f}s")
        print(f"   Success: {result['success_count']}/{result['total_images']}")
        print(f"   Failed: {result['failed_count']}/{result['total_images']}")
        print(f"   Output dir: {result['output_dir']}")
        
        for r in result['results']:
            status_icon = "✅" if r['status'] == 'completed' else "❌"
            print(f"   {status_icon} Image {r['index']}: {r['status']}")
            if r['status'] == 'completed':
                print(f"      Path: {r['image_path']}")
    else:
        print(f"❌ FAILED: {result.get('error')}")
    
    return result


def test_edit_single_image(image_path):
    """Test single image editing"""
    print("\n" + "="*60)
    print("TEST 3: Edit Single Image")
    print("="*60)
    
    payload = {
        "image_path": image_path,
        "edit_prompt": "Add a beautiful rainbow in the sky with vibrant colors",
        "aspect_ratio": "16:9",
        "resolution": "2K"
    }
    
    print(f"📤 Editing image: {image_path}")
    print(f"Edit prompt: {payload['edit_prompt']}")
    
    response = requests.post(f"{BASE_URL}/images/edit", json=payload)
    result = response.json()
    
    if result.get("success"):
        print(f"✅ SUCCESS!")
        print(f"   Input: {result['input_image']}")
        print(f"   Output: {result['output_path']}")
        if result.get('text_response'):
            print(f"   Text response: {result['text_response'][:100]}...")
    else:
        print(f"❌ FAILED: {result.get('error')}")
    
    return result


def test_edit_bulk_images(image_paths):
    """Test bulk image editing"""
    print("\n" + "="*60)
    print("TEST 4: Edit Bulk Images (Single Prompt)")
    print("="*60)
    
    payload = {
        "image_paths": image_paths[:2],  # Edit first 2 images
        "edit_prompts": ["Make the lighting warmer with golden hour tones"],
        "aspect_ratio": "16:9",
        "resolution": "2K",
        "delay_between_requests": 2.0,
        "output_dir": "test_edited_images"
    }
    
    print(f"📤 Editing {len(payload['image_paths'])} images...")
    print(f"Edit prompt (for all): {payload['edit_prompts'][0]}")
    
    start_time = time.time()
    response = requests.post(f"{BASE_URL}/images/edit-bulk", json=payload)
    result = response.json()
    elapsed = time.time() - start_time
    
    if result.get("success"):
        print(f"✅ SUCCESS!")
        print(f"   Total time: {elapsed:.1f}s")
        print(f"   Success: {result['success_count']}/{result['total_images']}")
        print(f"   Failed: {result['failed_count']}/{result['total_images']}")
        
        for r in result['results']:
            status_icon = "✅" if r['status'] == 'completed' else "❌"
            print(f"   {status_icon} Image {r['index']}: {r['status']}")
            if r['status'] == 'completed':
                print(f"      Output: {r['output_path']}")
    else:
        print(f"❌ FAILED: {result.get('error')}")
    
    return result


def test_weather_forecast():
    """Test weather forecast generation with Google Search"""
    print("\n" + "="*60)
    print("TEST 5: Weather Forecast with Google Search")
    print("="*60)
    
    payload = {
        "prompt": "Visualize the current weather forecast for the next 5 days in San Francisco as a clean, modern weather chart. Add a visual on what I should wear each day",
        "aspect_ratio": "16:9",
        "resolution": "2K",
        "use_google_search": True
    }
    
    print(f"📤 Generating weather forecast with Google Search...")
    
    response = requests.post(f"{BASE_URL}/images/generate", json=payload)
    result = response.json()
    
    if result.get("success"):
        print(f"✅ SUCCESS!")
        print(f"   Image saved to: {result['image_path']}")
        if result.get('text_response'):
            print(f"   Text response: {result['text_response'][:200]}...")
    else:
        print(f"❌ FAILED: {result.get('error')}")
    
    return result


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 IMAGE EDITING & GENERATION API TESTS")
    print("="*60)
    print("\nMake sure the server is running at http://localhost:8000")
    print("Press Enter to start tests...")
    input()
    
    try:
        # Test 1: Generate single image
        result1 = test_generate_single_image()
        time.sleep(2)
        
        # Test 2: Generate bulk images
        result2 = test_generate_bulk_images()
        time.sleep(2)
        
        # Test 3: Edit single image (use first generated image)
        if result1.get("success"):
            result3 = test_edit_single_image(result1['image_path'])
            time.sleep(2)
        
        # Test 4: Edit bulk images (use bulk generated images)
        if result2.get("success") and result2.get('results'):
            image_paths = [r['image_path'] for r in result2['results'] if r['status'] == 'completed']
            if image_paths:
                result4 = test_edit_bulk_images(image_paths)
                time.sleep(2)
        
        # Test 5: Weather forecast with Google Search
        result5 = test_weather_forecast()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
        print("\nCheck the following directories for generated images:")
        print("  - generated_images/")
        print("  - test_generated_images/")
        print("  - edited_images/")
        print("  - test_edited_images/")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    main()
