# Server-Side Video Merging Guide

## 🎬 **How Server-Side Merging Works**

Your video merger now supports **both approaches**:

### 🖥️ **Server-Side Merging** (What You Want)
- ✅ **Downloads** all video segments to server
- ✅ **Merges** them into a single video file
- ✅ **Returns** the merged video file path
- ✅ **Cleans up** individual segment files
- ✅ **Creates** thumbnail automatically

### 📱 **Client-Side Merging** (Cloud-Native)
- ✅ **Returns** video URLs + merge instructions
- ✅ **Frontend** handles merging using Web APIs
- ✅ **No server** processing overhead

## 🚀 **API Usage**

### **Server-Side Merge (Creates Actual File)**
```bash
POST /merge-content-videos
{
  "results": {
    "video_urls": ["url1", "url2", "url3"],
    "content_title": "My Video",
    "characters_roster": [...],
    "content_type": "story"
  },
  "server_side": true,        # KEY: Set to true for server merging
  "cleanup_segments": true,   # Delete individual segments after merge
  "output_filename": "my_awesome_video"
}
```

**Response:**
```json
{
  "success": true,
  "merge_method": "ffmpeg",           // or "moviepy"
  "server_side": true,
  "output_file": "merged_videos/my_awesome_video.mp4",
  "file_size": 52428800,             // File size in bytes
  "segments_merged": 3,
  "thumbnail_result": {
    "success": true,
    "thumbnail_path": "thumbnails/my_awesome_video_thumbnail.png"
  },
  "cleanup_result": {
    "deleted_count": 3,               // Segment files deleted
    "success": true
  }
}
```

### **Client-Side Instructions (Cloud-Native)**
```bash
POST /merge-content-videos
{
  "results": {...},
  "server_side": false       # Set to false for client instructions
}
```

## 🔧 **Merge Methods**

The server tries multiple methods in order:

### 1. **FFmpeg** (Fastest, Best Quality)
- Uses your installed FFmpeg
- Fastest merging with no re-encoding
- Best quality preservation

### 2. **MoviePy** (Python Fallback)
- Pure Python solution
- Works without FFmpeg
- Slower but reliable

### 3. **Client-Side** (Ultimate Fallback)
- Returns merge instructions
- No server processing

## 📁 **File Structure After Merge**

```
Backend/
├── merged_videos/
│   └── my_awesome_video.mp4     # ✅ Final merged video
├── thumbnails/
│   └── my_awesome_video_thumbnail.png  # ✅ Auto-generated thumbnail
└── downloads/                   # ❌ Segment files deleted (if cleanup=true)
    ├── segment_1.mp4           # Deleted
    ├── segment_2.mp4           # Deleted
    └── segment_3.mp4           # Deleted
```

## 🎯 **Auto-Merge in Video Generation**

You can also enable auto-merge during video generation:

```bash
POST /generate-full-content-videos
{
  "content_data": {...},
  "auto_merge": true,        # Enable auto-merge
  "server_side": true,       # Use server-side merging
  "cleanup_segments": true   # Clean up segments
}
```

This will:
1. Generate all video segments
2. Automatically merge them server-side
3. Create thumbnail
4. Clean up individual segments
5. Return final merged video + thumbnail

## 📊 **Benefits of Server-Side Merging**

- ✅ **Single File Output** - Get one merged video file
- ✅ **Automatic Cleanup** - Segments deleted after merge
- ✅ **No Frontend Work** - Backend handles everything
- ✅ **Quality Preservation** - FFmpeg maintains video quality
- ✅ **Thumbnail Included** - Auto-generated with AI
- ✅ **Ready for Upload** - Perfect for YouTube, social media

## 🔄 **Workflow Example**

1. **Generate Content**: `POST /generate-prompt-based-story`
2. **Generate Videos**: `POST /generate-full-content-videos` with `auto_merge: true, server_side: true`
3. **Get Results**: 
   - `merged_videos/story_complete.mp4` (final video)
   - `thumbnails/story_complete_thumbnail.png` (thumbnail)
   - Individual segments automatically deleted

**Result**: Ready-to-upload video + thumbnail! 🎉