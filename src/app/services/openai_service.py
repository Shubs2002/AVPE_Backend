import json
from openai import OpenAI
from app.config.settings import settings

client = OpenAI(
    base_url=settings.OPENROUTER_BASE_URL,
    api_key=settings.OPENAI_API_KEY
)

def generate_story_segments(idea: str, num_segments: int = 7):
    # For large segment counts, use chunked generation to avoid JSON parsing issues
    if num_segments > 20:
        return generate_story_segments_chunked(idea, num_segments)
    
    prompt = f"""
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
          [{{ "character": "id", "line": "..." }}] - Total dialogue must fit in 8 seconds
        * Narration to dialogue ratio: Aim for roughly 10/90 split across the entire story
        * Ensure clear character identification using roster ids for dialogue segments
        * Characters present (with short traits: look, personality, role)
        * Camera perspective / animation style
        * **Speech timing**: Count words to ensure 8-second limit (average 3 words per second)
    Return ONLY valid JSON with this EXACT structure:
    {{
      "title": "...",
      "short_summary": "...",
      "description": "...",
      "hashtags": ["...", "...", "..."],
      "narrator_voice": {{
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
          "video_prompt_description": "..." # Complete description for video generation
        }}
      ],
      "segments": [
        {{
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
          "narrator_voice_for_segment": {{ # ONLY if content_type is "narration"
            "voice_type": "...", # MUST be same as main narrator_voice selection
            "tone_variation": "...", # slight tone adjustment for this segment (dramatic, gentle, excited, etc.)
            "pace_variation": "...", # slight pace adjustment (slightly_faster, slightly_slower, same)
            "emotion": "...", # emotional delivery for this segment (suspenseful, warm, mysterious, etc.)
            "emphasis": "...", # what to emphasize in this segment
            "consistency_note": "Same narrator voice as previous segments, only tone/emotion varies"
          }},
          "dialogue": [
            {{ "character": "hero1", "line": "..." }},
            {{ "character": "villain1", "line": "..." }}
          ], # ONLY if content_type is "dialogue" - total max 25 words (8 seconds)
          "characters_present": ["hero1", "villain1"],
          "camera": "...",
          "clip_duration": 8, # always 8 seconds
          "word_count": "...", # actual word count to verify 8-second limit
          "estimated_speech_time": "...", # estimated seconds (should be ≤8)
          "background_definition": {{
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
          }},
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
        }}
      ]
    }}
    """
    raw_output = None
    try:
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

          # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        story_data = json.loads(raw_output)

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"  # Limit output length
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating story content: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

    return story_data

def generate_story_segments_chunked(idea: str, num_segments: int):
    """
    Generate story segments in chunks to handle large segment counts (100+)
    This prevents JSON parsing issues with very large responses
    """
    print(f"🔄 Generating {num_segments} segments in chunks to avoid JSON parsing issues...")
    
    # Parse special requirements from the idea
    idea_upper = idea.upper()
    no_narrations = 'NO NARRATION' in idea_upper
    narration_only_first = 'ONLY 1ST SEGMENT' in idea_upper or 'ONLY FIRST SEGMENT' in idea_upper
    adult_story = 'ADULT' in idea_upper
    
    # Look for cliffhanger patterns
    cliffhanger_interval = 0
    if '150TH SEGMENT' in idea_upper or 'EVERY 150' in idea_upper:
        cliffhanger_interval = 150
    elif 'CLIFFHANGER' in idea_upper:
        # Try to extract number
        import re
        match = re.search(r'EVERY (\d+)', idea_upper)
        if match:
            cliffhanger_interval = int(match.group(1))
    
    print(f"📋 Parsed requirements: no_narrations={no_narrations}, narration_only_first={narration_only_first}, cliffhanger_interval={cliffhanger_interval}, adult_story={adult_story}")
    
    # First, generate the story outline and metadata
    outline_prompt = f"""
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
    
    try:
        # Generate story outline and metadata
        print("📋 Generating story outline and metadata...")
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": outline_prompt}],
        )
        
        raw_output = response.choices[0].message.content.strip()
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        story_outline = json.loads(raw_output)
        print(f"✅ Story outline generated: {story_outline['title']}")
        
        # Now generate segments in chunks
        chunk_size = 15  # Generate 15 segments at a time
        all_segments = []
        
        for chunk_start in range(0, num_segments, chunk_size):
            chunk_end = min(chunk_start + chunk_size, num_segments)
            chunk_segments = chunk_end - chunk_start
            
            print(f"🎬 Generating segments {chunk_start + 1}-{chunk_end}...")
            
            # Get the relevant plot points for this chunk
            plot_points = story_outline["story_outline"][chunk_start:chunk_end]
            
            # Check for special requirements
            special_reqs = story_outline.get("special_requirements", {})
            no_narrations = special_reqs.get("no_narrations", False)
            narration_only_first = special_reqs.get("narration_only_first", False)
            cliffhanger_interval = special_reqs.get("cliffhanger_intervals", 0)
            
            # Check if any segments in this chunk should have cliffhangers
            cliffhanger_segments = []
            if cliffhanger_interval > 0:
                for seg_num in range(chunk_start + 1, chunk_end + 1):
                    if seg_num % cliffhanger_interval == 0:
                        cliffhanger_segments.append(seg_num)
            
            # Build segment generation prompt
            segment_prompt = f"""
            Generate {chunk_segments} detailed story segments (segments {chunk_start + 1} to {chunk_end}) for the story "{story_outline['title']}".
            
            Story Context:
            - Title: {story_outline['title']}
            - Summary: {story_outline['short_summary']}
            - Characters: {[char['name'] for char in story_outline['characters_roster']]}
            
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
              {{
                "segment": {chunk_start + 1},
                "scene": "...",
                "content_type": "dialogue",
                "dialogue": [
                  {{ "character": "char_id", "line": "..." }}
                ],
                "characters_present": ["char_id1", "char_id2"],
                "camera": "...",
                "clip_duration": 8,
                "word_count": "...",
                "estimated_speech_time": "...",
                "background_definition": {{
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
                }}
              }}
            ]
            """
            
            # Generate this chunk of segments
            chunk_response = client.chat.completions.create(
                model=settings.SCRIPT_MODEL,
                messages=[{"role": "user", "content": segment_prompt}],
            )
            
            chunk_raw = chunk_response.choices[0].message.content.strip()
            if chunk_raw.startswith("```"):
                chunk_raw = chunk_raw.split("```json")[-1].split("```")[0].strip()
            
            chunk_segments_data = json.loads(chunk_raw)
            all_segments.extend(chunk_segments_data)
            
            print(f"✅ Generated segments {chunk_start + 1}-{chunk_end}")
            
            # Small delay to avoid rate limits
            import time
            time.sleep(1)
        
        # Combine everything into final story data
        final_story = {
            "title": story_outline["title"],
            "short_summary": story_outline["short_summary"],
            "description": story_outline["description"],
            "hashtags": story_outline["hashtags"],
            "narrator_voice": story_outline["narrator_voice"],
            "characters_roster": story_outline["characters_roster"],
            "segments": all_segments
        }
        
        print(f"🎉 Successfully generated {len(all_segments)} segments for '{final_story['title']}'")
        return final_story
        
    except Exception as e:
        error_msg = f"Chunked story generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)

def generate_story_segments_in_sets(idea: str, total_segments: int, segments_per_set: int = 10, set_number: int = 1):
    """
    Generate story segments in sets of 10 (or specified amount) with complete metadata
    
    Args:
        idea: Story idea with special requirements
        total_segments: Total number of segments for the complete story
        segments_per_set: Number of segments to generate per set (default: 10)
        set_number: Which set to generate (1-based indexing)
    
    Returns:
        dict: Complete story data with metadata + only the requested set of segments
    """
    print(f"🎬 Generating set {set_number} ({segments_per_set} segments) of {total_segments} total segments...")
    
    # Parse special requirements from the idea
    idea_upper = idea.upper()
    no_narrations = 'NO NARRATION' in idea_upper
    narration_only_first = 'ONLY 1ST SEGMENT' in idea_upper or 'ONLY FIRST SEGMENT' in idea_upper
    adult_story = 'ADULT' in idea_upper
    
    # Look for cliffhanger patterns
    cliffhanger_interval = 0
    if '150TH SEGMENT' in idea_upper or 'EVERY 150' in idea_upper:
        cliffhanger_interval = 150
    elif 'CLIFFHANGER' in idea_upper:
        import re
        match = re.search(r'EVERY (\d+)', idea_upper)
        if match:
            cliffhanger_interval = int(match.group(1))
    
    # Calculate segment range for this set
    start_segment = (set_number - 1) * segments_per_set + 1
    end_segment = min(start_segment + segments_per_set - 1, total_segments)
    actual_segments_in_set = end_segment - start_segment + 1
    
    print(f"📊 Set {set_number}: Segments {start_segment}-{end_segment} ({actual_segments_in_set} segments)")
    print(f"📋 Requirements: no_narrations={no_narrations}, narration_only_first={narration_only_first}, cliffhanger_interval={cliffhanger_interval}, adult_story={adult_story}")
    
    # Check if any segments in this set should have cliffhangers
    cliffhanger_segments = []
    if cliffhanger_interval > 0:
        for seg_num in range(start_segment, end_segment + 1):
            if seg_num % cliffhanger_interval == 0:
                cliffhanger_segments.append(seg_num)
    
    # Generate the complete story with this specific set of segments
    prompt = f"""
    You are a professional Humanised Script-writer for viral films.
    you can add more custom fields for generating the best results as i am gonna feed your generated output into veo3 video generation model.

    Task:
    - Create a story for adults based on: "{idea}"
    - This is SET {set_number} of a {total_segments}-segment story
    - Generate segments {start_segment} to {end_segment} ({actual_segments_in_set} segments)
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
          [{{ "character": "id", "line": "..." }}] - Total dialogue must fit in 8 seconds
        * Ensure clear character identification using roster ids for dialogue segments
        * Characters present (with short traits: look, personality, role)
        * Camera perspective / animation style
        * **Speech timing**: Count words to ensure 8-second limit (average 3 words per second)

    Return ONLY valid JSON with this EXACT structure:
    {{
      "title": "...",
      "short_summary": "...",
      "description": "...",
      "hashtags": ["...", "...", "..."],
      "set_info": {{
        "set_number": {set_number},
        "segments_in_set": {actual_segments_in_set},
        "segment_range": "{start_segment}-{end_segment}",
        "total_segments": {total_segments},
        "segments_per_set": {segments_per_set}
      }},
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
      "segments": [
        {{
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
          "narrator_voice_for_segment": {{ 
            "voice_type": "...", 
            "tone_variation": "...", 
            "pace_variation": "...", 
            "emotion": "...", 
            "emphasis": "...", 
            "consistency_note": "Same narrator voice as previous segments, only tone/emotion varies"
          }},
          "dialogue": [
            {{ "character": "hero1", "line": "..." }},
            {{ "character": "villain1", "line": "..." }}
          ], 
          "characters_present": ["hero1", "villain1"],
          "camera": "...",
          "clip_duration": 8, 
          "word_count": "...", 
          "estimated_speech_time": "...", 
          "background_definition": {{
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
          }},
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
        }}
      ]
    }}
    """
    
    raw_output = None
    try:
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        story_data = json.loads(raw_output)
        
        print(f"✅ Successfully generated set {set_number} with {len(story_data.get('segments', []))} segments")
        print(f"📖 Title: {story_data.get('title', 'N/A')}")
        print(f"👥 Characters: {len(story_data.get('characters_roster', []))}")
        
        return story_data

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed for set {set_number}: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating story set {set_number}: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

def generate_meme_segments(idea: str, num_segments: int = 7):
    prompt = f"""
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
    {{
      "title": "...",
      "short_summary": "...",
      "description": "...",
      "hashtags": ["...", "...", "..."],
      "meme_type": "...", # e.g., "relatable", "absurd", "reaction", "trend"
      "narrator_voice": {{
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
            "typical_expressions": "...",
            "comedic_timing": "..."
          }},
          "video_prompt_description": "..." # Complete description for video generation
        }}
      ],
      "segments": [
        {{
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
          "narrator_voice_for_segment": {{ # for meme narration/commentary
            "voice_type": "...", # MUST be same as main narrator_voice selection
            "comedic_delivery_variation": "...", # slight delivery adjustment (more_sarcastic, extra_bubbly, deadpan_timing, etc.)
            "pace_variation": "...", # slight pace adjustment for comedic timing (punch_line_pause, quick_setup, etc.)
            "energy_adjustment": "...", # slight energy change (build_up_energy, peak_energy, calm_delivery)
            "joke_timing": "...", # how to time this segment's comedy
            "consistency_note": "Same narrator voice as previous segments, only comedic timing varies"
          }},
          "characters_present": ["main", "friend1"],
          "dialogue": [
            {{ "character": "main", "line": "..." }},
            {{ "character": "friend1", "line": "..." }}
          ],
          "reactions": [
            {{ "character": "main", "reaction": "..." }},
            {{ "character": "friend1", "reaction": "..." }}
          ],
          "camera": "...",
          "clip_duration": 8, # always 8 seconds
          "word_count": "...", # actual word count to verify 8-second limit
          "estimated_speech_time": "...", # estimated seconds (should be ≤8)
          "background_definition": {{
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
          }},
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
        }}
      ]
    }}
    """
    raw_output = None
    try:
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

          # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        meme_data = json.loads(raw_output)

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"  # Limit output length
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating meme content: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

    return meme_data

def generate_free_content(idea: str, num_segments: int = 7):
    prompt = f"""
    You are a Humanised viral content strategist and creator specializing in free, engaging content that gets millions of views.
    you can add more custom fields for generating the best results as i am gonna feed your generated output into veo3 video generation model.

    Task:
    - Create viral content based on: "{idea}"
    - **IMPORTANT**: Consider current season and upcoming festivals when creating content:
       * **Indian Festivals**: Diwali, Christmas, New Year, Navratri, Ganesh Chaturthi, Shivaji Maharaj Jayanti, Sambhaji Maharaj Jayanti, Marathi New Year (Gudi Padwa), Holi, Dussehra, Karva Chauth, Raksha Bandhan, Janmashtami, Makar Sankranti, Maha Shivratri, Ram Navami, Hanuman Jayanti, Akshaya Tritiya, Baisakhi, Onam, Durga Puja, Kali Puja, Poila Boishakh, Ugadi, Vishu, Pongal, Lohri
       * **International Festivals**: Easter, Halloween, Thanksgiving, Valentine's Day, Mother's Day, Father's Day, Independence Day, Memorial Day, Labor Day, St. Patrick's Day, Chinese New Year, Eid al-Fitr, Eid al-Adha, Ramadan
       * **Seasons**: Spring (March-May), Summer (June-August), Monsoon (June-September), Autumn (September-November), Winter (December-February)
       * **Monthly Themes**: Back to school (August-September), Holiday season (November-December), New Year resolutions (January), Summer vacation (May-July), Festival season (September-November)
    - Write a **short_summary** (2–3 sentences) explaining the content concept.
    - Create a **catchy title** (under 60 chars) optimized for maximum clicks and shares.
    - Write a **viral description** (2–3 sentences) that:
       * Creates curiosity or emotional hook
       * Promises value or entertainment
       * Ends with strong CTA like "Save this!" or "Share with friends!"
    - Break it into {num_segments} segments, each ~8s long.
    - **The first segment must be a HOOK**:
       * Grab attention in first 3 seconds
       * Promise what viewers will learn/see
       * Create curiosity gap
    - Generate **hashtags** (15-25). Mix trending tags (#fyp, #viral, #trending) with niche content tags and seasonal/festival hashtags.
    - **Content types to consider**:
        * Educational/How-to content
        * Life hacks and tips
        * Behind-the-scenes content
        * Transformation videos
        * Reaction content
        * Trending challenges
        * Motivational content
        * Entertainment/Comedy
        * Festival-specific content
        * Seasonal lifestyle content
    - Define **characters_roster** (1-3 characters) with DETAILED descriptions for video generation consistency:
        * id (short tag like "host", "expert", "friend")
        * name (can be generic like "Content Creator", "Expert", "Friend")
        * **Physical Appearance** (for video generation prompts):
          - gender, age, height, body_type, skin_tone
          - hair_color, hair_style, eye_color, eye_shape
          - facial_features, distinctive_marks
        * **Clothing & Style**:
          - primary_outfit (detailed description for consistency)
          - clothing_style (casual, professional, trendy, etc.)
          - colors (specific color palette for the character)
          - accessories (relevant to content type)
        * personality (engaging, knowledgeable, relatable traits)
        * role (host, demonstrator, expert, etc.)
        * **Voice & Mannerisms**:
          - speaking_style (clear/enthusiastic/calm/etc.)
          - typical_expressions (gestures, facial expressions)
    - **NARRATOR VOICE SELECTION** for free content:
        * **Primary Narrator**: Choose ONE consistent narrator voice for the ENTIRE content series based on content type and target audience:
          - **Kids Educational (3-8)**: Sweet, patient teacher voice (female 25-35) like Sesame Street - clear, encouraging, animated
          - **Kids Learning (8-12)**: Friendly, enthusiastic voice (female 28-38) with educational TV energy
          - **Teen Educational (13-17)**: Cool, knowledgeable voice (male/female 25-35) that doesn't talk down
          - **Educational/How-to (Adult)**: Deep, authoritative male voice (ages 30-45) with clear, professional tone
          - **Life Hacks/Tips**: Energetic, trustworthy voice (male 25-40) with enthusiastic delivery
          - **Motivational Content**: Inspiring, powerful voice (male 35-50) with emotional resonance
          - **Lifestyle/Wellness**: Warm, calming voice (female 28-40) with gentle authority
          - **Tech/Innovation**: Modern, confident voice (male 25-35) with tech-savvy appeal
          - **Finance/Business**: Professional, credible voice (male 35-50) with business authority
          - **Health/Fitness**: Energetic, motivating voice (male/female 25-40) with athletic confidence
          - **Cooking/Food**: Warm, inviting voice (female 30-45) with culinary passion
          - **Kids Science**: Excited, wonder-filled voice (male/female 25-35) like Bill Nye energy
          - **Parenting Tips**: Warm, experienced voice (female 30-45) with maternal authority
        * **CONSISTENCY RULE**: The same narrator voice must be used throughout ALL content segments. Only educational tone and emphasis can vary slightly per segment to match the lesson's focus.
        * **Target Age Demographics**: 
          - **Preschoolers (3-5)**: Very animated, patient voices like educational TV shows
          - **Elementary (6-10)**: Enthusiastic teacher voices with clear pronunciation
          - **Middle School (11-14)**: Cool but educational voices that respect their intelligence
          - **High School (15-17)**: Mature, knowledgeable voices with contemporary appeal
          - **Young Adults (18-30)**: Relatable, energetic voices with modern appeal
          - **Professionals (25-45)**: Authoritative, credible voices with expertise
          - **Parents (25-50)**: Trustworthy, experienced voices with practical wisdom
          - **General Audience (25-55)**: Trustworthy, clear voices with broad appeal
        * **Content Authority Level**:
          - **Expert Content**: Deep, mature voices (35-50) that convey knowledge and experience
          - **Peer-to-Peer**: Relatable voices (25-35) that feel like a knowledgeable friend
          - **Beginner-Friendly**: Encouraging voices (25-40) that make learning approachable
    - Define **content_elements** with:
        * content_type (educational, entertainment, lifestyle, etc.)
        * target_audience (Gen Z, Millennials, Parents, etc.)
        * value_proposition (what viewers gain)
        * engagement_strategy (how to get likes/shares/comments)
    - For each segment:
        * Scene description (visual elements, actions, demonstrations)
        * **Value delivery** should be 60% (actual useful content, tips, insights)
        * **Entertainment factor** 40% (keeping it engaging and fun)
        * Key message or takeaway
        * Visual elements and demonstrations
        * Engagement hooks (questions, challenges, calls-to-action)

    Return ONLY valid JSON with this EXACT structure:
    {{
      "title": "...",
      "short_summary": "...",
      "description": "...",
      "hashtags": ["...", "...", "..."],
      "content_type": "...", # educational, entertainment, lifestyle, etc.
      "target_audience": "...",
      "value_proposition": "...",
      "engagement_strategy": "...",
      "viral_potential": "...", # 1-10 rating
      "narrator_voice": {{
        "voice_type": "...", # sweet_teacher_female, enthusiastic_kids_educator, cool_teen_educator, deep_authoritative_male, energetic_trustworthy_male, warm_calming_female, etc.
        "age_range": "...", # 25-35, 25-40, 30-45, 35-50, etc.
        "accent": "...", # educational_tv_american, clear_teacher, professional_american, neutral_clear, authoritative_british, etc.
        "tone": "...", # sweet_patient, enthusiastic_educational, cool_knowledgeable, authoritative, enthusiastic, calming, inspiring, professional
        "target_demographic": "...", # Preschoolers, Elementary, Middle School, High School, Young Adults, Professionals, Parents, General Audience
        "speaking_pace": "...", # slow_patient_kids, moderate_educational, clear_moderate, enthusiastic_fast, calm_steady, authoritative_slow
        "authority_level": "...", # teacher, expert, peer, beginner_friendly, kids_educator
        "content_match": "...", # how voice matches content type (kids_educational, educational, lifestyle, etc.)
        "educational_style": "...", # kids_tv_teacher, sesame_street_style, bill_nye_energy, documentary_style, conversational_teacher
        "child_friendly_level": "...", # very_high_preschool, high_elementary, moderate_teen, low_adult, none
        "voice_pitch": "...", # high_sweet_teacher, medium_friendly, low_authoritative
        "patience_level": "...", # very_high_kids, high_educational, moderate, low_professional
        "voice_description": "..." # Complete description for voice generation
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
          "video_prompt_description": "..." # Complete description for video generation
        }}
      ],
      "content_elements": {{
        "hook_factor": "...", # what grabs attention
        "shareability": "...", # why people will share
        "save_factor": "...", # why people will save
        "comment_bait": "...", # what will make people comment
        "trending_elements": ["..."], # current trends incorporated
        "seasonal_relevance": "...", # how it connects to current season
        "festival_connection": "...", # relevant festivals or celebrations
        "cultural_elements": ["..."], # Indian/regional cultural aspects
        "timing_strategy": "..." # best time to post for maximum reach
      }},
      "segments": [
        {{
          "segment": 1,
          "scene": "...",
          "overlay_text": "...", # text overlays, captions, tips
          "overlay_text_position": "...",
          "overlay_text_style": "...",
          "overlay_text_duration": "...",
          "overlay_text_animation": "...",
          "overlay_text_color": "...",
          "overlay_text_font": "...",
          "key_message": "...", # main takeaway for this segment
          "value_content": "...", # educational/useful content, 60%
          "entertainment_element": "...", # fun/engaging aspect, 40%
          "visual_demonstration": "...", # what to show visually
          "engagement_hook": "...", # question, challenge, CTA
          "narrator_voice_for_segment": {{ # for educational narration
            "voice_type": "...", # MUST be same as main narrator_voice selection
            "tone_variation": "...", # slight tone adjustment (more_encouraging, extra_professional, warmer, etc.)
            "pace_variation": "...", # slight pace adjustment (slightly_slower_for_complex_info, normal, etc.)
            "emphasis_style": "...", # how to emphasize key points in this segment
            "teaching_approach": "...", # instructional style for this specific segment
            "consistency_note": "Same narrator voice as previous segments, only teaching emphasis varies"
          }},
          "characters_present": ["host", "expert"], # characters in this segment
          "camera": "...",
          "clip_duration": 8, # always 8 seconds
          "word_count": "...", # actual word count to verify 8-second limit
          "estimated_speech_time": "...", # estimated seconds (should be ≤8)
          "background_definition": {{
            "location": "...", # specific location name/type
            "environment_type": "...", # indoor/outdoor/studio/home/etc.
            "setting_description": "...", # detailed visual description for video generation
            "time_of_day": "...", # morning/afternoon/evening/night
            "weather_conditions": "...", # if outdoor - sunny/cloudy/etc.
            "lighting": "...", # bright/natural/studio/ring light/etc.
            "atmosphere": "...", # educational/inspiring/energetic/calm
            "key_visual_elements": ["..."], # important background objects/features
            "color_palette": "...", # dominant colors for the scene
            "architectural_style": "...", # if applicable - modern/home/studio/etc.
            "props_in_background": ["..."], # objects that should appear consistently
            "scale": "...", # intimate/medium/wide - helps with camera framing
            "continuity_notes": "...", # what must remain consistent across segments
            "video_prompt_background": "..." # Complete background description for video generation
          }},
          "transitions": "...", # how to transition to next segment
          "background_music": "...", # upbeat, trending sounds
          "sound_effects": ["..."], # emphasis sounds
          "visual_effects": ["..."], # text animations, highlights
          "props_needed": ["..."], # any items to demonstrate with
          "lighting": "...", # bright, natural, dramatic
          "color_scheme": "...", # vibrant, minimal, etc.
          "text_overlays": ["..."], # key points to highlight
          "call_to_action": "...", # specific action for viewers
          "curiosity_element": "...", # what keeps them watching
          "social_proof": "...", # testimonials, results, etc.
          "trending_audio": "...", # popular sounds to use
          "engagement_level": "...", # how engaging (1-10)
          "information_density": "...", # how much info (1-10)
          "entertainment_value": "...", # how fun (1-10)
          "practical_value": "...", # how useful (1-10)
          "emotional_impact": "...", # emotional response (1-10)
          "memorability": "...", # how memorable (1-10)
          "shareability_factor": "...", # likelihood to share (1-10)
          "seasonal_elements": ["..."], # seasonal decorations, themes, activities
          "festival_integration": "...", # how to incorporate festival themes
          "cultural_references": ["..."], # Indian cultural elements, traditions
          "regional_appeal": "...", # appeal to specific regions/communities
          "celebration_mood": "...", # festive, joyful, traditional elements
          "seasonal_colors": "...", # colors associated with season/festival
          "traditional_elements": ["..."], # traditional clothing, food, customs
          "modern_twist": "..." # contemporary take on traditional themes
        }}
      ]
    }}
    """
    raw_output = None
    try:
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

         # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        content_data = json.loads(raw_output)

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"  # Limit output length
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating free content: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

    return content_data
    
def generate_trending_ideas(content_type: str = "all", count: int = 5):
    """
    Generate trending, creative, and unique ideas for content creation
    
    Args:
        content_type: Type of content ("story", "meme", "free_content", or "all")
        count: Number of ideas to generate (default 5)
    
    Returns:
        dict: Generated ideas with metadata
    """
    
    if content_type == "all":
        content_types = ["story", "meme", "free_content"]
        ideas_per_type = max(1, count // 3)  # Distribute evenly
    else:
        content_types = [content_type]
        ideas_per_type = count

    prompt = f"""
    You are a viral content strategist and creative director specializing in trending, engaging content ideas.

    Task:
    Generate {ideas_per_type} highly creative, trending, and unique content ideas for each of these content types: {', '.join(content_types)}

    **IMPORTANT CRITERIA FOR IDEAS**:
    - **Trending**: Based on current social media trends, viral topics, and popular culture
    - **Creative**: Unique angles, unexpected twists, fresh perspectives
    - **Engaging**: High potential for audience interaction, shares, and comments
    - **Seasonal Relevance**: Consider current season, upcoming festivals, and cultural moments
    - **Target Demographics**: Appeal to Gen Z, Millennials, and broad audiences
    - **Viral Potential**: Ideas that have strong shareability and meme potential

    **CONTENT TYPE GUIDELINES**:

    **Story Ideas** should be:
    - Emotionally engaging narratives
    - Relatable characters and situations
    - Plot twists or surprising elements
    - Universal themes with unique execution
    - Visual storytelling potential

    **Meme Ideas** should be:
    - Highly relatable situations
    - Current internet culture references
    - Observational humor about daily life
    - Trending formats and templates
    - Cross-generational appeal

    **Free Content Ideas** should be:
    - Practical, actionable value
    - Trending topics in lifestyle, productivity, health
    - "How-to" content with unique angles
    - Problem-solving for common issues
    - Educational but entertaining

    **SEASONAL/CULTURAL CONSIDERATIONS**:
    - Current month and season themes
    - Upcoming holidays and festivals
    - Trending hashtags and challenges
    - Popular culture moments
    - Social media trends

    Return ONLY valid JSON with this EXACT structure:
    {{
      "trending_ideas": {{
        "generation_date": "...", # current date
        "trending_themes": ["..."], # current trending themes used
        "content_types": [
          {{
            "type": "story", # or "meme" or "free_content"
            "ideas": [
              {{
                "id": 1,
                "title": "...", # catchy title under 60 chars
                "concept": "...", # 2-3 sentence description
                "why_trending": "...", # why this idea is trending now
                "target_audience": "...", # primary demographic
                "viral_potential": "...", # 1-10 rating
                "hashtags": ["..."], # relevant trending hashtags
                "seasonal_relevance": "...", # how it connects to current time
                "unique_angle": "...", # what makes this idea special
                "engagement_hooks": ["..."] # elements that drive engagement
              }}
            ]
          }}
        ]
      }}
    }}
    """
    raw_output = None
    try:
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

          # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        ideas_data = json.loads(raw_output)

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"  # Limit output length
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating trending ideas: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

    return ideas_data