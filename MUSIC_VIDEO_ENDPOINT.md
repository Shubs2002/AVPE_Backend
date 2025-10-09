# AI Music Video Generation Endpoint

## Overview

New endpoint for generating AI music video prompts from song lyrics, optimized for Veo3 video generation. Creates professionally timed, visually stunning music video segments that sync perfectly with your song.

## Endpoint

```
POST /generate-music-video
```

## Request Model

```json
{
  "song_lyrics": "string (required)",
  "song_length": "integer (required, in seconds)",
  "background_voice_needed": "boolean (optional, default: false)",
  "additional_dialogues": "array (optional)",
  "custom_character_roster": "array (optional)",
  "music_genre": "string (optional)",
  "visual_theme": "string (optional)"
}
```

### Parameters

- **`song_lyrics`** (required): The complete song lyrics
- **`song_length`** (required): Song length in seconds
- **`background_voice_needed`** (optional): Whether to include background narration/voiceover
- **`additional_dialogues`** (optional): Dialogues to add between verses
  ```json
  [
    {"timestamp": 30, "character": "char_id", "line": "Dialogue text"},
    {"timestamp": 60, "character": "char_id", "line": "Another dialogue"}
  ]
  ```
- **`custom_character_roster`** (optional): Pre-defined characters/performers
- **`music_genre`** (optional): Music genre (pop, rock, hip-hop, R&B, etc.)
- **`visual_theme`** (optional): Visual concept/theme for the video

## Response Format

```json
{
  "music_video": {
    "title": "Song Title - Music Video",
    "artist": "Artist Name",
    "song_length": 180,
    "total_segments": 15,
    "music_genre": "Pop",
    "visual_theme": "Urban romance",
    "short_summary": "Video concept description",
    "description": "Compelling viewer description",
    "hashtags": ["#MusicVideo", "#AIGenerated", "#Pop"],
    "background_voice_info": {
      "enabled": false,
      "voice_type": "Narrator",
      "tone": "Emotional",
      "purpose": "Story narration"
    },
    "characters_roster": [...],
    "segments": [
      {
        "segment": 1,
        "segment_type": "intro",
        "start_time": 0,
        "end_time": 10,
        "duration": 10,
        "lyrics": "Lyrics for this segment",
        "scene": "Visual description",
        "visual_concept": "What this represents",
        "camera": "Cinematic camera movement",
        "shot_type": "performance/narrative/artistic",
        "characters_present": ["char_id"],
        "character_actions": {
          "char_id": "Singing emotionally"
        },
        "background_definition": {...},
        "visual_style": "Cinematic",
        "mood": "Emotional",
        "color_grading": "Warm tones",
        "special_effects": ["Slow-motion"],
        "sync_notes": "Camera push-in on chorus hit",
        "background_voice": "Optional narration",
        "editing_style": "Match cuts to beat"
      }
    ],
    "visual_themes": ["Love", "Urban life"],
    "color_palette_overall": "Warm with neon accents",
    "editing_notes": "Fast-paced, rhythm-based cuts",
    "performance_notes": "High energy, emotional delivery"
  }
}
```

## Key Features

### 🎵 **Lyric Synchronization**
- Segments perfectly timed to song structure
- Visuals sync with lyrics and music beats
- Accurate timing for Veo3 generation

### 🎬 **Cinematic Camera Work**
- Professional music video camera movements
- Dynamic angles and shots
- Performance, narrative, and artistic shots

### 🎭 **Character/Performer Support**
- Custom character rosters for performers
- Consistent visual descriptions
- Performance style specifications

### 🗣️ **Optional Background Voice**
- Add narration/voiceover if needed
- Complements the song
- Storytelling enhancement

### 💬 **Additional Dialogues**
- Insert dialogues at specific timestamps
- Dramatic moments between verses
- Story development

### 🎨 **Visual Themes**
- Genre-specific visual styles
- Custom visual concepts
- Color grading and mood

## Usage Examples

### Example 1: Basic Music Video
```bash
curl -X POST "http://localhost:8000/generate-music-video" \
  -H "Content-Type: application/json" \
  -d '{
    "song_lyrics": "Verse 1:\nWalking down the street\nFeeling the beat\n\nChorus:\nThis is my time\nThis is my rhyme",
    "song_length": 180,
    "music_genre": "Pop"
  }'
```

### Example 2: With Background Voice
```bash
curl -X POST "http://localhost:8000/generate-music-video" \
  -H "Content-Type: application/json" \
  -d '{
    "song_lyrics": "...",
    "song_length": 200,
    "background_voice_needed": true,
    "music_genre": "R&B",
    "visual_theme": "Urban romance story"
  }'
```

### Example 3: With Custom Characters
```bash
curl -X POST "http://localhost:8000/generate-music-video" \
  -H "Content-Type: application/json" \
  -d '{
    "song_lyrics": "...",
    "song_length": 240,
    "custom_character_roster": [
      {
        "name": "Lead Singer",
        "role": "Main Performer",
        "physical_appearance": {
          "gender": "Female",
          "age": "25",
          "hair_color": "Long black hair",
          "clothing": "Stylish urban outfit"
        }
      }
    ],
    "music_genre": "Hip-Hop"
  }'
```

### Example 4: With Additional Dialogues
```bash
curl -X POST "http://localhost:8000/generate-music-video" \
  -H "Content-Type: application/json" \
  -d '{
    "song_lyrics": "...",
    "song_length": 220,
    "additional_dialogues": [
      {
        "timestamp": 60,
        "character": "lead_singer",
        "line": "This is where it all began..."
      },
      {
        "timestamp": 120,
        "character": "lead_singer",
        "line": "And this is where it ends."
      }
    ],
    "music_genre": "Ballad"
  }'
```

### Python Example
```python
import requests

url = "http://localhost:8000/generate-music-video"
payload = {
    "song_lyrics": """
    Verse 1:
    In the city lights, I find my way
    Through the night, until the day
    
    Chorus:
    We're alive, we're free
    This is where we're meant to be
    Dancing through the night
    Everything feels right
    
    Verse 2:
    Hearts beating as one
    Our journey's just begun
    
    Chorus:
    We're alive, we're free
    This is where we're meant to be
    """,
    "song_length": 180,
    "background_voice_needed": False,
    "music_genre": "Electronic Pop",
    "visual_theme": "Neon city nightlife"
}

response = requests.post(url, json=payload)
music_video = response.json()["music_video"]

print(f"Title: {music_video['title']}")
print(f"Total Segments: {music_video['total_segments']}")
print(f"Genre: {music_video['music_genre']}")

# Access segments
for segment in music_video['segments']:
    print(f"\nSegment {segment['segment']}:")
    print(f"  Type: {segment['segment_type']}")
    print(f"  Time: {segment['start_time']}-{segment['end_time']}s")
    print(f"  Lyrics: {segment['lyrics'][:50]}...")
    print(f"  Camera: {segment['camera'][:60]}...")
```

## Music Video Structure

### Segment Types

1. **Intro** (0-10s)
   - Visual hook
   - Sets the mood
   - Establishes theme

2. **Verse** (8-12s each)
   - Story progression
   - Character development
   - Narrative moments

3. **Chorus** (8-10s each)
   - High-energy visuals
   - Memorable shots
   - Repeatable with variations

4. **Bridge** (8-12s)
   - Emotional peak
   - Visual twist
   - Dramatic moment

5. **Outro** (5-10s)
   - Powerful closing
   - Final image
   - Resolution

6. **Dialogue** (5-8s)
   - Story moments
   - Character interactions
   - Dramatic beats

## Camera Styles

### Performance Shots
- Close-up of face while singing
- Wide shot of full performance
- Instrument close-ups
- Dance/movement shots
- Dynamic angles

### Narrative Shots
- Story moments illustrating lyrics
- Character interactions
- Symbolic visuals
- Location establishing shots
- Emotional reactions

### Artistic Shots
- Abstract visuals
- Slow-motion beauty shots
- Light and shadow play
- Reflections and mirrors
- Silhouettes
- Creative perspectives

## Visual Styles by Genre

### Pop
- Colorful, energetic
- Performance-focused
- Upbeat, vibrant
- High production value

### Rock
- Edgy, high-energy
- Dramatic lighting
- Powerful, intense
- Raw performance

### Hip-Hop
- Urban settings
- Confident performances
- Stylish, cool
- Street culture

### R&B
- Smooth, sensual
- Intimate lighting
- Emotional, soulful
- Romantic themes

### Electronic
- Abstract, futuristic
- Light effects
- Surreal, creative
- Club/party vibes

### Ballad
- Emotional, intimate
- Story-driven
- Cinematic, beautiful
- Slow, meaningful

## Integration with Video Generation

The generated music video prompts are optimized for:
- **Veo3 AI Video Generation**
- **Precise Timing** (segments add up to song length)
- **Lyric Synchronization**
- **Professional Cinematography**
- **Character Consistency**

Use `/api/generate-full-content-videos` to convert the music video into actual video files.

## Best Practices

### For Song Lyrics
1. **Include Structure**: Mark verses, chorus, bridge
2. **Complete Lyrics**: Provide full song text
3. **Timing Info**: Accurate song length

### For Characters
1. **Detailed Descriptions**: Every visual detail
2. **Performance Style**: How they perform
3. **Outfit Specs**: Complete clothing description

### For Dialogues
1. **Strategic Placement**: Between verses or before chorus
2. **Brief and Impactful**: 5-8 seconds max
3. **Story Enhancement**: Complement the song

### For Visual Theme
1. **Clear Concept**: Specific visual direction
2. **Genre-Appropriate**: Match music style
3. **Memorable**: Create iconic moments

## Timing Guidelines

| Song Length | Suggested Segments | Average per Segment |
|-------------|-------------------|---------------------|
| 60-120s | 8-12 | 8-10s |
| 120-180s | 15-20 | 8-10s |
| 180-240s | 20-25 | 8-10s |
| 240-300s | 25-30 | 8-10s |

## Error Handling

The endpoint includes validation for:
- Missing song lyrics
- Invalid song length (must be > 0)
- JSON parsing errors
- Empty responses
- Character ID generation

## Future Enhancements

Potential additions:
- Beat detection and sync
- Automatic lyric timing
- Music video templates
- Style presets by genre
- Choreography suggestions
- VFX recommendations

## Summary

The Music Video Generation endpoint creates professionally timed, visually stunning AI music video prompts from song lyrics. With support for custom characters, additional dialogues, background voice, and genre-specific styling, it's perfect for creating viral music videos with Veo3 AI video generation.

**Endpoint:** `POST /generate-music-video`
**Purpose:** Transform song lyrics into cinematic music video prompts
**Output:** Perfectly timed segments ready for AI video generation
**Style:** Professional, cinematic, music video quality