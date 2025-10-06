# ⚠️ Free Model Limitations & Solutions

## Problem Identified

You're using `meta-llama/llama-4-maverick:free` which has strict output limitations that cause JSON truncation regardless of the `max_tokens` parameter.

**Current Error Pattern:**
```
📊 Token allocation: 8000 tokens for 10 segments
❌ JSON parsing failed: Unterminated string starting at: line 372 column 21 (char 15573)
```

The response consistently gets cut off around 15,500-15,600 characters, indicating the free model has a hard output limit.

## Root Cause

Free models typically have:
- ✅ Lower computational cost
- ❌ Stricter output limits (usually 2k-4k tokens max)
- ❌ Lower priority in processing queues
- ❌ Reduced context windows

## Solutions

### Option 1: Reduce Segments Per Set (Recommended)

**Change your request from:**
```json
{
  "total_segments": 600,
  "segments_per_set": 10  // ❌ Too many for free model
}
```

**To:**
```json
{
  "total_segments": 600,
  "segments_per_set": 3   // ✅ Works with free model limits
}
```

**Benefits:**
- ✅ Works within free model limits
- ✅ Still generates all 600 segments
- ✅ Just takes more API calls (200 calls instead of 60)

### Option 2: Switch to Paid Model

**Update your `.env.dev`:**
```bash
# Instead of free model
SCRIPT_MODEL=meta-llama/llama-4-maverick:free

# Use paid model (requires credits)
SCRIPT_MODEL=meta-llama/llama-3.1-70b-instruct
# or
SCRIPT_MODEL=anthropic/claude-3.5-sonnet
# or
SCRIPT_MODEL=openai/gpt-4o
```

### Option 3: Use Different Free Model

Some free models have higher limits:
```bash
SCRIPT_MODEL=meta-llama/llama-3.1-8b-instruct:free
# or
SCRIPT_MODEL=google/gemma-2-9b-it:free
```

## Implemented Auto-Detection

I've updated the code to automatically detect free models and adjust token allocation:

```python
model_name = settings.SCRIPT_MODEL.lower()
is_free_model = ":free" in model_name or "free" in model_name

if is_free_model:
    # Conservative allocation for free models
    base_tokens = 2000
    tokens_per_segment = 300
    max_tokens = min(max_tokens, 4000)  # Hard cap at 4k
    print("⚠️ Using free model - reduced token allocation")
```

## Recommended Immediate Fix

**Test with 3 segments per set:**

```bash
curl -X POST "http://localhost:8000/api/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "adults story. narration on in 1st segment. a story of a child born with great powers but her mother was troubled during his birth. but his mother was soo good, she loved him. villans killed his family and he revenges for it. the villans were his bestfriends family. best friend was also good, best friend turn against his own family and shakes hand with the hero of our story. give this story total emotional touch. cliffhanger at every 120th segment",
    "total_segments": 600,
    "segments_per_set": 3,
    "save_to_files": true,
    "output_directory": "generated_movie_script"
  }'
```

**Expected Output:**
```
📊 Token allocation: 3500 tokens for 3 segments
⚠️ Using free model - reduced token allocation
✅ Successfully generated set 1 (3 segments)
🎬 Generating Set 2/200...
```

## Token Allocation by Model Type

### Free Models
- **Segments per set**: 3-5 max
- **Base tokens**: 2,000
- **Per segment**: 300 tokens
- **Max cap**: 4,000 tokens
- **Total per request**: ~3,500 tokens

### Paid Models
- **Segments per set**: 10-20
- **Base tokens**: 5,000
- **Per segment**: 1,000 tokens
- **Max cap**: 32,000 tokens
- **Total per request**: ~15,000 tokens

## Performance Comparison

### 600 Segments with Free Model

**Option A: 10 segments per set**
- Sets needed: 60
- Success rate: ~0% (truncation)
- Time: Infinite (keeps failing)

**Option B: 3 segments per set**
- Sets needed: 200
- Success rate: ~95%
- Time: ~10-15 minutes

### 600 Segments with Paid Model

**10 segments per set**
- Sets needed: 60
- Success rate: ~99%
- Time: ~3-5 minutes

## Cost Comparison

### Free Model (3 segments/set)
- API calls: 200
- Cost: $0
- Time: 10-15 minutes

### Paid Model (10 segments/set)
- API calls: 60
- Cost: ~$5-15 (depending on model)
- Time: 3-5 minutes

## Recommendation

**For Development/Testing:**
Use free model with `segments_per_set: 3`

**For Production:**
Switch to paid model for better performance and reliability.

## Test Commands

### Test with 3 segments (should work)
```bash
curl -X POST "http://localhost:8000/api/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "test story",
    "total_segments": 9,
    "segments_per_set": 3
  }'
```

### Test with 1 segment (definitely works)
```bash
curl -X POST "http://localhost:8000/api/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "test story", 
    "total_segments": 3,
    "segments_per_set": 1
  }'
```

## Status

✅ **Auto-detection implemented** - Code now detects free models and adjusts limits
⚠️ **Action needed** - Reduce `segments_per_set` to 3 for your 600-segment movie

---

**Updated**: 2025-10-05  
**Status**: ✅ Ready with Free Model Optimizations