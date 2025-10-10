# File Storage Structure - Visual Guide

## 📁 Directory Structure

```
your_project/
│
├── generated_content/              ← New organized structure
│   │
│   ├── movies/                     ← All movies here
│   │   ├── Midnight_Protocol/      ← Each movie in its own folder
│   │   │   ├── metadata.json       ← Story metadata
│   │   │   ├── set_01.json         ← Set 1 (segments 1-10)
│   │   │   ├── set_02.json         ← Set 2 (segments 11-20)
│   │   │   ├── set_03.json         ← Set 3 (segments 21-30)
│   │   │   └── ...
│   │   │
│   │   ├── Action_Hero/
│   │   │   ├── metadata.json
│   │   │   ├── set_01.json
│   │   │   └── ...
│   │   │
│   │   └── Sci_Fi_Adventure/
│   │       └── ...
│   │
│   ├── stories/                    ← All stories here
│   │   ├── My_First_Story/
│   │   │   ├── metadata.json
│   │   │   └── segments.json       ← All segments in one file
│   │   │
│   │   └── Another_Story/
│   │       └── ...
│   │
│   ├── memes/                      ← All memes here
│   │   ├── Funny_Cat_Meme/
│   │   │   ├── metadata.json
│   │   │   └── segments.json
│   │   │
│   │   └── Trending_Meme/
│   │       └── ...
│   │
│   ├── free_content/               ← Free-form content
│   │   ├── Tutorial_Video/
│   │   │   ├── metadata.json
│   │   │   └── segments.json
│   │   │
│   │   └── Product_Demo/
│   │       └── ...
│   │
│   ├── music_videos/               ← Music videos
│   │   ├── My_Song_Title/
│   │   │   ├── metadata.json
│   │   │   └── segments.json
│   │   │
│   │   └── Another_Song/
│   │       └── ...
│   │
│   └── whatsapp_stories/           ← WhatsApp stories
│       ├── Daily_Update/
│       │   ├── metadata.json
│       │   └── segments.json
│       │
│       └── Product_Launch/
│           └── ...
│
└── generated_movie_script/         ← Old flat structure (to be migrated)
    ├── Midnight_Protocol_metadata.json
    ├── Midnight_Protocol_set_01.json
    ├── Midnight_Protocol_set_02.json
    ├── Another_Movie_metadata.json
    ├── Another_Movie_set_01.json
    └── ...                         ← Gets messy with many files!
```

## 🔄 Before vs After

### Before (Flat Structure)
```
generated_movie_script/
├── Movie1_metadata.json
├── Movie1_set_01.json
├── Movie1_set_02.json
├── Movie1_set_03.json
├── Movie2_metadata.json
├── Movie2_set_01.json
├── Movie2_set_02.json
├── Story1_segments.json
├── Story2_segments.json
├── Meme1_segments.json
└── ...                    ← 100+ files in one folder! 😱
```

### After (Organized Structure)
```
generated_content/
├── movies/
│   ├── Movie1/            ← Clean separation
│   │   ├── metadata.json
│   │   ├── set_01.json
│   │   ├── set_02.json
│   │   └── set_03.json
│   └── Movie2/
│       └── ...
├── stories/
│   ├── Story1/
│   └── Story2/
└── memes/
    └── Meme1/             ← Easy to find! 😊
```

## 📊 Content Type Organization

```
┌─────────────────────────────────────────────────────────┐
│                  generated_content/                      │
└─────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        │                 │                 │
    ┌───▼───┐        ┌────▼────┐      ┌────▼────┐
    │movies │        │ stories │      │  memes  │
    └───┬───┘        └────┬────┘      └────┬────┘
        │                 │                 │
    ┌───▼────────┐   ┌────▼─────┐     ┌────▼─────┐
    │ Movie_A/   │   │ Story_X/ │     │ Meme_1/  │
    │ Movie_B/   │   │ Story_Y/ │     │ Meme_2/  │
    │ Movie_C/   │   │ Story_Z/ │     │ Meme_3/  │
    └────────────┘   └──────────┘     └──────────┘

        ┌─────────────────┼─────────────────┐
        │                 │                 │
  ┌─────▼──────┐   ┌──────▼──────┐  ┌──────▼──────┐
  │free_content│   │music_videos │  │whatsapp_    │
  │            │   │             │  │stories      │
  └─────┬──────┘   └──────┬──────┘  └──────┬──────┘
        │                 │                 │
   ┌────▼─────┐      ┌────▼─────┐     ┌────▼─────┐
   │Content_1/│      │ Song_A/  │     │ Story_1/ │
   │Content_2/│      │ Song_B/  │     │ Story_2/ │
   └──────────┘      └──────────┘     └──────────┘
```

## 🎯 File Organization by Content Type

### Multi-Set Content (Movies, Long Stories)
```
movies/Midnight_Protocol/
├── metadata.json          ← Story info, characters, settings
├── set_01.json           ← Segments 1-10
├── set_02.json           ← Segments 11-20
├── set_03.json           ← Segments 21-30
└── ...                   ← More sets as needed
```

### Single-File Content (Memes, Music Videos, WhatsApp Stories)
```
memes/Funny_Meme/
├── metadata.json         ← Meme info
└── segments.json         ← All segments in one file
```

## 🔍 Finding Content

### Old Way (Manual Search)
```python
# Hard to find specific content
import os
files = os.listdir("generated_movie_script")
# Returns: ['Movie1_set_01.json', 'Movie1_set_02.json', 
#           'Movie2_set_01.json', 'Story1.json', ...]
# Which movie is which? 🤔
```

### New Way (Organized)
```python
from app.utils import storage_manager, ContentType

# Easy to find
movies = storage_manager.list_content(ContentType.MOVIE)
# Returns: ['Midnight_Protocol', 'Action_Hero', 'Sci_Fi_Adventure']

# Get specific movie info
info = storage_manager.get_content_info(ContentType.MOVIE, "Midnight_Protocol")
# Returns complete info about the movie
```

## 📈 Scalability Comparison

### Flat Structure (Old)
```
1 movie   = 31 files (1 metadata + 30 sets)
10 movies = 310 files in ONE folder! 😱
50 movies = 1,550 files in ONE folder! 💀
```

### Organized Structure (New)
```
1 movie   = 1 folder with 31 files
10 movies = 10 folders, each with ~31 files ✅
50 movies = 50 folders, each organized 🎉
```

## 🎨 Visual Flow

### Saving Content
```
Your Code
    │
    ├─► storage_manager.save_metadata(ContentType.MOVIE, "My Movie", data)
    │       │
    │       ├─► Sanitize title: "My Movie" → "My_Movie"
    │       ├─► Create folder: generated_content/movies/My_Movie/
    │       └─► Save file: generated_content/movies/My_Movie/metadata.json
    │
    └─► storage_manager.save_set(ContentType.MOVIE, "My Movie", 1, data)
            │
            ├─► Use existing folder: generated_content/movies/My_Movie/
            └─► Save file: generated_content/movies/My_Movie/set_01.json
```

### Loading Content
```
Your Code
    │
    └─► storage_manager.get_content_info(ContentType.MOVIE, "My Movie")
            │
            ├─► Find folder: generated_content/movies/My_Movie/
            ├─► Load metadata: metadata.json
            ├─► Scan for sets: set_01.json, set_02.json, ...
            └─► Return complete info:
                {
                  "exists": true,
                  "has_metadata": true,
                  "existing_sets": [1, 2, 3, ...],
                  "missing_sets": [26, 27, 28, 29, 30],
                  "is_complete": false
                }
```

## 🚀 Migration Flow

```
Old Structure                    Migration                    New Structure
─────────────                    ─────────                    ─────────────

generated_movie_script/          
├── Movie1_metadata.json    ──┐
├── Movie1_set_01.json      ──┤
├── Movie1_set_02.json      ──┤  storage_manager.migrate()   generated_content/
├── Movie2_metadata.json    ──┤         │                    ├── movies/
├── Movie2_set_01.json      ──┤         │                    │   ├── Movie1/
└── ...                     ──┘         │                    │   │   ├── metadata.json
                                        │                    │   │   ├── set_01.json
                                        ▼                    │   │   └── set_02.json
                                                            │   └── Movie2/
                              Analyzes files                │       └── ...
                              Groups by title               └── stories/
                              Creates folders                   └── ...
                              Copies files
                              Preserves data
```

## 💡 Quick Reference

| Task | Old Way | New Way |
|------|---------|---------|
| **Save** | Manual path construction | `storage_manager.save_set()` |
| **Load** | Manual file reading | `storage_manager.load_set()` |
| **Find** | Search through flat list | `storage_manager.list_content()` |
| **Info** | Manual checks | `storage_manager.get_content_info()` |
| **Delete** | Manual file deletion | `storage_manager.delete_content()` |

## 🎉 Result

**Before:** Messy, hard to manage, doesn't scale  
**After:** Clean, organized, scales beautifully!

```
😱 → 😊
```
