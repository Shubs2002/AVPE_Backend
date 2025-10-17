# Character Creation from Image - Complete Guide

## 🎭 Overview

This feature allows you to create complete character profiles from uploaded images using AI analysis, background removal, and cloud storage.

## 🚀 Pipeline Steps

1. **🔍 AI Analysis** - Gemini analyzes the image for ultra-detailed character description
2. **🎨 Background Removal** - Removes background using rembg for clean character image
3. **☁️ Cloudinary Upload** - Uploads processed image and gets public URL
4. **💾 MongoDB Storage** - Saves character data + image URL to database

## 📋 Prerequisites

### 1. Install Dependencies

```bash
pip install cloudinary rembg
```

Or update your dependencies:
```bash
pip install -r requirements.txt
```

### 2. Configure Cloudinary

Add these to your `.env.dev` file:

```env
# Cloudinary Configuration
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
```

**How to get Cloudinary credentials:**
1. Sign up at https://cloudinary.com (free tier available)
2. Go to Dashboard
3. Copy Cloud Name, API Key, and API Secret

### 3. Ensure MongoDB is Running

Make sure your MongoDB connection is configured in `.env.dev`:

```env
MONGODB_URI=mongodb+srv://...
MONGODB_DATABASE=avpe_dev
```

## 🎯 API Endpoint

### POST `/api/create-character-from-image`

Creates a complete character from an uploaded image.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`

**Parameters:**
- `image` (file, required) - Character image file (JPG, PNG, WEBP, max 10MB)
- `character_name` (string, required) - Name for the character
- `remove_background` (boolean, optional) - Remove image background (default: true)
- `upload_to_cloudinary` (boolean, optional) - Upload to Cloudinary (default: true)

**Example Request (cURL):**

```bash
curl -X POST "http://localhost:8000/api/create-character-from-image" \
  -F "image=@/path/to/character.png" \
  -F "character_name=Hero Knight" \
  -F "remove_background=true" \
  -F "upload_to_cloudinary=true"
```

**Example Request (Python):**

```python
import requests

url = "http://localhost:8000/api/create-character-from-image"

with open("character.png", "rb") as image_file:
    files = {"image": image_file}
    data = {
        "character_name": "Hero Knight",
        "remove_background": "true",
        "upload_to_cloudinary": "true"
    }
    
    response = requests.post(url, files=files, data=data)
    result = response.json()
    
    if result["success"]:
        print(f"Character created: {result['character_id']}")
        print(f"Image URL: {result['image_url']}")
```

**Example Response:**

```json
{
  "success": true,
  "character_id": "507f1f77bcf86cd799439011",
  "character_name": "Hero Knight",
  "image_url": "https://res.cloudinary.com/your-cloud/image/upload/v1234567890/characters/hero_knight.png",
  "cloudinary_public_id": "characters/hero_knight",
  "character_data": {
    "characters_roster": [
      {
        "name": "Hero Knight",
        "physical_appearance": {
          "gender": "male",
          "estimated_age": "28 years old",
          "height": "6'2\" / 188cm",
          "body_type": "muscular athletic",
          "skin_details": {
            "skin_tone": "fair with warm undertones",
            ...
          },
          "face_structure": {...},
          "hair_details": {...}
        },
        "clothing_style": {...},
        "personality": "brave, determined, protective",
        "role": "protagonist",
        "video_prompt_description": "A tall, muscular male knight..."
      }
    ]
  },
  "created_at": "2025-10-14T12:00:00Z"
}
```

## 🧪 Testing

### Using the Test Script

1. Update the test script with your image path:

```python
# In test_create_character_from_image.py
image_path = "path/to/your/character.png"
character_name = "My Character"

# Uncomment the test you want to run
test_create_character_from_image(image_path, character_name)
```

2. Run the test:

```bash
python test_create_character_from_image.py
```

### Using Postman/Thunder Client

1. Create a new POST request to `http://localhost:8000/api/create-character-from-image`
2. Set Body type to `form-data`
3. Add fields:
   - `image` (File) - Select your character image
   - `character_name` (Text) - Enter character name
   - `remove_background` (Text) - `true` or `false`
   - `upload_to_cloudinary` (Text) - `true` or `false`
4. Send the request

## 📊 What Gets Stored in MongoDB

```javascript
{
  "_id": ObjectId("507f1f77bcf86cd799439011"),
  "character_name": "Hero Knight",
  "character_data": {
    "characters_roster": [
      {
        "name": "Hero Knight",
        "physical_appearance": { /* ultra-detailed */ },
        "clothing_style": { /* complete outfit details */ },
        "personality": "brave, determined, protective",
        "role": "protagonist",
        "voice_mannerisms": { /* speaking style */ },
        "video_prompt_description": "Complete description for video generation"
      }
    ]
  },
  "image_url": "https://res.cloudinary.com/.../hero_knight.png",
  "cloudinary_public_id": "characters/hero_knight",
  "created_at": ISODate("2025-10-14T12:00:00Z"),
  "updated_at": ISODate("2025-10-14T12:00:00Z"),
  "version": "1.0"
}
```

## 🎨 Using the Character in Video Generation

Once created, you can use the character in video generation:

```python
# Get character from MongoDB
character = get_character_by_id("507f1f77bcf86cd799439011")

# Use in video generation
payload = {
    "idea": "A knight's adventure",
    "custom_character_roster": character["character_data"]["characters_roster"],
    "segments": 7
}

# The character's image_url can be used as keyframe
keyframe_uri = character["image_url"]
```

## 🔧 Troubleshooting

### Background Removal Fails

If background removal fails, the system will continue with the original image:

```
⚠️ Background removal failed: [error message]
⚠️ Continuing with original image...
```

### Cloudinary Upload Fails

If Cloudinary upload fails, the character will still be saved without the image URL:

```
⚠️ Cloudinary upload failed: [error message]
⚠️ Continuing without image URL...
```

### Gemini Analysis Fails

If Gemini analysis fails, check:
1. GOOGLE_STUDIO_API_KEY is set in .env.dev
2. Image is valid and not corrupted
3. Image size is under 10MB

## 💡 Best Practices

1. **Image Quality**: Use high-quality images (at least 512x512px)
2. **Single Character**: Ensure only one character is in the image
3. **Clear Background**: Images with simple backgrounds work best for removal
4. **Proper Lighting**: Well-lit images produce better AI analysis
5. **Character Name**: Use descriptive names for easy identification

## 🔄 Workflow Example

```
1. User uploads character image
   ↓
2. Gemini analyzes image
   → Extracts detailed physical appearance
   → Identifies clothing and style
   → Infers personality traits
   ↓
3. Background removal (optional)
   → Creates clean PNG with transparency
   ↓
4. Cloudinary upload (optional)
   → Gets public URL for image
   ↓
5. MongoDB storage
   → Saves character data + image URL
   ↓
6. Character ready for video generation!
```

## 📚 Related Endpoints

- `GET /api/characters` - List all characters
- `GET /api/characters/{character_id}` - Get specific character
- `PUT /api/characters/{character_id}` - Update character
- `DELETE /api/characters/{character_id}` - Delete character
- `POST /api/characters/search` - Search characters

## 🎉 Success!

You now have a complete character creation pipeline that:
- ✅ Analyzes images with AI
- ✅ Removes backgrounds automatically
- ✅ Stores images in the cloud
- ✅ Saves detailed character data
- ✅ Ready for video generation

Happy character creating! 🎭
