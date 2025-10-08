# Movie Auto Generation - New Parameters

## Overview

Added new input parameters to the `/generate-movie-auto` endpoint to give users more control over story generation without embedding these settings in the idea text.

## New Parameters

### 1. `no_narration` (boolean, default: `false`)
- **Description:** If `true`, no narration will be included in any segment
- **Use Case:** For dialogue-only stories or visual-focused content
- **Example:** `"no_narration": true`

### 2. `narration_only_first` (boolean, default: `false`)
- **Description:** If `true`, narration will only appear in the first segment
- **Use Case:** For stories that need context in the beginning but then focus on dialogue
- **Example:** `"narration_only_first": true`

### 3. `cliffhanger_interval` (integer, default: `0`)
- **Description:** Add cliffhangers every N segments (0 = no cliffhangers)
- **Use Case:** For episodic content or serialized stories
- **Example:** `"cliffhanger_interval": 150` (adds cliffhanger at segments 150, 300, 450, etc.)

### 4. `content_rating` (string, default: `"U"`)
- **Description:** Content rating for the story
- **Valid Values:**
  - `"U"` - Universal (suitable for all ages)
  - `"U/A"` - Parental Guidance (some content may not be suitable for children)
  - `"A"` - Adult (restricted to adult audiences)
- **Use Case:** Control the maturity level of generated content
- **Example:** `"content_rating": "A"`

## API Request Model

### Updated `GenerateFullmovieAutoRequest`

```json
{
  "idea": "string (required)",
  "total_segments": "integer (optional)",
  "segments_per_set": "integer (optional, default: 10)",
  "save_to_files": "boolean (optional, default: true)",
  "output_directory": "string (optional, default: 'generated_movie_script')",
  "custom_character_roster": "array (optional)",
  "no_narration": "boolean (optional, default: false)",
  "narration_only_first": "boolean (optional, default: false)",
  "cliffhanger_interval": "integer (optional, default: 0)",
  "content_rating": "string (optional, default: 'U')"
}
```

## Usage Examples

### Example 1: Universal Content with No Narration
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A romantic comedy about two coffee shop workers",
    "total_segments": 50,
    "no_narration": true,
    "content_rating": "U"
  }'
```

### Example 2: Adult Content with Cliffhangers
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A thriller about corporate espionage",
    "total_segments": 300,
    "cliffhanger_interval": 150,
    "content_rating": "A"
  }'
```

### Example 3: Parental Guidance with Narration Only in First Segment
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "An adventure story about treasure hunters",
    "total_segments": 100,
    "narration_only_first": true,
    "content_rating": "U/A"
  }'
```

### Example 4: All Parameters Combined
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A sci-fi epic spanning multiple planets",
    "total_segments": 600,
    "segments_per_set": 10,
    "no_narration": false,
    "narration_only_first": false,
    "cliffhanger_interval": 100,
    "content_rating": "U/A",
    "save_to_files": true,
    "output_directory": "my_scifi_movie"
  }'
```

### Example 5: Python Usage
```python
import requests

url = "http://localhost:8000/generate-movie-auto"
payload = {
    "idea": "A mystery thriller set in a haunted mansion",
    "total_segments": 200,
    "segments_per_set": 10,
    "no_narration": False,
    "narration_only_first": False,
    "cliffhanger_interval": 50,
    "content_rating": "A",
    "save_to_files": True,
    "output_directory": "haunted_mansion_movie"
}

response = requests.post(url, json=payload)
result = response.json()

print(f"Story Title: {result['result']['story_title']}")
print(f"Total Segments Generated: {result['result']['generation_summary']['total_segments_generated']}")
```

## Content Rating Guidelines

### U (Universal)
- Suitable for all ages
- No adult themes, violence, or explicit content
- Family-friendly language and situations
- **Example:** Children's stories, family comedies, educational content

### U/A (Parental Guidance)
- Some content may not be suitable for children
- Mild violence, suspense, or mature themes
- Requires parental guidance for younger viewers
- **Example:** Action adventures, thrillers, romantic dramas

### A (Adult)
- Restricted to adult audiences
- May contain explicit content, strong violence, or mature themes
- Not suitable for children
- **Example:** Horror, intense thrillers, mature dramas

## Validation

### Content Rating Validation
The API validates that `content_rating` is one of the allowed values:
- `"U"`
- `"U/A"`
- `"A"`

If an invalid value is provided, the API returns a 400 error:
```json
{
  "detail": "Invalid content_rating. Must be one of: U, U/A, A"
}
```

## Metadata Storage

All parameters are stored in the generated story metadata for consistency:

```json
{
  "generation_info": {
    "total_segments": 300,
    "segments_per_set": 10,
    "total_sets": 30,
    "generated_at": "2025-01-15T10:30:00Z",
    "idea": "Your story idea",
    "no_narration": false,
    "narration_only_first": false,
    "cliffhanger_interval": 150,
    "content_rating": "A"
  }
}
```

## Retry Functionality

When retrying failed sets using `/retry-failed-story-sets`, the original parameters are automatically extracted from the metadata and reused, ensuring consistency across retries.

## Migration from Old Format

### Before (Embedded in Idea)
```json
{
  "idea": "ADULT STORY: A thriller with NO NARRATION and cliffhangers EVERY 150 segments"
}
```

### After (Separate Parameters)
```json
{
  "idea": "A thriller",
  "no_narration": true,
  "cliffhanger_interval": 150,
  "content_rating": "A"
}
```

## Benefits

1. **Cleaner API:** Parameters are explicit and well-documented
2. **Better Validation:** Type checking and value validation
3. **Easier to Use:** No need to remember special keywords in the idea
4. **More Flexible:** Can combine parameters in any way
5. **Consistent Retries:** Parameters are preserved when retrying failed sets
6. **Better Logging:** Parameters are clearly logged during generation

## Backward Compatibility

The old method of embedding parameters in the idea text is no longer supported. Users should migrate to using the new explicit parameters.

## Testing

### Test 1: Universal Content
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{"idea": "A simple love story", "total_segments": 10, "content_rating": "U"}'
```

### Test 2: Adult Content with Cliffhangers
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{"idea": "A dark thriller", "total_segments": 20, "cliffhanger_interval": 10, "content_rating": "A"}'
```

### Test 3: No Narration
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{"idea": "A dialogue-heavy drama", "total_segments": 15, "no_narration": true, "content_rating": "U/A"}'
```

## Summary

The movie auto generation endpoint now provides explicit, well-documented parameters for controlling story generation, replacing the old method of embedding settings in the idea text. This makes the API more intuitive, easier to use, and better suited for programmatic access.