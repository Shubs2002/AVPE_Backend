# Daily Character Content - Quick Reference

## 🚀 One-Liner

```bash
POST /api/generate-daily-character
{"idea": "Your daily moment", "num_segments": 7}
```

## 📋 Parameters

```json
{
  "idea": "string (required)",
  "num_segments": 7,  // 1-10, default 7
  "character_info": {} // optional
}
```

## 💡 Quick Ideas

**Funny**: Mirror scare, noise investigation, selfie fails  
**Relatable**: Can't wake up, cooking disaster, losing keys  
**Quirks**: Talks to plants, dances alone, weird faces  
**Adventures**: Shopping distraction, parking fail, delivery wait  

## 📊 Response

```json
{
  "content": {
    "title": "...",
    "character": {...},
    "segments": [{...}],
    "tag_line": "...",
    "engagement_hook": "Tag someone!"
  }
}
```

## 🎬 Perfect For

✅ Instagram character pages  
✅ Daily 1-minute videos  
✅ Relatable comedy  
✅ Character personality  
✅ Viral content  

## 📱 Instagram Format

**Structure**: Hook (2s) → Build (24s) → Payoff (30s)  
**Length**: 7-10 segments = ~1 minute  
**Format**: 9:16 vertical  
**Style**: Visual storytelling, minimal dialogue  

## 🎯 Example

```bash
curl -X POST "http://127.0.0.1:8000/api/generate-daily-character" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Character sees reflection and gets scared",
    "num_segments": 7
  }'
```

## ✨ Features

✅ Max 10 segments  
✅ ~1 minute total  
✅ Character consistency  
✅ Visual focus  
✅ Instagram optimized  
✅ Engagement hooks  

---

**See DAILY_CHARACTER_GUIDE.md for full docs!**
