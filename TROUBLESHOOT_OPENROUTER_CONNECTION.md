# Troubleshooting OpenRouter Connection Error

## 🔴 Error: "Connection error"

When you see this error on `/api/generate-daily-character`, it means the OpenRouter API connection failed.

## 🔍 Diagnosis Steps

### Step 1: Test the Connection

Run the test script:

```bash
python test_openrouter_connection.py
```

This will tell you exactly what's wrong.

### Step 2: Check Your Configuration

Open `.env.dev` and verify:

```env
OpenAI_API_KEY=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
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
SCRIPT_MODEL=openai/gpt-oss-20b:free
```

### Step 3: Verify API Key

1. Go to: https://openrouter.ai/keys
2. Check if your API key is valid
3. Check if you have credits/quota remaining
4. Free models may have rate limits

## 🔧 Common Issues & Solutions

### Issue 1: Invalid API Key

**Symptoms:**
- "401 Unauthorized" error
- "Invalid API key" message

**Solution:**
1. Get a new API key from https://openrouter.ai/keys
2. Update `.env.dev` with the new key
3. Restart the server

### Issue 2: Rate Limit Exceeded

**Symptoms:**
- "429 Too Many Requests" error
- "Rate limit exceeded" message

**Solution:**
1. Wait a few minutes before trying again
2. Free models have strict rate limits
3. Consider upgrading to a paid model
4. Use a different model (see below)

### Issue 3: Model Not Available

**Symptoms:**
- "404 Not Found" error
- "Model not available" message

**Solution:**
1. Check available models at: https://openrouter.ai/models
2. Try a different model (see alternatives below)
3. Update `SCRIPT_MODEL` in `.env.dev`

### Issue 4: Network/Connection Issues

**Symptoms:**
- "Connection error" message
- Timeout errors
- "Failed to connect" message

**Solution:**
1. Check your internet connection
2. Check if OpenRouter is down: https://status.openrouter.ai/
3. Try disabling VPN/proxy
4. Check firewall settings

### Issue 5: Free Model Quota Exhausted

**Symptoms:**
- Works initially, then stops
- "Quota exceeded" message
- "Insufficient credits" message

**Solution:**
1. Wait for quota to reset (usually daily)
2. Switch to a different free model
3. Add credits to your OpenRouter account
4. Use a paid model

## 🔄 Alternative Models

If `openai/gpt-oss-20b:free` is not working, try these alternatives:

### Free Models

Update `SCRIPT_MODEL` in `.env.dev` to one of these:

```env
# Option 1: Meta Llama (Free)
SCRIPT_MODEL=meta-llama/llama-3.2-3b-instruct:free

# Option 2: Google Gemma (Free)
SCRIPT_MODEL=google/gemma-2-9b-it:free

# Option 3: Mistral (Free)
SCRIPT_MODEL=mistralai/mistral-7b-instruct:free

# Option 4: Qwen (Free)
SCRIPT_MODEL=qwen/qwen-2-7b-instruct:free
```

### Paid Models (Better Quality)

```env
# Option 1: GPT-3.5 Turbo (Cheap, Fast)
SCRIPT_MODEL=openai/gpt-3.5-turbo

# Option 2: GPT-4 (Best Quality)
SCRIPT_MODEL=openai/gpt-4

# Option 3: Claude 3 Haiku (Fast, Good)
SCRIPT_MODEL=anthropic/claude-3-haiku

# Option 4: Gemini Pro (Good Balance)
SCRIPT_MODEL=google/gemini-pro
```

## 🧪 Testing After Changes

After making changes:

1. **Restart the server:**
   ```bash
   # Stop the server (Ctrl+C)
   # Start again
   python -m uvicorn src.main:app --reload
   ```

2. **Test the connection:**
   ```bash
   python test_openrouter_connection.py
   ```

3. **Test the endpoint:**
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

## 💡 Quick Fix

If you need it working RIGHT NOW:

1. **Get a new API key:**
   - Go to: https://openrouter.ai/keys
   - Create a new key
   - Copy it

2. **Update `.env.dev`:**
   ```env
   OpenAI_API_KEY=your_new_key_here
   ```

3. **Try a different model:**
   ```env
   SCRIPT_MODEL=meta-llama/llama-3.2-3b-instruct:free
   ```

4. **Restart server:**
   ```bash
   python -m uvicorn src.main:app --reload
   ```

## 📊 Check OpenRouter Status

Before troubleshooting, check if OpenRouter is having issues:

- Status Page: https://status.openrouter.ai/
- Twitter: https://twitter.com/OpenRouterAI
- Discord: https://discord.gg/openrouter

## 🆘 Still Not Working?

If none of the above works:

1. **Check the server logs** for detailed error messages
2. **Run the test script** and share the output
3. **Verify your OpenRouter account** has credits
4. **Try a completely different model**
5. **Check if your IP is blocked** (rare, but possible)

## 📝 Example Working Configuration

Here's a configuration that should work:

```env
# .env.dev
OpenAI_API_KEY=sk-or-v1-YOUR_ACTUAL_KEY_HERE
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
SCRIPT_MODEL=meta-llama/llama-3.2-3b-instruct:free
```

## 🎯 Expected Behavior

When working correctly, you should see:

```json
{
  "content": {
    "title": "First Mirror Fumble",
    "character_name": "Floof",
    "segments": [
      {
        "segment": 1,
        "duration": 8,
        "scene": "...",
        ...
      }
    ]
  }
}
```

## 🔍 Debug Mode

To see detailed error messages, check the server console output when making the request. It will show:

- Connection attempts
- API responses
- Error details
- Raw output (if any)

---

**Need more help?** Run `python test_openrouter_connection.py` and share the output!
