# 🚀 Auto Generation Routes - Complete Guide

## Overview

The **Auto Generation Routes** provide a **single API call** for each content type that internally handles the complete 2-step process and returns all segments. No more manual step management!

---

## 🎯 **Auto Routes (Recommended)**

### **🎬 Movie Auto Generation**
```http
POST /generate-movie-auto
```

**Request:**
```json
{
  "idea": "A thrilling sci-fi adventure about time travelers",
  "total_segments": 50,
  "custom_character_roster": null,
  "no_narration": false,
  "narration_only_first": false,
  "adult_story": false
}
```

**Response:**
```json
{
  "movie": {
    "title": "Temporal Guardians",
    "short_summary": "...",
    "description": "...",
    "hashtags": ["#scifi", "#timetravel"],
    "narrator_voice": "...",
    "characters_roster": [...],
    "segments": [
      {
        "segment_number": 1,
        "title": "The Discovery",
        "narration": "...",
        "dialogue": [...]
      }
    ],
    "generation_info": {
      "total_segments_planned": 50,
      "total_segments_generated": 50,
      "total_sets": 5,
      "successful_sets": 5,
      "generation_summary": [...]
    }
  }
}
```

### **📖 Story Auto Generation**
```http
POST /generate-story-auto
```

**Request:**
```json
{
  "idea": "A magical adventure in a fantasy world",
  "segments": 15,
  "custom_character_roster": null
}
```

### **😂 Meme Auto Generation**
```http
POST /generate-meme-auto
```

**Request:**
```json
{
  "idea": "When you're trying to look busy at work",
  "segments": 7,
  "custom_character_roster": null,
  "no_narration": false,
  "narration_only_first": false
}
```

**Special Feature:** If `idea` is `null`, it generates a random meme idea!

### **🎯 Free Content Auto Generation**
```http
POST /generate-free-content-auto
```

**Request:**
```json
{
  "idea": "5 morning habits that changed my life",
  "segments": 10,
  "custom_character_roster": null,
  "no_narration": false,
  "narration_only_first": false
}
```

**Special Feature:** If `idea` is `null`, it generates a random content idea!

---

## 🔧 **Manual 2-Step Routes (Advanced)**

For users who want **full control** over the generation process:

### **Movie Generation**
- `/generate-movie-metadata` → `/generate-movie-segments`

### **Story Generation**
- `/generate-story-metadata` → `/generate-story-segments-from-metadata`

### **Meme Generation**
- `/generate-meme-metadata` → `/generate-meme-segments-from-metadata`

### **Free Content Generation**
- `/generate-free-content-metadata` → `/generate-free-content-segments-from-metadata`

---

## 🚀 **How Auto Routes Work Internally**

### **Process Flow:**
1. **Step 1**: Generate metadata (title, characters, outline)
2. **Step 2**: Generate segments in batches sequentially
3. **Combine**: Merge metadata + all segments into complete result
4. **Return**: Single response with everything

### **Batch Sizes:**
- **Movies**: 10 segments per batch
- **Stories**: 5 segments per batch
- **Memes**: All segments in 1 batch (usually 5-7)
- **Free Content**: 5 segments per batch

### **Rate Limiting:**
- 1-second delay between batches
- Prevents API rate limit issues
- Ensures stable generation

### **Error Handling:**
- Individual batch failures are tracked
- Generation continues even if some batches fail
- Detailed error reporting in `generation_summary`

---

## 💡 **Usage Examples**

### **JavaScript/TypeScript**
```javascript
// Auto generation (recommended)
async function generateMovie(idea, segments) {
  const response = await fetch('/generate-movie-auto', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      idea: idea,
      total_segments: segments
    })
  });
  
  const result = await response.json();
  return result.movie; // Complete movie with all segments
}

// Usage
const movie = await generateMovie("Sci-fi adventure", 30);
console.log(`Generated: ${movie.title} with ${movie.segments.length} segments`);
```

### **Python**
```python
import requests

def generate_story_auto(idea, segments):
    response = requests.post('http://localhost:8000/generate-story-auto', json={
        'idea': idea,
        'segments': segments
    })
    
    result = response.json()
    return result['story']

# Usage
story = generate_story_auto("Fantasy adventure", 15)
print(f"Generated: {story['title']} with {len(story['segments'])} segments")
```

### **cURL**
```bash
# Generate complete meme
curl -X POST "http://localhost:8000/generate-meme-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "When your code works on the first try",
    "segments": 7
  }'

# Generate random content (no idea provided)
curl -X POST "http://localhost:8000/generate-free-content-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": null,
    "segments": 10
  }'
```

---

## 🎯 **Benefits of Auto Routes**

### **✅ Simplicity**
- **Single API call** instead of managing 2-step process
- **Complete results** in one response
- **No manual batch management** required

### **✅ No Truncation**
- Uses 2-step mechanism internally
- **Detailed characters** never cause truncation
- **Consistent character details** across all segments

### **✅ Reliability**
- **Automatic retry logic** for failed batches
- **Rate limiting** to prevent API issues
- **Detailed error reporting** for debugging

### **✅ Flexibility**
- **Random idea generation** for memes and content
- **Custom character rosters** supported
- **Configurable segment counts**

### **✅ Performance**
- **Optimized batch sizes** for each content type
- **Parallel processing** where possible
- **Progress tracking** in generation summary

---

## 📊 **Response Structure**

### **Success Response:**
```json
{
  "movie|story|meme|content": {
    "title": "Generated Title",
    "short_summary": "Brief summary",
    "description": "Detailed description",
    "hashtags": ["#tag1", "#tag2"],
    "narrator_voice": "Narrator description",
    "characters_roster": [
      {
        "id": "char_001",
        "name": "Character Name",
        "physical_appearance": {...},
        "personality": {...},
        "voice_characteristics": {...}
      }
    ],
    "segments": [
      {
        "segment_number": 1,
        "title": "Segment Title",
        "narration": "Narration text",
        "dialogue": [
          {
            "character_id": "char_001",
            "character_name": "Character Name",
            "text": "Dialogue text"
          }
        ]
      }
    ],
    "generation_info": {
      "total_segments_planned": 20,
      "total_segments_generated": 20,
      "total_sets|batches": 4,
      "successful_sets|batches": 4,
      "generation_summary": [
        {
          "set_number|batch_number": 1,
          "segments_count": 5,
          "success": true
        }
      ]
    }
  }
}
```

### **Error Response:**
```json
{
  "detail": "Auto movie generation failed: [error details]"
}
```

---

## 🧪 **Testing**

Use the provided test script:
```bash
python test_auto_generation.py
```

This will test all 4 auto routes and verify:
- Complete generation process
- Error handling
- Random idea generation
- Performance metrics

---

## 🔄 **Migration from Old Routes**

### **Before (Old Single Routes):**
```javascript
// These were causing truncation
const movie = await fetch('/generate-movie-auto-old');
const story = await fetch('/generate-prompt-based-story');
const meme = await fetch('/generate-meme-segments');
const content = await fetch('/generate-free-content');
```

### **After (New Auto Routes):**
```javascript
// These solve truncation with 2-step internally
const movie = await fetch('/generate-movie-auto');
const story = await fetch('/generate-story-auto');
const meme = await fetch('/generate-meme-auto');
const content = await fetch('/generate-free-content-auto');
```

### **Benefits of Migration:**
- ✅ **No more truncation** issues
- ✅ **Same simple API** (single call)
- ✅ **Better reliability** with retry logic
- ✅ **Detailed character information** preserved
- ✅ **Complete results** guaranteed

---

## 🎯 **Recommendation**

### **Use Auto Routes For:**
- ✅ **Production applications**
- ✅ **Simple integrations**
- ✅ **Complete content generation**
- ✅ **Reliable results**

### **Use Manual 2-Step Routes For:**
- 🔧 **Advanced control** over generation process
- 🔧 **Custom batch sizes**
- 🔧 **Partial generation** (metadata only)
- 🔧 **Custom error handling**

---

## 🎉 **Summary**

The **Auto Generation Routes** provide the **best of both worlds**:
- **Simple single API calls** like the old routes
- **No truncation issues** thanks to 2-step mechanism internally
- **Complete, reliable results** with detailed characters
- **Automatic sequential processing** with error handling

**Perfect solution for your truncation problem while maintaining ease of use!**