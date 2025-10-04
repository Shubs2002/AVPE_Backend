"""
Prompts for AI content generation services - Story Segment Generation

This module contains all prompts used for generating story segments for video content.
The prompts are organized by their use case:

1. get_story_segments_prompt: 
   - Used for standard story generation (up to 20 segments)
   - Generates complete story with metadata, characters, and all segments in one call
   
2. get_outline_for_story_segments_chunked:
   - Used for large stories (100+ segments) - STEP 1 of chunked generation
   - Generates story outline, metadata, characters, and plot points
   - Parses special requirements (no narrations, cliffhangers, adult content)
   
3. get_chunk_segments_prompt:
   - Used for large stories (100+ segments) - STEP 2 of chunked generation
   - Generates a specific chunk of segments (typically 15 at a time)
   - Uses the outline and metadata from step 1 to maintain consistency
   
4. get_story_segments_in_sets_prompt:
   - Used for moderate-sized stories (20-100 segments) - Set-based generation
   - Generates complete metadata + specific segment range in one call
   - Each set includes full story context (title, characters, etc.) for consistency
   - Different from chunked: Each set is self-contained with metadata
"""

def get_story_segments_prompt(idea: str, num_segments: int) -> str:
    """
    Generate the prompt for creating story segments
    
    Args:
        idea: The story idea/concept
        num_segments: Number of segments to generate
        
    Returns:
        str: The formatted prompt
    """
    return f"""
    You are a professional Humanised Script-writer for viral films.
    you can add more custom fields for generating the best results as i am gonna feed your generated output into veo3 video generation model.

    Task:
    - Create a story for all ages idea based on: "{idea}"
    - Write a **short_summary** (2–3 sentences) giving a quick overview of the story.
    - Create a **catchy title** (under 60 chars) designed for maximum clicks on YouTube Shorts / Instagram Reels / TikTok.
    - Write a **viral description** (2–3 sentences). It should:
       * Hook viewers emotionally or with curiosity
       * Summarize the story briefly
       * End with a call-to-action like "Follow for more" or "Watch till the end!"
    - Break it into {num_segments} segments, each ~8s long (to fit Veo3 max length).
    - **The first segment must always be an INTRO scene**:
       * Title reveal in overlay text
       * Main characters introduction
       * Setting the tone 
    - Generate a list of **hashtags** (7–15). Mix general trending tags (#fyp, #viral, #shorts) with niche/story-related ones.
    - **Story continuity is critical**:
        * The same main characters must appear in all segments.
        * Each segment should logically follow the previous one.
        * The final segment must provide closure or a twist.
    - First, define a **characters_roster** (2–5 characters) with DETAILED descriptions for video generation consistency:
        * id (short unique tag like "hero1")
        * name
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
          - clothing_style (medieval, modern, fantasy, etc.)
          - colors (specific color palette for the character)
          - accessories (jewelry, weapons, tools, etc.)
        * personality (key traits for acting/expressions)
        * role (function in the story)
        * **Voice & Mannerisms** (for dialogue segments):
          - speaking_style (confident/shy/authoritative/etc.)
          - accent_or_tone (if applicable)
          - typical_expressions (facial expressions, gestures)
    - **NARRATOR VOICE SELECTION** for story segments:
        * **Primary Narrator**: Choose ONE consistent narrator voice for the ENTIRE story based on genre and target audience:
          - **Epic/Adventure Stories**: Deep, authoritative male voice (ages 30-50) with clear diction
          - **Romance/Drama**: Warm, emotional voice (male/female 25-40) with expressive tone
          - **Children's Stories (3-8)**: Sweet, animated female voice (25-35) like CoComelon - high-pitched, sing-song, very expressive
          - **Kids Stories (8-12)**: Friendly, energetic voice (female 25-35) with playful but clear delivery
          - **Teen Stories (13-17)**: Relatable, cool voice (male/female 20-30) with modern appeal
          - **Mystery/Thriller**: Mysterious, suspenseful voice (male 35-45) with dramatic pauses
          - **Fantasy**: Mystical, enchanting voice (male/female 30-45) with ethereal quality
          - **Historical**: Distinguished, scholarly voice (male 40-55) with refined accent
          - **Educational Kids**: Patient, encouraging teacher voice (female 28-40) with clear pronunciation
          - **Bedtime Stories**: Soft, soothing voice (female 30-40) with gentle, calming tone
        * **CONSISTENCY RULE**: The same narrator voice must be used throughout ALL story segments. Only tone and emotion can vary slightly per segment to match the scene's mood.
        * **Target Age Demographics**: 
          - **Toddlers (2-5)**: High-pitched, animated, sing-song voices like children's TV shows
          - **Young Kids (6-10)**: Cheerful, clear voices with animated expressions and sound effects
          - **Tweens (11-14)**: Fun but mature voices that don't talk down to them
          - **Teens (15-17)**: Cool, relatable voices with contemporary speech patterns
          - **Gen Z (18-24)**: Energetic, authentic voices with internet culture awareness
          - **Millennials (25-40)**: Professional yet approachable voices
          - **Gen X (41-56)**: Mature, trustworthy voices with authority
          - **Boomers (57+)**: Classic, clear voices with traditional appeal
        * **Narration Voice Styles**:
          - **Storyteller Style**: Theatrical, expressive with character voices and sound effects
          - **Documentary Style**: Authoritative, informative with clear pacing
          - **Conversational Style**: Friendly, casual like talking to a friend
          - **Educational Style**: Patient, clear with emphasis on learning
          - **Dramatic Style**: Intense, emotional with dynamic range
          - **Whimsical Style**: Playful, magical with varied inflections
    - **CRITICAL TIMING RULE**: Each segment must fit within exactly 8 seconds of speech time.
    - **NARRATION vs DIALOGUE RULE**: Each segment must contain EITHER narration OR dialogue, NEVER both together.
    - **WORD COUNT LIMITS**: 
      * Narration segments: Maximum 25 words (3 words per second × 8 seconds)
      * Dialogue segments: Maximum 25 words total across all characters
      * Count every word including articles (a, an, the) and conjunctions
    - **CONTENT DISTRIBUTION**: Alternate between narration and dialogue segments for variety
    - **SPEECH PACING**: Assume normal speaking pace of 3 words per second for timing calculations
    - **VIDEO GENERATION CONTINUITY**: 
      * Character descriptions must be IDENTICAL across all segments for visual consistency
      * Background elements should maintain continuity (same location features, lighting style, etc.)
      * Include complete "video_prompt_description" for each character and "video_prompt_background" for each scene
      * These descriptions should be detailed enough to generate consistent visuals when used separately
      * Specify exact colors, positions, and visual elements that must remain constant
    - For each segment, provide:
        * Scene description (location, atmosphere, key action)
        * **Choose ONE storytelling method per segment**:
          - **NARRATION SEGMENT**: Pure storytelling voice describing atmosphere, actions, emotions (8 seconds max)
          - **DIALOGUE SEGMENT**: Characters speaking directly (8 seconds max total for all dialogue)
        * If narration: Write 1-2 sentences that can be spoken in 8 seconds (approximately 20-25 words)
        * If dialogue: Write short, impactful lines using this structure:
          [{{"character": "id", "line": "..."}}] - Total dialogue must fit in 8 seconds
        * Narration to dialogue ratio: Aim for roughly 10/90 split across the entire story
        * Ensure clear character identification using roster ids for dialogue segments
        * Characters present (with short traits: look, personality, role)
        * Camera perspective / animation style
        * **Speech timing**: Count words to ensure 8-second limit (average 3 words per second)
    Return ONLY valid JSON with this EXACT structure:
    {{{{
      "title": "...",
      "short_summary": "...",
      "description": "...",
      "hashtags": ["...", "...", "..."],
      "narrator_voice": {{{{
        "voice_type": "...", # deep_male, warm_female, cute_animated_female, friendly_kids, cool_teen, etc.
        "age_range": "...", # 25-35, 30-45, 40-55, etc.
        "accent": "...", # neutral, british, american_southern, kids_tv_american, etc.
        "tone": "...", # dramatic, warm, mysterious, epic, gentle, animated_cute, playful
        "target_demographic": "...", # Toddlers, Young Kids, Tweens, Teens, Gen Z, Millennials, Gen X, Boomers
        "speaking_pace": "...", # slow_dramatic, moderate, fast_energetic, sing_song_animated
        "narration_style": "...", # storyteller, documentary, conversational, educational, dramatic, whimsical
        "child_friendly_level": "...", # none, mild, moderate, high, cocomelon_style
        "voice_pitch": "...", # very_high_cute, high_animated, medium, low_warm, very_low_authoritative
        "expressiveness": "...", # minimal, moderate, high_animated, very_expressive_kids_tv
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
            "typical_expressions": "..."
          }}}},
          "video_prompt_description": "..." # Complete description for video generation
        }}}}
      ],
      "segments": [
        {{{{
          "segment": 1,
          "scene": "...",
          "overlay_text": "...", # optional, text to appear on screen, e.g. title in intro
          "overlay_text_position": "...", # optional, position of the text to appear on the screen
          "overlay_text_style": "...", # optional, style of the text to appear on the screen, e.g. bold, italic, etc.
          "overlay_text_duration": "...", # optional duration in seconds for which the overlay text should appear on screen
          "overlay_text_animation": "...", # optional animation style for the overlay text, e.g. fade in, slide in, etc.
          "overlay_text_color": "...", # optional color of the overlay text
          "overlay_text_font": "...", # optional font of the overlay text
          "content_type": "...", # REQUIRED: either "narration" or "dialogue"
          "narration": "...", # ONLY if content_type is "narration" - max 25 words (8 seconds)
          "narrator_voice_for_segment": {{{{  # ONLY if content_type is "narration"
            "voice_type": "...", # MUST be same as main narrator_voice selection
            "tone_variation": "...", # slight tone adjustment for this segment (dramatic, gentle, excited, etc.)
            "pace_variation": "...", # slight pace adjustment (slightly_faster, slightly_slower, same)
            "emotion": "...", # emotional delivery for this segment (suspenseful, warm, mysterious, etc.)
            "emphasis": "...", # what to emphasize in this segment
            "consistency_note": "Same narrator voice as previous segments, only tone/emotion varies"
          }}}},
          "dialogue": [
            {{"character": "hero1", "line": "..."}},
            {{"character": "villain1", "line": "..."}}
          ], # ONLY if content_type is "dialogue" - total max 25 words (8 seconds)
          "characters_present": ["hero1", "villain1"],
          "camera": "...",
          "clip_duration": 8, # always 8 seconds
          "word_count": "...", # actual word count to verify 8-second limit
          "estimated_speech_time": "...", # estimated seconds (should be ≤8)
          "background_definition": {{{{
            "location": "...", # specific location name/type
            "environment_type": "...", # indoor/outdoor/fantasy/realistic
            "setting_description": "...", # detailed visual description for video generation
            "time_of_day": "...", # morning/afternoon/evening/night
            "weather_conditions": "...", # sunny/cloudy/rainy/stormy
            "lighting": "...", # natural/artificial/magical/dim/bright
            "atmosphere": "...", # peaceful/tense/mysterious/cheerful
            "key_visual_elements": ["..."], # important background objects/features
            "color_palette": "...", # dominant colors for the scene
            "architectural_style": "...", # if applicable - medieval/modern/fantasy
            "natural_elements": ["..."], # trees/mountains/water/etc.
            "props_in_background": ["..."], # objects that should appear consistently
            "scale": "...", # intimate/vast/medium - helps with camera framing
            "continuity_notes": "...", # what must remain consistent across segments
            "video_prompt_background": "..." # Complete background description for video generation
          }}}},
          "background_music": "...", # optional
          "sound_effects": ["..."], # optional
          "visual_style": "...", # optional
          "transitions": "...", # optional
          "props": ["..."], # optional
          "emotions": ["..."], # optional
          "lighting": "...", # optional
          "color_palette": "...", # optional
          "special_effects": ["..."], # optional
          "clothing": ["..."], # optional
          "time_of_day": "...", # optional
          "weather": "...", # optional
          "cultural_elements": ["..."], # optional
          "historical_context": "...", # optional
          "genre": "...", # optional
          "themes": ["..."], # optional
          "mood": "...", # optional
          "pacing": "...", # optional
          "narrative_techniques": ["..."], # optional
          "symbolism": ["..."], # optional
          "foreshadowing": ["..."] # optional
        }}}}
      ]
    }}}}
    """

def get_outline_for_story_segments_chunked(idea: str, num_segments: int, no_narrations: bool, narration_only_first: bool, cliffhanger_interval: int, adult_story: bool) -> str:
    """
    Generate the prompt for creating a story outline and metadata for chunked segment generation.
    This is the first step in the chunked generation process for large stories (100+ segments).
    
    Args:
        idea: The story idea/concept
        num_segments: Total number of segments for the complete story
        no_narrations: Whether narrations are completely disabled
        narration_only_first: Whether only the first segment can have narration
        cliffhanger_interval: Interval at which to add cliffhangers (e.g., every 150 segments)
        adult_story: Whether this is adult content vs family-friendly
        
    Returns:
        str: The formatted prompt for generating story outline and metadata
    """
    
    return f"""
      You are a professional Humanised Script-writer for viral films.
      
      Task: Create a story outline and metadata for: "{idea}"
      
      Requirements:
      - Write a **short_summary** (2–3 sentences) giving a quick overview of the story.
      - Create a **catchy title** (under 60 chars) designed for maximum clicks on YouTube Shorts / Instagram Reels / TikTok.
      - Write a **viral description** (2–3 sentences). It should:
        * Hook viewers emotionally or with curiosity
        * Summarize the story briefly
        * End with a call-to-action like "Follow for more" or "Watch till the end!"
      - Generate a list of **hashtags** (7–15). Mix general trending tags (#fyp, #viral, #shorts) with niche/story-related ones.
      - Define a **characters_roster** (2–5 characters) with DETAILED descriptions for video generation consistency
      - Create a **story_outline** breaking the story into {num_segments} brief plot points
      - **NARRATOR VOICE SELECTION** for story segments
      - Parse the idea for special requirements:
        * "NO Narrations" or "ONLY 1st segment can have narration" 
        * "cliffhangers at every 150th segment" or similar patterns
        * "adults story" vs family-friendly content
      
      Return ONLY valid JSON with this structure:
      {{
        "title": "...",
        "short_summary": "...",
        "description": "...",
        "hashtags": ["...", "...", "..."],
        "narrator_voice": {{
          "voice_type": "...",
          "age_range": "...",
          "accent": "...",
          "tone": "...",
          "target_demographic": "...",
          "speaking_pace": "...",
          "narration_style": "...",
          "child_friendly_level": "...",
          "voice_pitch": "...",
          "expressiveness": "...",
          "voice_description": "..."
        }},
        "characters_roster": [
          {{
            "id": "...",
            "name": "...",
            "physical_appearance": {{
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
            }},
            "clothing_style": {{
              "primary_outfit": "...",
              "clothing_style": "...",
              "colors": "...",
              "accessories": "..."
            }},
            "personality": "...",
            "role": "...",
            "voice_mannerisms": {{
              "speaking_style": "...",
              "accent_or_tone": "...",
              "typical_expressions": "..."
            }},
            "video_prompt_description": "..."
          }}
        ],
        "story_outline": [
          "Plot point 1: ...",
          "Plot point 2: ...",
          "... (continue for {num_segments} plot points)"
        ],
        "special_requirements": {{
          "no_narrations": {str(no_narrations).lower()},
          "narration_only_first": {str(narration_only_first).lower()},
          "cliffhanger_intervals": {cliffhanger_interval},
          "adult_story": {str(adult_story).lower()}
        }}
      }}
      """


def get_chunk_segments_prompt(
    chunk_segments: int,
    chunk_start: int,
    chunk_end: int,
    story_title: str,
    story_summary: str,
    character_names: list,
    plot_points: list,
    no_narrations: bool,
    narration_only_first: bool,
    cliffhanger_interval: int,
    cliffhanger_segments: list
) -> str:
    """
    Generate the prompt for creating a specific chunk of story segments.
    This is used in the chunked generation process to generate segments in batches.
    
    Args:
        chunk_segments: Number of segments in this chunk
        chunk_start: Starting segment number (0-indexed)
        chunk_end: Ending segment number (0-indexed)
        story_title: Title of the story
        story_summary: Short summary of the story
        character_names: List of character names
        plot_points: List of plot points for this chunk
        no_narrations: Whether narrations are completely disabled
        narration_only_first: Whether only the first segment can have narration
        cliffhanger_interval: Interval at which to add cliffhangers
        cliffhanger_segments: List of segment numbers that should have cliffhangers in this chunk
        
    Returns:
        str: The formatted prompt for generating this chunk of segments
    """
    
    return f"""
    Generate EXACTLY {chunk_segments} detailed story segments (segments {chunk_start + 1} to {chunk_end}) for the story "{story_title}".
    
    CRITICAL: You must generate exactly {chunk_segments} segments, no more, no less.
    
    Story Context:
    - Title: {story_title}
    - Summary: {story_summary}
    - Characters: {character_names}
    
    Plot Points for this chunk:
    {chr(10).join([f"{i+chunk_start+1}. {point}" for i, point in enumerate(plot_points)])}
    
    Special Requirements:
    - No narrations allowed: {no_narrations}
    - Narration only in first segment: {narration_only_first}
    - Add cliffhangers every {cliffhanger_interval} segments: {cliffhanger_interval > 0}
    - Cliffhanger segments in this chunk: {cliffhanger_segments}
    
    Rules:
    - Each segment must be exactly 8 seconds long
    - Use ONLY dialogue (no narration) unless it's segment 1 and narration_only_first is true
    - For segments {cliffhanger_segments}, end with dramatic cliffhangers that leave viewers wanting more
    - Maintain character consistency using the established roster
    - Each segment should advance the plot meaningfully
    - Keep dialogue concise and impactful (max 25 words per segment)
    
    Return ONLY a JSON array of segments:
    [
      {{{{
        "segment": {chunk_start + 1},
        "scene": "...",
        "content_type": "dialogue",
        "dialogue": [
          {{"character": "char_id", "line": "..."}}
        ],
        "characters_present": ["char_id1", "char_id2"],
        "camera": "...",
        "clip_duration": 8,
        "word_count": "...",
        "estimated_speech_time": "...",
        "background_definition": {{{{
          "location": "...",
          "environment_type": "...",
          "setting_description": "...",
          "time_of_day": "...",
          "weather_conditions": "...",
          "lighting": "...",
          "atmosphere": "...",
          "key_visual_elements": ["..."],
          "color_palette": "...",
          "video_prompt_background": "..."
        }}}}
      }}}}
    ]
    """


def get_story_segments_in_sets_prompt(
    idea: str,
    set_number: int,
    total_segments: int,
    segments_per_set: int,
    actual_segments_in_set: int,
    start_segment: int,
    end_segment: int,
    no_narrations: bool,
    narration_only_first: bool,
    cliffhanger_segments: list,
    adult_story: bool
) -> str:
    """
    Generate the prompt for creating a specific set of story segments with complete metadata.
    This is used when generating stories in sets (e.g., 10 segments per set) where each set
    includes the full story metadata (title, characters, etc.) along with the specific segments.
    
    This approach is different from chunked generation:
    - Chunked: Generates outline first, then segments in chunks (for 100+ segments)
    - Sets: Generates complete metadata + specific segment range in one call (for moderate segment counts)
    
    Args:
        idea: The story idea/concept
        set_number: Which set is being generated (1-based)
        total_segments: Total number of segments in the complete story
        segments_per_set: Number of segments per set
        actual_segments_in_set: Actual number of segments in this specific set
        start_segment: Starting segment number (1-based)
        end_segment: Ending segment number (1-based)
        no_narrations: Whether narrations are completely disabled
        narration_only_first: Whether only the first segment can have narration
        cliffhanger_segments: List of segment numbers that should have cliffhangers
        adult_story: Whether this is adult content vs family-friendly
        
    Returns:
        str: The formatted prompt for generating this set with metadata
    """
    
    return f"""
    You are a professional Humanised Script-writer for viral films.
    you can add more custom fields for generating the best results as i am gonna feed your generated output into veo3 video generation model.

    Task:
    - Create a story for adults based on: "{idea}"
    - This is SET {set_number} of a {total_segments}-segment story
    - Generate EXACTLY {actual_segments_in_set} segments (segments {start_segment} to {end_segment})
    - CRITICAL: You must generate exactly {actual_segments_in_set} segments, no more, no less
    - Write a **short_summary** (2–3 sentences) giving a quick overview of the COMPLETE story.
    - Create a **catchy title** (under 60 chars) designed for maximum clicks on YouTube Shorts / Instagram Reels / TikTok.
    - Write a **viral description** (2–3 sentences). It should:
       * Hook viewers emotionally or with curiosity
       * Summarize the story briefly
       * End with a call-to-action like "Follow for more" or "Watch till the end!"
    - Generate a list of **hashtags** (7–15). Mix general trending tags (#fyp, #viral, #shorts) with niche/story-related ones.
    - **The first segment (segment 1) must always be an INTRO scene** if this is set 1:
       * Title reveal in overlay text
       * Main characters introduction
       * Setting the tone 
    - Generate a list of **hashtags** (7–15). Mix general trending tags (#fyp, #viral, #shorts) with niche/story-related ones.
    - **Story continuity is critical**:
        * The same main characters must appear in all segments.
        * Each segment should logically follow the previous one.
        * If this is the final set, provide closure or a twist.
    - First, define a **characters_roster** (2–5 characters) with DETAILED descriptions for video generation consistency
    - **NARRATOR VOICE SELECTION** for story segments (consistent across all sets)
    - **CRITICAL TIMING RULE**: Each segment must fit within exactly 8 seconds of speech time.
    - **NARRATION vs DIALOGUE RULE**: Each segment must contain EITHER narration OR dialogue, NEVER both together.
    - **WORD COUNT LIMITS**: 
      * Narration segments: Maximum 25 words (3 words per second × 8 seconds)
      * Dialogue segments: Maximum 25 words total across all characters
      * Count every word including articles (a, an, the) and conjunctions
    - **CONTENT DISTRIBUTION**: Alternate between narration and dialogue segments for variety
    - **SPEECH PACING**: Assume normal speaking pace of 3 words per second for timing calculations

    Special Requirements for this story:
    - No narrations allowed: {no_narrations}
    - Narration only in first segment: {narration_only_first}
    - Add cliffhangers at segments: {cliffhanger_segments}
    - Adult story content: {adult_story}
    - Total story length: {total_segments} segments
    - Current set: {set_number} (segments {start_segment}-{end_segment})

    For each segment in this set, provide:
        * Scene description (location, atmosphere, key action)
        * **Choose ONE storytelling method per segment**:
          - **NARRATION SEGMENT**: Pure storytelling voice describing atmosphere, actions, emotions (8 seconds max)
          - **DIALOGUE SEGMENT**: Characters speaking directly (8 seconds max total for all dialogue)
        * If narration: Write 1-2 sentences that can be spoken in 8 seconds (approximately 20-25 words)
        * If dialogue: Write short, impactful lines using this structure:
          [{{"character": "id", "line": "..."}}] - Total dialogue must fit in 8 seconds
        * Ensure clear character identification using roster ids for dialogue segments
        * Characters present (with short traits: look, personality, role)
        * Camera perspective / animation style
        * **Speech timing**: Count words to ensure 8-second limit (average 3 words per second)

    Return ONLY valid JSON with this EXACT structure:
    {{{{
      "title": "...",
      "short_summary": "...",
      "description": "...",
      "hashtags": ["...", "...", "..."],
      "set_info": {{{{
        "set_number": {set_number},
        "segments_in_set": {actual_segments_in_set},
        "segment_range": "{start_segment}-{end_segment}",
        "total_segments": {total_segments},
        "segments_per_set": {segments_per_set}
      }}}},
      "narrator_voice": {{{{
        "voice_type": "...", 
        "age_range": "...", 
        "accent": "...", 
        "tone": "...", 
        "target_demographic": "...", 
        "speaking_pace": "...", 
        "narration_style": "...", 
        "child_friendly_level": "...", 
        "voice_pitch": "...", 
        "expressiveness": "...", 
        "voice_description": "..." 
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
            "typical_expressions": "..."
          }}}},
          "video_prompt_description": "..." 
        }}}}
      ],
      "segments": [
        {{{{
          "segment": {start_segment},
          "scene": "...",
          "overlay_text": "...", 
          "overlay_text_position": "...", 
          "overlay_text_style": "...", 
          "overlay_text_duration": "...", 
          "overlay_text_animation": "...", 
          "overlay_text_color": "...", 
          "overlay_text_font": "...", 
          "content_type": "...", 
          "narration": "...", 
          "narrator_voice_for_segment": {{{{
            "voice_type": "...", 
            "tone_variation": "...", 
            "pace_variation": "...", 
            "emotion": "...", 
            "emphasis": "...", 
            "consistency_note": "Same narrator voice as previous segments, only tone/emotion varies"
          }}}},
          "dialogue": [
            {{"character": "hero1", "line": "..."}},
            {{"character": "villain1", "line": "..."}}
          ], 
          "characters_present": ["hero1", "villain1"],
          "camera": "...",
          "clip_duration": 8, 
          "word_count": "...", 
          "estimated_speech_time": "...", 
          "background_definition": {{{{
            "location": "...", 
            "environment_type": "...", 
            "setting_description": "...", 
            "time_of_day": "...", 
            "weather_conditions": "...", 
            "lighting": "...", 
            "atmosphere": "...", 
            "key_visual_elements": ["..."], 
            "color_palette": "...", 
            "architectural_style": "...", 
            "natural_elements": ["..."], 
            "props_in_background": ["..."], 
            "scale": "...", 
            "continuity_notes": "...", 
            "video_prompt_background": "..." 
          }}}},
          "background_music": "...", 
          "sound_effects": ["..."], 
          "visual_style": "...", 
          "transitions": "...", 
          "props": ["..."], 
          "emotions": ["..."], 
          "lighting": "...", 
          "color_palette": "...", 
          "special_effects": ["..."], 
          "clothing": ["..."], 
          "time_of_day": "...", 
          "weather": "...", 
          "cultural_elements": ["..."], 
          "historical_context": "...", 
          "genre": "...", 
          "themes": ["..."], 
          "mood": "...", 
          "pacing": "...", 
          "narrative_techniques": ["..."], 
          "symbolism": ["..."], 
          "foreshadowing": ["..."] 
        }}}}
      ]
    }}}}
    """
  
      