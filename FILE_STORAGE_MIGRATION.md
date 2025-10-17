# File Storage Manager Migration

## Summary

The file storage manager has been moved from `utils` to `services` and integrated throughout the application to automatically manage file paths. Users no longer need to specify `output_directory` - the system handles it automatically based on content type.

## Changes Made

### 1. File Storage Manager Location
- **Moved**: `src/app/utils/file_storage_manager.py` → `src/app/services/file_storage_manager.py`
- **Reason**: It's a service that provides business logic, not just a utility

### 2. Automatic Path Management

#### Before:
```python
# User had to specify output directory
{
    "idea": "My story",
    "output_directory": "generated_movie_script"  # Manual path
}
```

#### After:
```python
# System automatically determines path based on content type
{
    "idea": "My story"
    # Path automatically set to: generated_content/movies/My_Story/
}
```

### 3. Updated API Endpoints

#### `/api/generate-movie-auto`
- **Removed**: `output_directory` parameter
- **Automatic**: Files saved to `generated_content/movies/{Title}/`

#### `/api/generate-anime-auto`
- **Removed**: `output_directory` parameter  
- **Automatic**: Files saved to `generated_content/anime/{Title}/`

#### `/api/story-status/{content_type}/{title}`
- **Changed**: Now requires `content_type` (e.g., "movies", "anime")
- **Before**: `/api/story-status/Midnight Protocol`
- **After**: `/api/story-status/movies/Midnight Protocol`

#### `/api/retry-story-by-title`
- **Updated**: Request body now includes `content_type`
```json
{
    "title": "Midnight Protocol",
    "content_type": "movies",
    "max_retries": 3
}
```

### 4. File Structure

#### New Organized Structure:
```
generated_content/
├── movies/
│   └── Midnight_Protocol/
│       ├── metadata.json
│       ├── set_01.json
│       ├── set_02.json
│       └── ...
├── anime/
│   └── My_Anime_Story/
│       ├── metadata.json
│       └── ...
├── stories/
├── memes/
├── free_content/
├── music_videos/
├── whatsapp_stories/
└── daily_character/
```

### 5. Updated Services

#### `openai_service.py`
- `generate_full_story_automatically()`: Now uses `storage_manager` automatically
- `generate_anime_story_automatically()`: Now uses `storage_manager` automatically
- `retry_failed_story_sets()`: Updated to use `storage_manager`

#### `story_retry_helper.py`
- All functions now use `storage_manager` instead of manual path construction
- Functions now accept `content_type` instead of `base_dir`

### 6. Benefits

✅ **No manual path management** - System handles it automatically
✅ **Consistent structure** - All content types follow same pattern
✅ **Better organization** - Content grouped by type and title
✅ **Easier migration** - Built-in migration tools for old files
✅ **Type safety** - ContentType constants prevent typos

## Migration Guide

### For Existing Code

If you have old files in flat directories like `generated_movie_script/`, you can migrate them:

```bash
POST /api/storage/migrate
{
    "old_directory": "generated_movie_script",
    "content_type": "movies"
}
```

### For API Clients

Update your API calls to remove `output_directory`:

```python
# Old way
response = requests.post("/api/generate-movie-auto", json={
    "idea": "My story",
    "output_directory": "generated_movie_script"  # Remove this
})

# New way
response = requests.post("/api/generate-movie-auto", json={
    "idea": "My story"
    # Path is automatic!
})
```

## Content Types

Available content types (use these in API calls):
- `movies` - Full-length movies with multiple sets
- `anime` - Japanese anime stories
- `stories` - Story segments
- `memes` - Meme content
- `free_content` - Free-form content
- `music_videos` - Music video segments
- `whatsapp_stories` - WhatsApp story format
- `daily_character` - Daily character life content

## Storage Management Endpoints

### List Content
```bash
GET /api/storage/list/movies
```

### Get Content Info
```bash
GET /api/storage/info/movies/Midnight Protocol
```

### Delete Content
```bash
DELETE /api/storage/delete/movies/Midnight Protocol
```

### Storage Stats
```bash
GET /api/storage/stats
```

## Notes

- All file operations now go through `storage_manager`
- Paths are automatically sanitized and validated
- Missing sets are automatically detected
- Metadata is stored consistently across all content types
