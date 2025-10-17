# Daily Character Content Generation Guide

## Overview

Generate viral Instagram content for your recurring character using **pure visual storytelling** with creature sounds only. Perfect for character-based Instagram pages.

## Key Features

✅ **NO Dialogue/Narration** - Character communicates through creature sounds only
✅ **Keyframe-Based** - Use your character's image as keyframe in Veo3
✅ **Visual Comedy** - Actions and reactions tell the story
✅ **Quick Content** - 7-10 segments (~1 minute videos)
✅ **Instagram Optimized** - Relatable, shareable, viral-ready

## API Endpoint

```
POST /api/generate-daily-character
```

## Request Format

```json
{
  "idea": "Character sees his own reflection in a puddle and gets scared",
  "character_name": "Floof",
  "creature_language": "Soft and High-Pitched",
  "num_segments": 7
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `idea` | string | ✅ Yes | The daily life moment/situation |
| `character_name` | string | ✅ Yes | Name of your character |
| `creature_language` | string | ❌ No | Voice type (default: "Soft and High-Pitched") |
| `num_segments` | integer | ❌ No | Number of segments 1-10 (default: 7) |

### Creature Language - Custom Descriptions

You can use **ANY description** that fits your character's voice! Here are some examples:

**Common Examples**:
1. **"Soft and High-Pitched"**
   - Cute, gentle squeaks and chirps
   - Perfect for: Cute characters, baby creatures

2. **"Magical or Otherworldly"**
   - Mystical, ethereal sounds with echo effects
   - Perfect for: Fantasy creatures, magical beings

3. **"Muffled and Low"**
   - Deep, grumbly sounds
   - Perfect for: Large creatures, gentle giants

**Custom Combinations**:
- "Soft and High-Pitched and mystical"
- "Deep and Grumbly with echoes"
- "Squeaky and playful"
- "Ethereal and melodic"
- "Raspy and mysterious"
- "Bubbly and energetic"

**Pro Tip**: Describe your character's voice however you imagine it! The AI will adapt the creature sounds to match your description.


## Example Usage

### Example 1: Floof Sees Reflection

```json
POST /api/generate-daily-character
{
  "idea": "Floof sees his own reflection in a puddle and gets scared, thinking it's another creature",
  "character_name": "Floof",
  "creature_language": "Soft and High-Pitched",
  "num_segments": 7
}
```

### Example 2: Floof Discovers Butterfly

```json
POST /api/generate-daily-character
{
  "idea": "Floof discovers a butterfly and tries to catch it but keeps missing",
  "character_name": "Floof",
  "creature_language": "Soft and High-Pitched",
  "num_segments": 8
}
```

### Example 3: Floof Tries to Eat Cookie

```json
POST /api/generate-daily-character
{
  "idea": "Floof tries to eat a cookie but it's too big for his mouth",
  "character_name": "Floof",
  "creature_language": "Soft and High-Pitched",
  "num_segments": 6
}
```

## Response Structure

The API returns a JSON with:

```json
{
  "content": {
    "title": "Floof's Reflection Scare",
    "character_name": "Floof",
    "creature_language": "Soft and High-Pitched",
    "keyframe_note": "Use Floof's image as first keyframe",
    "segments": [
      {
        "segment": 1,
        "duration": 8,
        "scene": "Visual description",
        "action": "What Floof does",
        "reaction": "Floof's emotion",
        "creature_sounds": [
          {
            "time": "2.5s",
            "sound_type": "curious chirp",
            "emotion": "curiosity",
            "description": "soft, high-pitched chirp"
          }
        ],
        "background": {
          "location": "Near a puddle",
          "video_prompt_background": "Complete scene description"
        },
        "audio_timing": {
          "creature_sounds": {...},
          "background_music": {...},
          "sound_effects": [...]
        }
      }
    ]
  }
}
```

## Using with Veo3 Keyframes

### Step 1: Generate Content
```bash
POST /api/generate-daily-character
{
  "idea": "Your idea here",
  "character_name": "Floof",
  "creature_language": "Soft and High-Pitched"
}
```

### Step 2: Upload Character Image to GCS
Upload your character's image (e.g., Floof.png) to Google Cloud Storage and get the URI:
```
gs://your-bucket/characters/floof.png
```

### Step 3: Generate Videos with Keyframes
For each segment, use the keyframe endpoint:

```bash
POST /api/generate-video-with-keyframes
{
  "prompt": "[segment.scene + segment.action + segment.background.video_prompt_background]",
  "first_frame_gcs_uri": "gs://your-bucket/characters/floof.png",
  "duration": 8,
  "aspect_ratio": "9:16"
}
```

## Content Ideas

### Funny Reactions
- Sees reflection and gets scared
- Hears strange noise and investigates
- Discovers mirror for first time
- Finds something unexpected

### Relatable Struggles
- Trying to wake up in morning
- Attempting to cook/eat
- Dealing with technology
- Cleaning up mess

### Character Quirks
- Weird sleeping positions
- Funny eating habits
- Strange walking style
- Unique way of playing

### Everyday Adventures
- Going shopping
- Exploring outdoors
- Meeting new things
- Discovering objects

### Emotional Moments
- Happy dance
- Sad moment
- Confused state
- Excited discovery

## Best Practices

### ✅ DO:
- Focus on visual comedy
- Use clear, simple actions
- Show emotions through body language
- Keep it relatable
- Make it shareable
- Use creature sounds to enhance emotion

### ❌ DON'T:
- Add dialogue or narration
- Make it too complex
- Use human speech
- Forget the creature sounds
- Make segments too long

## Tips for Viral Content

1. **Hook in 2 Seconds**: Start with immediate visual action
2. **Relatable Situations**: Everyday moments people recognize
3. **Cute Factor**: Emphasize character's adorable qualities
4. **Emotional Range**: Show different emotions through sounds and actions
5. **Shareable**: Create "Tag someone who..." moments
6. **Consistent Character**: Use same keyframe image for brand recognition

## Python Example

```python
import requests

# Generate content
response = requests.post("http://your-api/api/generate-daily-character", json={
    "idea": "Floof discovers a bubble and tries to catch it",
    "character_name": "Floof",
    "creature_language": "Soft and High-Pitched",
    "num_segments": 7
})

content = response.json()["content"]

# Generate videos for each segment
for segment in content["segments"]:
    # Combine scene description
    prompt = f"{segment['scene']}. {segment['action']}. {segment['background']['video_prompt_background']}"
    
    # Generate video with keyframe
    video_response = requests.post("http://your-api/api/generate-video-with-keyframes", json={
        "prompt": prompt,
        "first_frame_gcs_uri": "gs://your-bucket/characters/floof.png",
        "duration": 8,
        "aspect_ratio": "9:16"
    })
    
    print(f"Segment {segment['segment']}: {video_response.json()}")
```

## Character Consistency

Since you're using keyframes:
- ✅ Character appearance is **automatically consistent**
- ✅ No need to describe character in detail
- ✅ Focus on **actions and reactions**
- ✅ Same keyframe = same character every time

## Troubleshooting

**Q: Character doesn't look consistent?**
A: Make sure you're using the same keyframe image for all segments

**Q: Too much dialogue in output?**
A: This shouldn't happen - the system is configured for NO dialogue. If it does, report as bug.

**Q: Creature sounds don't match character?**
A: Choose the right `creature_language` option that fits your character's personality

**Q: Videos too long?**
A: Reduce `num_segments` (max 10, recommended 7 for ~1 minute)

## Support

For issues or questions, check the API documentation or contact support.


---

## NEW: Generate Videos with Keyframes

### Endpoint: `/api/generate-daily-character-videos`

This endpoint takes the output from `/api/generate-daily-character` and automatically generates videos for all segments using your character's image as a keyframe.

### Request Format

```json
POST /api/generate-daily-character-videos
{
  "content_data": {
    // Output from /api/generate-daily-character
    "title": "First Mirror Fumble",
    "character_name": "Floof",
    "segments": [...]
  },
  "character_keyframe_uri": "gs://your-bucket/characters/floof.png",
  "resolution": "720p",
  "aspect_ratio": "9:16",
  "download": false,
  "auto_merge": true,
  "cleanup_segments": true
}
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content_data` | object | ✅ Yes | Complete output from `/generate-daily-character` |
| `character_keyframe_uri` | string | ✅ Yes | Image URI: GCS (gs://...), HTTP/HTTPS URL, or Cloudinary URL |
| `resolution` | string | ❌ No | Video resolution: "720p" or "1080p" (default: "720p") |
| `aspect_ratio` | string | ❌ No | Video aspect ratio: "9:16", "16:9", "1:1" (default: "9:16") |
| `download` | boolean | ❌ No | Download videos to server (default: false) |
| `auto_merge` | boolean | ❌ No | Automatically merge segments into final video (default: false) |
| `cleanup_segments` | boolean | ❌ No | Delete individual segments after merge (default: true) |

### Complete Workflow Example

#### Step 1: Generate Content

```bash
POST /api/generate-daily-character
{
  "idea": "Floof sees his reflection and gets scared",
  "character_name": "Floof",
  "creature_language": "Soft and High-Pitched",
  "num_segments": 7
}
```

**Response:**
```json
{
  "content": {
    "title": "First Mirror Fumble",
    "character_name": "Floof",
    "segments": [
      {
        "segment": 1,
        "scene": "Floof waddles into a frosty cave...",
        "action": "He peers into the water...",
        ...
      }
    ]
  }
}
```

#### Step 2: Get Character Image URI

You can use any of these options:

**Option A: Cloudinary URL** (Easiest)
```
https://res.cloudinary.com/your-cloud/image/upload/v123/floof.png
```

**Option B: Google Cloud Storage**
```bash
gsutil cp floof.png gs://your-bucket/characters/floof.png
# URI: gs://your-bucket/characters/floof.png
```

**Option C: Any HTTP/HTTPS URL**
```
https://example.com/images/floof.png
```

#### Step 3: Generate Videos with Keyframes

```bash
POST /api/generate-daily-character-videos
{
  "content_data": {
    // Paste the entire "content" object from Step 1
    "title": "First Mirror Fumble",
    "character_name": "Floof",
    "segments": [...]
  },
  "character_keyframe_uri": "gs://your-bucket/characters/floof.png",
  "aspect_ratio": "9:16",
  "auto_merge": true
}
```

**Response:**
```json
{
  "success": true,
  "content_type": "daily_character",
  "character_name": "Floof",
  "title": "First Mirror Fumble",
  "total_segments": 7,
  "success_count": 7,
  "error_count": 0,
  "video_urls": [
    "https://storage.googleapis.com/...",
    "https://storage.googleapis.com/...",
    ...
  ],
  "segments_results": [
    {
      "segment_number": 1,
      "status": "completed",
      "video_url": "https://...",
      "prompt": "Floof waddles into a frosty cave..."
    }
  ],
  "merged_video": {
    "success": true,
    "video_urls": [...],
    "total_segments": 7
  }
}
```

### Python Example - Complete Workflow

```python
import requests

# Step 1: Generate content
content_response = requests.post("http://your-api/api/generate-daily-character", json={
    "idea": "Floof discovers a butterfly and tries to catch it",
    "character_name": "Floof",
    "creature_language": "Soft and High-Pitched",
    "num_segments": 7
})

content_data = content_response.json()["content"]

# Step 2: Generate videos with keyframes (using Cloudinary URL)
video_response = requests.post("http://your-api/api/generate-daily-character-videos", json={
    "content_data": content_data,
    "character_keyframe_uri": "https://res.cloudinary.com/.../floof.png",
    "aspect_ratio": "9:16",
    "auto_merge": True,
    "cleanup_segments": True
})

result = video_response.json()

print(f"✅ Generated {result['success_count']}/{result['total_segments']} videos")
print(f"Video URLs: {result['video_urls']}")

if result.get("merged_video", {}).get("success"):
    print(f"🎬 Merged video ready!")
```

### Features

✅ **Automatic Keyframe Application** - Character image used as first frame for every segment
✅ **Batch Processing** - Generates all segments automatically
✅ **Retry Logic** - Automatically retries failed segments up to 3 times
✅ **Progress Tracking** - Real-time status for each segment
✅ **Auto-Merge** - Optional automatic merging into final video
✅ **Error Handling** - Detailed error messages for failed segments

### Benefits

1. **Character Consistency** - Keyframe ensures character looks identical in every segment
2. **One-Click Generation** - No need to manually generate each segment
3. **Automatic Retry** - Handles temporary failures automatically
4. **Merge Ready** - Optional auto-merge creates final video instantly
5. **Production Ready** - Built-in error handling and progress tracking

### Retry Failed Segments

If some segments fail, you can retry them using the existing retry endpoint:

```bash
POST /api/retry-failed-segments
{
  "previous_results": {
    // Paste the response from /generate-daily-character-videos
  },
  "resolution": "720p",
  "aspectRatio": "9:16"
}
```

### Supported Image Sources

✅ **Cloudinary URLs** - Direct use, no upload needed
✅ **Google Cloud Storage** - GCS URIs (gs://...)
✅ **HTTP/HTTPS URLs** - Any publicly accessible image URL
✅ **Direct Upload** - Upload to your own server

### Notes

- Images are automatically downloaded from HTTP/HTTPS URLs
- Each segment uses the character image as first keyframe only (not last frame)
- Videos are generated sequentially with 2-second delays to avoid rate limits
- Failed segments can be retried individually
- Auto-merge requires at least 50% of segments to succeed

### Comparison: Old vs New Workflow

#### Old Workflow (Manual)
```python
# 1. Generate content
content = generate_daily_character(...)

# 2. For each segment manually:
for segment in content["segments"]:
    prompt = build_prompt(segment)
    video = generate_video_with_keyframes(
        prompt=prompt,
        first_frame="gs://bucket/floof.png",
        ...
    )
    # Handle errors, retries, etc.
```

#### New Workflow (Automatic)
```python
# 1. Generate content
content = generate_daily_character(...)

# 2. Generate all videos at once
result = generate_daily_character_videos(
    content_data=content,
    character_keyframe_uri="https://res.cloudinary.com/.../floof.png",
    auto_merge=True
)
# Done! All videos generated and merged
```

### Troubleshooting

**Q: Videos don't have consistent character appearance?**
A: Make sure you're using the correct GCS URI for the character image

**Q: Some segments fail?**
A: Use the retry endpoint or check the error messages in `segments_results`

**Q: Auto-merge fails?**
A: Ensure at least 50% of segments succeeded, or merge manually using `/api/merge-content-videos`

**Q: Rate limit errors?**
A: The system automatically retries with exponential backoff. Wait and retry failed segments.
