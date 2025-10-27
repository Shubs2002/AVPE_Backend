# Corrected Frame Interpolation Flow

## The Correct Approach

### Key Insight:
Use **extracted last frame from actual video** as the IMAGE parameter for the next segment. This ensures perfect continuity because it's the exact frame where the previous video ended.

## Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                      SEGMENT 1                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Generate FIRST FRAME with Imagen                         │
│     Input: Character Image                                   │
│     Output: first_frame_seg_1.png                           │
│                                                              │
│  2. Generate LAST FRAME with Imagen                          │
│     Input: Character Image + first_frame_seg_1.png          │
│     Output: last_frame_seg_1.png                            │
│                                                              │
│  3. Generate VIDEO with Veo 3.1                              │
│     image: first_frame_seg_1.png                            │
│     last_frame: last_frame_seg_1.png                        │
│     Output: video_seg_1.mp4                                 │
│                                                              │
│  4. EXTRACT last frame from video_seg_1.mp4                  │
│     Output: segment_1_last_frame_extracted.png              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ segment_1_last_frame_extracted.png
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      SEGMENT 2                               │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Use EXTRACTED frame from previous video                  │
│     image: segment_1_last_frame_extracted.png ✅            │
│                                                              │
│  2. Generate LAST FRAME with Imagen                          │
│     Input: Character Image + segment_1_last_frame_extracted │
│     Output: last_frame_seg_2.png                            │
│                                                              │
│  3. Generate VIDEO with Veo 3.1                              │
│     image: segment_1_last_frame_extracted.png               │
│     last_frame: last_frame_seg_2.png                        │
│     Output: video_seg_2.mp4                                 │
│                                                              │
│  4. EXTRACT last frame from video_seg_2.mp4                  │
│     Output: segment_2_last_frame_extracted.png              │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            │ segment_2_last_frame_extracted.png
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      SEGMENT 3 (Last)                        │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Use EXTRACTED frame from previous video                  │
│     image: segment_2_last_frame_extracted.png ✅            │
│                                                              │
│  2. Generate LAST FRAME with Imagen                          │
│     Input: Character Image + segment_2_last_frame_extracted │
│     Output: last_frame_seg_3.png ✅                         │
│                                                              │
│  3. Generate VIDEO with Veo 3.1                              │
│     image: segment_2_last_frame_extracted.png               │
│     last_frame: last_frame_seg_3.png ✅                     │
│     Output: video_seg_3.mp4                                 │
│                                                              │
│  4. No extraction needed (last segment - no next segment)    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   CLEANUP     │
                    │ Delete frames │
                    └───────────────┘
```

## Why Extract from Video?

### Option 1: Use Generated Last Frame (❌ Wrong)
```python
# Segment 1 generates: last_frame_seg_1.png
# Segment 2 uses: last_frame_seg_1.png as IMAGE

# Problem: The actual video might not end exactly at the generated frame
# Result: Discontinuity between segments
```

### Option 2: Extract from Video (✅ Correct)
```python
# Segment 1 generates video → Extract actual last frame
# Segment 2 uses: extracted_last_frame_seg_1.png as IMAGE

# Benefit: Perfect continuity - video starts exactly where previous ended
# Result: Seamless transitions
```

## Code Implementation

### Segment Processing Logic:

```python
for i, segment in enumerate(segments, 1):
    is_last_segment = (i == len(segments))
    
    # STEP 1: Determine IMAGE parameter
    if i == 1:
        # First segment: Generate with Imagen
        first_frame = generate_first_frame_with_imagen(
            character_image_url=character_keyframe_uri,
            frame_description=first_frame_description
        )
    else:
        # Subsequent segments: Use extracted frame from previous video
        first_frame = previous_frame  # This is the extracted frame
    
    # STEP 2: Generate LAST_FRAME parameter (for ALL segments)
    last_frame = generate_last_frame_with_imagen(
        character_image_url=character_keyframe_uri,
        first_frame_path=first_frame,
        last_frame_description=last_frame_description
    )
    
    # STEP 3: Generate video with Veo 3.1
    video_url = generate_video_with_keyframes(
        prompt=prompt,
        first_frame=first_frame,      # IMAGE parameter
        last_frame=last_frame,         # LAST_FRAME parameter
        duration=8
    )
    
    # STEP 4: Download and extract last frame for next segment
    video_path = download_video(video_url)
    
    if not is_last_segment:
        # Extract last frame from video for next segment
        extracted_frame = extract_last_frame_from_video(video_path)
        previous_frame = extracted_frame  # Store for next iteration
```

## Veo 3.1 API Call

```python
from google import genai

client = genai.Client()

operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt=prompt,
    image=first_image,  # Extracted from previous video (or generated for seg 1)
    config=types.GenerateVideosConfig(
        last_frame=last_image  # Generated with Imagen
    ),
)

# Poll until complete
while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation)

# Download video
video = operation.response.generated_videos[0]
client.files.download(file=video.video)
video.video.save("segment.mp4")

# Extract last frame for next segment
extract_last_frame_from_video("segment.mp4", "last_frame_extracted.png")
```

## Frame Cleanup

After all videos are successfully generated, temporary frames are deleted:

```python
if success_count == total_segments and error_count == 0:
    # All videos generated successfully
    shutil.rmtree(frames_dir)
    print("✅ Frames directory deleted")
else:
    # Some segments failed - keep frames for retry
    print("⚠️ Skipping frame cleanup (some segments failed)")
```

## Directory Structure

### During Generation:
```
generated_content/daily_character/Title/
├── frames/
│   ├── first_frame_20250120_143022.png          (Segment 1 first)
│   ├── last_frame_20250120_143045.png           (Segment 1 last - generated)
│   ├── segment_1_last_frame_extracted.png       (Extracted from video 1)
│   ├── last_frame_20250120_143112.png           (Segment 2 last - generated)
│   ├── segment_2_last_frame_extracted.png       (Extracted from video 2)
│   └── last_frame_20250120_143140.png           (Segment 3 last - generated)
└── videos/
    ├── floof_segment_1.mp4
    ├── floof_segment_2.mp4
    └── floof_segment_3.mp4
```

### After Successful Generation:
```
generated_content/daily_character/Title/
└── videos/
    ├── floof_segment_1.mp4
    ├── floof_segment_2.mp4
    └── floof_segment_3.mp4

(frames/ directory deleted ✅)
```

## Benefits

### 1. Perfect Continuity
- Video N+1 starts exactly where video N ended
- No jarring transitions
- Seamless flow

### 2. Character Consistency
- Generated last frames maintain character appearance
- Dual reference (character + first frame) ensures consistency
- Character always fully visible

### 3. Clean Storage
- Temporary frames deleted after success
- Only videos remain
- Organized directory structure

### 4. Retry Support
- If generation fails, frames are kept
- Can retry failed segments
- No need to regenerate frames

## Example Output

### Segment 1:
```
🎨 Generating first frame with Imagen...
✅ First frame generated: first_frame_20250120_143022.png

🎨 Generating last frame with Imagen...
✅ Last frame generated: last_frame_20250120_143045.png

🎬 Generating video with first and last frames...
✅ Video generated

📥 Downloaded to: floof_segment_1.mp4

🖼️ Extracting last frame from video for next segment...
✅ Last frame extracted: segment_1_last_frame_extracted.png
   → Will be used as IMAGE parameter for segment 2
```

### Segment 2:
```
🔗 Using extracted last frame from previous video: segment_1_last_frame_extracted.png

🎨 Generating last frame with Imagen...
✅ Last frame generated: last_frame_20250120_143112.png

🎬 Generating video with first and last frames...
✅ Video generated

📥 Downloaded to: floof_segment_2.mp4

🖼️ Extracting last frame from video for next segment...
✅ Last frame extracted: segment_2_last_frame_extracted.png
   → Will be used as IMAGE parameter for segment 3
```

### Segment 3 (Last):
```
🔗 Using extracted last frame from previous video: segment_2_last_frame_extracted.png

🎨 Generating last frame with Imagen...
✅ Last frame generated: last_frame_20250120_143140.png
   → Last segment: Frame will be used for video interpolation only (no extraction needed)

🎬 Generating video with first and last frames...
✅ Video generated

📥 Downloaded to: floof_segment_3.mp4

⏭️ Last segment - no frame extraction needed
```

### Cleanup:
```
🎉 Daily Character Video Generation Complete!
✅ Successful: 3/3

🧹 Cleaning up temporary frames...
✅ Frames directory deleted: generated_content/daily_character/Title/frames
```

## Summary

✅ **Extracted Frames** - Use actual video last frame for perfect continuity
✅ **Generated Last Frames** - Use Imagen for character consistency
✅ **Dual Reference** - Character image + first frame for best results
✅ **Automatic Cleanup** - Frames deleted after successful generation
✅ **Retry Support** - Frames kept if generation fails
✅ **Organized Storage** - Clean directory structure

This approach ensures seamless video transitions with perfect character consistency!
