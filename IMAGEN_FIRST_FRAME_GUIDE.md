# Imagen First Frame Generation Guide

## 🎨 Overview

The system now generates the first frame using **Imagen (nano banana model)** and downloads it to the `frames/` folder before using it as the starting point for video generation.

## 🔄 How It Works

```
1. Daily character content generated
   ↓
2. First segment has "first_frame_description"
   ↓
3. Imagen generates frame from description + character image
   ↓
4. Frame downloaded to frames/ folder
   ↓
5. Downloaded frame used as first_frame for video generation
   ↓
6. Video generated with consistent starting point
```

## 📁 File Structure

```
Backend/
├── frames/                          # Generated first frames
│   ├── first_frame_20250117_143022.png
│   ├── first_frame_20250117_143145.png
│   └── ...
├── src/
│   └── app/
│       └── services/
│           ├── imagen_service.py    # NEW: Imagen generation
│           └── content_to_video_service.py  # UPDATED: Uses Imagen
```

## 🎯 Usage

### Automatic (Daily Character Content)

When you generate daily character content, the first segment automatically includes a `first_frame_description`:

```json
{
  "segments": [
    {
      "segment": 1,
      "first_frame_description": "Floof standing at cave entrance, looking curious, surrounded by icy rocks and snow, soft moonlight from above",
      "scene": "Floof walks into cave...",
      ...
    }
  ]
}
```

The system will:
1. ✅ Generate this frame with Imagen
2. ✅ Download to `frames/first_frame_TIMESTAMP.png`
3. ✅ Use the downloaded frame as the starting point

### Manual (Custom Frame Generation)

You can also generate frames manually:

```python
from app.services.imagen_service import generate_first_frame_with_imagen

# Generate and download first frame
image, filepath = generate_first_frame_with_imagen(
    character_image_url="https://res.cloudinary.com/.../floof.png",
    frame_description="Floof standing in a snowy cave, looking curious",
    aspect_ratio="9:16",
    output_dir="frames"
)

print(f"Frame saved to: {filepath}")
# Output: Frame saved to: frames/first_frame_20250117_143022.png
```

## 📊 Frame Details

### Aspect Ratios Supported

| Aspect Ratio | Dimensions | Use Case |
|--------------|------------|----------|
| `9:16` | 720x1280 | Instagram/TikTok (Vertical) |
| `16:9` | 1280x720 | YouTube (Horizontal) |
| `1:1` | 1024x1024 | Instagram (Square) |
| `4:5` | 1024x1280 | Instagram (Vertical) |

### File Naming

Frames are saved with timestamps:
```
first_frame_YYYYMMDD_HHMMSS.png
```

Example:
```
first_frame_20250117_143022.png
```

## 🎨 Imagen Generation Process

### Step 1: Character Image Download
```
📥 Downloading character image from: https://res.cloudinary.com/...
✅ Character image loaded: (1024, 1024)
```

### Step 2: Frame Generation
```
🎨 Generating frame with Imagen...
📐 Target size: 720x1280 (9:16)
✅ Image generated: (720, 1280)
```

### Step 3: Frame Download
```
💾 First frame saved: frames/first_frame_20250117_143022.png
📊 Size: (720, 1280)
```

### Step 4: Video Generation
```
🎬 Generating video for Segment 1/6...
🖼️ Using first frame: frames/first_frame_20250117_143022.png
✅ Video generated successfully
```

## 🔧 Configuration

### Default Settings

```python
# In content_to_video_service.py
output_dir = "frames"  # Where frames are saved
aspect_ratio = "9:16"  # Default aspect ratio
```

### Custom Settings

```python
# Generate with custom settings
image, filepath = generate_first_frame_with_imagen(
    character_image_url="https://...",
    frame_description="...",
    aspect_ratio="16:9",      # Custom aspect ratio
    output_dir="custom_frames"  # Custom directory
)
```

## 🎯 Benefits

### 1. Consistent Starting Point
- ✅ Every video starts with the exact same frame
- ✅ Character position and pose are consistent
- ✅ Background and environment match the description

### 2. Better Continuity
- ✅ First frame matches the scene description
- ✅ Smooth transition from frame to video
- ✅ Professional-looking results

### 3. Reusable Frames
- ✅ Frames saved to disk for reuse
- ✅ Can be used for thumbnails
- ✅ Can be used for previews

### 4. Debugging & Quality Control
- ✅ Can review frames before video generation
- ✅ Can regenerate if frame doesn't match expectations
- ✅ Can manually edit frames if needed

## 📝 Example Workflow

### Complete Daily Character Video Generation

```bash
# 1. Generate daily character content
curl -X POST "http://localhost:8000/api/generate-daily-character" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "floof gets shy and turns red",
    "character_name": "Floof",
    "creature_language": "Soft and low-Pitched and mystical",
    "num_segments": 6
  }'

# Response includes first_frame_description in segment 1

# 2. Generate videos with first frame
curl -X POST "http://localhost:8000/api/generate-daily-character-videos" \
  -H "Content-Type: application/json" \
  -d '{
    "content_data": { /* from step 1 */ },
    "character_keyframe_uri": "https://res.cloudinary.com/.../floof.png",
    "aspect_ratio": "9:16"
  }'

# System automatically:
# - Generates first frame with Imagen
# - Downloads to frames/first_frame_TIMESTAMP.png
# - Uses frame as starting point for video
```

## 🔍 Checking Generated Frames

### List All Frames

```bash
# Windows
dir frames

# Linux/Mac
ls -la frames/
```

### View Frame Details

```python
from PIL import Image

# Load frame
frame = Image.open("frames/first_frame_20250117_143022.png")

# Check details
print(f"Size: {frame.size}")
print(f"Mode: {frame.mode}")
print(f"Format: {frame.format}")
```

## ⚠️ Fallback Behavior

If Imagen generation fails, the system automatically falls back to using the character keyframe:

```
⚠️ Imagen generation failed: [error message]
⚠️ Using character image as fallback
💾 Fallback frame saved: frames/first_frame_fallback_20250117_143022.png
```

## 🎊 Result

Your videos now start with:
- ✅ AI-generated first frame from Imagen
- ✅ Downloaded to `frames/` folder
- ✅ Used as consistent starting point
- ✅ Better visual continuity
- ✅ Professional quality

## 📚 Related Files

- `src/app/services/imagen_service.py` - Imagen generation service
- `src/app/services/content_to_video_service.py` - Video generation with frames
- `frames/` - Downloaded first frames directory

---

**Happy frame generating! 🎨✨**
