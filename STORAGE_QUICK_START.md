# File Storage Manager - Quick Start

## 🚀 Get Started in 3 Steps

### Step 1: Test the System (2 minutes)

```bash
python test_storage_manager.py
```

This will show you:
- ✅ All content types
- ✅ How to list content
- ✅ How to get content info
- ✅ Storage statistics

### Step 2: Check Your Current Content (1 minute)

```bash
# See what you have in old structure
curl "http://127.0.0.1:8000/api/storage/stats"
```

### Step 3: Start Using It! (Now!)

```python
from app.utils import storage_manager, ContentType

# Save a movie set
storage_manager.save_set(
    ContentType.MOVIE,
    "My Movie Title",
    set_number=1,
    set_data=your_data
)

# That's it! File is saved to:
# generated_content/movies/My_Movie_Title/set_01.json
```

## 📚 Common Tasks

### Save Movie Content
```python
from app.utils import storage_manager, ContentType

# Save metadata
storage_manager.save_metadata(
    ContentType.MOVIE,
    "Midnight Protocol",
    metadata_dict
)

# Save sets
for i in range(1, 31):
    storage_manager.save_set(
        ContentType.MOVIE,
        "Midnight Protocol",
        i,
        set_data
    )
```

### Save Meme/Music Video/WhatsApp Story
```python
# Single file content
storage_manager.save_segments(
    ContentType.MEME,  # or MUSIC_VIDEO, WHATSAPP_STORY
    "My Meme Title",
    segments_data
)
```

### Check What's Missing
```python
info = storage_manager.get_content_info(
    ContentType.MOVIE,
    "Midnight Protocol"
)

print(f"Missing sets: {info['missing_sets']}")
# Output: Missing sets: [26, 27, 28, 29, 30]
```

### List All Content
```python
movies = storage_manager.list_content(ContentType.MOVIE)
print(f"All movies: {movies}")
```

## 🔧 API Quick Reference

```bash
# List all movies
curl "http://127.0.0.1:8000/api/storage/list/movies"

# Get movie info
curl "http://127.0.0.1:8000/api/storage/info/movies/Midnight%20Protocol"

# Get all stats
curl "http://127.0.0.1:8000/api/storage/stats"

# Migrate old content
curl -X POST "http://127.0.0.1:8000/api/storage/migrate" \
  -H "Content-Type: application/json" \
  -d '{"old_directory": "generated_movie_script", "content_type": "movies"}'
```

## 📁 Where Files Go

```
generated_content/
├── movies/
│   └── Your_Movie_Title/
│       ├── metadata.json
│       └── set_01.json
├── memes/
│   └── Your_Meme_Title/
│       └── segments.json
└── ... (other types)
```

## 🎯 Content Types

Use these constants:
- `ContentType.MOVIE` → `movies/`
- `ContentType.STORY` → `stories/`
- `ContentType.MEME` → `memes/`
- `ContentType.FREE_CONTENT` → `free_content/`
- `ContentType.MUSIC_VIDEO` → `music_videos/`
- `ContentType.WHATSAPP_STORY` → `whatsapp_stories/`

## 💡 Pro Tips

1. **Title Sanitization is Automatic**
   - "My Movie!" → "My_Movie"
   - "Test/Video" → "TestVideo"
   - Spaces → Underscores

2. **Folders Created Automatically**
   - No need to create directories
   - Just call save methods

3. **Use get_content_info() for Everything**
   - Shows what exists
   - Shows what's missing
   - Shows completion status

4. **Migration is Safe**
   - Doesn't delete old files
   - Creates copies in new structure
   - Test before removing old files

## 🔄 Migrate Existing Content

```bash
# Migrate movies
curl -X POST "http://127.0.0.1:8000/api/storage/migrate" \
  -H "Content-Type: application/json" \
  -d '{
    "old_directory": "generated_movie_script",
    "content_type": "movies"
  }'

# Check migration result
curl "http://127.0.0.1:8000/api/storage/list/movies"
```

## 📖 Full Documentation

- **STORAGE_MANAGER_SUMMARY.md** - Overview and features
- **FILE_STORAGE_MANAGER_GUIDE.md** - Complete guide
- **STORAGE_INTEGRATION_EXAMPLE.md** - How to update services
- **STORAGE_STRUCTURE_VISUAL.md** - Visual diagrams

## ✅ You're Ready!

That's all you need to know to get started. The storage manager handles:
- ✅ Path construction
- ✅ Directory creation
- ✅ Title sanitization
- ✅ File organization
- ✅ Content discovery

Just use the simple methods and enjoy organized content! 🎉
