# Story Retry by Title - Quick Guide

## Overview

New simplified endpoints that let you retry failed story sets by just providing the story title. No need to manually construct payloads or track failed sets!

## New Endpoints

### 1. Check Story Status (GET)

Check which sets succeeded and which failed for any story.

```bash
GET /api/story-status/{title}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/story-status/Midnight%20Protocol"
```

**Response:**
```json
{
  "success": true,
  "title": "Midnight Protocol",
  "failed_sets": [26, 27, 28, 29, 30],
  "total_sets": 30,
  "successful_sets": 25,
  "failed_count": 5,
  "message": "Found 5 failed sets out of 30 total sets"
}
```

### 2. Retry by Title (POST)

Automatically retry all failed sets for a story.

```bash
POST /api/retry-story-by-title
```

**Request Body:**
```json
{
  "title": "Midnight Protocol",
  "max_retries": 3
}
```

**Response:**
```json
{
  "success": true,
  "story_result": {
    "story_title": "Midnight Protocol",
    "generation_summary": {
      "successful_sets": 5,
      "failed_sets": 0,
      "total_segments_generated": 50,
      "failed_set_numbers": []
    },
    "retry_info": {
      "total_retry_attempts": 5,
      "successful_retries": 5
    }
  },
  "original_failed_sets": [26, 27, 28, 29, 30],
  "original_failed_count": 5
}
```

## Usage Examples

### Using Python Script

```bash
# Check status and retry if needed
python test_retry_by_title.py
```

### Using cURL

```bash
# Check status
curl "http://127.0.0.1:8000/api/story-status/Midnight%20Protocol"

# Retry failed sets
curl -X POST "http://127.0.0.1:8000/api/retry-story-by-title" \
  -H "Content-Type: application/json" \
  -d '{"title": "Midnight Protocol", "max_retries": 3}'
```

### Using Python Requests

```python
import requests

# Check status
response = requests.get(
    "http://127.0.0.1:8000/api/story-status/Midnight Protocol"
)
print(response.json())

# Retry failed sets
response = requests.post(
    "http://127.0.0.1:8000/api/retry-story-by-title",
    json={"title": "Midnight Protocol", "max_retries": 3}
)
print(response.json())
```

## How It Works

1. **Automatic Detection**: The system automatically:
   - Finds the story metadata file by title
   - Checks which set files exist in the directory
   - Determines which sets are missing (failed)
   - Loads existing successful sets to preserve them

2. **Smart Retry**: 
   - Constructs a complete `previous_result` with all set information
   - Uses exponential backoff (2s, 4s, 8s delays)
   - Retries each failed set up to `max_retries` times
   - Preserves all existing successful sets
   - Saves new sets to the same directory

3. **Progress Tracking**:
   - Shows original failed count
   - Shows how many were successfully retried
   - Lists any sets that still failed
   - Provides retry attempt statistics

## Utility Functions

The new `story_retry_helper.py` utility provides:

- `find_story_metadata(title)` - Find metadata file by title
- `load_story_metadata(path)` - Load metadata from file
- `find_failed_sets(title)` - Detect which sets are missing
- `construct_retry_payload(...)` - Build retry request payload
- `get_retry_info_by_title(title)` - Get comprehensive status info

## Benefits

✅ **Simple**: Just provide the story title  
✅ **Automatic**: Detects failed sets automatically  
✅ **Flexible**: Works with any story in your generated_movie_script folder  
✅ **Safe**: Never overwrites existing successful sets  
✅ **Informative**: Clear status and progress reporting  

## For Your Use Case

For "Midnight Protocol" with failed sets [26, 27, 28, 29, 30]:

```python
import requests

# Tomorrow when rate limit resets:
response = requests.post(
    "http://127.0.0.1:8000/api/retry-story-by-title",
    json={"title": "Midnight Protocol", "max_retries": 3}
)

result = response.json()
print(f"Successfully generated: {result['story_result']['generation_summary']['successful_sets']} sets")
```

That's it! No need to manually track failed sets or construct complex payloads.
