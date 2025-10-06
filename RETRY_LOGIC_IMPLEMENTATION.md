# Movie Auto Generation Retry Logic

## Overview

The `/generate-movie-auto` endpoint now includes robust retry logic to handle failed sets during story generation. If any sets fail during the initial generation, they can be automatically retried with exponential backoff.

## Features

### 1. Automatic Retry During Generation
- Each set is automatically retried up to 3 times if it fails
- Uses exponential backoff: 2s, 4s, 8s delays between retries
- Continues with other sets even if one fails permanently

### 2. Manual Retry Endpoint
- New endpoint: `/retry-failed-story-sets`
- Allows retrying specific failed sets from a previous generation
- Maintains story consistency using original metadata

### 3. Enhanced Response Format
- Clear status tracking for each set (`success` or `failed`)
- Retry information included in responses
- Failed set numbers listed for easy identification

## API Endpoints

### Generate Movie Auto (Enhanced)
```http
POST /generate-movie-auto
```

**Request:**
```json
{
  "idea": "Your story idea",
  "total_segments": 30,
  "segments_per_set": 10,
  "save_to_files": true,
  "output_directory": "generated_movie_script"
}
```

**Response (Enhanced):**
```json
{
  "result": {
    "success": false,
    "story_title": "Your Story Title",
    "generation_summary": {
      "total_segments_requested": 30,
      "total_segments_generated": 20,
      "total_sets_requested": 3,
      "successful_sets": 2,
      "failed_sets": 1,
      "failed_set_numbers": [3]
    },
    "retry_info": {
      "can_retry": true,
      "failed_sets": [3],
      "retry_endpoint": "/retry-failed-story-sets"
    },
    "sets": [
      {
        "set_number": 1,
        "status": "success",
        "segments_count": 10,
        "file_path": "generated_movie_script/Story_Title_set_01.json"
      },
      {
        "set_number": 2,
        "status": "success",
        "segments_count": 10,
        "file_path": "generated_movie_script/Story_Title_set_02.json"
      },
      {
        "set_number": 3,
        "status": "failed",
        "error": "Failed to generate set 3 after 3 attempts: API timeout"
      }
    ]
  }
}
```

### Retry Failed Sets (New)
```http
POST /retry-failed-story-sets
```

**Request:**
```json
{
  "previous_result": {
    // The entire result object from /generate-movie-auto
  },
  "max_retries": 3
}
```

**Response:**
```json
{
  "result": {
    "success": true,
    "retry_info": {
      "retry_performed": true,
      "retry_timestamp": "2024-01-15T10:30:00Z",
      "retry_results": [
        {
          "set_number": 3,
          "status": "success",
          "segments_generated": 10
        }
      ]
    },
    "generation_summary": {
      "total_segments_generated": 30,
      "successful_sets": 3,
      "failed_sets": 0
    }
  }
}
```

## Implementation Details

### Retry Logic Flow

1. **Initial Generation:**
   - Each set is attempted with automatic retry (up to 3 times)
   - Exponential backoff between retries: 2s, 4s, 8s
   - Failed sets are marked with `status: "failed"`

2. **Manual Retry:**
   - Use `/retry-failed-story-sets` with the previous result
   - Only failed sets are retried
   - Original story metadata is preserved for consistency
   - Updated files are saved to the same directory

### Error Handling

- **Network timeouts:** Automatically retried with backoff
- **API rate limits:** Handled with delays between requests
- **Invalid responses:** Logged and marked as failed
- **File system errors:** Reported but don't stop other sets

### Consistency Guarantees

- Story metadata (title, characters, etc.) from Set 1 is reused
- Character roster remains consistent across all sets
- Narrative continuity is maintained during retries

## Usage Examples

### Basic Usage
```python
import requests

# Generate movie
response = requests.post("http://localhost:8000/generate-movie-auto", json={
    "idea": "A sci-fi adventure about time travel",
    "total_segments": 50,
    "segments_per_set": 10
})

result = response.json()["result"]

# Check for failures
if not result["success"]:
    failed_sets = result["retry_info"]["failed_sets"]
    print(f"Failed sets: {failed_sets}")
    
    # Retry failed sets
    retry_response = requests.post("http://localhost:8000/retry-failed-story-sets", json={
        "previous_result": result,
        "max_retries": 5
    })
    
    final_result = retry_response.json()["result"]
    print(f"Final success: {final_result['success']}")
```

### Testing the Retry Logic
```bash
# Run the test script
python test_retry_logic.py
```

## Configuration

### Retry Parameters
- **Default retries per set:** 3
- **Maximum retries per set:** 10 (configurable via API)
- **Backoff strategy:** Exponential (2^attempt seconds)
- **Delay between sets:** 2 seconds (to avoid rate limits)

### File Management
- Failed sets don't create files
- Successful retries overwrite any existing files
- Metadata files are updated with retry information

## Benefits

1. **Improved Reliability:** Handles temporary API failures gracefully
2. **Cost Efficiency:** Only retries failed sets, not entire generation
3. **User Experience:** Clear feedback on what failed and what succeeded
4. **Flexibility:** Configurable retry attempts and manual retry option
5. **Consistency:** Maintains story coherence across retries

## Error Scenarios Handled

- OpenAI API timeouts
- Rate limiting
- Network connectivity issues
- Temporary service unavailability
- Invalid API responses
- File system write errors

## Monitoring and Logging

The retry logic includes comprehensive logging:
- Retry attempts with timestamps
- Exponential backoff delays
- Success/failure status for each attempt
- Final summary with retry statistics

This ensures full visibility into the generation process and helps with debugging any persistent issues.