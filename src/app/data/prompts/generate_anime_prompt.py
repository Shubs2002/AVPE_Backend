"""
Prompts for Japanese Anime Generation (English Language)

This module contains prompts for generating Japanese-style anime content with English dialogue/narration.
Focuses on anime aesthetics, character designs, and storytelling conventions.
"""

def get_anime_story_prompt(idea: str, num_segments: int, custom_character_roster: list = None, anime_style: str = "shonen") -> str:
    """
    Generate the prompt for creating anime-style story segments in English.
    
    Args:
        idea: The anime story idea/concept
        num_segments: Number of segments to generate
        custom_character_roster: Optional user-provided character roster
        anime_style: Type of anime - "shonen", "shojo", "seinen", "slice_of_life", "mecha", "isekai"
        
    Returns:
        str: The formatted prompt
    """
    
    # Build custom character roster instruction if provided
    custom_roster_instruction = ""
    if custom_character_roster and len(custom_character_roster) > 0:
        import json
        roster_json = json.dumps(custom_character_roster, indent=2)
        custom_roster_instruction = f"""
    
    **MANDATORY ANIME CHARACTER ROSTER**:
    You MUST use the following pre-defined anime characters:
    
    {roster_json}
    
    These characters MUST appear as the main cast with their exact anime-style designs.
    """
    
    # Anime style descriptions
    style_descriptions = {
        "shonen": "Action-packed shonen anime with dynamic battles, friendship themes, and character growth",
        "shojo": "Romantic shojo anime with emotional depth, beautiful aesthetics, and relationship focus",
        "seinen": "Mature seinen anime with complex themes, realistic characters, and deeper storytelling",
        "slice_of_life": "Heartwarming slice-of-life anime with everyday moments, gentle humor, and relatable situations",
        "mecha": "Epic mecha anime with giant robots, sci-fi technology, and large-scale battles",
        "isekai": "Fantasy isekai anime with another world, magic systems, and adventure"
    }
    
    style_desc = style_descriptions.get(anime_style, "Japanese anime")
    
    return f"""
    You are a professional Japanese Anime Scriptwriter and Character Designer specializing in {style_desc}.
    
    Create anime content in ENGLISH language with authentic Japanese anime aesthetics, storytelling, and character designs.
    {custom_roster_instruction}

    **CRITICAL ANIME AESTHETIC REQUIREMENTS**:
    
    **ANIME ART STYLE SPECIFICATIONS**:
    - **Visual Style**: Classic Japanese anime/manga art style
    - **Character Proportions**: Anime-style proportions (large expressive eyes, stylized features)
    - **Color Palette**: Vibrant, saturated anime colors with cel-shaded look
    - **Line Art**: Clean, bold outlines typical of anime
    - **Shading**: Cel-shading with distinct shadow areas
    - **Backgrounds**: Detailed anime-style backgrounds (urban Japan, fantasy worlds, school settings)
    - **Effects**: Anime-style visual effects (speed lines, impact frames, dramatic lighting)
    
    **ANIME CHARACTER DESIGN REQUIREMENTS**:
    
    **FACE & EYES** (Most Important for Anime):
    - **Eyes**: LARGE, expressive anime eyes with:
      * Detailed iris with multiple colors/highlights
      * Large pupils with shine/reflection spots
      * Thick, defined eyelashes
      * Expressive eyebrows (thick or thin based on character)
      * Eye shape: round, almond, sharp, droopy (defines personality)
    - **Face Shape**: Soft, rounded anime face with small chin
    - **Nose**: Small, simple anime nose (often just a small line or dot)
    - **Mouth**: Small, expressive anime mouth with varied expressions
    - **Facial Structure**: Smooth, youthful features typical of anime
    
    **HAIR** (Signature Anime Feature):
    - **Style**: Distinctive anime hairstyles with:
      * Spiky, gravity-defying styles OR
      * Long, flowing hair with movement OR
      * Unique cuts with bangs, ahoge (hair antenna), etc.
    - **Color**: Vibrant anime hair colors (natural or fantasy colors)
    - **Shine**: Prominent hair highlights and shine effects
    - **Movement**: Dynamic hair that flows dramatically
    - **Accessories**: Hair clips, ribbons, headbands (common in anime)
    
    **BODY & PROPORTIONS**:
    - **Build**: Anime-style body proportions:
      * Slender, athletic builds for action characters
      * Petite, cute proportions for moe characters
      * Tall, elegant for mature characters
    - **Height**: Specify in anime terms (short/average/tall for anime standards)
    - **Posture**: Dynamic anime poses with energy
    
    **CLOTHING** (Anime Fashion):
    - **School Uniforms**: Japanese school uniforms (sailor fuku, blazers, gakuran)
    - **Casual Wear**: Modern Japanese street fashion
    - **Fantasy Outfits**: Elaborate anime fantasy costumes
    - **Accessories**: Scarves, badges, unique items that define character
    - **Color Coordination**: Signature color schemes per character
    
    **DISTINCTIVE ANIME FEATURES**:
    - **Ahoge**: Hair antenna (for energetic/airhead characters)
    - **Facial Marks**: Beauty marks, scars, face paint
    - **Accessories**: Glasses, eyepatches, headphones, etc.
    - **Expressions**: Wide range of anime expressions (chibi faces, sweat drops, anger marks)
    
    **ANIME STORYTELLING CONVENTIONS**:
    
    **NARRATIVE STYLE**:
    - **Opening**: Dramatic hook with anime-style intensity
    - **Pacing**: Fast-paced action OR slow emotional moments
    - **Cliffhangers**: End episodes on dramatic reveals or questions
    - **Internal Monologue**: Characters thinking/narrating their thoughts
    - **Flashbacks**: Use flashbacks for backstory and emotional impact
    
    **DIALOGUE STYLE** (English with Anime Flavor):
    - **Character Speech Patterns**: Distinct speaking styles per character
    - **Emotional Delivery**: Passionate, dramatic dialogue
    - **Battle Cries**: Epic attack names and power declarations
    - **Catchphrases**: Signature phrases for main characters
    - **Honorifics**: Optional use of -san, -kun, -chan for authenticity
    
    **ANIME TROPES & ELEMENTS**:
    - **Power Systems**: Clearly defined abilities/magic systems
    - **Training Arcs**: Character growth through training
    - **Rival Characters**: Friendly or antagonistic rivals
    - **Comic Relief**: Lighthearted moments between serious scenes
    - **Emotional Peaks**: Powerful emotional climaxes
    - **Transformation Sequences**: Power-ups or magical transformations
    
    **SCENE COMPOSITION** (Anime Cinematography):
    - **Dynamic Angles**: Dutch angles, low angles, dramatic perspectives
    - **Speed Lines**: Motion blur and speed lines for action
    - **Impact Frames**: Still frames on powerful moments
    - **Reaction Shots**: Close-ups of character reactions
    - **Dramatic Lighting**: High contrast, dramatic shadows
    - **Sakura Petals/Effects**: Atmospheric anime effects
    
    **ANIME STYLE SPECIFIC ELEMENTS**:
    
    **Shonen Anime**:
    - Epic battles with power escalation
    - Friendship and determination themes
    - Training montages and power-ups
    - Rival characters pushing protagonist
    - Tournament arcs or major conflicts
    
    **Shojo Anime**:
    - Romantic tension and relationships
    - Beautiful, sparkly visual effects
    - Emotional character development
    - School or social settings
    - Internal emotional struggles
    
    **Seinen Anime**:
    - Complex, mature themes
    - Realistic character psychology
    - Moral ambiguity
    - Detailed world-building
    - Strategic thinking and planning
    
    **Slice of Life**:
    - Everyday moments with warmth
    - Character interactions and bonding
    - Gentle humor and heartwarming scenes
    - Seasonal events and traditions
    - Personal growth through daily life
    
    **Mecha Anime**:
    - Giant robot designs and battles
    - Pilot-mecha connection
    - Large-scale warfare
    - Technical specifications
    - Human drama within sci-fi setting
    
    **Isekai Anime**:
    - Another world with unique rules
    - Overpowered or growing protagonist
    - Fantasy races and magic
    - Adventure and exploration
    - Game-like systems (levels, skills)

    Task:
    Create a {anime_style} anime story based on: "{idea}"
    
    - Generate {num_segments} segments, each ~8 seconds
    - Write in ENGLISH language (dialogue and narration)
    - Use authentic Japanese anime visual style and aesthetics
    - Follow anime storytelling conventions
    - Create memorable anime characters with distinct designs
    
    **CRITICAL AUDIO TIMING** (Same as other content):
    - Dialogue/Narration: 6 seconds + 2 seconds fade out = 8 seconds total
    - Maximum 18 words per dialogue/narration
    - Background music with exact timing
    - Sound effects with precise start times
    
    **ANIME-SPECIFIC AUDIO**:
    - **Opening Theme**: Energetic J-pop/J-rock style music
    - **Background Music**: Emotional orchestral or electronic tracks
    - **Sound Effects**: Anime-style SFX (whoosh, impact, magic sounds)
    - **Voice Acting Style**: Expressive anime voice acting (even in English)
    
    Return ONLY valid JSON with this structure:
    {{
      "title": "Anime Title (English)",
      "anime_style": "{anime_style}",
      "short_summary": "Brief anime synopsis (2-3 sentences)",
      "description": "Compelling description for anime viewers",
      "hashtags": ["#Anime", "#AnimeShorts", "#{anime_style.title()}", "#Viral", "#AnimeEdit"],
      "target_demographic": "Anime fans, {anime_style} enthusiasts, ages 13-35",
      "narrator_voice": {{
        "voice_type": "anime_narrator_male/anime_narrator_female",
        "age_range": "20-35",
        "accent": "clear_english_with_anime_energy",
        "tone": "dramatic_anime_style",
        "speaking_pace": "moderate_with_dramatic_pauses",
        "narration_style": "anime_storytelling",
        "expressiveness": "high_anime_energy",
        "voice_description": "Energetic anime narrator voice with dramatic delivery"
      }},
      "characters_roster": [
        {{
          "name": "Character Name",
          "anime_archetype": "protagonist/rival/mentor/comic_relief/love_interest/villain",
          "physical_appearance": {{
            "anime_style_notes": "CRITICAL: This is ANIME art style, not realistic",
            "gender": "male/female/non-binary",
            "estimated_age": "appears 16-18 (anime age)",
            "height": "short/average/tall (for anime standards)",
            "body_type": "slender_anime/athletic_anime/petite_moe/tall_elegant",
            "anime_face": {{
              "face_shape": "soft_rounded_anime/heart_shaped/angular_cool",
              "eyes": {{
                "size": "LARGE anime eyes",
                "shape": "round/almond/sharp/droopy",
                "color": "vibrant anime color (blue, green, red, purple, etc.)",
                "iris_detail": "multi-colored iris with highlights",
                "shine_spots": "prominent eye shine/reflection",
                "eyelashes": "thick defined lashes",
                "eyebrows": "expressive anime eyebrows",
                "expression": "determined/gentle/mischievous/serious"
              }},
              "nose": "small simple anime nose",
              "mouth": "small expressive anime mouth",
              "facial_features": "smooth youthful anime features"
            }},
            "anime_hair": {{
              "style": "spiky/long_flowing/short_messy/twin_tails/ponytail/unique_anime_cut",
              "color": "vibrant anime color (can be fantasy colors)",
              "length": "specific length",
              "texture": "smooth anime hair with shine",
              "special_features": "ahoge/bangs/hair_clips/unique_style",
              "movement": "dynamic flowing hair"
            }},
            "skin_tone": "anime skin tone (fair/tan/pale with anime shading)",
            "distinctive_anime_features": {{
              "ahoge": "yes/no (hair antenna)",
              "facial_marks": "any unique marks",
              "accessories": "glasses/eyepatch/headband/etc.",
              "special_traits": "any unique anime features"
            }}
          }},
          "anime_outfit": {{
            "primary_outfit": "school_uniform/casual_anime_fashion/fantasy_costume/battle_gear",
            "detailed_description": "Complete outfit description with anime style",
            "signature_colors": "character's signature color scheme",
            "accessories": "scarves/badges/weapons/magical_items",
            "outfit_significance": "what the outfit says about character"
          }},
          "personality": "Anime character personality with tropes",
          "role": "Role in the anime story",
          "signature_moves": ["Special attacks or abilities"],
          "catchphrase": "Character's signature phrase",
          "voice_style": "How they speak (energetic/cool/shy/aggressive)",
          "character_arc": "How they grow throughout the story",
          "video_prompt_description": "COMPLETE anime character description for AI generation - MUST specify ANIME ART STYLE"
        }}
      ],
      "segments": [
        {{
          "segment": 1,
          "scene_type": "action/emotional/comedy/dramatic/training/battle",
          "scene": "Anime scene description with visual style",
          "anime_cinematography": {{
            "camera_angle": "dynamic_low_angle/dutch_angle/close_up_reaction/wide_dramatic",
            "visual_effects": ["speed_lines", "impact_frame", "dramatic_lighting"],
            "color_grading": "vibrant_anime_colors/dramatic_shadows/soft_pastel",
            "animation_style": "fluid_action/emotional_stillness/comedic_exaggeration"
          }},
          "dialogue": [
            {{
              "character": "char_id",
              "line": "Dialogue in English (max 18 words total)",
              "emotion": "determined/angry/sad/excited/shocked",
              "delivery": "shouting/whispering/dramatic/casual"
            }}
          ],
          "narration": "Narrator text if no dialogue (6s + 2s fade)",
          "characters_present": ["char_id1", "char_id2"],
          "character_actions": {{
            "char_id1": "Specific anime-style action with energy"
          }},
          "background_definition": {{
            "location": "Japanese school/fantasy world/urban Tokyo/etc.",
            "anime_setting": "Detailed anime-style background",
            "time_of_day": "morning/afternoon/sunset/night",
            "weather": "clear/rainy/snowy/dramatic_storm",
            "atmosphere": "tense/peaceful/exciting/mysterious",
            "anime_effects": ["sakura_petals", "sparkles", "dramatic_sky"],
            "video_prompt_background": "Complete anime background description"
          }},
          "audio_timing": {{
            "dialogue_narration": {{
              "present": true,
              "type": "dialogue",
              "duration": "6s",
              "fade_out": "2s",
              "total_time": "8s",
              "word_count": 18,
              "text": "The dialogue or narration"
            }},
            "background_music": {{
              "present": true,
              "track_type": "epic_anime_ost/emotional_piano/battle_theme/slice_of_life_bgm",
              "start_time": "0s",
              "end_time": "continuous",
              "volume": "medium",
              "mood": "intense/emotional/upbeat/mysterious",
              "continues_to_next_segment": true
            }},
            "sound_effects": [
              {{
                "type": "anime_whoosh/impact_sound/magic_effect/sword_clash",
                "start_time": "2.5s",
                "duration": "0.5s",
                "volume": "loud",
                "description": "Anime-style sound effect"
              }}
            ]
          }},
          "emotional_beat": "What emotion this segment conveys",
          "story_progression": "How this advances the plot"
        }}
      ],
      "anime_themes": ["Main themes of the anime"],
      "power_system": "Description of abilities/magic system if applicable",
      "world_building": "Key details about the anime world",
      "episode_structure": "How segments flow together",
      "target_audience": "Specific anime audience demographics"
    }}
    
    **REMEMBER**: 
    - This is ANIME art style, not realistic
    - Characters have LARGE expressive anime eyes
    - Vibrant anime colors and cel-shading
    - Dynamic anime poses and expressions
    - English dialogue with anime energy
    - Follow {anime_style} anime conventions
    - Create memorable, distinctive anime characters
    
    Generate an authentic Japanese anime experience in English!
    """

