# 🚀 Character CRUD - Quick Reference

## API Endpoints Summary

```
CREATE:  POST   /analyze-character-image-file
CREATE:  POST   /analyze-multiple-character-images-files
READ:    GET    /characters
READ:    GET    /characters/{filename}
SEARCH:  POST   /characters/search
UPDATE:  PUT    /characters/{filename}
DELETE:  DELETE /characters/{filename}
```

## Quick Examples

### 📝 Create (Analyze & Save)
```bash
curl -X POST "http://localhost:8000/analyze-character-image-file" \
  -F "image=@hero.jpg" \
  -F "character_name=Hero" \
  -F "save_character=true"
```

### 📖 Read All
```bash
curl -X GET "http://localhost:8000/characters"
```

### 📖 Read One
```bash
curl -X GET "http://localhost:8000/characters/Hero_20251005_123456.json"
```

### 🔍 Search
```bash
curl -X POST "http://localhost:8000/characters/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "hero", "gender": "male"}'
```

### ✏️ Update
```bash
curl -X PUT "http://localhost:8000/characters/Hero_20251005_123456.json" \
  -H "Content-Type: application/json" \
  -d '{"updated_data": {"name": "Super Hero", "personality": "brave"}}'
```

### 🗑️ Delete
```bash
curl -X DELETE "http://localhost:8000/characters/Hero_20251005_123456.json"
```

## Response Formats

### List All Characters
```json
{
  "success": true,
  "total_characters": 5,
  "characters": [
    {
      "filename": "Hero_20251005_123456.json",
      "character_name": "Hero",
      "saved_at": "2025-10-05T12:34:56"
    }
  ]
}
```

### Get Character
```json
{
  "success": true,
  "character_data": {
    "name": "Hero",
    "physical_appearance": {...},
    "personality": "brave"
  },
  "metadata": {
    "saved_at": "2025-10-05T12:34:56"
  }
}
```

### Update/Delete Success
```json
{
  "success": true,
  "message": "Character updated/deleted successfully"
}
```

## Common Workflows

### 1️⃣ Create Character Library
```bash
# Analyze multiple characters
curl -X POST ".../analyze-multiple-character-images-files" \
  -F "images=@hero.jpg" -F "images=@villain.jpg" \
  -F "character_names=Hero,Villain" \
  -F "save_characters=true"
```

### 2️⃣ Browse Characters
```bash
# List all
curl -X GET ".../characters"

# Search specific
curl -X POST ".../characters/search" \
  -d '{"query": "hero"}'
```

### 3️⃣ Use in Story
```bash
# Get character
CHARACTER=$(curl -s ".../characters/Hero_20251005_123456.json")

# Generate story with character
curl -X POST ".../generate-prompt-based-story" \
  -d '{
    "idea": "Adventure",
    "custom_character_roster": ['"$(echo $CHARACTER | jq '.character_data')"']
  }'
```

### 4️⃣ Manage Characters
```bash
# Update
curl -X PUT ".../characters/Hero_20251005_123456.json" \
  -d '{"updated_data": {"personality": "brave, wise"}}'

# Delete
curl -X DELETE ".../characters/Hero_20251005_123456.json"
```

## Search Filters

| Filter | Type | Example |
|--------|------|---------|
| query | string | "captain" |
| gender | string | "male" / "female" |
| age_range | string | "25-30" / "30-35" |

## Tips

✅ **Do:**
- Save characters with descriptive names
- Use search to find characters quickly
- Update characters to refine details
- Back up important characters

❌ **Don't:**
- Use special characters in names
- Delete without confirmation
- Update without checking current data
- Forget to save after analysis

## File Naming

Characters are saved as:
```
{character_name}_{timestamp}.json
```

Example:
```
Captain_Thunder_20251005_123456.json
```

## Integration

### Python
```python
import requests

# Get character
response = requests.get("http://localhost:8000/characters/Hero_20251005_123456.json")
character = response.json()['character_data']

# Use in story
requests.post("http://localhost:8000/generate-prompt-based-story", json={
    "idea": "Adventure",
    "custom_character_roster": [character]
})
```

### JavaScript
```javascript
// Get character
const response = await fetch('http://localhost:8000/characters/Hero_20251005_123456.json');
const { character_data } = await response.json();

// Use in story
await fetch('http://localhost:8000/generate-prompt-based-story', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    idea: 'Adventure',
    custom_character_roster: [character_data]
  })
});
```

---

**Quick Reference Version:** 1.0  
**For Full Documentation:** See CHARACTER_CRUD_API_DOCUMENTATION.md
