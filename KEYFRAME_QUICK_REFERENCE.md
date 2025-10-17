# Keyframe Video Generation - Quick Reference

## 🚀 Quick Start

### Python Function
```python
from app.services import genai_service

video_urls = genai_service.generate_video_with_keyframes(
    prompt="Your video description",
    first_frame="gs://bucket/start.png",  # Optional
    last_frame="gs://bucket/end.png",     # Optional
    duration=8,
    aspect_ratio="9:16"
)
```

### API Endpoint
```bash
POST /api/generate-video-with-keyframes
{
  "prompt": "Your video description",
  "first_frame_gcs_uri": "gs://bucket/start.png",
  "last_frame_gcs_uri": "gs://bucket/end.png",
  "duration": 8,
  "aspect_ratio": "9:16"
}
```

## 📋 Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | ✅ Yes | - | Video description |
| `first_frame` | image | ❌ No | None | First frame image |
| `last_frame` | image | ❌ No | None | Last frame image |
| `duration` | int | ❌ No | 8 | Duration in seconds |
| `resolution` | string | ❌ No | "720p" | Video resolution |
| `aspect_ratio` | string | ❌ No | "9:16" | Aspect ratio |

## 🎨 Image Input Formats

```python
# 1. GCS URI (Recommended)
first_frame = "gs://my-bucket/image.png"

# 2. PIL Image
from PIL import Image
first_frame = Image.open("image.png")

# 3. Bytes
with open("image.png", "rb") as f:
    first_frame = f.read()

# 4. Dictionary
first_frame = {"gcs_uri": "gs://bucket/img.png"}
```

## 💡 Common Use Cases

### 1. Character Consistency
```python
character = "gs://bucket/character.png"
video = generate_video_with_keyframes(
    prompt="Character walks across room",
    first_frame=character
)
```

### 2. Scene Transition
```python
video = generate_video_with_keyframes(
    prompt="Transition from day to night",
    first_frame="gs://bucket/day.png",
    last_frame="gs://bucket/night.png"
)
```

### 3. Multi-Segment Chain
```python
# Segment 1
seg1 = generate_video_with_keyframes(
    prompt="Character enters"
)

# Segment 2 (continues from seg1)
seg2 = generate_video_with_keyframes(
    prompt="Character walks",
    first_frame=extract_last_frame(seg1[0])
)
```

### 4. Perfect Loop
```python
loop_point = "gs://bucket/loop.png"
video = generate_video_with_keyframes(
    prompt="Camera orbits object",
    first_frame=loop_point,
    last_frame=loop_point
)
```

## 🔧 Integration

### Update Existing Payload
```python
# Add keyframes to existing payload
payload["first_frame_gcs_uri"] = "gs://bucket/start.png"
payload["last_frame_gcs_uri"] = "gs://bucket/end.png"

# Works with generate_video_from_payload()
video_urls = genai_service.generate_video_from_payload(payload)
```

### Segment Generation
```python
def generate_with_continuity(segment, prev_frame=None):
    return generate_video_with_keyframes(
        prompt=segment["prompt"],
        first_frame=prev_frame,
        duration=8
    )
```

## ✅ Response Format

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

## 📝 Best Practices

✅ Use high-resolution images (1280x720+)  
✅ Match image aspect ratio to video  
✅ Use PNG format for best quality  
✅ Store in GCS for production  
✅ Keep lighting consistent  
✅ Describe transitions in prompt  

## ⚠️ Notes

- Keyframes are **optional** - old code still works
- GCS URIs recommended for production
- Images should match target aspect ratio
- Processing may take slightly longer

## 🎯 Quick Examples

```python
# Image-to-Video
generate_video_with_keyframes(
    prompt="Pan across landscape",
    first_frame="gs://bucket/landscape.png"
)

# Video-to-Image
generate_video_with_keyframes(
    prompt="Character reaches door",
    last_frame="gs://bucket/at_door.png"
)

# Both Keyframes
generate_video_with_keyframes(
    prompt="Character walks left to right",
    first_frame="gs://bucket/left.png",
    last_frame="gs://bucket/right.png"
)

# No Keyframes (normal generation)
generate_video_with_keyframes(
    prompt="Character enters room"
)
```

## 📚 Full Documentation

See **KEYFRAME_VIDEO_GENERATION_GUIDE.md** for:
- Detailed examples
- Advanced use cases
- Troubleshooting
- Best practices
- Integration patterns

---

**Quick Tip**: Start with first frame only for character consistency, then add last frame for precise transitions!
