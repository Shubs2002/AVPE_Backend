"""
Test script for Batch Style Transfer API

This tests converting multiple images to the same style.
"""

import requests
import json
import os

BASE_URL = "http://localhost:8000/api"


def test_batch_style_transfer():
    """Test batch style transfer with sample images"""
    print("\n" + "="*60)
    print("TEST: Batch Style Transfer")
    print("="*60)
    
    # NOTE: Replace these with actual image paths on your system
    # For testing, you can use images from previous tests
    image_paths = [
        "generated_images/image_1_20260220_143022.png",
        "generated_images/image_2_20260220_143025.png",
        "generated_images/image_3_20260220_143028.png"
    ]
    
    # Check if images exist
    existing_images = [path for path in image_paths if os.path.exists(path)]
    
    if not existing_images:
        print("⚠️  No test images found!")
        print("   Please run test_image_editing.py first to generate test images")
        print("   Or update image_paths in this script with your own images")
        return
    
    print(f"📸 Found {len(existing_images)} test images")
    
    payload = {
        "image_paths": existing_images,
        "style_prompt": "Convert to anime style with vibrant colors, bold outlines, and cel-shaded look",
        "aspect_ratio": "16:9",
        "resolution": "2K",
        "delay_between_requests": 2.0,
        "variations_per_image": 1,
        "output_dir": "test_styled_images"
    }
    
    print(f"\n🎨 Style: {payload['style_prompt'][:80]}...")
    print(f"📊 Processing {len(existing_images)} images")
    print(f"⏱️  Delay: {payload['delay_between_requests']}s")
    
    print(f"\n📤 Sending request...")
    
    response = requests.post(f"{BASE_URL}/images/batch-style-transfer", json=payload)
    result = response.json()
    
    if result.get("success"):
        print(f"\n✅ SUCCESS!")
        print(f"   Total images: {result['total_images']}")
        print(f"   Total operations: {result['total_operations']}")
        print(f"   Success: {result['success_count']}/{result['total_operations']}")
        print(f"   Failed: {result['failed_count']}/{result['total_operations']}")
        print(f"   Output dir: {result['output_dir']}")
        
        print(f"\n📁 Styled images:")
        for r in result['results']:
            status_icon = "✅" if r['status'] == 'completed' else "❌"
            print(f"   {status_icon} Image {r['index']}: {r['status']}")
            if r['status'] == 'completed':
                print(f"      Input:  {os.path.basename(r['input_image'])}")
                print(f"      Output: {r['output_path']}")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")
    
    return result


def test_batch_with_variations():
    """Test batch style transfer with multiple variations"""
    print("\n" + "="*60)
    print("TEST: Batch Style Transfer with Variations")
    print("="*60)
    
    # Use 2 images, generate 2 variations each
    image_paths = [
        "generated_images/image_1_20260220_143022.png",
        "generated_images/image_2_20260220_143025.png"
    ]
    
    existing_images = [path for path in image_paths if os.path.exists(path)]
    
    if not existing_images:
        print("⚠️  No test images found!")
        return
    
    # Only use first 2 images for variation test
    existing_images = existing_images[:2]
    
    payload = {
        "image_paths": existing_images,
        "style_prompt": "Transform into watercolor painting with soft, flowing colors",
        "variations_per_image": 2,
        "delay_between_requests": 2.0,
        "output_dir": "test_styled_variations"
    }
    
    print(f"\n🎨 Style: {payload['style_prompt'][:80]}...")
    print(f"📊 Processing {len(existing_images)} images")
    print(f"🔢 Variations per image: {payload['variations_per_image']}")
    print(f"📈 Total operations: {len(existing_images) * payload['variations_per_image']}")
    
    print(f"\n📤 Sending request...")
    
    response = requests.post(f"{BASE_URL}/images/batch-style-transfer", json=payload)
    result = response.json()
    
    if result.get("success"):
        print(f"\n✅ SUCCESS!")
        print(f"   Total images: {result['total_images']}")
        print(f"   Total operations: {result['total_operations']}")
        print(f"   Success: {result['success_count']}/{result['total_operations']}")
        
        print(f"\n📁 Styled variations:")
        for r in result['results']:
            status_icon = "✅" if r['status'] == 'completed' else "❌"
            print(f"   {status_icon} Image {r['index']}, Variation {r['variation']}: {r['status']}")
            if r['status'] == 'completed':
                print(f"      Output: {r['output_path']}")
    else:
        print(f"\n❌ FAILED: {result.get('error')}")
    
    return result


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 BATCH STYLE TRANSFER API TESTS")
    print("="*60)
    print("\nMake sure the server is running at http://localhost:8000")
    print("Press Enter to start tests...")
    input()
    
    try:
        # Test 1: Basic batch style transfer
        result1 = test_batch_style_transfer()
        
        if result1 and result1.get("success"):
            print("\n" + "="*60)
            input("Press Enter to continue to variation test...")
            
            # Test 2: Batch with variations
            result2 = test_batch_with_variations()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS COMPLETED!")
        print("="*60)
        print("\nCheck the following directories for styled images:")
        print("  - test_styled_images/")
        print("  - test_styled_variations/")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to server")
        print("Make sure the server is running at http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")


if __name__ == "__main__":
    main()
