# Video Download Endpoint

## Overview

The `/api/download-video` endpoint allows you to download videos from URLs using the same robust download logic that's used during video generation. This endpoint handles authentication, retries, and error handling automatically.

## Endpoint Details

### URL
```
POST /api/download-video
```

### Request Model
```json
{
  "video_url": "string (required)",
  "filename": "string (optional)",
  "download_dir": "string (optional, default: 'downloads')"
}
```

### Response Model
```json
{
  "success": "boolean",
  "filepath": "string or null",
  "error": "string or null"
}
```

## Parameters

### `video_url` (required)
- **Type:** String
- **Description:** The URL of the video to download
- **Example:** `"https://generativelanguage.googleapis.com/v1beta/files/abc123:download?alt=media"`

### `filename` (optional)
- **Type:** String
- **Description:** Custom filename for the downloaded video (without extension)
- **Default:** Auto-generated timestamp-based name
- **Example:** `"my_harvest_moon_video"`
- **Note:** `.mp4` extension is automatically added if not present

### `download_dir` (optional)
- **Type:** String
- **Description:** Directory where the video should be saved
- **Default:** `"downloads"`
- **Example:** `"downloads/custom_folder"`
- **Note:** Directory is created automatically if it doesn't exist

## Usage Examples

### Basic Download
```bash
curl -X POST "http://localhost:8000/api/download-video" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://generativelanguage.googleapis.com/v1beta/files/lk8kxsr49b3j:download?alt=media"
  }'
```

### Download with Custom Filename
```bash
curl -X POST "http://localhost:8000/api/download-video" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://generativelanguage.googleapis.com/v1beta/files/lk8kxsr49b3j:download?alt=media",
    "filename": "harvest_moon_segment_26"
  }'
```

### Download to Custom Directory
```bash
curl -X POST "http://localhost:8000/api/download-video" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://generativelanguage.googleapis.com/v1beta/files/lk8kxsr49b3j:download?alt=media",
    "filename": "my_video",
    "download_dir": "downloads/movies"
  }'
```

### Python Example
```python
import requests

url = "http://localhost:8000/api/download-video"
payload = {
    "video_url": "https://generativelanguage.googleapis.com/v1beta/files/lk8kxsr49b3j:download?alt=media",
    "filename": "harvest_moon_video",
    "download_dir": "downloads"
}

response = requests.post(url, json=payload)
result = response.json()

if result["success"]:
    print(f"Video downloaded to: {result['filepath']}")
else:
    print(f"Download failed: {result['error']}")
```

## Response Examples

### Successful Download
```json
{
  "success": true,
  "filepath": "downloads/harvest_moon_segment_26.mp4",
  "error": null
}
```

### Failed Download
```json
{
  "success": false,
  "filepath": null,
  "error": "All authentication methods failed. The video URL may have expired or the API key may be incorrect."
}
```

### Validation Error
```json
{
  "success": false,
  "filepath": null,
  "error": "video_url is required"
}
```

## Features

### 🔐 **Multiple Authentication Methods**
- Bearer token authentication
- API key header authentication
- Fallback to no authentication
- Automatic retry with different methods

### 🔄 **Retry Logic**
- Automatic retry for transient errors (429, 502, 503)
- Exponential backoff (3s, 6s, 12s delays)
- Up to 3 retry attempts per authentication method

### 📊 **Progress Tracking**
- Real-time download progress display
- File size reporting
- Download speed information

### 🛡️ **Error Handling**
- Network timeout handling
- Invalid URL detection
- Authentication failure handling
- File system error handling

### 📁 **File Management**
- Automatic directory creation
- Filename sanitization
- Extension validation
- Duplicate file handling

## Error Scenarios

### Common Errors and Solutions

1. **"video_url is required"**
   - **Cause:** Missing or empty video_url parameter
   - **Solution:** Provide a valid video URL

2. **"All authentication methods failed"**
   - **Cause:** Invalid API key or expired video URL
   - **Solution:** Check API key configuration or regenerate video URL

3. **Network timeout errors**
   - **Cause:** Slow network connection or server issues
   - **Solution:** Automatic retry with exponential backoff

4. **File permission errors**
   - **Cause:** Insufficient permissions to write to download directory
   - **Solution:** Check directory permissions or use different download_dir

## Integration with Video Generation

This endpoint uses the same download logic as the video generation system, ensuring consistency across the application. When videos are generated, they use the same authentication methods and retry logic.

### Automatic Download During Generation
```json
{
  "content_data": { ... },
  "generate_videos": true,
  "download": true,  // Uses the same download logic
  "resolution": "1080p"
}
```

### Manual Download After Generation
```json
{
  "video_url": "URL_FROM_GENERATION_RESPONSE",
  "filename": "custom_name"
}
```

## Testing

Run the test suite to verify the endpoint functionality:

```bash
python test_download_endpoint.py
```

The test suite covers:
- Basic download functionality
- Custom filename and directory options
- Input validation
- Error handling scenarios

## Security Considerations

- Video URLs from Google's API typically have expiration times
- API keys are handled securely through environment variables
- Downloaded files are saved to configurable directories
- Input validation prevents directory traversal attacks

## Performance Notes

- Downloads are streamed to handle large video files efficiently
- Progress tracking provides real-time feedback
- Retry logic handles temporary network issues
- Multiple authentication methods ensure maximum compatibility