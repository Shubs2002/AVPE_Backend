# Fix: Daily Character "Connection Error"

## 🔴 Problem

When calling `/api/generate-daily-character`, you get:
```json
{
  "detail": "Daily character content generation failed: Connection error."
}
```

## ✅ Solution

The issue is with your OpenRouter API connection. Here's how to fix it:

### Quick Fix (2 minutes)

1. **Test the connection:**
   ```bash
   python test_openrouter_connection.py
   ```

2. **If it fails, try a different model:**
   
   Open `.env.dev` and change:
   ```env
   # FROM:
   SCRIPT_MODEL=openai/gpt-oss-20b:free
   
   # TO:
   SCRIPT_MODEL=meta-llama/llama-3.2-3b-instruct:free
   ```

3. **Restart the server:**
   ```bash
   # Stop server (Ctrl+C)
   python -m uvicorn src.main:app --reload
   ```

4. **Test again:**
   ```bash
   curl -X POST "http://localhost:8000/api/generate-daily-character" \
     -H "Content-Type: application/json" \
     -d '{
       "idea": "floof gets shy and turns red",
       "character_name": "Floof",
       "creature_language": "Soft and low-Pitched and mystical",
       "num_segments": 6
     }'
   ```

## 🔍 What Was Fixed

I updated the code to:
1. ✅ Remove `response_format={"type": "json_object"}` (not supported by free models)
2. ✅ Add better error handling and validation
3. ✅ Add detailed error messages
4. ✅ Handle code block wrappers in responses

## 🎯 Why It Happened

The free OpenRouter model (`openai/gpt-oss-20b:free`) has limitations:
- May have rate limits
- May not support structured output
- May have connection issues
- May have quota limits

## 💡 Recommended Models

### Free Models (No Cost)
```env
SCRIPT_MODEL=meta-llama/llama-3.2-3b-instruct:free
SCRIPT_MODEL=google/gemma-2-9b-it:free
SCRIPT_MODEL=mistralai/mistral-7b-instruct:free
```

### Paid Models (Better Quality)
```env
SCRIPT_MODEL=openai/gpt-3.5-turbo  # Cheap & fast
SCRIPT_MODEL=openai/gpt-4          # Best quality
SCRIPT_MODEL=anthropic/claude-3-haiku  # Good balance
```

## 📋 Checklist

- [ ] Run `python test_openrouter_connection.py`
- [ ] Check if API key is valid at https://openrouter.ai/keys
- [ ] Try a different model in `.env.dev`
- [ ] Restart the server
- [ ] Test the endpoint again

## 🆘 Still Not Working?

See `TROUBLESHOOT_OPENROUTER_CONNECTION.md` for detailed troubleshooting steps.

## ✨ Expected Result

After fixing, you should get:

```json
{
  "content": {
    "title": "Shy Floof Moment",
    "character_name": "Floof",
    "creature_language": "Soft and low-Pitched and mystical",
    "segments": [
      {
        "segment": 1,
        "duration": 8,
        "scene": "Floof encounters something that makes them shy",
        "action": "...",
        "creature_sounds": [...]
      },
      ...
    ]
  }
}
```

---

**Quick Test:** `python test_openrouter_connection.py`
