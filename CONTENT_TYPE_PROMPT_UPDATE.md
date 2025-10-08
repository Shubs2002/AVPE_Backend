# Content Type Prompt Update

## Overview

Updated the story generation prompts to dynamically change the script-writer description based on the type of content being generated.

## Changes Made

### Prompt Descriptions

The opening line of the prompts now changes based on content type:

- **For Movies** (`/generate-movie-auto`):
  ```
  You are a professional Humanised Script-writer for viral Movies.
  ```

- **For Short Films** (`/generate-prompt-based-story`):
  ```
  You are a professional Humanised Script-writer for Short Films.
  ```

## Implementation Details

### 1. Updated Functions

#### `get_story_segments_prompt()`
- **Used by:** `/generate-prompt-based-story` (short films)
- **New parameter:** `content_type: str = "short_film"`
- **Default:** "Short Films"

#### `get_story_segments_in_sets_prompt()`
- **Used by:** `/generate-movie-auto` (movies)
- **New parameter:** `content_type: str = "movie"`
- **Default:** "viral Movies"

#### `get_outline_for_story_segments_chunked()`
- **Used by:** Large movie generation (chunked)
- **New parameter:** `content_type: str = "movie"`
- **Default:** "viral Movies"

### 2. Service Layer Updates

**File:** `src/app/services/openai_service.py`

#### For Short Films:
```python
prompt = get_story_segments_prompt(
    idea, 
    num_segments, 
    custom_character_roster, 
    content_type="short_film"  # ← Added
)
```

#### For Movies:
```python
prompt = get_story_segments_in_sets_prompt(
    # ... other parameters ...
    content_type="movie"  # ← Added
)
```

#### For Chunked Movies:
```python
outline_prompt = get_outline_for_story_segments_chunked(
    # ... other parameters ...
    content_type="movie"  # ← Added
)
```

## Logic

The prompt functions now include this logic:

```python
# Determine the content type description
content_description = "Short Films" if content_type == "short_film" else "viral Movies"

return f"""
You are a professional Humanised Script-writer for {content_description}.
...
"""
```

## Route Mapping

| Route | Content Type | Prompt Description |
|-------|-------------|-------------------|
| `/generate-prompt-based-story` | `short_film` | "Short Films" |
| `/generate-movie-auto` | `movie` | "viral Movies" |
| `/generate-story-set` | `movie` | "viral Movies" |

## Benefits

1. **Context-Appropriate:** AI receives the right context for the type of content
2. **Flexible:** Easy to add more content types in the future
3. **Consistent:** All three prompt functions use the same logic
4. **Backward Compatible:** Default values ensure existing code works

## Testing

### Test Short Film Generation
```bash
curl -X POST "http://localhost:8000/generate-prompt-based-story" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A heartwarming story",
    "segments": 7
  }'
```
**Expected:** Prompt will say "Script-writer for Short Films"

### Test Movie Generation
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "An epic adventure",
    "total_segments": 50
  }'
```
**Expected:** Prompt will say "Script-writer for viral Movies"

## Future Extensibility

To add more content types, simply:

1. Add the new type to the logic:
```python
if content_type == "short_film":
    content_description = "Short Films"
elif content_type == "movie":
    content_description = "viral Movies"
elif content_type == "documentary":
    content_description = "Documentaries"
else:
    content_description = "viral Movies"  # default
```

2. Pass the appropriate `content_type` when calling the prompt function

## Files Modified

- ✅ `src/app/data/prompts/generate_segmented_story_prompt.py`
  - Updated `get_story_segments_prompt()`
  - Updated `get_story_segments_in_sets_prompt()`
  - Updated `get_outline_for_story_segments_chunked()`

- ✅ `src/app/services/openai_service.py`
  - Updated calls to pass `content_type="short_film"` for short films
  - Updated calls to pass `content_type="movie"` for movies

## Summary

The AI now receives context-appropriate descriptions:
- **Short films** → "professional Humanised Script-writer for Short Films"
- **Movies** → "professional Humanised Script-writer for viral Movies"

This helps the AI generate more appropriate content for each format!