# Frame Interpolation with Imagen (Nano Banana) - Complete Guide

## Overview

Enhanced video generation system that uses **Imagen (Nano Banana)** to generate BOTH first and last frames for each segment, ensuring perfect character consistency and smooth continuity between segments.

## Key Improvements

### Before (Old System):
- ❌ Only first frame generated for segment 1
- ❌ Subsequent segments used extracted frames from videos (quality loss)
- ❌ Character consistency issues between segments
- ❌ Environment/lighting inconsistencies

### After (New System):
- ✅ **Both first AND last frames generated** with Imagen for each segment
- ✅ **Dual reference system**: Character image + First frame
- ✅ **Perfect continuity**: Last frame of segment N = First frame of segment N+1
- ✅ **Character always fully visible** in generated frames
- ✅ **Organized storage** using file_storage_manager

## How It Works

### 1. Prompt Generation

The AI now generates **both** `first_frame_description` and `last_frame_description` for each segment:

```json
{
  "segments": [
    {
      "segment": 1,
      "first_frame_description": "Floof standing at cave entrance, looking curious, full body visible, moonlight from above",
      "last_frame_description": "Floof bent over puddle, eyes wide in surprise, full body visible, same cave environment",
      "scene": "Floof walks to puddle and looks down",
      ...
    },
    {
      "segment": 2,
      "first_frame_description": "Floof bent over puddle, eyes wide (same as segment 1 last frame)",
      "last_frame_description": "Floof jumping back, paws raised, full body visible, shocked expression",
      ...
    }
  ]
}
```

### 2. Frame Generation Process

#### Segment 1:
```
1. Generate FIRST FRAME with Imagen
   - Input: Character image (reference)
   - Prompt: first_frame_description
   - Output: first_frame_seg_1.png
   
2. Generate LAST FRAME with Imagen
   - Input: Character image + first_frame_seg_1.png (dual reference)
   - Prompt: last_frame_description
   - Output: last_frame_seg_1.png
   
3. Generate VIDEO with Veo 3.1
   - first_frame: first_frame_seg_1.png
   - last_frame: last_frame_seg_1.png
   - Veo interpolates between them
```

#### Segment 2:
```
1. Use PREVIOUS LAST FRAME as first frame
   - first_frame: last_frame_seg_1.png (from segment 1)
   
2. Generate LAST FRAME with Imagen
   - Input: Character image + last_frame_seg_1.png (dual reference)
   - Prompt: last_frame_description
   - Output: last_frame_seg_2.png
   
3. Generate VIDEO with Veo 3.1
   - first_frame: last_frame_seg_1.png
   - last_frame: last_frame_seg_2.png
   - Perfect continuity!
```

#### Segment 3 (Last):
```
1. Use PREVIOUS LAST FRAME as first frame
   - first_frame: last_frame_seg_2.png
   
2. NO last frame generation (last segment)
   
3. Generate VIDEO with Veo 3.1
   - first_frame: last_frame_seg_2.png
   - last_frame: None (Veo decides ending)
```

## Dual Reference System

### Why Two References?

The `generate_last_frame_with_imagen()` function uses **TWO reference images**:

1. **Character Image** (User-provided)
   - Ensures character appearance stays consistent
   - Maintains colors, features, style
   - Character looks exactly the same

2. **First Frame** (Generated for this segment)
   - Ensures environment consistency
   - Maintains lighting and atmosphere
   - Keeps background elements consistent

### Example:

```python
generate_last_frame_with_imagen(
    character_image_url="https://cloudinary.com/.../floof.png",  # Character reference
    first_frame_path="frames/first_frame_seg_2.png",              # Environment reference
    last_frame_description="Floof jumping back, shocked, full body visible",
    aspect_ratio="9:16",
    output_dir="generated_content/daily_character/Title/frames"
)
```

**Result**: Character looks like Floof (from character image) in the same environment/lighting (from first frame) but in a new pose (from description).

## Directory Structure

All frames and videos are organized using `file_storage_manager`:

```
generated_content/
└── daily_character/
    └── Floof's_Diwali_Cloud_Dance/
        ├── frames/
        │   ├── first_frame_20250120_143022.png    (Segment 1 first frame)
        │   ├── last_frame_20250120_143045.png     (Segment 1 last frame)
        │   ├── last_frame_20250120_143112.png     (Segment 2 last frame)
        │   └── last_frame_20250120_143140.png     (Segment 3 last frame - if generated)
        └── videos/
            ├── floof_segment_1.mp4
            ├── floof_segment_2.mp4
            └── floof_segment_3.mp4
```

## Character Visibility Rule

**CRITICAL**: Character MUST be fully visible (whole body) in BOTH first and last frames.

### Why?

- Imagen needs to see the full character to maintain consistency
- Partial views (close-ups) make it harder for AI to recreate the character
- Full body visibility = better character consistency

### Prompt Instructions:

```
"Character MUST be fully visible (whole body in frame)"
```

### Example Descriptions:

✅ **GOOD**:
- "Floof standing at cave entrance, full body visible, looking curious"
- "Floof bent over puddle, whole body in frame, eyes wide"
- "Floof jumping back, complete body visible, paws raised"

❌ **BAD**:
- "Close-up of Floof's face" (character not fully visible)
- "Floof's paws reaching" (only partial view)
- "Extreme close-up on eyes" (character cropped)

## API Usage

### Request:

```json
POST /api/generate-daily-character-videos
{
  "content_data": {
    "title": "Floof's Diwali Cloud Dance",
    "character_name": "Floof",
    "segments": [
      {
        "segment": 1,
        "first_frame_description": "Floof standing on platform, full body visible...",
        "last_frame_description": "Floof leaping upward, full body visible...",
        ...
      }
    ]
  },
  "character_keyframe_uri": "https://res.cloudinary.com/.../floof.png",
  "resolution": "720p",
  "aspect_ratio": "9:16",
  "download": true,
  "auto_merge": true
}
```

### Response:

```json
{
  "content_title": "Floof's Diwali Cloud Dance",
  "character_name": "Floof",
  "total_segments": 3,
  "success_count": 3,
  "segments_results": [
    {
      "segment_number": 1,
      "status": "completed",
      "video_url": "https://...",
      "video_file": "generated_content/.../videos/floof_segment_1.mp4",
      "last_frame_generated": "generated_content/.../frames/last_frame_20250120_143045.png"
    },
    {
      "segment_number": 2,
      "status": "completed",
      "video_url": "https://...",
      "video_file": "generated_content/.../videos/floof_segment_2.mp4",
      "last_frame_generated": "generated_content/.../frames/last_frame_20250120_143112.png"
    },
    {
      "segment_number": 3,
      "status": "completed",
      "video_url": "https://...",
      "video_file": "generated_content/.../videos/floof_segment_3.mp4"
    }
  ]
}
```

## Frame Generation Flow

```
┌─────────────────────────────────────────────────────────────┐
│                      SEGMENT 1                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Generate First Frame (Imagen)                           │
│     Input: Character Image                                   │
│     Output: first_frame_seg_1.png                           │
│                                                              │
│  2. Generate Last Frame (Imagen)                            │
│     Input: Character Image + first_frame_seg_1.png          │
│     Output: last_frame_seg_1.png                            │
│                                                              │
│  3. Generate Video (Veo 3.1)                                │
│     first_frame: first_frame_seg_1.png                      │
│     last_frame: last_frame_seg_1.png                        │
│     Output: video_seg_1.mp4                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ last_frame_seg_1.png
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      SEGMENT 2                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Use Previous Last Frame                                  │
│     first_frame: last_frame_seg_1.png (from segment 1)      │
│                                                              │
│  2. Generate Last Frame (Imagen)                            │
│     Input: Character Image + last_frame_seg_1.png           │
│     Output: last_frame_seg_2.png                            │
│                                                              │
│  3. Generate Video (Veo 3.1)                                │
│     first_frame: last_frame_seg_1.png                       │
│     last_frame: last_frame_seg_2.png                        │
│     Output: video_seg_2.mp4                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ last_frame_seg_2.png
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      SEGMENT 3 (Last)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Use Previous Last Frame                                  │
│     first_frame: last_frame_seg_2.png (from segment 2)      │
│                                                              │
│  2. No Last Frame Generation (last segment)                  │
│                                                              │
│  3. Generate Video (Veo 3.1)                                │
│     first_frame: last_frame_seg_2.png                       │
│     last_frame: None                                         │
│     Output: video_seg_3.mp4                                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Benefits

### 1. Perfect Character Consistency
- Character looks identical across all segments
- No quality degradation from video extraction
- AI-generated frames maintain character features

### 2. Smooth Continuity
- Last frame of segment N = First frame of segment N+1
- No jarring transitions between segments
- Seamless flow from start to finish

### 3. Environment Consistency
- Dual reference system maintains lighting and atmosphere
- Background elements stay consistent
- Professional, polished look

### 4. Better Quality
- High-quality Imagen-generated frames
- No compression artifacts from video extraction
- Clean, crisp keyframes

### 5. Organized Storage
- All frames in one place
- Easy to find and manage
- Consistent directory structure

## Fallback Mechanisms

### If Imagen Generation Fails:

1. **First Frame Fallback**:
   - Use character keyframe image
   - Or use previous segment's last frame

2. **Last Frame Fallback**:
   - Extract last frame from generated video
   - Use first frame of segment

3. **Video Generation Continues**:
   - System doesn't fail if frame generation fails
   - Graceful degradation to extraction method

## Code Reference

### New Functions:

1. **`generate_last_frame_with_imagen()`** - `src/app/services/imagen_service.py`
   - Generates last frame with dual reference
   - Uses character image + first frame

2. **Updated `execute_daily_character_video_generation()`** - `src/app/services/content_to_video_service.py`
   - Generates both first and last frames
   - Chains frames between segments
   - Uses file_storage_manager for organization

3. **Updated `get_daily_character_prompt()`** - `src/app/data/prompts/generate_daily_character_prompt.py`
   - Includes `last_frame_description` in output
   - Enforces character visibility rule

## Example Workflow

```python
# 1. Generate content with frame descriptions
content = generate_daily_character_content(
    idea="Floof celebrating Diwali",
    character_name="Floof",
    creature_language="Soft and High-Pitched",
    num_segments=3
)

# Content includes first_frame_description AND last_frame_description for each segment

# 2. Generate videos with frame interpolation
result = generate_daily_character_videos(
    content_data=content,
    character_keyframe_uri="https://cloudinary.com/.../floof.png",
    aspect_ratio="9:16",
    download=True
)

# System automatically:
# - Generates first frame for segment 1 with Imagen
# - Generates last frame for segment 1 with Imagen (dual reference)
# - Uses segment 1 last frame as segment 2 first frame
# - Generates last frame for segment 2 with Imagen (dual reference)
# - Uses segment 2 last frame as segment 3 first frame
# - Generates videos with Veo 3.1 using both frames
# - Downloads all videos to organized directory
```

## Summary

✅ **Dual Reference System** - Character image + First frame for consistency
✅ **Frame Chaining** - Last frame → Next first frame for continuity
✅ **Character Visibility** - Full body in all generated frames
✅ **Organized Storage** - file_storage_manager for clean structure
✅ **Fallback Mechanisms** - Graceful degradation if generation fails
✅ **Better Quality** - AI-generated frames vs extracted frames
✅ **Perfect Continuity** - Seamless transitions between segments

This system ensures your character videos have professional quality with perfect character consistency and smooth continuity throughout!
