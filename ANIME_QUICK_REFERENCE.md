# Anime Generation - Quick Reference

## 🚀 Quick Start

```bash
POST /api/generate-anime-auto
{
  "idea": "Your anime concept",
  "anime_style": "shonen",
  "total_segments": 30
}
```

## 🎨 Anime Styles

| Style | Target | Features |
|-------|--------|----------|
| **shonen** | Young male | Action, battles, friendship |
| **shojo** | Young female | Romance, emotions, beauty |
| **seinen** | Adult male | Mature, complex themes |
| **slice_of_life** | All ages | Daily life, warmth, humor |
| **mecha** | Teens/adults | Giant robots, sci-fi |
| **isekai** | Teens/young adults | Fantasy world, magic |

## 📋 Parameters

```json
{
  "idea": "string (required)",
  "anime_style": "shonen|shojo|seinen|slice_of_life|mecha|isekai",
  "total_segments": 30,
  "segments_per_set": 10,
  "cliffhanger_interval": 10,
  "content_rating": "U|U/A|A",
  "no_narration": false,
  "narration_only_first": false,
  "custom_character_roster": []
}
```

## 💡 Quick Examples

### Shonen Action
```json
{
  "idea": "Martial artist enters tournament",
  "anime_style": "shonen",
  "cliffhanger_interval": 10
}
```

### Shojo Romance
```json
{
  "idea": "Girl and boy fall in love",
  "anime_style": "shojo",
  "narration_only_first": true
}
```

### Isekai Fantasy
```json
{
  "idea": "Gamer transported to RPG world",
  "anime_style": "isekai",
  "total_segments": 40
}
```

## 🎭 Anime Character Features

**Eyes**: LARGE, expressive, detailed iris, shine spots  
**Hair**: Distinctive style, vibrant colors, shine effects  
**Face**: Soft rounded, small nose, small mouth  
**Body**: Anime proportions, dynamic poses  
**Clothing**: School uniforms, Japanese fashion, fantasy costumes  

## 📊 Response

```json
{
  "result": {
    "anime_title": "...",
    "anime_style": "shonen",
    "generation_summary": {
      "total_segments_generated": 30,
      "successful_sets": 3
    },
    "output_directory": "generated_anime"
  }
}
```

## 📁 Output

```
generated_anime/
├── Anime_Title_metadata.json
├── Anime_Title_set_01.json
├── Anime_Title_set_02.json
└── Anime_Title_set_03.json
```

## 🎬 Anime Features

✅ Large expressive anime eyes  
✅ Vibrant anime colors  
✅ Cel-shading style  
✅ Speed lines & effects  
✅ Dynamic camera angles  
✅ Anime storytelling  
✅ English dialogue  
✅ Power systems  
✅ Cliffhangers  

## 🔧 Python Usage

```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/api/generate-anime-auto",
    json={
        "idea": "Your anime concept",
        "anime_style": "shonen",
        "total_segments": 30
    }
)

result = response.json()
print(f"Anime: {result['result']['anime_title']}")
```

## 📚 Full Docs

See **ANIME_GENERATION_GUIDE.md** for complete documentation!

---

**Quick Tip**: Use `cliffhanger_interval: 10` for engaging episodic content!
