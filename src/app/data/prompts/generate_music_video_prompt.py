"""
Prompts for AI Music Video Generation

This module contains prompts for generating AI music video prompts from song lyrics,
optimized for Veo3 video generation.
"""

def get_music_video_prompt(song_lyrics: str, song_length: int, background_voice_needed: bool, additional_dialogues: list = None, custom_character_roster: list = None, music_genre: str = None, visual_theme: str = None) -> str:
    """
    Generate the prompt for creating AI music video segments from song lyrics
    
    Args:
        song_lyrics: The complete song lyrics
        song_length: Song length in seconds
        background_voice_needed: Whether background narration/voice is needed
        additional_dialogues: Optional dialogues to add between verses
        custom_character_roster: Optional user-provided character roster
        music_genre: Optional music genre
        visual_theme: Optional visual theme/concept
        
    Returns:
        str: The formatted prompt
    """
    # Build custom character roster instruction if provided
    custom_roster_instruction = ""
    if custom_character_roster and len(custom_character_roster) > 0:
        import json
        roster_json = json.dumps(custom_character_roster, indent=2)
        custom_roster_instruction = f"""
    
    **MANDATORY CHARACTER ROSTER FOR MUSIC VIDEO**:
    You MUST use the following pre-defined characters in the music video:
    
    {roster_json}
    
    These characters are the performers/actors in the music video and must appear throughout.
    Ensure visual consistency across all segments - use EXACT same descriptions.
    """
    
    # Build additional dialogues instruction if provided
    dialogues_instruction = ""
    if additional_dialogues and len(additional_dialogues) > 0:
        import json
        dialogues_json = json.dumps(additional_dialogues, indent=2)
        dialogues_instruction = f"""
    
    **ADDITIONAL DIALOGUES TO INCLUDE**:
    The user wants to add these dialogues at specific timestamps in the music video:
    
    {dialogues_json}
    
    Create separate segments for these dialogues at the specified timestamps.
    These should be dramatic moments that complement the song.
    """
    
    # Build genre and theme instructions
    genre_instruction = f"\n    **Music Genre**: {music_genre}" if music_genre else ""
    theme_instruction = f"\n    **Visual Theme/Concept**: {visual_theme}" if visual_theme else ""
    
    # Calculate approximate number of segments based on song length
    # Assuming 8-10 seconds per segment on average
    suggested_segments = max(int(song_length / 8), 1)
    
    return f"""
    You are a professional Music Video Director and Cinematographer specializing in AI-generated music videos.
    
    Your expertise is creating visually stunning, emotionally powerful music videos that perfectly sync with song lyrics.
    You understand how to translate music and lyrics into compelling visual narratives for AI video generation (Veo3).
    {custom_roster_instruction}
    {dialogues_instruction}
    {genre_instruction}
    {theme_instruction}

    **MUSIC VIDEO CHARACTERISTICS**:
    - **Song Length**: {song_length} seconds
    - **Suggested Segments**: {suggested_segments} (adjust based on song structure)
    - **Background Voice**: {"YES - Include background narration/voiceover" if background_voice_needed else "NO - Only song lyrics"}
    - **Format**: Cinematic music video optimized for AI generation
    - **Style**: Professional, visually stunning, emotionally engaging
    
    **MUSIC VIDEO STRUCTURE**:
    - **Intro**: Visual hook that sets the mood (0-10 seconds)
    - **Verses**: Story progression, character development
    - **Chorus**: High-energy, memorable visuals (repeatable)
    - **Bridge**: Emotional peak or visual twist
    - **Outro**: Powerful closing image
    
    **VISUAL STORYTELLING FOR MUSIC VIDEOS**:
    - Sync visuals with lyrics and music beats
    - Use cinematic camera movements (dolly, crane, tracking)
    - Create visual metaphors for lyrical themes
    - Build emotional intensity through visuals
    - Use lighting and color to convey mood
    - Include performance shots (if characters are performers)
    - Add narrative/story elements between performances
    
    **CINEMATIC CAMERA REQUIREMENTS**:
    ALL camera work must be CINEMATIC and MUSIC VIDEO STYLE:
    - **Performance Shots**: Close-ups of singing, wide shots of dancing, dynamic angles
    - **Narrative Shots**: Story moments that illustrate lyrics
    - **Artistic Shots**: Abstract visuals, slow-motion, creative angles
    - **Movement**: Constant motion - dolly, crane, steadicam, orbital
    - **Cuts**: Match cuts to music beats, rhythm-based editing
    
    Task:
    Create a complete AI music video prompt based on these song lyrics:
    
    ```
    {song_lyrics}
    ```
    
    **CRITICAL REQUIREMENTS**:
    
    1. **Lyric Synchronization**: Each segment must align with specific lyrics
    2. **Timing Accuracy**: Segment durations must add up to {song_length} seconds
    3. **Visual Variety**: Mix performance, narrative, and artistic shots
    4. **Emotional Arc**: Build emotional intensity throughout the video
    5. **Character Consistency**: If using characters, maintain exact visual descriptions
    6. **AI-Ready**: Detailed descriptions for Veo3 video generation
    7. **Music Video Style**: Professional, cinematic, visually stunning
    
    **SEGMENT TIMING GUIDELINES**:
    - Intro/Outro: 5-10 seconds
    - Verse segments: 8-12 seconds
    - Chorus segments: 8-10 seconds (repeatable visuals)
    - Bridge: 8-12 seconds
    - Dialogue segments (if any): 5-8 seconds
    
    **OUTPUT FORMAT** (JSON):
    {{
      "title": "Song Title - Music Video",
      "artist": "Artist Name (if mentioned in lyrics)",
      "song_length": {song_length},
      "total_segments": "Number of segments",
      "music_genre": "{music_genre or 'Not specified'}",
      "visual_theme": "{visual_theme or 'Lyric-based narrative'}",
      "short_summary": "Brief description of the music video concept",
      "description": "Compelling description for viewers",
      "hashtags": ["#MusicVideo", "#AIGenerated", "#Veo3", "#ViralMusic", genre-specific tags],
      "background_voice_info": {{
        "enabled": {str(background_voice_needed).lower()},
        "voice_type": "Narrator/Character voice type",
        "tone": "Tone of background voice",
        "purpose": "Why background voice is used"
      }},
      "characters_roster": [
        {{{{
          "name": "Character Name",
          "physical_appearance": {{{{
            "gender": "male/female/non-binary/unknown - be explicit",
            "estimated_age": "exact age like '28 years old' or narrow range '25-27'",
            "height": "exact measurement like '5\\'8\\\" / 173cm' or '6\\'2\\\" / 188cm'",
            "weight_build": "specific like '165 lbs, athletic build' or '180 lbs, muscular'",
            "body_type": "very specific: 'lean athletic', 'muscular mesomorph', 'slim ectomorph', 'curvy hourglass', etc.",
            "skin_details": {{{{
              "skin_tone": "ultra-specific: 'warm honey beige', 'cool porcelain', 'deep mahogany', 'olive tan', 'fair with pink undertones'",
              "skin_texture": "smooth/textured/freckled/clear/etc.",
              "skin_undertone": "warm/cool/neutral - specify",
              "complexion_details": "any blemishes, freckles, beauty marks - exact locations",
              "skin_condition": "matte/dewy/oily/dry appearance"
            }}}},
            "face_structure": {{{{
              "face_shape": "oval/round/square/heart/diamond/oblong - be precise",
              "forehead": "high/medium/low, wide/narrow, any lines",
              "eyebrows": "exact shape: 'thick straight', 'arched thin', 'bushy natural', color, thickness",
              "eyes_detailed": {{{{
                "eye_color": "ultra-specific: 'hazel with gold flecks', 'steel blue-gray', 'warm chocolate brown'",
                "eye_shape": "almond/round/hooded/monolid/deep-set/protruding",
                "eye_size": "large/medium/small relative to face",
                "eyelid_type": "single/double/hooded",
                "eyelashes": "long/short/thick/sparse, natural/mascara",
                "eye_spacing": "close-set/wide-set/average",
                "under_eye": "bags/dark circles/smooth - describe"
              }}}},
              "nose_detailed": {{{{
                "nose_shape": "straight/aquiline/button/roman/snub/bulbous",
                "nose_size": "small/medium/large relative to face",
                "nose_bridge": "high/low/wide/narrow",
                "nostrils": "flared/narrow/round"
              }}}},
              "cheeks_detailed": {{{{
                "cheekbone_prominence": "high/low/prominent/subtle",
                "cheek_fullness": "full/hollow/average",
                "dimples": "yes/no, location if yes"
              }}}},
              "mouth_lips_detailed": {{{{
                "lip_shape": "full/thin/bow-shaped/heart-shaped/wide",
                "lip_size": "upper and lower - be specific",
                "lip_color": "natural pink/rose/brown/red tones",
                "mouth_width": "wide/narrow/proportionate",
                "teeth": "visible/hidden, straight/gap/etc.",
                "smile_type": "wide/subtle/crooked/symmetric"
              }}}},
              "jaw_chin_detailed": {{{{
                "jawline": "sharp/soft/square/rounded/defined",
                "jaw_width": "wide/narrow/proportionate",
                "chin_shape": "pointed/rounded/square/cleft",
                "chin_prominence": "receding/prominent/average"
              }}}},
              "ears": {{{{
                "ear_size": "small/medium/large",
                "ear_shape": "attached/detached lobes, etc."
              }}}}
            }}}},
            "head_skull_shape": {{{{
              "head_size": "large/medium/small relative to body",
              "head_shape": "round/oval/square/long/etc.",
              "skull_prominence": "flat back/rounded/prominent occipital bone",
              "cranium_height": "high/medium/low crown"
            }}}},
            "hair_details": {{{{
              "hair_presence": "full head of hair/thinning/balding/completely bald",
              "baldness_pattern": "if applicable: 'male pattern baldness with receding temples', 'bald crown with side hair', 'completely smooth bald', 'thinning on top', 'no baldness'",
              "hair_density": "thick coverage/normal/sparse/very thin/bald patches",
              "hair_color": "ultra-specific: 'ash blonde with platinum highlights', 'jet black with blue undertones', 'auburn with copper tones', 'silver-gray', 'salt and pepper', 'dyed vs natural'",
              "hair_color_variations": "roots showing, highlights, lowlights, gray streaks, fading",
              "hair_length": "exact: 'shoulder-length', 'mid-back', 'chin-length bob', 'buzz cut 1/4 inch', 'completely shaved/bald'",
              "hair_texture": "straight/wavy/curly/coily - specify curl pattern like 2A, 3B, 4C, or 'no hair/bald'",
              "hair_thickness": "fine/medium/thick/coarse strands, or 'no hair'",
              "hair_volume": "flat/voluminous/medium, or 'bald/no volume'",
              "hair_style": "exact description: 'center-parted long layers', 'side-swept bangs with ponytail', 'slicked back undercut', 'buzz cut', 'completely bald and shaved', 'bald with horseshoe pattern'",
              "hair_condition": "shiny/matte/frizzy/sleek/greasy/dry, or 'smooth bald scalp'",
              "hairline": "straight/widow\\'s peak/receding/high/low/completely receded/no hairline if bald",
              "hair_part": "center/side/no part/zigzag, or 'no part - bald'",
              "scalp_visibility": "scalp showing through hair/no scalp visible/completely visible if bald",
              "scalp_condition": "if visible or bald: smooth/textured/shiny/matte/freckled/scarred",
              "facial_hair": "if applicable - exact style: 'full beard', 'goatee', 'mustache', 'stubble', 'clean shaven', length, color, coverage, thickness, grooming style",
              "facial_hair_pattern": "even/patchy/sparse/thick, exact areas covered",
              "eyebrow_hair": "ensure consistency with head hair color"
            }}}},
            "neck_shoulders": {{{{
              "neck_length": "long/short/average",
              "neck_width": "thin/thick/proportionate",
              "shoulder_width": "broad/narrow/average",
              "shoulder_shape": "rounded/square/sloped"
            }}}},
            "hands_arms": {{{{
              "arm_length": "long/short/proportionate",
              "arm_musculature": "toned/soft/muscular/thin",
              "hand_size": "large/small/proportionate",
              "finger_length": "long/short/average",
              "nails": "short/long, manicured/natural, color"
            }}}},
            "distinctive_marks": {{{{
              "scars": "location, size, shape, color",
              "tattoos": "exact design, location, size, colors",
              "birthmarks": "location, size, shape, color",
              "moles_beauty_marks": "exact facial/body locations",
              "piercings": "type, location, jewelry description",
              "other_identifiers": "any other unique features"
            }}}},
            "facial_expression": "current expression in the image - be very specific",
            "pose_and_posture": "how they're positioned/standing/sitting - exact description"
          }}}},
          "clothing_style": {{{{
            "primary_outfit": {{{{
              "top_garment": "exact type, fit, fabric, color, pattern, condition",
              "bottom_garment": "exact type, fit, fabric, color, pattern, length",
              "outerwear": "jacket/coat - exact style, length, color, material",
              "footwear": "exact type, color, material, condition, heel height if applicable",
              "undergarments_visible": "if any parts visible - straps, waistbands, etc."
            }}}},
            "clothing_details": {{{{
              "fabric_type": "cotton/silk/leather/denim/wool - be specific",
              "fabric_texture": "smooth/rough/shiny/matte/textured",
              "fit_style": "tight/loose/fitted/oversized/tailored",
              "clothing_condition": "new/worn/vintage/distressed/pristine",
              "layering": "describe each visible layer from inner to outer",
              "closures": "buttons/zippers/laces - describe",
              "pockets": "visible pockets, flaps, etc.",
              "seams_stitching": "visible details, decorative stitching"
            }}}},
            "color_palette": {{{{
              "primary_colors": "exact shades: 'navy blue #001f3f', 'burgundy red', 'forest green'",
              "secondary_colors": "accent colors, patterns",
              "color_combinations": "how colors work together",
              "color_wear_patterns": "fading, stains, variations"
            }}}},
            "accessories": {{{{
              "jewelry": "exact pieces: 'silver chain necklace 18 inches', 'gold hoop earrings 1 inch diameter'",
              "watches_timepieces": "brand style, wrist, exact appearance",
              "bags_carried": "type, size, color, material, how carried",
              "belts": "width, color, buckle style, material",
              "hats_headwear": "exact style, color, how worn",
              "scarves_neckwear": "material, color, how tied/worn",
              "glasses_eyewear": "frame style, color, lens type",
              "gloves": "if worn - material, length, color",
              "weapons_tools": "exact type, how carried/worn, condition"
            }}}},
            "style_characteristics": {{{{
              "overall_aesthetic": "modern/vintage/fantasy/professional/casual/etc.",
              "fashion_era": "if period-specific - exact era and region",
              "cultural_influences": "specific cultural elements in clothing",
              "personal_style_markers": "signature pieces, unique combinations",
              "formality_level": "very formal/business/casual/athletic/etc.",
              "weather_appropriateness": "summer/winter/all-season wear"
            }}}},
            "clothing_consistency_notes": "which items never change, which might vary, how clothing moves"
          }}}},
          "personality": "key personality traits inferred from appearance (e.g., 'confident, mysterious, friendly')",
          "role": "suggested role in story (e.g., 'protagonist', 'antagonist', 'mentor', 'comic relief')",
          "voice_mannerisms": {{{{
            "speaking_style": "confident/shy/authoritative/playful/etc.",
            "accent_or_tone": "neutral/regional/foreign/etc.",
            "typical_expressions": "facial expressions and gestures they might use"
          }}}},
          "video_prompt_description": "ULTRA-COMPLETE description combining ALL above details in a single comprehensive paragraph for video generation - must include EVERY physical feature, skin detail, facial feature, hair characteristic, and clothing item to ensure ZERO variation between segments. This should be a complete, standalone description that can be used directly for video generation."
        }}}}
      ],
      "segments": [
        {{
          "segment": 1,
          "segment_type": "intro/verse/chorus/bridge/outro/dialogue",
          "start_time": 0,
          "end_time": 10,
          "duration": 10,
          "lyrics": "Lyrics for this segment",
          "scene": "Visual scene description",
          "visual_concept": "What this segment represents visually",
          "camera": "CINEMATIC camera movement (dolly, crane, tracking, etc.)",
          "shot_type": "performance/narrative/artistic/mixed",
          "characters_present": ["char_id1"],
          "character_actions": {{
            "char_id1": "What the character is doing (singing, dancing, acting)"
          }},
          "background_definition": {{
            "location": "Specific location",
            "environment_type": "Studio/Outdoor/Urban/Fantasy/etc.",
            "setting_description": "Detailed setting",
            "time_of_day": "Time of day",
            "weather_conditions": "Weather",
            "lighting": "Lighting setup (dramatic, colorful, natural)",
            "atmosphere": "Mood and atmosphere",
            "key_visual_elements": ["Stage", "Lights", "Props"],
            "color_palette": "Color scheme for this segment",
            "props": ["Microphone", "Guitar", "etc."],
            "video_prompt_background": "Complete background description for AI"
          }},
          "visual_style": "Cinematic/Artistic/Performance/Narrative",
          "mood": "Emotional mood",
          "color_grading": "Color grading style (warm, cool, vibrant, desaturated)",
          "special_effects": ["Slow-motion", "Light flares", "etc."],
          "sync_notes": "How visuals sync with music/lyrics",
          "background_voice": "Background narration text (if enabled)",
          "editing_style": "Fast cuts/Smooth transitions/Match cuts to beat"
        }}
      ],
      "visual_themes": [
        "Main visual themes throughout the video"
      ],
      "color_palette_overall": "Overall color scheme for the music video",
      "editing_notes": "Overall editing style and rhythm",
      "performance_notes": "Notes about performance style and energy"
    }}
    
    **MUSIC VIDEO BEST PRACTICES**:
    
    1. **Lyric Visualization**: Create visual metaphors for abstract lyrics
    2. **Rhythm Matching**: Sync camera movements and cuts to music beats
    3. **Emotional Peaks**: Build to visual climaxes during chorus/bridge
    4. **Repetition with Variation**: Chorus visuals can repeat but with variations
    5. **Story Arc**: Even abstract videos should have beginning, middle, end
    6. **Performance Energy**: Match visual energy to song energy
    7. **Memorable Moments**: Create iconic shots that define the video
    
    **VISUAL CONCEPTS BY GENRE**:
    - **Pop**: Colorful, energetic, performance-focused, upbeat
    - **Rock**: Edgy, high-energy, dramatic lighting, powerful
    - **Hip-Hop**: Urban settings, confident performances, stylish
    - **R&B**: Smooth, sensual, intimate lighting, emotional
    - **Electronic**: Abstract, futuristic, light effects, surreal
    - **Ballad**: Emotional, intimate, story-driven, cinematic
    - **Country**: Natural settings, authentic, storytelling
    
    **CAMERA MOVEMENTS FOR MUSIC VIDEOS**:
    - **Intro**: Slow reveal, crane up, dolly in
    - **Verse**: Steady tracking, medium shots, story focus
    - **Chorus**: Dynamic movement, orbital shots, wide to close
    - **Bridge**: Dramatic push-in, crane shots, emotional close-ups
    - **Outro**: Pull back, crane up, final wide shot
    
    **PERFORMANCE SHOT TYPES**:
    - Close-up of face while singing (emotional connection)
    - Wide shot of full performance (energy and movement)
    - Instrument close-ups (if applicable)
    - Dance/movement shots (dynamic angles)
    - Crowd/audience reactions (if applicable)
    - Behind-the-scenes style (intimate, raw)
    
    **NARRATIVE SHOT TYPES**:
    - Story moments that illustrate lyrics
    - Character interactions
    - Symbolic/metaphorical visuals
    - Location establishing shots
    - Emotional reaction shots
    
    **ARTISTIC SHOT TYPES**:
    - Abstract visuals
    - Slow-motion beauty shots
    - Light and shadow play
    - Reflections and mirrors
    - Silhouettes
    - Creative angles and perspectives
    
    Generate a complete music video prompt that will create a visually stunning, emotionally powerful AI-generated music video.
    Each segment should be perfectly timed to the song and ready for Veo3 video generation.
    
    Return ONLY valid JSON without any markdown formatting or code blocks.
    """
