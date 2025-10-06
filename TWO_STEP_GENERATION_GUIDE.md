# Two-Step Generation Mechanism

## Problem Solved

The original routes (`/generate-movie-auto`, `/generate-prompt-based-story`, `/generate-meme-segments`, `/generate-free-content`) were experiencing **response truncation** due to detailed character narrator information being too large for a single response.

## Solution

Implemented a **two-step generation mechanism** that separates:

1. **Step 1**: Generate metadata and character details (without segments)
2. **Step 2**: Generate segments sequentially in small batches using the metadata

This prevents truncation and allows for **automatic sequential generation**.

---

## New Endpoints

### 🎬 Movie Generation

#### Step 1: Generate Movie Metadata
```http
POST /generate-movie-metadata
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
  "metadata": {
    "title": "Temporal Guardians",
    "short_summary": "...",
    "description": "...",
    "hashtags": ["#scifi", "#timetravel"],
    "narrator_voice": "...",
    "characters_roster": [
      {
        "id": "char_001",
        "name": "Alex Chen",
        "physical_appearance": {...},
        "personality": {...},
        "voice_characteristics": {...}
      }
    ],
    "story_outline": ["Plot point 1", "Plot point 2", ...],
    "generation_info": {
      "total_segments": 50,
      "generated_at": "2024-01-01T12:00:00",
      "idea": "...",
      "no_narration": false,
      "narration_only_first": false,
      "adult_story": false
    }
  }
}
```

#### Step 2: Generate Movie Segments
```http
POST /generate-movie-segments
```

**Request:**
```json
{
  "metadata": { /* metadata from step 1 */ },
  "set_number": 1,
  "segments_per_set": 10,
  "save_to_files": true,
  "output_directory": "generated_movie_script"
}
```

**Response:**
```json
{
  "segments": {
    "success": true,
    "set_number": 1,
    "segments_count": 10,
    "story_set": {
      "title": "Temporal Guardians",
      "segments": [
        {
          "segment_number": 1,
          "title": "The Discovery",
          "narration": "...",
          "dialogue": [...]
        }
      ]
    },
    "next_set_number": 2,
    "is_complete": false
  }
}
```

### 📖 Story Generation

#### Step 1: Generate Story Metadata
```http
POST /generate-story-metadata
```

#### Step 2: Generate Story Segments
```http
POST /generate-story-segments-from-metadata
```

### 😂 Meme Generation

#### Step 1: Generate Meme Metadata
```http
POST /generate-meme-metadata
```

#### Step 2: Generate Meme Segments
```http
POST /generate-meme-segments-from-metadata
```

### 🎯 Free Content Generation

#### Step 1: Generate Free Content Metadata
```http
POST /generate-free-content-metadata
```

#### Step 2: Generate Free Content Segments
```http
POST /generate-free-content-segments-from-metadata
```

---

## Usage Workflow

### Automatic Sequential Generation

```javascript
// Step 1: Generate metadata
const metadataResponse = await fetch('/generate-movie-metadata', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    idea: "Your movie idea",
    total_segments: 50
  })
});

const { metadata } = await metadataResponse.json();

// Step 2: Generate all segments sequentially
const allSegments = [];
let setNumber = 1;
let isComplete = false;

while (!isComplete) {
  const segmentsResponse = await fetch('/generate-movie-segments', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      metadata: metadata,
      set_number: setNumber,
      segments_per_set: 10,
      save_to_files: true
    })
  });
  
  const { segments } = await segmentsResponse.json();
  
  allSegments.push(...segments.story_set.segments);
  
  isComplete = segments.is_complete;
  setNumber = segments.next_set_number;
  
  // Optional: Add delay to avoid rate limits
  await new Promise(resolve => setTimeout(resolve, 1000));
}

console.log(`Generated ${allSegments.length} segments total`);
```

### Manual Step-by-Step Generation

```javascript
// Generate metadata once
const metadata = await generateMetadata();

// Generate segments in batches as needed
const batch1 = await generateSegments(metadata, 1); // Segments 1-10
const batch2 = await generateSegments(metadata, 2); // Segments 11-20
const batch3 = await generateSegments(metadata, 3); // Segments 21-30
```

---

## Benefits

### ✅ Solves Truncation Issues
- **Before**: Large responses with detailed characters got truncated
- **After**: Small, manageable responses that never truncate

### ✅ Sequential Generation
- Generate segments automatically one batch at a time
- Each batch uses consistent metadata and character details
- No loss of character information between batches

### ✅ Better Control
- Generate only the segments you need
- Resume generation from any point
- Adjust batch sizes based on your needs

### ✅ File Management
- Each set is saved to a separate JSON file
- Easy to manage and process individual sets
- Metadata is preserved across all sets

### ✅ Consistent Characters
- Character details are generated once in metadata
- All segments use the same character information
- No character inconsistencies between batches

---

## Migration Guide

### Old Way (Single Request)
```javascript
// This could truncate with detailed characters
const response = await fetch('/generate-movie-auto', {
  method: 'POST',
  body: JSON.stringify({
    idea: "Movie idea",
    total_segments: 100
  })
});
```

### New Way (Two Steps)
```javascript
// Step 1: Get metadata (never truncates)
const metadata = await fetch('/generate-movie-metadata', {
  method: 'POST',
  body: JSON.stringify({
    idea: "Movie idea",
    total_segments: 100
  })
});

// Step 2: Generate segments in batches (never truncates)
for (let set = 1; set <= 10; set++) {
  const segments = await fetch('/generate-movie-segments', {
    method: 'POST',
    body: JSON.stringify({
      metadata: metadata,
      set_number: set,
      segments_per_set: 10
    })
  });
}
```

---

## Configuration

### Batch Sizes
- **Movies**: 10 segments per set (recommended)
- **Stories**: 5 segments per batch (recommended)
- **Memes**: 5 segments per batch (recommended)
- **Free Content**: 5 segments per batch (recommended)

### Token Allocation
- **Free Models**: Fixed 2000 tokens per batch
- **Paid Models**: Dynamic allocation based on batch size
- **Maximum**: 32,000 tokens per request

### File Output
- Each set saved as: `{title}_set_{number:02d}.json`
- Metadata saved as: `{title}_metadata.json`
- Default directory: `generated_movie_script/`

---

## Error Handling

### Retry Logic
```javascript
async function generateSegmentsWithRetry(metadata, setNumber, maxRetries = 3) {
  for (let attempt = 1; attempt <= maxRetries; attempt++) {
    try {
      return await generateSegments(metadata, setNumber);
    } catch (error) {
      if (attempt === maxRetries) throw error;
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  }
}
```

### Validation
- Metadata is validated before segment generation
- Segment counts are verified after generation
- File paths are checked before saving

---

## Testing

Run the test script to verify the implementation:

```bash
python test_two_step_generation.py
```

This will test both movie and story generation with the new two-step mechanism.

---

## Backward Compatibility

The original endpoints (`/generate-movie-auto`, `/generate-prompt-based-story`, etc.) are still available and unchanged. The new two-step endpoints are additional options to solve the truncation issue.

Choose the approach that works best for your use case:
- **Original endpoints**: For smaller content or when truncation isn't an issue
- **Two-step endpoints**: For detailed characters or large content that might truncate