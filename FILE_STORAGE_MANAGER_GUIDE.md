# File Storage Manager - Complete Guide

## Overview

The File Storage Manager provides a clean, organized structure for all your generated content. No more messy flat directories!

## New Directory Structure

```
generated_content/
├── movies/
│   ├── Midnight_Protocol/
│   │   ├── metadata.json
│   │   ├── set_01.json
│   │   ├── set_02.json
│   │   └── ...
│   └── Another_Movie/
│       └── ...
├── stories/
│   └── My_Story/
│       ├── metadata.json
│       └── segments.json
├── memes/
│   └── Funny_Meme/
│       ├── metadata.json
│       └── segments.json
├── free_content/
│   └── Tutorial_Video/
│       └── ...
├── music_videos/
│   └── Song_Title/
│       └── ...
└── whatsapp_stories/
    └── Daily_Story/
        └── ...
```

## Content Types

| Type | Constant | Description |
|------|----------|-------------|
| Movies | `ContentType.MOVIE` | Full-length movies with multiple sets |
| Stories | `ContentType.STORY` | Story segments |
| Memes | `ContentType.MEME` | Meme content |
| Free Content | `ContentType.FREE_CONTENT` | Free-form content |
| Music Videos | `ContentType.MUSIC_VIDEO` | Music video segments |
| WhatsApp Stories | `ContentType.WHATSAPP_STORY` | WhatsApp story format |

## API Endpoints

### 1. Get Content Types

```bash
GET /api/storage/content-types
```

**Response:**
```json
{
  "content_types": ["movies", "stories", "memes", ...],
  "descriptions": {
    "movies": "Full-length movies with multiple sets",
    ...
  }
}
```

### 2. List Content

```bash
GET /api/storage/list/{content_type}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/storage/list/movies"
```

**Response:**
```json
{
  "success": true,
  "content_type": "movies",
  "count": 5,
  "items": ["Midnight_Protocol", "Another_Movie", ...]
}
```

### 3. Get Content Info

```bash
GET /api/storage/info/{content_type}/{title}
```

**Example:**
```bash
curl "http://127.0.0.1:8000/api/storage/info/movies/Midnight%20Protocol"
```

**Response:**
```json
{
  "success": true,
  "exists": true,
  "title": "Midnight Protocol",
  "content_type": "movies",
  "directory": "generated_content/movies/Midnight_Protocol",
  "has_metadata": true,
  "has_sets": true,
  "existing_sets": [1, 2, 3, ..., 25],
  "set_count": 25,
  "total_sets_expected": 30,
  "missing_sets": [26, 27, 28, 29, 30],
  "missing_count": 5,
  "is_complete": false
}
```

### 4. Delete Content

```bash
DELETE /api/storage/delete/{content_type}/{title}
```

**Example:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/storage/delete/movies/Old_Movie"
```

### 5. Get Storage Stats

```bash
GET /api/storage/stats
```

**Response:**
```json
{
  "success": true,
  "total_items": 15,
  "by_type": {
    "movies": {
      "count": 5,
      "items": ["Midnight_Protocol", ...]
    },
    "stories": {
      "count": 3,
      "items": [...]
    },
    ...
  }
}
```

### 6. Migrate Old Content

```bash
POST /api/storage/migrate
```

**Request:**
```json
{
  "old_directory": "generated_movie_script",
  "content_type": "movies"
}
```

**Response:**
```json
{
  "success": true,
  "migrated_count": 5,
  "error_count": 0,
  "migrated": [
    {
      "title": "Midnight Protocol",
      "metadata": "generated_content/movies/Midnight_Protocol/metadata.json",
      "sets_migrated": 25
    },
    ...
  ]
}
```

## Python Usage

### Basic Usage

```python
from app.utils import storage_manager, ContentType

# Save metadata
storage_manager.save_metadata(
    ContentType.MOVIE,
    "My Movie Title",
    metadata_dict
)

# Save a set
storage_manager.save_set(
    ContentType.MOVIE,
    "My Movie Title",
    set_number=1,
    set_data=set_dict
)

# Load metadata
metadata = storage_manager.load_metadata(
    ContentType.MOVIE,
    "My Movie Title"
)

# Get content info
info = storage_manager.get_content_info(
    ContentType.MOVIE,
    "My Movie Title"
)

# Check for missing sets
missing = storage_manager.find_missing_sets(
    ContentType.MOVIE,
    "My Movie Title",
    total_sets=30
)
```

### Advanced Usage

```python
# List all movies
movies = storage_manager.list_content(ContentType.MOVIE)

# Get all existing sets
existing_sets = storage_manager.get_all_sets(
    ContentType.MOVIE,
    "My Movie Title"
)

# Save segments (for single-file content)
storage_manager.save_segments(
    ContentType.MEME,
    "Funny Meme",
    segments_data
)

# Delete content
storage_manager.delete_content(
    ContentType.MOVIE,
    "Old Movie"
)
```

## Integration with Existing Code

### Update Story Generation

**Before:**
```python
# Old way
output_dir = "generated_movie_script"
filename = f"{title}_set_{set_num:02d}.json"
filepath = os.path.join(output_dir, filename)
```

**After:**
```python
# New way
from app.utils import storage_manager, ContentType

filepath = storage_manager.save_set(
    ContentType.MOVIE,
    title,
    set_num,
    set_data
)
```

### Update Retry Logic

**Before:**
```python
# Old way - manually construct paths
metadata_path = f"generated_movie_script/{title}_metadata.json"
```

**After:**
```python
# New way - use storage manager
metadata = storage_manager.load_metadata(ContentType.MOVIE, title)
missing_sets = storage_manager.find_missing_sets(ContentType.MOVIE, title, 30)
```

## Migration Guide

### Step 1: Migrate Existing Content

```bash
# Migrate movies
curl -X POST "http://127.0.0.1:8000/api/storage/migrate" \
  -H "Content-Type: application/json" \
  -d '{"old_directory": "generated_movie_script", "content_type": "movies"}'

# Migrate other content types as needed
```

### Step 2: Update Generation Endpoints

Update your generation endpoints to use the storage manager:

```python
# In your controller/service
from app.utils import storage_manager, ContentType

# Save metadata
storage_manager.save_metadata(ContentType.MOVIE, title, metadata)

# Save sets
for set_num, set_data in enumerate(sets, 1):
    storage_manager.save_set(ContentType.MOVIE, title, set_num, set_data)
```

### Step 3: Update Retry Logic

```python
# Use storage manager to find missing sets
info = storage_manager.get_content_info(ContentType.MOVIE, title)
missing_sets = info.get('missing_sets', [])
```

## Benefits

✅ **Organized** - Each content item in its own folder  
✅ **Type-Safe** - Content types are clearly separated  
✅ **Scalable** - Easy to find and manage content  
✅ **Clean** - No more flat directories with hundreds of files  
✅ **Flexible** - Works with all content types  
✅ **Backward Compatible** - Migration tool for old content  

## File Naming

The storage manager automatically:
- Sanitizes titles for filesystem safety
- Removes invalid characters (`<>:"/\|?*`)
- Replaces spaces with underscores
- Limits length to 100 characters
- Handles edge cases (empty titles, etc.)

## Testing

```bash
# Run the test suite
python test_storage_manager.py
```

This will test all features:
- Getting content types
- Listing content
- Getting content info
- Storage statistics
- Migration (example only)

## Next Steps

1. **Test the endpoints** - Run `python test_storage_manager.py`
2. **Migrate existing content** - Use the `/storage/migrate` endpoint
3. **Update generation code** - Integrate storage manager into your services
4. **Enjoy organized content!** - No more messy directories

## Troubleshooting

**Q: Can I use both old and new structure?**  
A: Yes! The migration doesn't delete old files. You can migrate and test before removing old files.

**Q: What happens to existing code?**  
A: Old code continues to work. Update gradually as you integrate the storage manager.

**Q: How do I find content in the new structure?**  
A: Use the API endpoints or storage manager methods. They handle all path construction.

**Q: Can I customize the base directory?**  
A: Yes! Initialize with custom path: `FileStorageManager(base_dir="my_custom_dir")`
