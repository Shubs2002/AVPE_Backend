# 🎭 Custom Character Roster Feature

## Quick Start

You can now pass your own custom characters to ensure they appear in your generated stories, memes, and free content!

### Basic Example

```json
{
  "idea": "A superhero saves the city",
  "segments": 10,
  "custom_character_roster": [
    {
      "id": "hero1",
      "name": "Captain Thunder",
      "physical_appearance": {
        "gender": "male",
        "age": "32",
        "height": "6'2\"",
        "skin_tone": "bronze tan",
        "hair_color": "jet black"
      },
      "personality": "brave, selfless, leader",
      "role": "main superhero"
    }
  ]
}
```

## 📚 Documentation Files

1. **[CUSTOM_CHARACTER_ROSTER_GUIDE.md](CUSTOM_CHARACTER_ROSTER_GUIDE.md)**
   - Complete user guide
   - API endpoint details
   - Character roster format
   - Example requests
   - Tips and best practices

2. **[test_custom_roster_example.json](test_custom_roster_example.json)**
   - Ready-to-use example requests
   - Story generation example
   - Meme generation example
   - Free content generation example

3. **[CUSTOM_ROSTER_IMPLEMENTATION_SUMMARY.md](CUSTOM_ROSTER_IMPLEMENTATION_SUMMARY.md)**
   - Technical implementation details
   - Code changes summary
   - Architecture overview

## 🚀 Supported Endpoints

All content generation endpoints now support `custom_character_roster`:

- ✅ `/generate-prompt-based-story` - Story generation
- ✅ `/generate-story-set` - Story set generation
- ✅ `/generate-movie-auto` - Full movie generation
- ✅ `/generate-meme-segments` - Meme generation
- ✅ `/generate-free-content` - Free content generation

## 💡 Key Features

- **Mandatory Usage**: Your characters MUST appear as the main cast
- **Exact Descriptions**: Character details are preserved exactly as provided
- **Visual Consistency**: Detailed descriptions ensure consistent video generation
- **All Content Types**: Works with stories, memes, and free content
- **All Generation Modes**: Works with standard, chunked, and set-based generation
- **Backward Compatible**: Optional parameter - existing code works unchanged

## 🎨 Use Cases

1. **Brand Mascots**: Use your brand characters in all content
2. **Character Franchises**: Build stories with recurring characters
3. **Personalized Content**: Create content featuring specific people/avatars
4. **Consistent Branding**: Maintain visual consistency across all videos
5. **Character Development**: Evolve characters across multiple stories

## 🔗 Integration with Character Analysis

Generate detailed character rosters from images:

```bash
curl -X POST "http://localhost:8000/analyze-character-image-file" \
  -F "image=@photo.jpg" \
  -F "character_name=Captain Thunder" \
  -F "save_character=true"
```

Use the generated roster directly in content generation!

## 📖 Quick Reference

### Minimal Character Object
```json
{
  "id": "hero1",
  "name": "Hero Name",
  "physical_appearance": {
    "gender": "male",
    "age": "30",
    "skin_tone": "tan",
    "hair_color": "black"
  },
  "personality": "brave, kind",
  "role": "protagonist"
}
```

### Detailed Character Object
```json
{
  "id": "hero1",
  "name": "Captain Thunder",
  "physical_appearance": {
    "gender": "male",
    "age": "32 years old",
    "height": "6'2\" / 188cm",
    "body_type": "muscular athletic",
    "skin_tone": "warm bronze tan",
    "hair_color": "jet black",
    "hair_style": "short military cut",
    "eye_color": "electric blue",
    "facial_features": "chiseled jawline, strong cheekbones",
    "distinctive_marks": "lightning bolt scar on temple"
  },
  "clothing_style": {
    "primary_outfit": "blue superhero suit with lightning emblem",
    "colors": "blue, silver, red",
    "accessories": "silver utility belt"
  },
  "personality": "brave, selfless, natural leader",
  "role": "main superhero protagonist",
  "voice_mannerisms": {
    "speaking_style": "commanding yet compassionate",
    "accent_or_tone": "deep resonant voice"
  },
  "video_prompt_description": "Complete detailed description for video generation..."
}
```

## ⚡ Quick Test

1. Copy an example from `test_custom_roster_example.json`
2. Send POST request to any generation endpoint
3. Your characters will be the stars of the content!

## 🎯 Best Practices

1. **Be Detailed**: More details = better visual consistency
2. **Include Video Prompt**: Always add `video_prompt_description`
3. **Physical Specifics**: Exact measurements and colors
4. **Clothing Details**: Describe every piece of clothing
5. **Personality Traits**: Influences dialogue and actions

## 📞 Need Help?

- Read the full guide: [CUSTOM_CHARACTER_ROSTER_GUIDE.md](CUSTOM_CHARACTER_ROSTER_GUIDE.md)
- Check examples: [test_custom_roster_example.json](test_custom_roster_example.json)
- Review implementation: [CUSTOM_ROSTER_IMPLEMENTATION_SUMMARY.md](CUSTOM_ROSTER_IMPLEMENTATION_SUMMARY.md)

## ✨ Example Workflow

```
1. Create/Analyze Characters
   ↓
2. Save Character Roster
   ↓
3. Generate Content (Story/Meme/Free Content)
   ↓
4. Generate Videos with Consistent Characters
   ↓
5. Reuse Characters in New Content
```

---

**Your characters, your story!** 🎬
