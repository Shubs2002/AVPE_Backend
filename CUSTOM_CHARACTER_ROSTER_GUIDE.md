# Custom Character Roster Feature Guide

## Overview
You can now provide your own custom character roster to ensure specific characters appear in your generated stories, memes, and free content. This feature guarantees that YOUR characters are the main stars of the content.

## How It Works

When you provide a `custom_character_roster`, the AI will:
- Use ONLY your provided characters as the main cast
- Maintain exact character descriptions across all segments
- Build the story/meme/content around YOUR characters
- Ensure visual consistency for video generation

## API Endpoints That Support Custom Roster

All content generation endpoints now support the `custom_character_roster` field:

1. `/generate-prompt-based-story` - Story generation
2. `/generate-story-set` - Story set generation
3. `/generate-movie-auto` - Automatic full movie generation
4. `/generate-meme-segments` - Meme generation
5. `/generate-free-content` - Free content generation

## Character Roster Format

The `custom_character_roster` should be an array of character objects. Each character should include:

```json
{
  "custom_character_roster": [
    {
      "id": "hero1",
      "name": "Alex Thunder",
      "physical_appearance": {
        "gender": "male",
        "age": "28 years old",
        "height": "6'0\" / 183cm",
        "body_type": "athletic mesomorph",
        "skin_tone": "warm olive tan",
        "hair_color": "dark brown with subtle highlights",
        "hair_style": "short textured quiff, side-parted",
        "eye_color": "steel blue-gray",
        "eye_shape": "almond-shaped",
        "facial_features": "strong jawline, high cheekbones, straight nose",
        "distinctive_marks": "small scar above left eyebrow"
      },
      "clothing_style": {
        "primary_outfit": "black leather jacket over white t-shirt, dark blue jeans",
        "clothing_style": "modern casual with edge",
        "colors": "black, white, dark blue",
        "accessories": "silver chain necklace, black leather watch"
      },
      "personality": "confident, brave, quick-witted, protective",
      "role": "main protagonist and hero",
      "voice_mannerisms": {
        "speaking_style": "confident and authoritative",
        "accent_or_tone": "neutral American accent",
        "typical_expressions": "determined gaze, slight smirk when confident"
      },
      "video_prompt_description": "A 28-year-old athletic male with warm olive tan skin, standing 6'0\" tall with a mesomorph build. He has dark brown hair styled in a short textured quiff with side part, steel blue-gray almond-shaped eyes, strong jawline, high cheekbones, and a straight nose. Small scar above left eyebrow. Wearing black leather jacket over white t-shirt, dark blue jeans, silver chain necklace, and black leather watch. Confident posture with determined expression."
    },
    {
      "id": "sidekick1",
      "name": "Maya Swift",
      "physical_appearance": {
        "gender": "female",
        "age": "25 years old",
        "height": "5'6\" / 168cm",
        "body_type": "slim athletic",
        "skin_tone": "fair with pink undertones",
        "hair_color": "auburn with copper tones",
        "hair_style": "long wavy hair, usually in high ponytail",
        "eye_color": "hazel with gold flecks",
        "eye_shape": "large round eyes",
        "facial_features": "heart-shaped face, button nose, full lips",
        "distinctive_marks": "freckles across nose and cheeks"
      },
      "clothing_style": {
        "primary_outfit": "red bomber jacket, black tank top, gray cargo pants",
        "clothing_style": "sporty and practical",
        "colors": "red, black, gray",
        "accessories": "fitness tracker watch, small backpack"
      },
      "personality": "energetic, tech-savvy, loyal, optimistic",
      "role": "tech expert and best friend",
      "voice_mannerisms": {
        "speaking_style": "fast-paced and enthusiastic",
        "accent_or_tone": "upbeat with slight valley girl inflection",
        "typical_expressions": "bright smile, animated hand gestures"
      },
      "video_prompt_description": "A 25-year-old slim athletic female with fair skin and pink undertones, standing 5'6\" tall. She has long wavy auburn hair with copper tones in a high ponytail, large round hazel eyes with gold flecks, heart-shaped face, button nose, full lips, and freckles across nose and cheeks. Wearing red bomber jacket, black tank top, gray cargo pants, fitness tracker watch, and carrying a small backpack. Energetic posture with bright smile."
    }
  ]
}
```

## Example API Requests

### 1. Story Generation with Custom Characters

```bash
curl -X POST "http://localhost:8000/generate-prompt-based-story" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "A thrilling adventure where heroes save the city from a mysterious threat",
    "segments": 10,
    "custom_character_roster": [
      {
        "id": "hero1",
        "name": "Alex Thunder",
        "physical_appearance": {
          "gender": "male",
          "age": "28",
          "height": "6 feet",
          "skin_tone": "olive tan",
          "hair_color": "dark brown",
          "hair_style": "short quiff",
          "eye_color": "blue-gray"
        },
        "clothing_style": {
          "primary_outfit": "black leather jacket, white t-shirt, jeans"
        },
        "personality": "confident, brave, protective",
        "role": "main hero"
      }
    ]
  }'
```

### 2. Meme Generation with Custom Characters

```bash
curl -X POST "http://localhost:8000/generate-meme-segments" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "When you try to act cool but fail hilariously",
    "segments": 7,
    "custom_character_roster": [
      {
        "id": "main",
        "name": "Charlie",
        "physical_appearance": {
          "gender": "male",
          "age": "22",
          "skin_tone": "fair",
          "hair_color": "blonde",
          "hair_style": "messy"
        },
        "personality": "awkward, tries too hard, lovable",
        "role": "comedic protagonist"
      }
    ]
  }'
```

### 3. Full Movie Generation with Custom Characters

```bash
curl -X POST "http://localhost:8000/generate-movie-auto" \
  -H "Content-Type: application/json" \
  -d '{
    "idea": "Epic fantasy adventure with dragons and magic",
    "total_segments": 50,
    "segments_per_set": 10,
    "save_to_files": true,
    "custom_character_roster": [
      {
        "id": "wizard",
        "name": "Merlin Stormweaver",
        "physical_appearance": {
          "gender": "male",
          "age": "45",
          "height": "5 feet 10 inches",
          "skin_tone": "pale",
          "hair_color": "silver-gray",
          "hair_style": "long flowing beard and hair"
        },
        "clothing_style": {
          "primary_outfit": "purple wizard robes with gold trim, pointed hat"
        },
        "personality": "wise, mysterious, powerful",
        "role": "mentor and guide"
      }
    ]
  }'
```

## Using Character Analysis to Create Custom Roster

You can use the character analysis endpoints to generate detailed character rosters from images:

```bash
# Analyze a single character image
curl -X POST "http://localhost:8000/analyze-character-image-file" \
  -F "image=@character_photo.jpg" \
  -F "character_name=Alex Thunder" \
  -F "character_count=1" \
  -F "save_character=true"
```

The response will include a detailed `characters_roster` that you can use directly in your content generation requests!

## Benefits

1. **Brand Consistency**: Use your brand mascots or characters across all content
2. **Character Continuity**: Same characters appear in multiple stories/memes
3. **Visual Consistency**: Detailed descriptions ensure video generation produces consistent visuals
4. **Personalization**: Create content featuring specific people, avatars, or characters
5. **Franchise Building**: Build a universe with recurring characters

## Tips for Best Results

1. **Be Detailed**: The more detailed your character descriptions, the better the visual consistency
2. **Include Video Prompt**: Always include a comprehensive `video_prompt_description` field
3. **Physical Specifics**: Specify exact measurements, colors, and features
4. **Clothing Details**: Describe every piece of clothing for consistency
5. **Personality Traits**: Include personality to influence dialogue and actions
6. **Use Character Analysis**: Upload images to auto-generate detailed character rosters

## Important Notes

- Custom characters become the MAIN CAST - the story revolves around them
- The AI can add minor supporting characters, but your roster characters are the stars
- All physical descriptions are maintained exactly as specified
- Character consistency is critical for video generation quality
- You can provide 1-5 main characters per roster

## Example Workflow

1. **Create/Analyze Characters**: Use character analysis endpoint or manually create roster
2. **Save Character Data**: Store your character roster for reuse
3. **Generate Content**: Pass the roster to any content generation endpoint
4. **Generate Videos**: Use the consistent character descriptions for video generation
5. **Reuse Characters**: Use the same roster across multiple stories/memes/content

## Questions?

The custom character roster feature ensures YOUR characters are always the stars of the show!
