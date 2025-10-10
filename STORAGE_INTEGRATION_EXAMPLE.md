# Storage Manager Integration Examples

## How to Update Your Existing Services

### Example 1: Update Movie Generation Service

**File:** `src/app/services/openai_service.py`

**Before:**
```python
def generate_full_story_automatically(...):
    # Old way
    output_directory = "generated_movie_script"
    os.makedirs(output_directory, exist_ok=True)
    
    # Save set
    safe_title = title.replace(' ', '_')
    filename = f"{safe_title}_set_{set_number:02d}.json"
    filepath = os.path.join(output_directory, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(story_set, f, indent=2, ensure_ascii=False)
    
    # Save metadata
    metadata_filename = f"{safe_title}_metadata.json"
    metadata_filepath = os.path.join(output_directory, metadata_filename)
    
    with open(metadata_filepath, 'w', encoding='utf-8') as f:
        json.dump(story_metadata, f, indent=2, ensure_ascii=False)
```

**After:**
```python
from app.utils import storage_manager, ContentType

def generate_full_story_automatically(...):
    # New way - much cleaner!
    
    # Save set
    filepath = storage_manager.save_set(
        ContentType.MOVIE,
        title,
        set_number,
        story_set
    )
    
    # Save metadata
    metadata_filepath = storage_manager.save_metadata(
        ContentType.MOVIE,
        title,
        story_metadata
    )
```

### Example 2: Update Retry Logic

**File:** `src/app/services/openai_service.py`

**Before:**
```python
def retry_failed_story_sets(previous_result: dict, max_retries: int = 3):
    # Old way - manual path construction
    output_directory = previous_result.get('output_directory', 'generated_movie_script')
    story_metadata = previous_result.get('story_metadata')
    
    # Find failed sets manually
    failed_sets = [s for s in previous_result['sets'] if s.get('status') == 'failed']
```

**After:**
```python
from app.utils import storage_manager, ContentType

def retry_failed_story_sets(previous_result: dict, max_retries: int = 3):
    # New way - use storage manager
    story_title = previous_result.get('story_title')
    
    # Get content info (includes missing sets)
    info = storage_manager.get_content_info(ContentType.MOVIE, story_title)
    
    if not info['exists']:
        raise ValueError(f"Story '{story_title}' not found")
    
    # Missing sets are automatically detected
    missing_sets = info.get('missing_sets', [])
    
    # Save retried sets
    for set_number in missing_sets:
        # Generate set...
        storage_manager.save_set(
            ContentType.MOVIE,
            story_title,
            set_number,
            generated_set_data
        )
```

### Example 3: Update Meme Generation

**File:** `src/app/services/openai_service.py`

**Before:**
```python
def generate_meme_segments(...):
    # Old way
    output_dir = "generated_memes"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{title.replace(' ', '_')}_segments.json"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w') as f:
        json.dump(segments, f, indent=2)
```

**After:**
```python
from app.utils import storage_manager, ContentType

def generate_meme_segments(...):
    # New way
    filepath = storage_manager.save_segments(
        ContentType.MEME,
        title,
        segments
    )
```

### Example 4: Update WhatsApp Story Generation

**Before:**
```python
def generate_whatsapp_story(...):
    output_dir = "generated_whatsapp_stories"
    os.makedirs(output_dir, exist_ok=True)
    
    safe_title = title.replace(' ', '_')
    filepath = os.path.join(output_dir, f"{safe_title}.json")
    
    with open(filepath, 'w') as f:
        json.dump(story_data, f, indent=2)
```

**After:**
```python
from app.utils import storage_manager, ContentType

def generate_whatsapp_story(...):
    filepath = storage_manager.save_segments(
        ContentType.WHATSAPP_STORY,
        title,
        story_data
    )
```

### Example 5: Update Music Video Generation

**Before:**
```python
def generate_music_video(...):
    output_dir = "generated_music_videos"
    os.makedirs(output_dir, exist_ok=True)
    
    filename = f"{song_title.replace(' ', '_')}_segments.json"
    filepath = os.path.join(output_dir, filename)
```

**After:**
```python
from app.utils import storage_manager, ContentType

def generate_music_video(...):
    filepath = storage_manager.save_segments(
        ContentType.MUSIC_VIDEO,
        song_title,
        segments_data
    )
```

## Complete Service Update Template

Here's a template for updating any generation service:

```python
from app.utils import storage_manager, ContentType

def your_generation_function(
    title: str,
    content_data: dict,
    content_type: str = ContentType.MOVIE  # or STORY, MEME, etc.
):
    """Generate content and save using storage manager."""
    
    # 1. Generate your content
    generated_data = generate_content(...)
    
    # 2. Prepare metadata
    metadata = {
        "title": title,
        "generated_at": datetime.now().isoformat(),
        "generation_info": {
            # Your generation info
        }
    }
    
    # 3. Save using storage manager
    
    # For multi-set content (movies, long stories)
    if has_multiple_sets:
        # Save metadata
        storage_manager.save_metadata(content_type, title, metadata)
        
        # Save each set
        for set_num, set_data in enumerate(sets, 1):
            storage_manager.save_set(content_type, title, set_num, set_data)
    
    # For single-file content (memes, music videos, whatsapp stories)
    else:
        # Save metadata
        storage_manager.save_metadata(content_type, title, metadata)
        
        # Save segments
        storage_manager.save_segments(content_type, title, generated_data)
    
    # 4. Return info about saved content
    info = storage_manager.get_content_info(content_type, title)
    
    return {
        "success": True,
        "title": title,
        "content_type": content_type,
        "directory": info['directory'],
        "files_saved": True
    }
```

## Migration Strategy

### Phase 1: Add Storage Manager (Non-Breaking)

1. Keep existing code working
2. Add storage manager alongside old code
3. Save to both locations temporarily

```python
# Dual save during migration
# Old way
old_filepath = os.path.join("generated_movie_script", filename)
with open(old_filepath, 'w') as f:
    json.dump(data, f)

# New way (in parallel)
storage_manager.save_set(ContentType.MOVIE, title, set_num, data)
```

### Phase 2: Test New Structure

1. Verify new structure works
2. Test all endpoints
3. Ensure nothing breaks

### Phase 3: Switch to New Structure

1. Remove old save code
2. Use only storage manager
3. Update all references

### Phase 4: Migrate Old Content

1. Use migration endpoint
2. Verify migrated content
3. Archive or delete old files

## Benefits Summary

| Aspect | Before | After |
|--------|--------|-------|
| **Organization** | Flat directory | Organized by type and title |
| **Code** | Manual path construction | Simple method calls |
| **Maintenance** | Hard to find files | Easy navigation |
| **Scalability** | Gets messy with many files | Stays organized |
| **Type Safety** | String paths everywhere | ContentType constants |
| **Error Handling** | Manual checks | Built-in validation |

## Quick Reference

```python
from app.utils import storage_manager, ContentType

# Save
storage_manager.save_metadata(ContentType.MOVIE, title, metadata)
storage_manager.save_set(ContentType.MOVIE, title, 1, set_data)
storage_manager.save_segments(ContentType.MEME, title, segments)

# Load
metadata = storage_manager.load_metadata(ContentType.MOVIE, title)
set_data = storage_manager.load_set(ContentType.MOVIE, title, 1)
segments = storage_manager.load_segments(ContentType.MEME, title)

# Info
info = storage_manager.get_content_info(ContentType.MOVIE, title)
missing = storage_manager.find_missing_sets(ContentType.MOVIE, title, 30)
all_sets = storage_manager.get_all_sets(ContentType.MOVIE, title)

# List
movies = storage_manager.list_content(ContentType.MOVIE)

# Delete
storage_manager.delete_content(ContentType.MOVIE, title)
```

## Next Steps

1. Choose a service to update first (recommend starting with a simple one like memes)
2. Update the service using the examples above
3. Test thoroughly
4. Repeat for other services
5. Migrate old content once all services are updated
