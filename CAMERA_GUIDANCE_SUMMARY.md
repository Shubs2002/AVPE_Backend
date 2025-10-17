# Camera Guidance for Daily Character Content

## Overview

Enhanced the daily character prompt with comprehensive camera guidance to create more dynamic, engaging, and professional-looking Instagram content.

## What Was Added

### 1. Camera Angles Section

Detailed guidance on different camera angles:
- **Close-up** - Face/eyes for emotions and reactions
- **Medium shot** - Upper body, shows actions and gestures
- **Wide shot** - Full body and environment
- **Extreme close-up** - Specific details
- **Over-the-shoulder** - POV perspective
- **Low angle** - Looking up (powerful/bigger)
- **High angle** - Looking down (vulnerable/smaller)
- **Eye level** - Neutral, relatable

### 2. Camera Movements Section

Guidance on dynamic camera work:
- **Static** - Stable shot for calm moments
- **Pan** - Horizontal movement
- **Tilt** - Vertical movement
- **Zoom in/out** - Building tension or revealing context
- **Tracking** - Following character
- **Shaky cam** - Chaos/excitement
- **Slow motion** - Dramatic emphasis
- **Quick cuts** - Fast-paced energy

### 3. Camera Examples for Different Moments

Practical examples matching camera work to emotions:
- **Surprise/Shock**: "Extreme close-up on eyes, quick zoom in"
- **Discovery**: "Wide shot, slow pan to reveal object"
- **Confusion**: "Medium shot, camera tilts with character's head"
- **Action/Chase**: "Tracking shot, following character movement"
- **Reaction**: "Close-up on face, static to capture expression"
- **Comedy Beat**: "Low angle looking up, static for comedic timing"
- **Reveal**: "Start close-up, zoom out to show full scene"
- **Chaos**: "Shaky cam, quick cuts between angles"
- **Cute Moment**: "Soft close-up, slight slow motion"
- **Ending**: "Wide shot, slow zoom out as character exits"

### 4. Instagram-Specific Tips

- Vary angles - Don't use same shot for every segment
- Match emotion - Close-ups for reactions, wide for action
- Dynamic movement - Static shots can be boring
- POV shots - Make viewers feel present
- Comedic framing - Unexpected angles enhance humor

## Benefits

✅ **More Dynamic Content** - Varied camera work keeps viewers engaged
✅ **Professional Look** - Proper camera angles elevate production quality
✅ **Better Storytelling** - Camera matches emotion and action
✅ **Instagram Optimized** - Fast-paced, visually interesting
✅ **Clearer Guidance** - AI knows exactly what camera work to specify

## Example Output

Before (vague):
```json
{
  "camera": "Close-up"
}
```

After (specific):
```json
{
  "camera": "Extreme close-up on eyes, quick zoom in as character realizes"
}
```

## Image Download Location

**Question**: Where is the character image downloaded from the URL?

**Answer**: The image is downloaded **in memory only** (RAM), not saved to disk.

### Technical Details:

```python
# In genai_service.py, line ~370
response = requests.get(image_input, timeout=30)  # Downloads to RAM
img = Image.open(BytesIO(response.content))       # Converts to PIL Image in RAM
```

### Key Points:

✅ **In-Memory Only** - Never saved to disk
✅ **Temporary** - Deleted after video generation
✅ **Fast** - No disk I/O overhead
✅ **Secure** - No files left on server
✅ **Fresh Download** - Downloaded for each segment, then discarded

### Process Flow:

1. User provides URL (Cloudinary, HTTP, HTTPS)
2. System detects it's a URL (not GCS URI)
3. Downloads image to RAM using `requests.get()`
4. Converts to PIL Image object in memory
5. Passes to video generation API
6. Image is garbage collected after use
7. Process repeats for next segment

### Storage Locations:

| Type | Location | Persistent? |
|------|----------|-------------|
| Character Image | RAM (memory) | ❌ No - deleted after use |
| Generated Videos | Google Cloud Storage | ✅ Yes - returned as URLs |
| Downloaded Videos (optional) | Server disk | ✅ Yes - if download=true |

## Usage

The enhanced camera guidance is automatically included when you call:

```bash
POST /api/generate-daily-character
{
  "idea": "Floof discovers a butterfly",
  "character_name": "Floof",
  "creature_language": "Soft and High-Pitched",
  "num_segments": 7
}
```

The AI will now generate segments with specific, varied camera work like:

```json
{
  "segment": 1,
  "camera": "Wide shot, slow pan right as Floof enters frame",
  ...
},
{
  "segment": 2,
  "camera": "Medium shot, tracking Floof's movement toward butterfly",
  ...
},
{
  "segment": 3,
  "camera": "Extreme close-up on eyes, static as they widen in surprise",
  ...
}
```

## Files Updated

- ✅ `src/app/data/prompts/generate_daily_character_prompt.py` - Added comprehensive camera guidance

## Result

Your daily character content will now have:
- More dynamic and varied camera work
- Professional-looking cinematography
- Better visual storytelling
- Instagram-optimized pacing
- Emotion-matched camera angles
