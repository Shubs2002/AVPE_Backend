# Character ID Generation Fix - Correct Implementation

## What Was Actually Requested

Remove automatic character ID generation **ONLY when IDs are already present** in user-provided custom character rosters. If users provide their own IDs, those should be preserved and used.

## What Was Fixed

### ✅ **Correct Behavior Now:**

1. **User provides character WITH ID:**
   ```json
   {
     "custom_character_roster": [
       {
         "id": "my_custom_id_123",
         "name": "Alice",
         "physical_appearance": {...}
       }
     ]
   }
   ```
   **Result:** ✅ Uses `"my_custom_id_123"` - NO auto-generation

2. **User provides character WITHOUT ID:**
   ```json
   {
     "custom_character_roster": [
       {
         "name": "Bob",
         "physical_appearance": {...}
       }
     ]
   }
   ```
   **Result:** ✅ Auto-generates ID like `"char_a1b2c3d4e5f6"`

3. **User provides character with 'unknown' ID:**
   ```json
   {
     "custom_character_roster": [
       {
         "id": "unknown",
         "name": "Charlie",
         "physical_appearance": {...}
       }
     ]
   }
   ```
   **Result:** ✅ Auto-generates new ID to replace 'unknown'

## Implementation Details

### Modified Function: `ensure_character_ids()`

**Location:** `src/app/services/openai_service.py`

```python
def ensure_character_ids(custom_character_roster: list) -> list:
    """
    Ensure all characters in the roster have unique IDs.
    ONLY generates IDs for characters that don't already have them.
    If user provides IDs, they are preserved.
    """
    if not custom_character_roster:
        return custom_character_roster
    
    for character in custom_character_roster:
        # Only generate ID if character doesn't have one or has 'unknown'
        if not character.get('id') or character.get('id') == 'unknown':
            character['id'] = generate_character_id()
            print(f"🆔 Auto-generated ID for character '{character.get('name', 'Unknown')}': {character['id']}")
        else:
            # User provided an ID, keep it
            print(f"✅ Using user-provided ID for character '{character.get('name', 'Unknown')}': {character['id']}")
    
    return custom_character_roster
```

## Key Logic

### ID Generation Decision Tree

```
Character has 'id' field?
├─ NO → Auto-generate ID
├─ YES → Is it 'unknown'?
│  ├─ YES → Auto-generate ID
│  └─ NO → Keep user-provided ID
```

## Files Restored/Fixed

- ✅ `src/app/utils/id_generator.py` - Restored (needed for auto-generation)
- ✅ `src/app/utils/__init__.py` - Restored imports
- ✅ `src/app/services/openai_service.py` - Fixed to respect user IDs
- ✅ `src/app/services/story_to_video_service.py` - Restored ID-based lookup
- ✅ `src/app/services/content_to_video_service.py` - Restored ID-based lookup
- ✅ `src/app/data/prompts/generate_segmented_story_prompt.py` - Restored ID examples

## Usage Examples

### Example 1: User Provides Custom IDs
```python
payload = {
    "idea": "A love story",
    "total_segments": 10,
    "custom_character_roster": [
        {
            "id": "protagonist_001",  # User's custom ID
            "name": "Alice",
            "physical_appearance": {...}
        },
        {
            "id": "antagonist_001",  # User's custom ID
            "name": "Bob",
            "physical_appearance": {...}
        }
    ]
}
```
**Output:** Uses `protagonist_001` and `antagonist_001` ✅

### Example 2: User Doesn't Provide IDs
```python
payload = {
    "idea": "A love story",
    "total_segments": 10,
    "custom_character_roster": [
        {
            "name": "Alice",
            "physical_appearance": {...}
        },
        {
            "name": "Bob",
            "physical_appearance": {...}
        }
    ]
}
```
**Output:** Auto-generates `char_a1b2c3d4e5f6` and `char_x9y8z7w6v5u4` ✅

### Example 3: Mixed (Some with IDs, Some without)
```python
payload = {
    "idea": "A love story",
    "total_segments": 10,
    "custom_character_roster": [
        {
            "id": "my_hero",  # User provided
            "name": "Alice",
            "physical_appearance": {...}
        },
        {
            # No ID provided
            "name": "Bob",
            "physical_appearance": {...}
        }
    ]
}
```
**Output:** Uses `my_hero` for Alice, auto-generates ID for Bob ✅

## Benefits

1. **Flexibility:** Users can provide their own IDs or let the system generate them
2. **Consistency:** User-provided IDs are preserved throughout the story
3. **Backward Compatible:** Existing code without IDs still works
4. **No Breaking Changes:** All existing functionality maintained

## Testing

### Test 1: With Custom IDs
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A simple story",
    "total_segments": 5,
    "custom_character_roster": [
      {
        "id": "hero_001",
        "name": "Hero",
        "physical_appearance": {"gender": "Male", "age": "30s"}
      }
    ]
  }'
```
**Expected:** Story uses `hero_001` as character ID

### Test 2: Without Custom IDs
```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A simple story",
    "total_segments": 5,
    "custom_character_roster": [
      {
        "name": "Hero",
        "physical_appearance": {"gender": "Male", "age": "30s"}
      }
    ]
  }'
```
**Expected:** Story auto-generates ID like `char_a1b2c3d4e5f6`

## Summary

The system now correctly:
- ✅ **Preserves** user-provided character IDs
- ✅ **Auto-generates** IDs only when missing or 'unknown'
- ✅ **Maintains** all existing functionality
- ✅ **Provides** clear logging of which IDs are user-provided vs auto-generated

This is the correct implementation of what was requested!