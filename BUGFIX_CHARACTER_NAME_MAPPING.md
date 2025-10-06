# 🐛 Bug Fix: Character Name Mapping for Failed Images

## Issue Description

When analyzing multiple character images, if one image fails (e.g., unsupported format), the character names were being mapped incorrectly.

### Example Problem:
```
Input:
- Image 1: test0 ✅ Success
- Image 2: test1 ❌ Failed (unsupported format)
- Image 3: test2 ✅ Success

Previous Behavior (WRONG):
- Character from Image 1 → Named "test0" ✅
- Character from Image 3 → Named "test1" ❌ (Should be "test2")

Expected Behavior (CORRECT):
- Character from Image 1 → Named "test0" ✅
- Character from Image 3 → Named "test2" ✅
```

## Root Cause

The controller was mapping character names sequentially based on the **roster index** instead of the **source image index**.

### Old Code (Buggy):
```python
# Update character names in the roster
if 'characters_roster' in combined_analysis:
    for i, character in enumerate(combined_analysis['characters_roster']):
        if i < len(names_list):
            character['name'] = names_list[i]  # ❌ Wrong! Uses roster index
```

**Problem:** 
- `enumerate(characters_roster)` gives indices 0, 1, 2... for successful characters only
- But `names_list[i]` includes ALL names (including failed images)
- So character from image 3 gets `names_list[1]` which is "test1" instead of "test2"

## Solution

Map character names based on the **source_description** or **source_image** field, which correctly tracks which original image the character came from.

### New Code (Fixed):
```python
# Update character names in the roster based on source_description
# This ensures that if an image fails, the correct name is still used
if 'characters_roster' in combined_analysis:
    for character in combined_analysis['characters_roster']:
        # The source_description contains the original character name
        source_desc = character.get('source_description', '')
        # Find the matching name from the original names_list
        if source_desc in names_list:
            character['name'] = source_desc  # ✅ Use the original name
        else:
            # Fallback: try to match by source_image index
            source_img = character.get('source_image', 0)
            if source_img > 0 and source_img <= len(names_list):
                character['name'] = names_list[source_img - 1]  # ✅ Use source image index
```

**How it works:**
1. Each character has a `source_description` field set to the original character name
2. We match the `source_description` directly to find the correct name
3. Fallback: Use `source_image` index to map to the correct position in `names_list`

### Also Fixed: Save Function

The save function was also using the wrong name list:

**Old Code (Buggy):**
```python
save_results = openai_service.save_multiple_characters_to_files(
    combined_analysis['characters_roster'], names_list  # ❌ Includes failed image names
)
```

**New Code (Fixed):**
```python
# Extract actual character names from the roster (only successful ones)
actual_names = [char.get('name', f'character_{i}') for i, char in enumerate(combined_analysis['characters_roster'], 1)]
save_results = openai_service.save_multiple_characters_to_files(
    combined_analysis['characters_roster'], actual_names  # ✅ Only successful character names
)
```

## Test Case

### Input:
```bash
curl -X POST "http://localhost:8000/analyze-multiple-character-images-files" \
  -F "images=@image1.jpg" \
  -F "images=@corrupted.jpg" \
  -F "images=@image3.jpg" \
  -F "character_names=test0,test1,test2"
```

### Expected Output:
```json
{
  "combined_character_analysis": {
    "total_images_analyzed": 3,
    "successful_analyses": 2,
    "characters_roster": [
      {
        "id": "img1_char1",
        "name": "test0",  // ✅ Correct
        "source_image": 1,
        "source_description": "test0"
      },
      {
        "id": "img3_char1",
        "name": "test2",  // ✅ Correct (was "test1" before fix)
        "source_image": 3,
        "source_description": "test2"
      }
    ]
  },
  "save_results": {
    "save_results": [
      {
        "character_name": "test0",  // ✅ Correct
        "filepath": "saved_characters\\test0_20251005_190351.json"
      },
      {
        "character_name": "test2",  // ✅ Correct (was "test1" before fix)
        "filepath": "saved_characters\\test2_20251005_190351.json"
      }
    ]
  }
}
```

## Files Modified

- `src/app/controllers/screenwriter_controller.py`
  - Fixed character name mapping logic
  - Fixed save function to use actual character names

## Status

✅ **FIXED** - Character names now correctly map to their source images, even when some images fail.

## Testing

Run the test with intentionally corrupted/unsupported images to verify:
1. Failed images are skipped
2. Successful characters get the correct names from their original position
3. Saved files use the correct character names

---

**Bug reported by:** User
**Fixed on:** 2025-10-05
**Severity:** Medium (incorrect data mapping)
**Impact:** Character names were mismatched when images failed
