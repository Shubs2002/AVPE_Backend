"""
Prompts for AI meme content generation services

This module contains prompts used for generating viral meme video segments.
Memes require different structure and tone compared to story segments, focusing on:
- Visual comedy and reactions (70% of content)
- Quick punchlines and comedic timing
- Relatable or absurd humor
- Viral potential and shareability

Functions:
1. get_meme_segments_prompt:
   - Used for generating viral meme video concepts
   - Creates segments optimized for TikTok/Instagram Reels/YouTube Shorts
   - Focuses on visual comedy, reactions, and comedic timing
   - Includes meme-specific metadata (meme_type, relatability_factor, etc.)
"""


def get_meme_segments_prompt(idea: str, num_segments: int) -> str:
    """
    Generate the prompt for creating viral meme video segments.
    
    Meme videos differ from story videos in several ways:
    - Emphasis on visual comedy (70%) over dialogue (30%)
    - Focus on reactions, facial expressions, and physical comedy
    - Shorter setup-punchline structure
    - Higher energy and faster pacing
    - Meme-specific metadata (relatability, absurdity levels)
    
    Args:
        idea: The meme concept/idea
        num_segments: Number of segments to generate (typically 5-10 for memes)
        
    Returns:
        str: The formatted prompt for generating meme segments
    """
    
    return f"""
    You are a professional Humanised meme creator and viral content specialist.
    you can add more custom fields for generating the best results as i am gonna feed your generated output into veo3 video generation model.

    Task:
    - Create a viral meme video concept based on: "{idea}"
    - Write a **short_summary** (2–3 sentences) explaining the meme concept.
    - Create a **catchy title** (under 60 chars) designed for maximum viral potential on TikTok/Instagram Reels/YouTube Shorts.
    - Write a **viral description** (2–3 sentences) that:
       * Hooks viewers with humor or relatability
       * Explains the meme briefly
       * Ends with engagement bait like "Tag someone who does this!" or "Rate this meme 1-10!"
    - Break it into {num_segments} segments, each ~8s long.
    - **The first segment must be a SETUP**:
       * Introduce the meme concept
       * Set up the joke/situation
       * Hook the viewer immediately
    - Generate **hashtags** (10-20). Mix trending meme tags (#meme, #funny, #relatable, #viral) with specific ones.
    - **Meme continuity**:
        * Each segment should build on the previous one
        * Escalate the humor or absurdity
        * Final segment should deliver the punchline or peak comedy
    - Define **characters_roster** (1-4 characters) with DETAILED descriptions for video generation consistency:
        * id (short tag like "main", "friend1")
        * name (can be generic like "Main Character", "Best Friend")
        * **Physical Appearance** (for video generation prompts):
          - gender (male/female/non-binary)
          - age (specific age or range)
          - height (tall/medium/short with approximate measurements)
          - body_type (slim/athletic/average/muscular/etc.)
          - skin_tone (fair/olive/tan/dark/etc. - be specific)
          - hair_color (exact color like "golden blonde", "dark brown", "jet black")
          - hair_style (length, texture, style - "shoulder-length wavy", "short curly", etc.)
          - eye_color (specific color like "emerald green", "deep brown", "bright blue")
          - eye_shape (almond/round/narrow/wide)
          - facial_features (distinctive features like "sharp jawline", "soft features", "prominent cheekbones")
          - distinctive_marks (scars, tattoos, birthmarks, etc.)
        * **Clothing & Style**:
          - primary_outfit (detailed description for consistency)
          - clothing_style (casual, trendy, quirky, etc.)
          - colors (specific color palette for the character)
          - accessories (jewelry, hats, glasses, etc.)
        * personality (comedic traits and mannerisms)
        * role (straight man, comic relief, etc.)
        * **Voice & Mannerisms** (for dialogue segments):
          - speaking_style (sarcastic/bubbly/deadpan/etc.)
          - accent_or_tone (if applicable)
          - typical_expressions (facial expressions, gestures)
          - comedic_timing (fast/slow/dramatic pauses)
    - **NARRATOR VOICE SELECTION** for meme content:
        * **Primary Narrator**: Choose ONE consistent narrator voice for the ENTIRE meme series based on meme type and target audience:
          - **Kids Memes (5-12)**: Super animated, cute voice (female 25-35) like kids' cartoon characters - high-pitched and bubbly
          - **Teen Memes (13-17)**: Cool, relatable voice (male/female 18-25) with teen slang and energy
          - **Relatable Memes**: Casual, conversational voice (male/female 20-30) with Gen Z energy
          - **Reaction Memes**: Expressive, animated voice (female 18-28) with high energy
          - **Absurd/Random Memes**: Quirky, unpredictable voice (male 22-32) with comedic timing
          - **Trending Memes**: Hip, current voice (male/female 18-25) with social media slang
          - **Observational Memes**: Witty, sarcastic voice (male 25-35) with dry humor
          - **Physical Comedy**: Energetic, playful voice (female 20-30) with animated delivery
          - **Family-Friendly Memes**: Clean, wholesome voice (male/female 25-40) suitable for all ages
        * **CONSISTENCY RULE**: The same narrator voice must be used throughout ALL meme segments. Only comedic delivery and energy can vary slightly per segment to match the joke's timing.
        * **Target Age Demographics**: 
          - **Young Kids (5-10)**: Super animated, cartoon-like voices with sound effects and giggles
          - **Tweens (11-14)**: Fun, energetic voices that are cool but not too mature
          - **Teens (15-17)**: Trendy, authentic voices with current slang and references
          - **Gen Z (18-24)**: Fast-paced, meme-savvy voices with internet culture references
          - **Young Millennials (25-32)**: Relatable, slightly nostalgic voices with pop culture refs
          - **Broad Appeal**: Universally funny voices that work across age groups
    - **CRITICAL TIMING RULE**: Each segment must fit within exactly 8 seconds of speech/action time.
    - **CONTENT SEPARATION**: Each segment should focus on either visual comedy OR dialogue, with clear emphasis.
    - For each segment:
        * Scene description (setting, visual gags, reactions)
        * **Visual comedy** should be 70% of the content (facial expressions, physical comedy, visual gags)
        * **Dialogue/text** 30% (punchlines, reactions, meme text overlays)
        * Characters present and their reactions
        * Camera style (close-ups for reactions, wide shots for physical comedy)
        * Meme format (if applicable: Drake pointing, Distracted boyfriend, etc.)
        * **Detailed background definition** for video generation consistency

    Return ONLY valid JSON with this EXACT structure:
    {{{{
      "title": "...",
      "short_summary": "...",
      "description": "...",
      "hashtags": ["...", "...", "..."],
      "meme_type": "...", # e.g., "relatable", "absurd", "reaction", "trend"
      "narrator_voice": {{{{
        "voice_type": "...", # cute_animated_female, cool_teen_male, casual_male, energetic_female, sarcastic_male, bubbly_female, etc.
        "age_range": "...", # 18-25, 20-30, 22-32, 25-35, etc.
        "accent": "...", # kids_cartoon_american, teen_slang, gen_z_american, millennial_neutral, internet_culture, etc.
        "tone": "...", # super_animated_cute, cool_teen, sarcastic, energetic, deadpan, animated, witty
        "target_demographic": "...", # Young Kids, Tweens, Teens, Gen Z, Young Millennials, Broad Appeal
        "speaking_pace": "...", # animated_kids_pace, teen_cool_pace, fast_meme_pace, moderate_relatable, quick_punchy
        "comedic_style": "...", # kids_cartoon_fun, teen_cool_humor, dry_humor, animated_energy, sarcastic_wit, bubbly_fun
        "child_friendly_level": "...", # very_high_kids_cartoon, high_family_friendly, moderate_teen, low_adult_humor
        "voice_pitch": "...", # very_high_cartoon, high_animated, medium_cool, low_sarcastic
        "expressiveness": "...", # cartoon_level_expressive, high_animated, moderate_cool, minimal_deadpan
        "voice_description": "..." # Complete description for voice generation
      }}}},
      "characters_roster": [
        {{{{
          "id": "...",
          "name": "...",
          "physical_appearance": {{{{
            "gender": "...",
            "age": "...",
            "height": "...",
            "body_type": "...",
            "skin_tone": "...",
            "hair_color": "...",
            "hair_style": "...",
            "eye_color": "...",
            "eye_shape": "...",
            "facial_features": "...",
            "distinctive_marks": "..."
          }}}},
          "clothing_style": {{{{
            "primary_outfit": "...",
            "clothing_style": "...",
            "colors": "...",
            "accessories": "..."
          }}}},
          "personality": "...",
          "role": "...",
          "voice_mannerisms": {{{{
            "speaking_style": "...",
            "accent_or_tone": "...",
            "typical_expressions": "...",
            "comedic_timing": "..."
          }}}},
          "video_prompt_description": "..." # Complete description for video generation
        }}}}
      ],
      "segments": [
        {{{{
          "segment": 1,
          "scene": "...",
          "overlay_text": "...", # meme text, captions, etc.
          "overlay_text_position": "...",
          "overlay_text_style": "...",
          "overlay_text_duration": "...",
          "overlay_text_animation": "...",
          "overlay_text_color": "...",
          "overlay_text_font": "...",
          "visual_comedy": "...", # main comedic element, 70% of content
          "narrator_voice_for_segment": {{{{  # for meme narration/commentary
            "voice_type": "...", # MUST be same as main narrator_voice selection
            "comedic_delivery_variation": "...", # slight delivery adjustment (more_sarcastic, extra_bubbly, deadpan_timing, etc.)
            "pace_variation": "...", # slight pace adjustment for comedic timing (punch_line_pause, quick_setup, etc.)
            "energy_adjustment": "...", # slight energy change (build_up_energy, peak_energy, calm_delivery)
            "joke_timing": "...", # how to time this segment's comedy
            "consistency_note": "Same narrator voice as previous segments, only comedic timing varies"
          }}}},
          "characters_present": ["main", "friend1"],
          "dialogue": [
            {{"character": "main", "line": "..."}},
            {{"character": "friend1", "line": "..."}}
          ],
          "reactions": [
            {{"character": "main", "reaction": "..."}},
            {{"character": "friend1", "reaction": "..."}}
          ],
          "camera": "...",
          "clip_duration": 8, # always 8 seconds
          "word_count": "...", # actual word count to verify 8-second limit
          "estimated_speech_time": "...", # estimated seconds (should be ≤8)
          "background_definition": {{{{
            "location": "...", # specific location name/type
            "environment_type": "...", # indoor/outdoor/realistic/stylized
            "setting_description": "...", # detailed visual description for video generation
            "time_of_day": "...", # morning/afternoon/evening/night
            "weather_conditions": "...", # sunny/cloudy/rainy/stormy
            "lighting": "...", # natural/artificial/bright/dim
            "atmosphere": "...", # comedic/chaotic/relatable/absurd
            "key_visual_elements": ["..."], # important background objects/features
            "color_palette": "...", # dominant colors for the scene
            "architectural_style": "...", # if applicable - modern/home/office/etc.
            "props_in_background": ["..."], # objects that should appear consistently
            "scale": "...", # intimate/medium/wide - helps with camera framing
            "continuity_notes": "...", # what must remain consistent across segments
            "video_prompt_background": "..." # Complete background description for video generation
          }}}},
          "meme_format": "...", # optional: specific meme template
          "visual_gags": ["..."], # physical comedy, sight gags
          "sound_effects": ["..."], # comedic sounds
          "background_music": "...", # upbeat, comedic
          "facial_expressions": ["..."], # key to meme success
          "timing": "...", # comedic timing notes
          "escalation_level": "...", # how intense the comedy is (1-10)
          "relatability_factor": "...", # how relatable (1-10)
          "absurdity_level": "...", # how absurd (1-10)
          "meme_potential": "...", # viral potential (1-10)
          "target_audience": "...", # Gen Z, Millennials, etc.
          "comedy_style": "...", # slapstick, dry humor, etc.
          "cultural_references": ["..."], # pop culture refs
          "trending_elements": ["..."] # current trends incorporated
        }}}}
      ]
    }}}}
    """
