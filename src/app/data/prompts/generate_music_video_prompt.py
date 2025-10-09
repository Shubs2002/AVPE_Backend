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
        {{
          "id": "char_unique_id",
          "name": "Character/Performer Name",
          "role": "Lead Singer/Dancer/Actor/etc.",
          "physical_appearance": {{
            "gender": "Male/Female",
            "age": "Age",
            "height": "Height",
            "body_type": "Body type",
            "skin_tone": "Detailed skin tone",
            "hair_color": "Hair color",
            "hair_style": "Hair style",
            "eye_color": "Eye color",
            "facial_features": "Detailed facial features",
            "distinctive_marks": "Any unique features"
          }},
          "clothing_style": {{
            "primary_outfit": "Main outfit for music video",
            "style": "Fashion style",
            "colors": "Color scheme",
            "accessories": "Accessories"
          }},
          "performance_style": "How they perform (energetic, emotional, etc.)",
          "video_prompt_description": "ULTRA-DETAILED description for AI - every visual detail"
        }}
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
