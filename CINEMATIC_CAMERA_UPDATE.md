# Cinematic Camera Features for Movie Auto Route

## Overview

Updated the movie generation prompts to enforce CINEMATIC camera movements and angles when triggered by the `/generate-movie-auto` route, ensuring professional, high-quality cinematography for all movie content.

## Changes Made

### 1. Movie Auto Route (`content_type="movie"`)

When generating movies through `/generate-movie-auto`, the AI now receives explicit instructions to use CINEMATIC camera work:

#### Cinematic Requirements Added:

**Cinematic Movements:**
- Slow dolly in/out
- Smooth tracking shots
- Crane shots
- Steadicam follows
- Orbital shots

**Professional Angles:**
- Dutch angles
- Low angles for power
- High angles for vulnerability
- Over-the-shoulder for dialogue

**Dynamic Shots:**
- Whip pans for energy
- Rack focus for emphasis
- Push-in for intensity
- Pull-out for revelation

**Establishing Shots:**
- Wide establishing shots
- Aerial views
- Sweeping panoramas

**Intimate Moments:**
- Close-ups with shallow depth of field
- Extreme close-ups for emotion

**Action Sequences:**
- Handheld for intensity
- Slow-motion for impact
- Quick cuts with varied angles

### 2. Examples Provided to AI

The prompt now includes specific examples of cinematic camera descriptions:

```
✅ GOOD (Cinematic):
- "Slow dolly in on character's face as realization dawns, shallow depth of field"
- "Sweeping crane shot rising from ground level to reveal the vast landscape"
- "Steadicam tracking shot following character through crowded street"
- "Low angle shot looking up at character, emphasizing power and dominance"
- "Orbital shot circling the couple as they embrace, golden hour lighting"
- "Extreme close-up of eyes with rack focus to background action"
- "Wide establishing shot with slow pan across the cityscape at sunset"

❌ BAD (Too Simple):
- "medium shot"
- "close-up"
- "wide shot"
```

### 3. Implementation Details

#### Updated Functions:

**`get_story_segments_in_sets_prompt()`**
- Used by: `/generate-movie-auto`
- Added: Cinematic camera instruction block when `content_type="movie"`
- Location: Lines after content_description is set

**`get_outline_for_story_segments_chunked()`**
- Used by: Large movie generation (chunked)
- Added: Cinematic camera instruction block when `content_type="movie"`
- Location: Lines after content_description is set

#### Code Logic:

```python
# Add cinematic camera instructions for movies
camera_instruction = ""
if content_type == "movie":
    camera_instruction = """
    
    **CRITICAL CINEMATIC CAMERA REQUIREMENT FOR MOVIES**:
    ALL camera movements and angles MUST be CINEMATIC and PROFESSIONAL.
    [... detailed instructions ...]
    """

return f"""
You are a professional Humanised Script-writer for {content_description}.
{custom_roster_instruction}
{camera_instruction}  # ← Only added for movies
{metadata_instruction}
"""
```

## Route Behavior

### `/generate-movie-auto` (Movies)
- ✅ **Cinematic camera enforced**
- Content type: `"movie"`
- Camera style: Professional, cinematic, purposeful
- Examples: Dolly shots, crane shots, tracking shots

### `/generate-prompt-based-story` (Short Films)
- ⚪ **Flexible camera work**
- Content type: `"short_film"`
- Camera style: Flexible, no forced requirements
- Examples: Can be simple or cinematic as needed

### `/generate-whatsapp-story` (WhatsApp)
- ⚪ **Aesthetic-focused camera**
- Content type: N/A (separate prompt)
- Camera style: Optimized for mobile, aesthetic moments

## Benefits

### 1. **Professional Quality**
Movies now have Hollywood-style cinematography with purposeful camera movements

### 2. **Visual Storytelling**
Camera work enhances narrative through:
- Power dynamics (low/high angles)
- Emotional intensity (push-ins, close-ups)
- Scale and scope (crane shots, wide shots)
- Character relationships (over-the-shoulder, two-shots)

### 3. **AI Video Generation Ready**
Detailed camera descriptions help AI video generators (Veo3) create:
- Smooth, professional movements
- Appropriate framing
- Dynamic visual storytelling

### 4. **Differentiation**
Clear distinction between content types:
- **Movies**: Cinematic, professional
- **Short Films**: Flexible, varied
- **WhatsApp**: Aesthetic, mobile-optimized

## Examples

### Before (Generic)
```json
{
  "camera": "close-up",
  "scene": "Character looks worried"
}
```

### After (Cinematic)
```json
{
  "camera": "Slow dolly in on character's face, shallow depth of field isolating them from the blurred background, emphasizing their growing anxiety",
  "scene": "Character's worry intensifies as realization dawns"
}
```

## Testing

### Test Movie Generation
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "An epic adventure across mountains",
    "total_segments": 20
  }'
```

**Expected:** All camera descriptions will be cinematic (dolly, crane, tracking, etc.)

### Test Short Film Generation
```bash
curl -X POST "http://localhost:8000/generate-prompt-based-story" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A simple conversation between friends",
    "segments": 7
  }'
```

**Expected:** Camera descriptions will be flexible and appropriate to the story

## Camera Movement Glossary

### Dolly
- **In**: Camera moves toward subject
- **Out**: Camera moves away from subject
- **Purpose**: Creates intimacy or reveals context

### Tracking
- **Following**: Camera follows subject's movement
- **Parallel**: Camera moves alongside subject
- **Purpose**: Maintains engagement, shows journey

### Crane
- **Up**: Camera rises from low to high
- **Down**: Camera descends from high to low
- **Purpose**: Reveals scale, creates drama

### Steadicam
- **Follow**: Smooth handheld following
- **Navigate**: Moves through spaces fluidly
- **Purpose**: Immersive, dynamic feel

### Orbital
- **Circle**: Camera circles around subject
- **Arc**: Camera moves in an arc
- **Purpose**: Shows all angles, creates drama

### Angles
- **Low**: Camera below subject (power)
- **High**: Camera above subject (vulnerability)
- **Dutch**: Tilted angle (unease, tension)
- **Over-the-shoulder**: From behind one character

### Focus
- **Rack Focus**: Shift focus from foreground to background
- **Shallow Depth**: Blurred background, sharp subject
- **Deep Focus**: Everything in focus

## Impact on Generated Content

### Story Segments Now Include:
```json
{
  "segment": 1,
  "scene": "Hero stands at cliff edge",
  "camera": "Sweeping crane shot rising from ground level, revealing the vast mountain range stretching to the horizon, hero silhouetted against golden sunset",
  "visual_style": "Cinematic",
  "lighting": "Golden hour backlight"
}
```

### Instead of:
```json
{
  "segment": 1,
  "scene": "Hero stands at cliff edge",
  "camera": "wide shot",
  "visual_style": "Standard"
}
```

## Files Modified

- ✅ `src/app/data/prompts/generate_segmented_story_prompt.py`
  - Updated `get_story_segments_in_sets_prompt()` - Added cinematic camera block
  - Updated `get_outline_for_story_segments_chunked()` - Added cinematic camera block
  - No changes to `get_story_segments_prompt()` - Keeps flexibility for short films

## Summary

Movies generated through `/generate-movie-auto` now feature professional, cinematic camera work with:
- **Purposeful movements** (dolly, crane, tracking)
- **Professional angles** (low, high, Dutch, OTS)
- **Dynamic techniques** (rack focus, push-in, pull-out)
- **Varied shots** (establishing, close-ups, action)

This ensures all movie content has Hollywood-quality cinematography that enhances visual storytelling and creates a professional viewing experience.