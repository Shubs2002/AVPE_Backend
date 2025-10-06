# 🔧 API Parameters Removed - Breaking Changes

## Summary

Removed `character_count` and `character_count_per_image` parameters from character analysis endpoints to enforce single character per image analysis.

## Breaking Changes

### 1. `/api/analyze-character-image-file`

**Before:**
```bash
curl -X POST "http://localhost:8000/api/analyze-character-image-file" \
  -F "image=@person.jpg" \
  -F "character_name=John" \
  -F "character_count=1" \      # ❌ REMOVED
  -F "save_character=true"
```

**After:**
```bash
curl -X POST "http://localhost:8000/api/analyze-character-image-file" \
  -F "image=@person.jpg" \
  -F "character_name=John" \
  -F "save_character=true"      # ✅ character_count removed
```

**Parameters:**
- ✅ `image` (file, required) - Image file containing 1 person
- ✅ `character_name` (string, required) - Name for the character
- ✅ `save_character` (boolean, optional) - Save to MongoDB
- ❌ `character_count` - **REMOVED** (always 1)

---

### 2. `/api/analyze-multiple-character-images-files`

**Before:**
```bash
curl -X POST "http://localhost:8000/api/analyze-multiple-character-images-files" \
  -F "images=@person1.jpg" \
  -F "images=@person2.jpg" \
  -F "character_names=Alice,Bob" \
  -F "character_count_per_image=1" \  # ❌ REMOVED
  -F "save_characters=true"
```

**After:**
```bash
curl -X POST "http://localhost:8000/api/analyze-multiple-character-images-files" \
  -F "images=@person1.jpg" \
  -F "images=@person2.jpg" \
  -F "character_names=Alice,Bob" \
  -F "save_characters=true"           # ✅ character_count_per_image removed
```

**Parameters:**
- ✅ `images` (files, required) - Multiple image files, each with 1 person
- ✅ `character_names` (string, required) - Comma-separated names
- ✅ `save_characters` (boolean, optional) - Save to MongoDB
- ❌ `character_count_per_image` - **REMOVED** (always 1 per image)

---

## Why These Parameters Were Removed

1. **Simplicity** - Enforces clear API design (1 character per image)
2. **Reliability** - Prevents JSON truncation issues with multiple characters
3. **Consistency** - Both endpoints now work the same way (1 character per image)
4. **Performance** - Optimized token allocation (8,000 tokens per character)

---

## Migration Guide

### If you were using `character_count=1` (default)

**No changes needed!** Just remove the parameter:

```bash
# Before
curl -X POST "http://localhost:8000/api/analyze-character-image-file" \
  -F "image=@person.jpg" \
  -F "character_name=John" \
  -F "character_count=1"

# After (just remove character_count)
curl -X POST "http://localhost:8000/api/analyze-character-image-file" \
  -F "image=@person.jpg" \
  -F "character_name=John"
```

---

### If you were using `character_count > 1`

**You need to change your approach:**

**Option 1: Crop images and analyze separately**
```bash
# Crop your group photo into individual images first
# Then analyze each person separately

curl -X POST "http://localhost:8000/api/analyze-character-image-file" \
  -F "image=@person1_cropped.jpg" \
  -F "character_name=Alice"

curl -X POST "http://localhost:8000/api/analyze-character-image-file" \
  -F "image=@person2_cropped.jpg" \
  -F "character_name=Bob"
```

**Option 2: Use multiple images endpoint**
```bash
curl -X POST "http://localhost:8000/api/analyze-multiple-character-images-files" \
  -F "images=@person1.jpg" \
  -F "images=@person2.jpg" \
  -F "character_names=Alice,Bob"
```

---

## Error Handling

### Using removed parameters

**Request:**
```bash
curl -X POST "http://localhost:8000/api/analyze-character-image-file" \
  -F "image=@person.jpg" \
  -F "character_name=John" \
  -F "character_count=1"  # ❌ This parameter no longer exists
```

**Response (422 Unprocessable Entity):**
```json
{
  "detail": [
    {
      "type": "extra_forbidden",
      "loc": ["body", "character_count"],
      "msg": "Extra inputs are not permitted",
      "input": "1"
    }
  ]
}
```

**Fix:** Remove the `character_count` parameter from your request.

---

## Updated API Documentation

### Single Character Analysis

```
POST /api/analyze-character-image-file
```

**Request:**
```bash
curl -X POST "http://localhost:8000/api/analyze-character-image-file" \
  -F "image=@john.jpg" \
  -F "character_name=John" \
  -F "save_character=true"
```

**Response:**
```json
{
  "characters_roster": [
    {
      "id": "char1",
      "name": "John",
      "physical_appearance": {...},
      "clothing_style": {...},
      "source_image_url": "/static/uploads/character_images/char_analysis_20251005_143022_a1b2c3d4.jpg"
    }
  ]
}
```

---

### Multiple Characters Analysis

```
POST /api/analyze-multiple-character-images-files
```

**Request:**
```bash
curl -X POST "http://localhost:8000/api/analyze-multiple-character-images-files" \
  -F "images=@alice.jpg" \
  -F "images=@bob.jpg" \
  -F "images=@charlie.jpg" \
  -F "character_names=Alice,Bob,Charlie" \
  -F "save_characters=true"
```

**Response:**
```json
{
  "characters_roster": [
    {
      "id": "img1_char1",
      "name": "Alice",
      "physical_appearance": {...},
      "source_image_url": "/static/uploads/character_images/multi_char_1_20251005_143022_a1b2c3d4.jpg"
    },
    {
      "id": "img2_char1",
      "name": "Bob",
      "physical_appearance": {...},
      "source_image_url": "/static/uploads/character_images/multi_char_2_20251005_143022_b2c3d4e5.jpg"
    },
    {
      "id": "img3_char1",
      "name": "Charlie",
      "physical_appearance": {...},
      "source_image_url": "/static/uploads/character_images/multi_char_3_20251005_143022_c3d4e5f6.jpg"
    }
  ]
}
```

---

## Files Modified

- ✅ `src/app/api/routes.py` - Removed parameters from route definitions
- ✅ `src/app/controllers/screenwriter_controller.py` - Removed parameters from functions
- ✅ `src/app/services/openai_service.py` - Updated documentation

---

## Testing

### Test single character endpoint
```bash
curl -X POST "http://localhost:8000/api/analyze-character-image-file" \
  -F "image=@test_person.jpg" \
  -F "character_name=TestUser"
```

### Test multiple characters endpoint
```bash
curl -X POST "http://localhost:8000/api/analyze-multiple-character-images-files" \
  -F "images=@person1.jpg" \
  -F "images=@person2.jpg" \
  -F "character_names=User1,User2"
```

---

## Status

✅ **Complete** - Parameters removed, API simplified

---

**Updated**: 2025-10-05  
**Status**: ✅ Breaking Change - Update Your Clients!
