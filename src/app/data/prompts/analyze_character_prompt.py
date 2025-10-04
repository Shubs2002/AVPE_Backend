"""
Prompts for AI character analysis from images

This module contains prompts used for analyzing images to extract character information.
Used for creating detailed character rosters for video generation by:
- Analyzing character physical appearance
- Inferring personality traits from visual cues
- Generating consistent character descriptions
- Creating video generation prompts

Functions:
1. get_character_analysis_prompt:
   - Used for analyzing images to extract character details
   - Creates detailed character rosters for video generation
   - Maintains visual consistency across segments
   - Infers personality and voice characteristics
"""


def get_character_analysis_prompt(character_count: int, character_name: str = None) -> str:
    """
    Generate the prompt for analyzing characters from an image.
    
    This function creates a prompt for extracting detailed character information
    from images, which is essential for:
    - Creating consistent character descriptions for video generation
    - Maintaining visual continuity across multiple video segments
    - Inferring personality traits and voice characteristics
    - Generating complete character rosters
    
    Args:
        character_count: Number of characters to identify in the image
        character_name: Optional specific name to use for the main character
        
    Returns:
        str: The formatted prompt for character analysis
    """
    
    return f"""
    You are a professional character designer and visual analyst for film production.
    
    Task: Analyze this image and create detailed character roster(s) for video generation.
    
    Instructions:
    - Identify and analyze {character_count} character(s) in this image
    - If there are fewer than {character_count} characters visible, analyze all visible characters
    - If there are more than {character_count} characters, focus on the most prominent ones
    - Create detailed descriptions suitable for consistent video generation
    - Each character should be described in enough detail to maintain visual consistency across multiple video segments
    {f"- Use '{character_name}' as the character name for the main character" if character_name else ""}
    
    For each character, provide:
    - Unique character ID (short, like "char1", "hero", "villain", etc.)
    - Character name (can be descriptive like "Mysterious Woman", "Young Warrior", etc.)
    - Complete physical appearance details
    - Clothing and style information
    - Personality traits (inferred from appearance/pose)
    - Role suggestions (protagonist, antagonist, supporting, etc.)
    - Voice and mannerism suggestions
    - Complete video generation prompt description
    
    Return ONLY valid JSON with this EXACT structure:
    {{{{
      "analysis_summary": "Brief description of what you see in the image",
      "characters_detected": {character_count},
      "characters_roster": [
        {{{{
          "id": "char1",
          "name": "Character Name",
          "confidence_score": 0.95,
          "position_in_image": "center/left/right/background",
          "physical_appearance": {{{{
            "gender": "male/female/non-binary/unknown",
            "estimated_age": "specific age or range like '25-30'",
            "height": "tall/medium/short with approximate description",
            "body_type": "slim/athletic/average/muscular/etc.",
            "skin_tone": "fair/olive/tan/dark/etc. - be specific",
            "hair_color": "exact color like 'golden blonde', 'dark brown', 'jet black'",
            "hair_style": "detailed description of length, texture, style",
            "eye_color": "specific color like 'emerald green', 'deep brown', 'bright blue'",
            "eye_shape": "almond/round/narrow/wide",
            "facial_features": "distinctive features like jawline, cheekbones, etc.",
            "distinctive_marks": "scars, tattoos, birthmarks, glasses, etc.",
            "facial_expression": "current expression in the image",
            "pose_and_posture": "how they're positioned/standing/sitting"
          }}}},
          "clothing_style": {{{{
            "primary_outfit": "detailed description of main clothing",
            "clothing_style": "modern/vintage/fantasy/formal/casual/etc.",
            "colors": "specific color palette of their outfit",
            "accessories": "jewelry, hats, bags, weapons, tools, etc.",
            "footwear": "shoes, boots, sandals, etc.",
            "overall_style": "elegant/rugged/professional/artistic/etc."
          }}}},
          "inferred_personality": {{{{
            "primary_traits": ["confident", "mysterious", "friendly", "etc."],
            "energy_level": "high/medium/low",
            "approachability": "very approachable/somewhat reserved/intimidating/etc.",
            "likely_role": "protagonist/antagonist/mentor/comic relief/etc."
          }}}},
          "suggested_voice_mannerisms": {{{{
            "speaking_style": "confident/shy/authoritative/playful/etc.",
            "likely_accent": "neutral/regional/foreign/etc.",
            "speech_pace": "fast/moderate/slow",
            "typical_expressions": "facial expressions and gestures they might use"
          }}}},
          "video_prompt_description": "Complete, detailed description for video generation that captures all visual elements consistently",
          "character_backstory_suggestions": "Brief suggestions for potential character background",
          "scene_context": "What this character appears to be doing in the image"
        }}}}
      ],
      "image_context": {{{{
        "setting": "description of the background/environment",
        "lighting": "natural/artificial/dramatic/soft/etc.",
        "mood": "overall mood of the image",
        "style": "photographic/artistic/cartoon/realistic/etc.",
        "quality": "high/medium/low resolution and clarity"
      }}}},
      "video_generation_notes": "Additional notes for maintaining consistency in video generation"
    }}}}
    """
