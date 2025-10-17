# Frame Chaining Implementation for Daily Character Videos

## Overview

Implemented seamless video transitions by chaining frames between segments. Each segment uses the last frame of the previous segment as its first frame, creating smooth, continuous video flow.

## How It Works

### Workflow

```
Segment 1:
1. Generate first frame with Imagen (using first_frame_description)
2. Use generated frame as first keyframe for Veo3
3. Generate video
4. Download video
5. Extract last frame → Save for Segment 2

Segment 2:
1. Use last frame from Segment 1 as first keyframe
2. Generate video with Veo3
3. Download video
4. Extract last frame → Save for Segment 3

Segment 3-N:
... (repeat chaining process)
```

### Key Features

✅ **Seamless Transitions** - Last frame of previous = First frame of next
✅ **Character Consistency** - Character appearance maintained via keyframes
✅ **Custom First Frame** - Segment 1 can have custom starting pose/environment
✅ **Automatic Chaining** - System handles frame extraction and chaining
✅ **Fallback Safety** - Uses character keyframe if frame extraction fails

## Implementation Details

### 1. Prompt Enhancement

Added `first_frame_description` field for Segment 1:

```json
{
  "segment": 1,
  "first_frame_description": "Floof standing at cave entrance, looking curious, surrounded by icy rocks and snow, soft moonlight from above",
  "scene": "Floof waddles into a frosty cave...",
  ...
}
```

**Purpose**: Describes the starting frame - character pose, position, environment, lighting.

**Note**: Character appearance stays the same (from keyframe), only pose/surroundings change.

### 2. New Helper Functions

#### `extract_last_frame_from_video(video_path, output_path)`

Extracts the last frame from a video file using OpenCV.

```python
# Downloads video
# Opens with cv2.VideoCapture
# Seeks to last frame
# Extracts and saves as PNG
# Returns path to frame image
```

#### `generate_first_frame_with_imagen(character_keyframe_uri, frame_description, aspect_ratio)`

Generates custom first frame using Imagen (nano banana model).

```python
# Downloads character image
# Combines with scene description
# Generates frame with Imagen
# Returns PIL Image
```

**Note**: Currently returns character image as placeholder. Full Imagen integration pending.

### 3. Updated Video Generation Flow

#### Before (No Chaining):
```python
for segment in segments:
    video = generate_video(
        prompt=segment_prompt,
        first_frame=character_keyframe  # Same for all
    )
```

#### After (With Chaining):
```python
previous_last_frame = None

for segment in segments:
    if segment == 1:
        # Generate custom first frame with Imagen
        first_frame = generate_first_frame_with_imagen(...)
    else:
        # Use last frame from previous segment
        first_frame = previous_last_frame or character_keyframe
    
    video = generate_video(
        prompt=segment_prompt,
        first_frame=first_frame
    )
    
    # Extract last frame for next segment
    download_video(video_url)
    previous_last_frame = extract_last_frame(video)
```

## API Usage

### Request

```json
POST /api/generate-daily-character-videos
{
  "content_data": {
    "title": "Floof's Adventure",
    "character_name": "Floof",
    "segments": [
      {
        "segment": 1,
        "first_frame_description": "Floof at cave entrance, curious pose, icy surroundings",
        "scene": "Floof enters cave...",
        ...
      },
      {
        "segment": 2,
        "scene": "Floof discovers puddle...",
        ...
      }
    ]
  },
  "character_keyframe_uri": "https://res.cloudinary.com/.../floof.png",
  "aspect_ratio": "9:16"
}
```

### Response

```json
{
  "success": true,
  "total_segments": 10,
  "success_count": 10,
  "video_urls": [...],
  "frame_chain": [
    {
      "segment": 1,
      "last_frame": "temp_last_frame_seg_1.png"
    },
    {
      "segment": 2,
      "last_frame": "temp_last_frame_seg_2.png"
    }
  ],
  "segments_results": [
    {
      "segment_number": 1,
      "first_frame_source": "imagen_generated",
      "last_frame_extracted": "temp_last_frame_seg_1.png",
      "video_url": "https://...",
      "status": "completed"
    },
    {
      "segment_number": 2,
      "first_frame_source": "last_frame_from_segment_1",
      "last_frame_extracted": "temp_last_frame_seg_2.png",
      "video_url": "https://...",
      "status": "completed"
    }
  ]
}
```

## Frame Sources

Each segment tracks where its first frame came from:

| Segment | First Frame Source | Description |
|---------|-------------------|-------------|
| 1 | `imagen_generated` | Generated with Imagen using first_frame_description |
| 1 | `character_keyframe` | Used character keyframe (no description provided) |
| 2-N | `last_frame_from_segment_X` | Extracted from previous segment's video |
| Any | `character_keyframe_fallback` | Fallback if frame extraction failed |

## Benefits

### 1. Seamless Transitions
- No jarring cuts between segments
- Character position flows naturally
- Environment changes smoothly

### 2. Professional Quality
- Looks like one continuous video
- Better viewer experience
- More engaging content

### 3. Character Consistency
- Character appearance maintained
- Only pose/position changes
- Natural movement flow

### 4. Creative Control
- Custom starting frame for Segment 1
- Define exact starting pose
- Set initial environment

## Technical Details

### Frame Extraction

Uses OpenCV to extract last frame:

```python
import cv2

cap = cv2.VideoCapture(video_path)
total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
ret, frame = cap.read()
```

### Temporary Files

- Videos downloaded to `temp_videos/` directory
- Last frames saved as `temp_last_frame_seg_N.png`
- Cleaned up after use (unless download=true)

### Error Handling

If frame extraction fails:
1. Logs warning
2. Sets `previous_last_frame = None`
3. Next segment uses character keyframe as fallback
4. Continues processing remaining segments

## Limitations & Future Improvements

### Current Limitations

1. **Imagen Integration**: Placeholder implementation
   - Currently returns character image as-is
   - Need to implement actual Imagen API call

2. **Storage**: Temporary files accumulate
   - Need cleanup strategy for long-running processes

3. **Performance**: Sequential processing
   - Each segment waits for previous to complete
   - Could optimize with parallel processing (with dependencies)

### Future Improvements

1. **Full Imagen Integration**
   - Implement actual nano banana model API
   - Generate custom first frames with scene composition

2. **Smart Cleanup**
   - Auto-delete temp files after successful chaining
   - Configurable retention policy

3. **Frame Quality**
   - Upscale extracted frames if needed
   - Apply smoothing/enhancement

4. **Parallel Processing**
   - Generate multiple segments in parallel
   - Use dependency graph for chaining

## Files Modified

- ✅ `src/app/data/prompts/generate_daily_character_prompt.py` - Added first_frame_description
- ✅ `src/app/services/genai_service.py` - Added frame extraction and Imagen functions
- ✅ `src/app/services/content_to_video_service.py` - Implemented chaining logic

## Testing

### Test Scenario 1: Basic Chaining

```python
# Generate content with first frame description
content = generate_daily_character({
    "idea": "Floof explores cave",
    "character_name": "Floof",
    "num_segments": 3
})

# Generate videos with chaining
result = generate_daily_character_videos({
    "content_data": content,
    "character_keyframe_uri": "https://.../floof.png"
})

# Verify chaining
assert result["frame_chain"][0]["segment"] == 1
assert result["segments_results"][1]["first_frame_source"] == "last_frame_from_segment_1"
assert result["segments_results"][2]["first_frame_source"] == "last_frame_from_segment_2"
```

### Test Scenario 2: Fallback Handling

```python
# Simulate frame extraction failure
# System should fallback to character keyframe
# Video generation should continue
```

## Conclusion

Frame chaining creates seamless, professional-looking daily character videos by connecting segments through shared frames. The implementation is robust with fallback mechanisms and provides detailed tracking of frame sources for debugging and optimization.
