"""
Test script for keyframe video generation.
Demonstrates how to use first and last frame images with Veo 3.
"""
import requests
import json

BASE_URL = "http://127.0.0.1:8000/api"

def test_keyframe_generation():
    """Test video generation with keyframes"""
    
    print("🎬 Testing Keyframe Video Generation\n")
    print("="*60)
    
    # Example 1: Video with both first and last frames
    print("\n1️⃣  Test: Video with First and Last Frames")
    print("-"*60)
    
    payload_both = {
        "prompt": "A cat walking gracefully across a sunlit room, smooth camera tracking",
        "first_frame_gcs_uri": "gs://your-bucket/cat_start.png",
        "last_frame_gcs_uri": "gs://your-bucket/cat_end.png",
        "duration": 8,
        "aspect_ratio": "9:16"
    }
    
    print("Request:")
    print(json.dumps(payload_both, indent=2))
    print("\nNote: Replace GCS URIs with your actual image locations")
    
    # Uncomment to actually test:
    # response = requests.post(f"{BASE_URL}/generate-video-with-keyframes", json=payload_both)
    # print(f"\nResponse: {response.json()}")
    
    # Example 2: Video with only first frame (image-to-video)
    print("\n\n2️⃣  Test: Image-to-Video (First Frame Only)")
    print("-"*60)
    
    payload_first_only = {
        "prompt": "Camera slowly pans across a beautiful landscape at golden hour",
        "first_frame_gcs_uri": "gs://your-bucket/landscape.png",
        "duration": 8,
        "aspect_ratio": "16:9"
    }
    
    print("Request:")
    print(json.dumps(payload_first_only, indent=2))
    
    # Example 3: Video with only last frame (video-to-image)
    print("\n\n3️⃣  Test: Video-to-Image (Last Frame Only)")
    print("-"*60)
    
    payload_last_only = {
        "prompt": "Character walks towards the door and reaches for the handle",
        "last_frame_gcs_uri": "gs://your-bucket/at_door.png",
        "duration": 8,
        "aspect_ratio": "9:16"
    }
    
    print("Request:")
    print(json.dumps(payload_last_only, indent=2))
    
    # Example 4: Using the Python service directly
    print("\n\n4️⃣  Test: Direct Python Service Usage")
    print("-"*60)
    
    python_example = '''
from app.services import genai_service
from PIL import Image

# Load images
first_img = Image.open("start_frame.png")
last_img = Image.open("end_frame.png")

# Generate video
video_urls = genai_service.generate_video_with_keyframes(
    prompt="Smooth transition between two scenes",
    first_frame=first_img,
    last_frame=last_img,
    duration=8,
    aspect_ratio="9:16"
)

print(f"Generated video: {video_urls[0]}")
'''
    
    print("Python Code:")
    print(python_example)
    
    # Example 5: Multi-segment story with continuity
    print("\n\n5️⃣  Test: Multi-Segment Story with Continuity")
    print("-"*60)
    
    continuity_example = '''
# Segment 1: Generate normally
segment_1 = requests.post(f"{BASE_URL}/generate-video-with-keyframes", json={
    "prompt": "Character enters the room and looks around",
    "duration": 8
})

# Extract last frame from segment 1 (you'd implement frame extraction)
# last_frame_uri = extract_and_upload_last_frame(segment_1_video_url)

# Segment 2: Use segment 1's last frame as first frame
segment_2 = requests.post(f"{BASE_URL}/generate-video-with-keyframes", json={
    "prompt": "Character walks to the window",
    "first_frame_gcs_uri": last_frame_uri,  # Continuity!
    "duration": 8
})

# Segment 3: Continue the chain
segment_3 = requests.post(f"{BASE_URL}/generate-video-with-keyframes", json={
    "prompt": "Character looks out the window at the sunset",
    "first_frame_gcs_uri": extract_and_upload_last_frame(segment_2_video_url),
    "duration": 8
})
'''
    
    print("Continuity Chain:")
    print(continuity_example)
    
    print("\n" + "="*60)
    print("\n✅ Test Examples Complete!")
    print("\n📚 Documentation: See KEYFRAME_VIDEO_GENERATION_GUIDE.md")
    print("\n💡 Next Steps:")
    print("   1. Upload your keyframe images to Google Cloud Storage")
    print("   2. Update the GCS URIs in the examples above")
    print("   3. Uncomment the API calls to test")
    print("   4. Implement frame extraction for multi-segment continuity")


def test_payload_structure():
    """Test the payload structure for existing generate_video_from_payload"""
    
    print("\n\n🔧 Testing Updated Payload Structure")
    print("="*60)
    
    # Example payload with all new optional fields
    full_payload = {
        "prompt": "A serene sunrise over misty mountains",
        "durationSeconds": 8,
        "resolution": "720p",
        "aspectRatio": "16:9",
        # New optional fields:
        "first_frame_gcs_uri": "gs://my-bucket/sunrise_start.png",
        "last_frame_gcs_uri": "gs://my-bucket/sunrise_end.png"
    }
    
    print("\nFull Payload Structure:")
    print(json.dumps(full_payload, indent=2))
    
    print("\n✅ This payload can be used with:")
    print("   - genai_service.generate_video_from_payload(payload)")
    print("   - Any existing endpoint that calls generate_video_from_payload")
    
    print("\n📝 Backward Compatible:")
    print("   - Old payloads without keyframes still work")
    print("   - Keyframes are completely optional")
    print("   - No breaking changes to existing code")


if __name__ == "__main__":
    test_keyframe_generation()
    test_payload_structure()
    
    print("\n\n" + "="*60)
    print("🎉 Keyframe Video Generation is Ready!")
    print("="*60)
    print("\n📖 Features:")
    print("   ✅ Optional first frame (image-to-video)")
    print("   ✅ Optional last frame (video-to-image)")
    print("   ✅ Both frames (keyframe interpolation)")
    print("   ✅ Multiple input formats (GCS URI, PIL Image, bytes)")
    print("   ✅ New convenience function: generate_video_with_keyframes()")
    print("   ✅ New API endpoint: /api/generate-video-with-keyframes")
    print("   ✅ Backward compatible with existing code")
    
    print("\n🚀 Use Cases:")
    print("   • Character consistency across segments")
    print("   • Smooth scene transitions")
    print("   • Action sequence control")
    print("   • Perfect video loops")
    print("   • Multi-segment story continuity")
