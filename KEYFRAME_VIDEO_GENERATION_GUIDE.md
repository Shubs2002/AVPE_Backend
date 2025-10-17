# Keyframe Video Generation - Complete Guide

## Overview

Veo 3 now supports generating videos with optional **first and last frame keyframes**. This allows you to:
- Maintain character consistency across segments
- Create smooth transitions between scenes
- Ensure visual continuity in multi-segment stories
- Control exact start and end frames

## Features Added

### 1. Updated `generate_video_from_payload()`
Now accepts optional frame parameters:
- `first_frame_image` - First frame (PIL Image, bytes, or dict)
- `last_frame_image` - Last frame (PIL Image, bytes, or dict)
- `first_frame_gcs_uri` - GCS URI for first frame (e.g., "gs://bucket/img.png")
- `last_frame_gcs_uri` - GCS URI for last frame

### 2. New `generate_video_with_keyframes()` Function
Convenience function for easy keyframe usage:

```python
from app.services import genai_service

# Using GCS URIs
video_urls = genai_service.generate_video_with_keyframes(
    prompt="A cat walking across the room",
    first_frame="gs://my-bucket/cat_start.png",
    last_frame="gs://my-bucket/cat_end.png",
    duration=8,
    aspect_ratio="9:16"
)

# Using PIL Images
from PIL import Image
first_img = Image.open("start.png")
last_img = Image.open("end.png")

video_urls = genai_service.generate_video_with_keyframes(
    prompt="A cat walking across the room",
    first_frame=first_img,
    last_frame=last_img
)
```

### 3. New API Endpoint
**POST `/api/generate-video-with-keyframes`**

```bash
curl -X POST "http://127.0.0.1:8000/api/generate-video-with-keyframes" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A cat walking across the room",
    "first_frame_gcs_uri": "gs://my-bucket/cat_start.png",
    "last_frame_gcs_uri": "gs://my-bucket/cat_end.png",
    "duration": 8,
    "aspect_ratio": "9:16"
  }'
```

## Usage Examples

### Example 1: Basic Keyframe Usage

```python
from app.services import genai_service

# Generate video with start and end frames
video_urls = genai_service.generate_video_with_keyframes(
    prompt="Character walking from left to right",
    first_frame="gs://my-bucket/character_left.png",
    last_frame="gs://my-bucket/character_right.png",
    duration=8
)

print(f"Generated video: {video_urls[0]}")
```

### Example 2: Using PIL Images

```python
from PIL import Image
from app.services import genai_service

# Load images
start_frame = Image.open("segment_1_end.png")
end_frame = Image.open("segment_3_start.png")

# Generate transition video
video_urls = genai_service.generate_video_with_keyframes(
    prompt="Smooth transition between scenes",
    first_frame=start_frame,
    last_frame=end_frame,
    duration=8
)
```

### Example 3: Only First Frame (Image-to-Video)

```python
from app.services import genai_service

# Generate video starting from a specific image
video_urls = genai_service.generate_video_with_keyframes(
    prompt="Camera pans across the landscape",
    first_frame="gs://my-bucket/landscape.png",
    # No last_frame - Veo 3 will generate naturally
    duration=8
)
```

### Example 4: Only Last Frame (Video-to-Image)

```python
from app.services import genai_service

# Generate video ending at a specific frame
video_urls = genai_service.generate_video_with_keyframes(
    prompt="Character approaches the door",
    last_frame="gs://my-bucket/at_door.png",
    # No first_frame - Veo 3 will generate naturally
    duration=8
)
```

### Example 5: Multi-Segment Story with Continuity

```python
from app.services import genai_service
from PIL import Image

# Segment 1: Generate normally
segment_1_urls = genai_service.generate_video_from_payload({
    "prompt": "Character enters the room",
    "durationSeconds": 8
})

# Extract last frame from segment 1 (you'd need to implement frame extraction)
# last_frame_seg1 = extract_last_frame(segment_1_urls[0])

# Segment 2: Use segment 1's last frame as first frame
segment_2_urls = genai_service.generate_video_with_keyframes(
    prompt="Character looks around the room",
    first_frame=last_frame_seg1,  # Ensures continuity!
    duration=8
)
```

## API Endpoint Details

### Request

**POST `/api/generate-video-with-keyframes`**

```json
{
  "prompt": "Description of the video",
  "first_frame_gcs_uri": "gs://bucket/start.png",  // Optional
  "last_frame_gcs_uri": "gs://bucket/end.png",     // Optional
  "duration": 8,                                    // Optional, default: 8
  "resolution": "720p",                             // Optional, default: "720p"
  "aspect_ratio": "9:16"                            // Optional, default: "9:16"
}
```

### Response

```json
{
  "success": true,
  "video_urls": [
    "https://storage.googleapis.com/..."
  ],
  "keyframes_used": {
    "first_frame": true,
    "last_frame": true
  }
}
```

## Image Input Formats

The system supports multiple image input formats:

### 1. GCS URI (Recommended for Production)
```python
first_frame = "gs://my-bucket/image.png"
```

### 2. PIL Image Object
```python
from PIL import Image
first_frame = Image.open("image.png")
```

### 3. Bytes
```python
with open("image.png", "rb") as f:
    first_frame = f.read()
```

### 4. Dictionary with GCS URI
```python
first_frame = {
    "gcs_uri": "gs://my-bucket/image.png",
    "mime_type": "image/png"
}
```

### 5. Dictionary with Bytes
```python
first_frame = {
    "data": image_bytes,
    "mime_type": "image/png"
}
```

## Use Cases

### 1. Character Consistency
Ensure the same character appearance across multiple segments:

```python
# Generate character image first
character_img = generate_character_image(character_description)

# Use as first frame for all segments
for segment in segments:
    video = generate_video_with_keyframes(
        prompt=segment["prompt"],
        first_frame=character_img,
        duration=8
    )
```

### 2. Scene Transitions
Create smooth transitions between different scenes:

```python
# End of scene 1
scene1_end = "gs://bucket/scene1_end.png"

# Start of scene 2
scene2_start = "gs://bucket/scene2_start.png"

# Generate transition
transition = generate_video_with_keyframes(
    prompt="Fade from indoor to outdoor",
    first_frame=scene1_end,
    last_frame=scene2_start,
    duration=8
)
```

### 3. Action Sequences
Control specific action start and end points:

```python
# Character at point A
start_position = "gs://bucket/character_at_A.png"

# Character at point B
end_position = "gs://bucket/character_at_B.png"

# Generate movement
movement = generate_video_with_keyframes(
    prompt="Character runs from point A to point B",
    first_frame=start_position,
    last_frame=end_position,
    duration=8
)
```

### 4. Looping Videos
Create perfect loops by using the same image for first and last frame:

```python
loop_frame = "gs://bucket/loop_point.png"

looping_video = generate_video_with_keyframes(
    prompt="Camera orbits around the object",
    first_frame=loop_frame,
    last_frame=loop_frame,
    duration=8
)
```

## Best Practices

### 1. Image Quality
- Use high-resolution images (1280x720 or higher)
- Ensure images match the target aspect ratio
- Use PNG format for best quality

### 2. Consistency
- Keep lighting consistent between keyframes
- Maintain character appearance details
- Match background elements

### 3. Prompt Alignment
- Describe the transition between frames in the prompt
- Be specific about camera movement
- Mention key actions that should occur

### 4. GCS Storage
- Store frequently used keyframes in GCS for faster access
- Organize by content type and segment
- Use descriptive filenames

### 5. Testing
- Test keyframe combinations before full generation
- Verify frame extraction quality
- Check transition smoothness

## Integration with Existing Code

### Update Segment Generation

```python
# In your segment generation code
def generate_segment_with_continuity(segment_data, previous_last_frame=None):
    """Generate segment with optional continuity from previous segment"""
    
    payload = {
        "prompt": segment_data["prompt"],
        "durationSeconds": 8,
        "aspectRatio": "9:16"
    }
    
    # Add first frame if we have previous segment's last frame
    if previous_last_frame:
        payload["first_frame_gcs_uri"] = previous_last_frame
    
    # Generate video
    video_urls = genai_service.generate_video_from_payload(payload)
    
    # Extract last frame for next segment (implement frame extraction)
    last_frame = extract_last_frame(video_urls[0])
    
    return video_urls[0], last_frame
```

### Batch Processing with Continuity

```python
def generate_story_with_continuity(segments):
    """Generate all segments with visual continuity"""
    
    videos = []
    last_frame = None
    
    for i, segment in enumerate(segments):
        print(f"Generating segment {i+1}/{len(segments)}...")
        
        video_url, last_frame = generate_segment_with_continuity(
            segment,
            previous_last_frame=last_frame
        )
        
        videos.append(video_url)
    
    return videos
```

## Limitations

1. **GCS Storage Required**: For production use, images should be in Google Cloud Storage
2. **Image Size**: Large images may increase processing time
3. **Format Support**: Best results with PNG format
4. **Aspect Ratio**: Images should match target video aspect ratio
5. **Processing Time**: Keyframe videos may take slightly longer to generate

## Troubleshooting

### Issue: "Unsupported image input type"
**Solution**: Ensure image is in one of the supported formats (GCS URI, PIL Image, bytes, or dict)

### Issue: Keyframes not applied
**Solution**: Verify GCS URIs are accessible and images are valid PNG files

### Issue: Poor transition quality
**Solution**: Ensure keyframes are high quality and prompt describes the transition clearly

### Issue: Character inconsistency
**Solution**: Use more detailed character descriptions in keyframes and prompts

## Future Enhancements

Potential improvements:
- Automatic frame extraction from generated videos
- Frame interpolation for smoother transitions
- Batch keyframe generation
- Keyframe quality validation
- Automatic GCS upload for local images

## Summary

✅ **Added**: Optional first and last frame support  
✅ **Function**: `generate_video_with_keyframes()`  
✅ **Endpoint**: `/api/generate-video-with-keyframes`  
✅ **Formats**: GCS URI, PIL Image, bytes, dict  
✅ **Use Cases**: Continuity, transitions, consistency  

The keyframe feature is now fully integrated and ready to use! 🎬
