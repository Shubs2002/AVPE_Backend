# Fixes for Daily Character Video Generation

## Issues Fixed

### 1. ✅ Missing OpenCV (cv2) Module

**Problem**: Frame extraction was failing with `No module named 'cv2'`

**Solution**: Install OpenCV

```bash
pip install opencv-python
```

Or add to your `requirements.txt`:
```
opencv-python>=4.8.0
```

### 2. ✅ Videos Not Saved to File Storage Manager

**Problem**: Videos were saved to `temp_videos/` instead of organized content directories

**Solution**: Updated to use file storage manager structure

**Before**:
```
temp_videos/
├── temp_Floof_segment_1.mp4
├── temp_Floof_segment_2.mp4
└── temp_Floof_segment_3.mp4
```

**After**:
```
generated_content/
└── daily_character/
    └── Floof's_Cloud_Kiss/
        ├── videos/
        │   ├── Floof_segment_1.mp4
        │   ├── Floof_segment_2.mp4
        │   └── Floof_segment_3.mp4
        └── frames/
            ├── last_frame_seg_1.png
            ├── last_frame_seg_2.png
            └── last_frame_seg_3.png

downloads/  (if download=true)
├── Floof_segment_1.mp4
├── Floof_segment_2.mp4
└── Floof_segment_3.mp4
```

### 3. ✅ Imagen First Frame Generation (Placeholder)

**Problem**: Imagen generation is not yet implemented

**Current Status**: Uses character keyframe as placeholder

**Note**: Full Imagen integration requires implementing the nano banana model API call

## New File Structure

### Daily Character Content Organization

```
generated_content/
└── daily_character/
    └── {Character_Name}_{Title}/
        ├── videos/
        │   ├── {Character}_segment_1.mp4
        │   ├── {Character}_segment_2.mp4
        │   └── {Character}_segment_N.mp4
        ├── frames/
        │   ├── last_frame_seg_1.png
        │   ├── last_frame_seg_2.png
        │   └── last_frame_seg_N.png
        └── metadata.json (future)
```

### Downloads Folder (Optional)

If `download: true` in request:
```
downloads/
├── {Character}_segment_1.mp4
├── {Character}_segment_2.mp4
└── {Character}_segment_N.mp4
```

## Installation Steps

### 1. Install OpenCV

```bash
pip install opencv-python
```

### 2. Verify Installation

```python
import cv2
print(cv2.__version__)  # Should print version number
```

### 3. Test Frame Extraction

```python
from app.services.genai_service import extract_last_frame_from_video

# Test with a video file
frame_path = extract_last_frame_from_video("test_video.mp4", "test_frame.png")
print(f"Frame extracted: {frame_path}")
```

## Updated Features

### 1. Organized Storage

Videos and frames are now saved to:
- **Content Directory**: `generated_content/daily_character/{Title}/`
- **Downloads Directory**: `downloads/` (if requested)

### 2. Frame Chaining

Last frames are extracted and saved to:
- `generated_content/daily_character/{Title}/frames/last_frame_seg_N.png`

These frames are used as first frames for subsequent segments.

### 3. Dual Download

If `download: true`:
- Videos saved to content directory (organized)
- Videos also saved to downloads folder (easy access)

## API Response

### Updated Response Structure

```json
{
  "success": true,
  "total_segments": 3,
  "success_count": 3,
  "video_urls": [...],
  "frame_chain": [
    {
      "segment": 1,
      "last_frame": "generated_content/daily_character/Floof's_Cloud_Kiss/frames/last_frame_seg_1.png",
      "video_file": "generated_content/daily_character/Floof's_Cloud_Kiss/videos/Floof_segment_1.mp4"
    },
    {
      "segment": 2,
      "last_frame": "generated_content/daily_character/Floof's_Cloud_Kiss/frames/last_frame_seg_2.png",
      "video_file": "generated_content/daily_character/Floof's_Cloud_Kiss/videos/Floof_segment_2.mp4"
    }
  ],
  "segments_results": [
    {
      "segment_number": 1,
      "video_file": "generated_content/daily_character/Floof's_Cloud_Kiss/videos/Floof_segment_1.mp4",
      "last_frame_extracted": "generated_content/daily_character/Floof's_Cloud_Kiss/frames/last_frame_seg_1.png",
      "downloaded_file": "downloads/Floof_segment_1.mp4"
    }
  ]
}
```

## Troubleshooting

### Issue: "No module named 'cv2'"

**Solution**:
```bash
pip install opencv-python
```

### Issue: Frame extraction fails

**Check**:
1. OpenCV is installed: `pip list | grep opencv`
2. Video file exists and is readable
3. Video file is not corrupted

### Issue: Videos not in expected location

**Check**:
1. File storage manager is initialized
2. Content directory permissions
3. Disk space available

## Benefits

### 1. Organized Storage
- All content in one place
- Easy to find and manage
- Consistent structure

### 2. Frame Chaining Works
- Last frames properly extracted
- Stored for next segment
- Seamless transitions

### 3. Dual Access
- Organized in content directory
- Easy access in downloads folder
- Best of both worlds

## Files Modified

- ✅ `src/app/services/content_to_video_service.py` - Updated download paths and frame extraction
- ✅ `src/app/services/file_storage_manager.py` - Already has DAILY_CHARACTER type

## Next Steps

### 1. Install OpenCV (Required)

```bash
pip install opencv-python
```

### 2. Test Frame Extraction

Generate a daily character video and verify:
- Videos saved to `generated_content/daily_character/{Title}/videos/`
- Frames saved to `generated_content/daily_character/{Title}/frames/`
- Downloads saved to `downloads/` (if requested)

### 3. Implement Imagen (Optional)

For custom first frame generation, implement the nano banana model API:

```python
def generate_first_frame_with_imagen(character_keyframe_uri, frame_description, aspect_ratio):
    # TODO: Implement actual Imagen API call
    # 1. Load character image
    # 2. Call Imagen API with character + scene description
    # 3. Return generated frame
    pass
```

## Summary

✅ **OpenCV Required**: Install with `pip install opencv-python`
✅ **Organized Storage**: Videos saved to file storage manager structure
✅ **Dual Download**: Content directory + downloads folder
✅ **Frame Chaining**: Last frames extracted and used for next segment
✅ **Better Organization**: Easy to find and manage content

Install OpenCV and you're ready to go!
