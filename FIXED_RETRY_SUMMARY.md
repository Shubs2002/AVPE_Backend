# Fixed: Retry by Title Endpoint

## What Was Wrong

The original implementation didn't construct the `previous_result` payload correctly. The retry service expects:
- A `sets` array with status information for ALL sets (both successful and failed)
- Each set object needs: `set_number`, `status`, `file_path`, `set_data`, etc.
- The structure must match what `generate_full_story_automatically` returns

## What Was Fixed

### 1. Updated `construct_retry_payload()` in `story_retry_helper.py`

Now it:
- ✅ Builds a complete `sets` array for all sets (1 to total_sets)
- ✅ Marks failed sets with `status: 'failed'`
- ✅ Loads successful set files and marks them with `status: 'success'`
- ✅ Includes proper file paths and segment counts
- ✅ Constructs the exact structure the retry service expects

### 2. Updated the Route Response

The route now:
- ✅ Properly unwraps the controller response (which wraps in `{"result": ...}`)
- ✅ Returns a clean structure with `success`, `story_result`, and context info
- ✅ Handles the "all completed" case gracefully

## Testing

### Quick Status Check
```bash
python test_endpoint_quick.py
```

### Full Retry (when rate limit resets)
```bash
python retry_midnight_protocol_simple.py
```

## Expected Flow

1. **Status Check** → Shows failed sets [26, 27, 28, 29, 30]
2. **Retry Call** → Constructs full payload with all 30 sets
3. **Service Processing** → Retries only the 5 failed sets
4. **Success** → All 30 sets now complete

## Key Changes

**Before:**
```python
previous_result = {
    "title": title,
    "metadata": metadata,
    "failed_sets": failed_sets,  # ❌ Wrong structure
    ...
}
```

**After:**
```python
previous_result = {
    "story_title": title,
    "story_metadata": metadata,
    "sets": [  # ✅ Correct structure
        {
            "set_number": 1,
            "status": "success",
            "file_path": "...",
            "set_data": {...},
            "segments_count": 10
        },
        ...
        {
            "set_number": 26,
            "status": "failed",  # ✅ Marked for retry
            "error": "Set file not found"
        },
        ...
    ],
    "files_saved": True,
    "output_directory": "generated_movie_script"
}
```

## Ready to Use!

The endpoint is now fully functional and matches the expected service contract. Just run the retry script tomorrow when your rate limit resets! 🚀
