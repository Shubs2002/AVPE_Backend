# 📚 Character CRUD API Documentation

## Overview

Complete CRUD (Create, Read, Update, Delete) operations for managing saved character analyses.

## Endpoints

### 1. Create Character (Already Implemented)

#### Analyze Single Character Image
```http
POST /analyze-character-image-file
Content-Type: multipart/form-data
```

**Parameters:**
- `image` (file): Character image file
- `character_name` (string): Name for the character
- `character_count` (int): Number of characters to detect (default: 1)
- `save_character` (bool): Whether to save the character (default: false)

**Response:**
```json
{
  "character_analysis": {
    "characters_roster": [...]
  },
  "save_result": {
    "success": true,
    "filepath": "saved_characters/hero_20251005_123456.json",
    "filename": "hero_20251005_123456.json",
    "character_name": "hero",
    "saved_at": "2025-10-05T12:34:56.789"
  }
}
```

#### Analyze Multiple Character Images
```http
POST /analyze-multiple-character-images-files
Content-Type: multipart/form-data
```

**Parameters:**
- `images` (files): Multiple character image files
- `character_names` (string): Comma-separated names
- `character_count_per_image` (int): Characters per image (default: 1)
- `save_characters` (bool): Whether to save characters (default: false)

---

### 2. Read Operations

#### Get All Characters
```http
GET /characters
```

**Response:**
```json
{
  "success": true,
  "total_characters": 5,
  "characters": [
    {
      "filename": "hero_20251005_123456.json",
      "filepath": "saved_characters/hero_20251005_123456.json",
      "character_id": "img1_char1",
      "character_name": "Captain Thunder",
      "saved_at": "2025-10-05T12:34:56.789",
      "file_size_bytes": 15234,
      "has_image_data": true
    },
    {
      "filename": "villain_20251005_123457.json",
      "filepath": "saved_characters/villain_20251005_123457.json",
      "character_id": "img1_char1",
      "character_name": "Dr. Evil",
      "saved_at": "2025-10-05T12:34:57.123",
      "file_size_bytes": 14892,
      "has_image_data": true
    }
  ]
}
```

#### Get Character by Filename
```http
GET /characters/{filename}
```

**Example:**
```http
GET /characters/hero_20251005_123456.json
```

**Response:**
```json
{
  "success": true,
  "filename": "hero_20251005_123456.json",
  "filepath": "saved_characters/hero_20251005_123456.json",
  "character_data": {
    "id": "img1_char1",
    "name": "Captain Thunder",
    "physical_appearance": {
      "gender": "male",
      "estimated_age": "32",
      "height": "6'2\"",
      "skin_tone": "bronze tan",
      "hair_color": "jet black",
      ...
    },
    "clothing_style": {...},
    "personality": "brave, selfless, leader",
    "role": "main superhero",
    ...
  },
  "metadata": {
    "saved_at": "2025-10-05T12:34:56.789",
    "character_name": "Captain Thunder",
    "filename": "hero_20251005_123456.json",
    "version": "1.0"
  }
}
```

#### Search Characters
```http
POST /characters/search
Content-Type: application/json
```

**Request Body:**
```json
{
  "query": "captain",
  "gender": "male",
  "age_range": "30-35"
}
```

**Response:**
```json
{
  "success": true,
  "total_results": 2,
  "query": "captain",
  "filters": {
    "gender": "male",
    "age_range": "30-35"
  },
  "characters": [
    {
      "filename": "hero_20251005_123456.json",
      "filepath": "saved_characters/hero_20251005_123456.json",
      "character_id": "img1_char1",
      "character_name": "Captain Thunder",
      "gender": "male",
      "age": "32 years old",
      "saved_at": "2025-10-05T12:34:56.789"
    }
  ]
}
```

---

### 3. Update Operation

#### Update Character
```http
PUT /characters/{filename}
Content-Type: application/json
```

**Example:**
```http
PUT /characters/hero_20251005_123456.json
```

**Request Body:**
```json
{
  "updated_data": {
    "name": "Captain Thunder Updated",
    "personality": "brave, selfless, leader, strategic",
    "role": "main superhero and team leader"
  }
}
```

**Response:**
```json
{
  "success": true,
  "filename": "hero_20251005_123456.json",
  "filepath": "saved_characters/hero_20251005_123456.json",
  "updated_at": "2025-10-05T13:45:23.456",
  "message": "Character updated successfully"
}
```

**Note:** The update merges the `updated_data` with existing character data. You can update any field in the character data.

---

### 4. Delete Operation

#### Delete Character
```http
DELETE /characters/{filename}
```

**Example:**
```http
DELETE /characters/hero_20251005_123456.json
```

**Response:**
```json
{
  "success": true,
  "filename": "hero_20251005_123456.json",
  "message": "Character deleted successfully"
}
```

---

## Usage Examples

### Example 1: Create and Save Character

```bash
# Upload and analyze character image
curl -X POST "http://localhost:8000/analyze-character-image-file" \
  -F "image=@hero.jpg" \
  -F "character_name=Captain Thunder" \
  -F "character_count=1" \
  -F "save_character=true"
```

### Example 2: List All Characters

```bash
curl -X GET "http://localhost:8000/characters"
```

### Example 3: Get Specific Character

```bash
curl -X GET "http://localhost:8000/characters/hero_20251005_123456.json"
```

### Example 4: Search Characters

```bash
curl -X POST "http://localhost:8000/characters/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "captain",
    "gender": "male"
  }'
```

### Example 5: Update Character

```bash
curl -X PUT "http://localhost:8000/characters/hero_20251005_123456.json" \
  -H "Content-Type: application/json" \
  -d '{
    "updated_data": {
      "name": "Captain Thunder Updated",
      "personality": "brave, selfless, leader, strategic"
    }
  }'
```

### Example 6: Delete Character

```bash
curl -X DELETE "http://localhost:8000/characters/hero_20251005_123456.json"
```

---

## Complete Workflow Example

### 1. Analyze and Save Multiple Characters

```bash
# Analyze 3 character images
curl -X POST "http://localhost:8000/analyze-multiple-character-images-files" \
  -F "images=@hero.jpg" \
  -F "images=@sidekick.jpg" \
  -F "images=@villain.jpg" \
  -F "character_names=Captain Thunder,Spark,Dr. Evil" \
  -F "save_characters=true"
```

### 2. List All Saved Characters

```bash
curl -X GET "http://localhost:8000/characters"
```

### 3. Get Specific Character Details

```bash
curl -X GET "http://localhost:8000/characters/Captain_Thunder_20251005_123456.json"
```

### 4. Update Character Information

```bash
curl -X PUT "http://localhost:8000/characters/Captain_Thunder_20251005_123456.json" \
  -H "Content-Type: application/json" \
  -d '{
    "updated_data": {
      "personality": "brave, selfless, leader, strategic thinker",
      "role": "main superhero and team leader"
    }
  }'
```

### 5. Search for Characters

```bash
curl -X POST "http://localhost:8000/characters/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "captain",
    "gender": "male"
  }'
```

### 6. Use Character in Story Generation

```bash
# First, get the character
CHARACTER=$(curl -s -X GET "http://localhost:8000/characters/Captain_Thunder_20251005_123456.json")

# Extract character_data and use in story generation
curl -X POST "http://localhost:8000/generate-prompt-based-story" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A superhero saves the city",
    "segments": 10,
    "custom_character_roster": ['"$(echo $CHARACTER | jq '.character_data')"']
  }'
```

---

## Error Responses

### 404 Not Found
```json
{
  "detail": "Character file not found: hero_20251005_123456.json"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Failed to update character: [error details]"
}
```

---

## Character Data Structure

### Saved Character File Format

```json
{
  "character_data": {
    "id": "img1_char1",
    "name": "Captain Thunder",
    "confidence_score": 0.95,
    "position_in_image": "center",
    "physical_appearance": {
      "gender": "male",
      "estimated_age": "32 years old",
      "height": "6'2\" / 188cm",
      "body_type": "muscular athletic",
      "skin_details": {...},
      "face_structure": {...},
      "hair_details": {...},
      ...
    },
    "clothing_style": {
      "primary_outfit": {...},
      "clothing_details": {...},
      "accessories": {...}
    },
    "personality": "brave, selfless, leader",
    "role": "main superhero",
    "voice_mannerisms": {...},
    "video_prompt_description": "...",
    "source_image": 1,
    "source_description": "Captain Thunder"
  },
  "metadata": {
    "saved_at": "2025-10-05T12:34:56.789",
    "updated_at": "2025-10-05T13:45:23.456",
    "character_name": "Captain Thunder",
    "filename": "hero_20251005_123456.json",
    "version": "1.0"
  }
}
```

---

## Search Filters

### Available Filters

1. **query** (string): Search in character name
2. **gender** (string): Filter by gender (male/female/non-binary)
3. **age_range** (string): Filter by age range (e.g., "25-30", "30-35")

### Search Examples

**Search by name:**
```json
{
  "query": "captain"
}
```

**Search by gender:**
```json
{
  "gender": "male"
}
```

**Search by age range:**
```json
{
  "age_range": "30-35"
}
```

**Combined search:**
```json
{
  "query": "captain",
  "gender": "male",
  "age_range": "30-35"
}
```

---

## Best Practices

### 1. Naming Characters
- Use descriptive names
- Avoid special characters
- Keep names under 50 characters

### 2. Updating Characters
- Only update fields that need changes
- Preserve original analysis data when possible
- Add custom fields as needed

### 3. Searching Characters
- Use specific queries for better results
- Combine filters for precise searches
- Handle empty results gracefully

### 4. Deleting Characters
- Confirm before deletion (no undo)
- Consider archiving instead of deleting
- Keep backups of important characters

---

## Integration with Content Generation

### Using Saved Characters in Stories

```python
# 1. Get saved character
response = requests.get("http://localhost:8000/characters/hero_20251005_123456.json")
character = response.json()['character_data']

# 2. Use in story generation
story_request = {
    "idea": "A superhero adventure",
    "segments": 10,
    "custom_character_roster": [character]
}

story_response = requests.post(
    "http://localhost:8000/generate-prompt-based-story",
    json=story_request
)
```

---

## Summary

| Operation | Endpoint | Method | Description |
|-----------|----------|--------|-------------|
| **Create** | `/analyze-character-image-file` | POST | Analyze and save single character |
| **Create** | `/analyze-multiple-character-images-files` | POST | Analyze and save multiple characters |
| **Read** | `/characters` | GET | List all saved characters |
| **Read** | `/characters/{filename}` | GET | Get specific character |
| **Read** | `/characters/search` | POST | Search characters |
| **Update** | `/characters/{filename}` | PUT | Update character data |
| **Delete** | `/characters/{filename}` | DELETE | Delete character |

---

**API Version:** 1.0  
**Last Updated:** 2025-10-05  
**Status:** ✅ Production Ready
