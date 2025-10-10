# Quick Retry Reference Card

## 🚀 Tomorrow's Action (When Rate Limit Resets)

```bash
python retry_midnight_protocol_simple.py
```

That's it! The script will:
- Find your Midnight Protocol metadata
- Detect failed sets [26, 27, 28, 29, 30]
- Retry them automatically
- Save completed sets to `generated_movie_script/`

## 📊 Check Status First (Optional)

```bash
python test_endpoint_quick.py
```

## 🔧 Manual API Calls

### Check Status
```bash
curl "http://127.0.0.1:8000/api/story-status/Midnight%20Protocol"
```

### Retry Failed Sets
```bash
curl -X POST "http://127.0.0.1:8000/api/retry-story-by-title" \
  -H "Content-Type: application/json" \
  -d '{"title": "Midnight Protocol", "max_retries": 3}'
```

## 📁 Files Created

- ✅ `src/app/utils/story_retry_helper.py` - Core retry logic
- ✅ `src/app/api/routes.py` - Two new endpoints added
- ✅ `retry_midnight_protocol_simple.py` - Your quick retry script
- ✅ `test_endpoint_quick.py` - Status checker
- ✅ Documentation files

## 🎯 What Happens

1. Script calls `/api/retry-story-by-title`
2. System finds `Midnight_Protocol_metadata.json`
3. Checks which set files exist (1-25 ✅, 26-30 ❌)
4. Constructs retry payload with all 30 sets
5. Retries only the 5 failed sets
6. Saves: `Midnight_Protocol_set_26.json` through `set_30.json`
7. Returns success summary

## ⏰ Rate Limit Info

- **Limit**: 16 requests/minute (free tier)
- **Reset Time**: Check the timestamp in your error (1760032920000)
- **Tip**: Wait a few extra minutes to be safe

## 🎉 Expected Result

```
✅ Success! Generated 5 sets
📊 Total segments: 50
🎉 All failed sets now completed!
💾 Files saved to: generated_movie_script
```

Then you'll have all 30 sets complete! (300 segments total)
