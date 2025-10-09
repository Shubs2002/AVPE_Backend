"""
Prompts for WhatsApp AI Story Generation

This module contains prompts for generating WhatsApp AI stories with beautiful sceneries
and moments animated by AI.
"""

def get_whatsapp_story_prompt(idea: str, num_segments: int, custom_character_roster: list = None) -> str:
    """
    Generate the prompt for creating WhatsApp AI story segments
    
    Args:
        idea: The story idea/concept
        num_segments: Number of segments to generate (typically 7 for WhatsApp stories)
        custom_character_roster: Optional user-provided character roster
        
    Returns:
        str: The formatted prompt
    """
    # Build custom character roster instruction if provided
    custom_roster_instruction = ""
    if custom_character_roster and len(custom_character_roster) > 0:
        import json
        roster_json = json.dumps(custom_character_roster, indent=2)
        custom_roster_instruction = f"""
    
    **MANDATORY CHARACTER ROSTER**:
    You MUST use the following pre-defined characters in your WhatsApp story:
    
    {roster_json}
    
    These characters are the main cast and must appear throughout the story.
    """
    
    return f"""
    You are a professional creator for WhatsApp AI stories with beautiful sceneries and moments animated by AI.
    
    Your specialty is creating visually stunning, emotionally engaging short stories perfect for WhatsApp status updates.
    Each segment should focus on beautiful scenery, aesthetic moments, and visual storytelling that captivates viewers.
    {custom_roster_instruction}

    **WHATSAPP STORY CHARACTERISTICS**:
    - **Duration**: Each segment is 6-8 seconds (perfect for WhatsApp status)
    - **Visual Focus**: Emphasize beautiful sceneries, aesthetic moments, and stunning visuals
    - **Emotional Impact**: Create moments that resonate emotionally with viewers
    - **AI Animation Ready**: Descriptions must be detailed enough for AI video generation
    - **Vertical Format**: Optimized for 9:16 aspect ratio (mobile viewing)
    - **Quick Engagement**: Hook viewers in the first second
    
    **SCENERY & VISUAL EMPHASIS**:
    - Describe breathtaking landscapes, cityscapes, or intimate settings
    - Focus on lighting (golden hour, blue hour, dramatic shadows)
    - Include atmospheric elements (mist, rain, sunbeams, stars)
    - Emphasize colors, textures, and visual mood
    - Create cinematic moments that look stunning when animated
    
    **STORY STRUCTURE FOR WHATSAPP**:
    - **Opening**: Establish mood with a stunning visual
    - **Build-up**: Create emotional connection through beautiful moments
    - **Peak**: Deliver the most visually striking or emotionally powerful moment
    - **Closing**: Leave viewers with a memorable image or feeling
    
    Task:
    Create a WhatsApp AI story with {num_segments} segments based on this idea: "{idea}"
    
    Each segment should be a visual masterpiece that tells part of the story through stunning scenery and aesthetic moments.
    
    **CRITICAL REQUIREMENTS**:
    
    1. **Visual Storytelling**: Every segment must have a strong visual focus
    2. **Scenery Details**: Describe locations with cinematic detail
    3. **Lighting & Atmosphere**: Specify time of day, weather, and mood
    4. **Character Integration**: Characters should be part of the beautiful scenery
    5. **Emotional Moments**: Create visually stunning emotional beats
    6. **AI-Ready Descriptions**: Detailed enough for AI video generation (Veo3)
    
    **CHARACTER CONSISTENCY** (CRITICAL) - ULTRA-DETAILED REQUIREMENTS:
    For AI video generation, characters MUST look identical across all segments. Provide FORENSIC-LEVEL DETAILED descriptions:
    
    **SKIN**: Exact skin tone with undertones (e.g., "warm olive skin with golden undertones"), texture, any features (freckles, moles, dimples, laugh lines)
    
    **FACE**: Exact face shape (oval/round/square/heart), forehead, cheekbones, jawline, chin shape
    
    **HAIR - COMPLETE DETAILS**:
    - Exact color with undertones/highlights
    - Precise length and style
    - Texture (thick/fine/coarse/silky, straight/wavy/curly)
    - Hairline description
    - **BALDNESS STAGE**: If applicable - Norwood Scale (e.g., "No baldness", "Norwood 2 - temple recession", "Completely bald", "Thinning at crown")
    - Facial hair: exact style, length, grooming
    
    **EYES**: Exact color with flecks/rings, shape, size, spacing, eyelashes, eyebrows (thickness, arch, color)
    
    **NOSE**: Bridge height, width, tip shape, nostril details
    
    **LIPS**: Fullness, cupid's bow, natural color, smile width
    
    **OTHER**: Ears, neck, body type (detailed), height (exact), posture
    
    **CLOTHING**: Every item with colors, patterns, style, fit, fabric
    
    **DISTINCTIVE MARKS**: Every scar, birthmark, tattoo, piercing, mole with exact location
    
    **AGE INDICATORS**: Wrinkles, gray hair, skin elasticity
    
    Think of it as creating a police sketch that must match perfectly across all segments.
    
    **OUTPUT FORMAT** (JSON):
    {{
      "title": "Engaging WhatsApp Story Title",
      "short_summary": "Brief description of the story (1-2 sentences)",
      "description": "Compelling description for WhatsApp viewers",
      "hashtags": ["#WhatsAppStory", "#AIAnimation", "#BeautifulScenery", "#AestheticMoments", "#Viral"],
      "narrator_voice": {{
        "voice_type": "Female/Male/Child",
        "age_range": "20-30",
        "accent": "Neutral/British/American",
        "tone": "Warm/Dreamy/Romantic/Inspiring",
        "target_demographic": "Young Adults/All Ages",
        "speaking_pace": "Slow (2 wps) / Standard (3 wps) / Fast (4 wps)",
        "narration_style": "Poetic/Descriptive/Minimal",
        "child_friendly_level": "All Ages/Teen+/Adult",
        "voice_pitch": "Low/Mid/High",
        "expressiveness": "High/Medium/Low",
        "voice_description": "Detailed voice characteristics for consistency"
      }},
      "characters_roster": [
        {{
          "id": "char_unique_id",
          "name": "Character Name",
          "physical_appearance": {{
            "gender": "Male/Female",
            "age": "25",
            "height": "5'8\"",
            "body_type": "Slim/Athletic/Average",
            "skin_tone": "Fair/Olive/Dark with specific undertones",
            "hair_color": "Specific color",
            "hair_style": "Detailed style description",
            "eye_color": "Specific color",
            "eye_shape": "Almond/Round/etc.",
            "facial_features": "Detailed description",
            "distinctive_marks": "Any unique features"
          }},
          "clothing_style": {{
            "primary_outfit": "Detailed outfit description",
            "clothing_style": "Casual/Elegant/Bohemian/etc.",
            "colors": "Specific colors",
            "accessories": "Any accessories"
          }},
          "personality": "Brief personality description",
          "role": "Role in the story",
          "voice_mannerisms": {{
            "speaking_style": "Soft/Energetic/Calm",
            "accent_or_tone": "Specific accent or tone",
            "typical_expressions": "Common phrases or expressions"
          }},
          "video_prompt_description": "ULTRA-DETAILED description for AI video generation - include EVERY visual detail for perfect consistency across segments"
        }}
      ],
      "segments": [
        {{
          "segment": 1,
          "scene": "Brief scene description focusing on visual beauty",
          "content_type": "narration/dialogue/visual_only",
          "narration": "Poetic narration text (if applicable)",
          "dialogue": [
            {{"character": "char_id", "line": "Dialogue text"}}
          ],
          "characters_present": ["char_id1", "char_id2"],
          "camera": "Camera angle/movement (e.g., 'Slow pan across sunset horizon', 'Close-up of character's face with bokeh background')",
          "clip_duration": 7,
          "word_count": "Approximate word count",
          "estimated_speech_time": "7s",
          "background_definition": {{
            "location": "Specific beautiful location",
            "environment_type": "Nature/Urban/Indoor/Fantasy",
            "setting_description": "Detailed scenery description",
            "time_of_day": "Golden Hour/Blue Hour/Midnight/Dawn",
            "weather_conditions": "Clear/Misty/Rainy/Snowy",
            "lighting": "Warm golden light/Soft diffused light/Dramatic shadows",
            "atmosphere": "Dreamy/Romantic/Peaceful/Magical",
            "key_visual_elements": ["Sunset", "Mountains", "Flowers", "Water reflections"],
            "color_palette": "Warm oranges and pinks/Cool blues/Vibrant colors",
            "natural_elements": ["Trees", "Clouds", "Water", "Flowers"],
            "props_in_background": ["Lanterns", "Benches", "etc."],
            "scale": "Vast/Intimate/Medium",
            "continuity_notes": "What must remain consistent",
            "video_prompt_background": "COMPLETE detailed background description for AI video generation"
          }},
          "visual_style": "Cinematic/Dreamy/Aesthetic/Vintage",
          "mood": "Romantic/Peaceful/Inspiring/Melancholic",
          "emotions": ["Peace", "Wonder", "Love"],
          "lighting": "Detailed lighting description",
          "color_palette": "Specific color scheme",
          "aesthetic_focus": "What makes this segment visually stunning",
          "whatsapp_hook": "What will make viewers stop scrolling"
        }}
      ]
    }}
    
    **WHATSAPP-SPECIFIC GUIDELINES**:
    
    1. **First Segment Hook**: Must be visually stunning to stop scrolling
    2. **Pacing**: Quick, engaging, perfect for 6-8 second segments
    3. **Visual Variety**: Each segment should offer a different beautiful view
    4. **Emotional Arc**: Build emotional connection through visual storytelling
    5. **Shareable**: Create moments people want to share on their status
    6. **Mobile-Optimized**: Vertical format, clear visuals, readable text
    
    **SCENERY INSPIRATION**:
    - Golden hour on a beach with waves and silhouettes
    - Misty mountain peaks at dawn
    - City lights reflecting on wet streets at night
    - Cherry blossoms falling in slow motion
    - Starry night sky over a peaceful landscape
    - Cozy café with warm lighting and rain outside
    - Sunset through autumn leaves
    - Northern lights dancing over snow
    
    **AESTHETIC MOMENTS TO CAPTURE**:
    - Character silhouette against stunning backdrop
    - Close-up of emotions with beautiful bokeh
    - Slow-motion moments (hair flowing, leaves falling)
    - Reflections in water or glass
    - Dramatic lighting on faces
    - Wide shots of breathtaking landscapes
    - Intimate moments in beautiful settings
    
    Generate a complete WhatsApp AI story that will captivate viewers with its visual beauty and emotional resonance.
    Each segment should be a work of art that showcases the power of AI animation combined with stunning scenery.
    
    Return ONLY valid JSON without any markdown formatting or code blocks.
    """
