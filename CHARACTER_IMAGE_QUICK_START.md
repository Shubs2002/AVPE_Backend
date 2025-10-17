# Character Creation from Image - Quick Start

## 🚀 Quick Setup (3 Steps)

### 1. Install Dependencies

```bash
pip install cloudinary rembg
```

### 2. Configure Cloudinary in `.env.dev`

```env
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

Get credentials from: https://cloudinary.com/console

### 3. Start Server

```bash
python -m uvicorn src.main:app --reload
```

## 📤 Create Character (cURL)

```bash
curl -X POST "http://localhost:8000/api/create-character-from-image" \
  -F "image=@character.png" \
  -F "character_name=Hero Knight"
```

## 📤 Create Character (Python)

```python
import requests

with open("character.png", "rb") as f:
    response = requests.post(
        "http://localhost:8000/api/create-character-from-image",
        files={"image": f},
        data={"character_name": "Hero Knight"}
    )
    
result = response.json()
print(f"Character ID: {result['character_id']}")
print(f"Image URL: {result['image_url']}")
```

## 📋 What You Get

```json
{
  "success": true,
  "character_id": "507f...",
  "character_name": "Hero Knight",
  "image_url": "https://res.cloudinary.com/.../hero_knight.png",
  "character_data": {
    "characters_roster": [{
      "name": "Hero Knight",
      "physical_appearance": { /* detailed */ },
      "clothing_style": { /* detailed */ },
      "personality": "brave, determined",
      "video_prompt_description": "Complete description..."
    }]
  }
}
```

## 🎯 Use in Video Generation

```python
# Get character
character = requests.get(
    f"http://localhost:8000/api/characters/{character_id}"
).json()

# Use in story generation
response = requests.post(
    "http://localhost:8000/api/generate-prompt-based-story",
    json={
        "idea": "A knight's adventure",
        "custom_character_roster": character["character"]["character_data"]["characters_roster"]
    }
)
```

## 🔧 Options

```python
data = {
    "character_name": "Hero Knight",
    "remove_background": "true",      # Remove background (default: true)
    "upload_to_cloudinary": "true"    # Upload to cloud (default: true)
}
```

## ✅ Done!

Your character is now:
- ✅ Analyzed by AI
- ✅ Background removed
- ✅ Stored in Cloudinary
- ✅ Saved in MongoDB
- ✅ Ready for video generation

See `CHARACTER_IMAGE_CREATION_GUIDE.md` for full documentation.
