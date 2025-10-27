# Reference Images - Future Implementation

## 📋 Current Status

**Reference images are NOT YET SUPPORTED** in the current `google-genai` SDK version (1.38.0).

The feature has been **temporarily disabled** to allow video generation to work properly.

## ⚠️ What Was Removed

All reference image code has been commented out:

```python
# In genai_service.py
# reference_images = payload.get("reference_images", [])
# reference_image_urls = payload.get("reference_image_urls", [])

# In content_to_video_service.py
# reference_image_urls=[character_keyframe_uri]  # TODO: Add when SDK supports it
```

## 🔮 When Available

When Google releases SDK support for reference images, follow these steps:

### Step 1: Check SDK Version

```bash
pip show google-genai
```

Look for version that mentions reference images support in changelog.

### Step 2: Update Package

```bash
pip install --upgrade google-genai
```

### Step 3: Uncomment Code

**In `src/app/services/genai_service.py`:**

```python
# Uncomment these lines:
reference_images = payload.get("reference_images", [])
reference_image_urls = payload.get("reference_image_urls", [])

# Uncomment the reference image processing section
# Around line 100-150
```

**In `src/app/services/content_to_video_service.py`:**

```python
# Uncomment this line:
reference_image_urls=[character_keyframe_uri]
```

### Step 4: Test

```bash
# Test with a simple video generation
POST /api/generate-daily-character-videos
```

## 📚 Expected API (Based on Documentation)

According to Google's documentation, the API should look like:

```python
from google import genai
from google.genai import types

client = genai.Client()

# Create reference image
character_reference = types.VideoGenerationReferenceImage(
    image=character_image,
    reference_type="asset"
)

# Generate video with reference
operation = client.models.generate_videos(
    model="veo-3.1-generate-preview",
    prompt="Character walks...",
    image=first_frame,
    config=types.GenerateVideosConfig(
        reference_images=[character_reference],
        duration_seconds=8,
        aspect_ratio="9:16"
    )
)
```

## 🎯 What to Enable

### 1. Reference Image Download
```python
# Download character images from URLs
if reference_image_urls:
    for url in reference_image_urls:
        response = requests.get(url)
        ref_image = Image.open(BytesIO(response.content))
        reference_images.append(ref_image)
```

### 2. Reference Image Objects
```python
# Create VideoGenerationReferenceImage objects
reference_image_objects = []
for ref_img in reference_images:
    ref_obj = types.VideoGenerationReferenceImage(
        image=_prepare_image_input(ref_img),
        reference_type="asset"
    )
    reference_image_objects.append(ref_obj)
```

### 3. Add to Config
```python
# Add to GenerateVideosConfig
config_params["reference_images"] = reference_image_objects
```

## 🔍 How to Check if Available

### Method 1: Check SDK Documentation
```bash
python -c "from google.genai import types; print(dir(types))"
```

Look for `VideoGenerationReferenceImage` in the output.

### Method 2: Try Import
```python
try:
    from google.genai import types
    ref = types.VideoGenerationReferenceImage
    print("✅ Reference images supported!")
except AttributeError:
    print("❌ Reference images not yet supported")
```

### Method 3: Check Changelog
Visit: https://github.com/googleapis/python-genai/releases

## 📝 Code Locations

Files that need to be updated when reference images become available:

1. **`src/app/services/genai_service.py`**
   - Line ~95: Uncomment reference_images extraction
   - Line ~100-150: Uncomment reference image processing
   - Line ~160: Uncomment adding to config

2. **`src/app/services/content_to_video_service.py`**
   - Line ~950: Uncomment reference_image_urls parameter

## 🎊 Benefits When Available

Once reference images are supported, you'll get:

- ✅ **Perfect character consistency** across all segments
- ✅ **Better visual quality** with character references
- ✅ **Smoother transitions** between segments
- ✅ **More accurate character representation**

## 🔄 Current Workaround

For now, the system uses:
- ✅ **First frame** from previous segment (good continuity)
- ✅ **Detailed prompts** (helps with consistency)
- ✅ **Veo 3.1 model** (better quality)

This provides good results, but not as perfect as with reference images.

## 📞 Stay Updated

Check for updates:
- Google GenAI SDK: https://github.com/googleapis/python-genai
- Vertex AI Documentation: https://cloud.google.com/vertex-ai/docs

---

**Status:** ⏳ Waiting for SDK support
**Priority:** 🔥 High (for character consistency)
**Difficulty:** ⭐ Easy (just uncomment code)
