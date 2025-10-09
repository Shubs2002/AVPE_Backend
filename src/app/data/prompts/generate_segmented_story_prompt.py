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

def get_story_segments_prompt(idea: str, num_segments: int, custom_character_roster: list = None, content_type: str = "short_film") -> str:
    """
    Generate the prompt for creating story segments
    
    Args:
        idea: The story idea/concept
        num_segments: Number of segments to generate
        custom_character_roster: Optional user-provided character roster that MUST be used
        content_type: Type of content - "short_film" or "movie" (default: "short_film")
        
    Returns:
        str: The formatted prompt
    """
    # Build custom character roster instruction if provided
    custom_roster_instruction = ""
    if custom_character_roster and len(custom_character_roster) > 0:
        import json
        roster_json = json.dumps(custom_character_roster, indent=2)
        custom_roster_instruction = f"""
    
    **CRITICAL REQUIREMENT - MANDATORY CHARACTER ROSTER**:
    You MUST use the following pre-defined character roster in your story. These are the MAIN CHARACTERS that the user has specifically requested. DO NOT create new main characters - use ONLY these characters as the primary cast:
    
    {roster_json}
    
    **RULES FOR USING CUSTOM CHARACTER ROSTER**:
    - These characters MUST appear in the story as the main cast
    - Use the EXACT character descriptions, names, IDs, and details provided
    - You can add minor supporting characters if needed, but the custom roster characters are the STARS
    - Ensure these characters drive the plot and appear in multiple segments
    - Maintain ALL the physical appearance, clothing, and personality details exactly as specified
    - The story MUST revolve around these characters - they are not optional
    """
    
    # Determine the content type description
    content_description = "Short Films" if content_type == "short_film" else "viral Movies"
    
    return f"""
    You are a professional Humanised Script-writer for {content_description}.
    you can add more custom fields for generating the best results as i am gonna feed your generated output into veo3 video generation model.
    {custom_roster_instruction}

    **CRITICAL CONSISTENCY REQUIREMENT - ULTRA-DETAILED CHARACTER DESCRIPTIONS**:
    The video generation model (Veo3) creates each segment independently. To ensure the SAME character appears identically across ALL segments, you MUST provide EXTREMELY DETAILED character descriptions covering EVERY visible feature.
    
    **MANDATORY CHARACTER DETAIL REQUIREMENTS**:
    
    **SKIN**: Exact skin tone with undertones (e.g., "Fair skin with warm peachy undertones", "Deep brown with rich mahogany undertones"), skin texture (smooth/textured/porous), any skin features (freckles, moles, dimples, laugh lines)
    
    **FACE STRUCTURE**: Exact face shape (oval/round/square/heart/diamond), forehead height and width, cheekbone prominence, jawline definition (strong/soft/angular), chin shape (pointed/rounded/square/cleft)
    
    **HAIR - COMPLETE DETAILS**: 
    - Exact color with undertones and highlights
    - Precise length (e.g., "shoulder-length", "3mm buzz cut", "waist-length")
    - Texture (thick/fine/coarse/silky, straight/wavy/curly type)
    - Style (how it's worn, parting, layers)
    - Hairline (straight/widow's peak/receding)
    - **BALDNESS STAGE** if applicable: Use Norwood Scale (e.g., "No baldness", "Norwood 2 - slight temple recession", "Norwood 4 - crown thinning", "Completely bald", "Thinning at crown")
    - Facial hair: exact style, length, grooming (clean-shaven/stubble/beard/goatee/mustache)
    
    **EYES - FORENSIC DETAIL**:
    - Exact color with any flecks or rings (e.g., "Deep brown with amber flecks", "Blue with gray outer ring")
    - Shape (almond/round/hooded/monolid/upturned/downturned)
    - Size (large/medium/small), spacing (wide-set/close-set)
    - Eyelashes (long/short/thick/sparse/curled)
    - Eyebrows (thick/thin/arched/straight/bushy, exact color)
    
    **NOSE**: Complete description - bridge height (high/low), width (narrow/wide), tip shape (pointed/rounded/bulbous), nostril size and flare
    
    **LIPS**: Fullness (thin/medium/full), cupid's bow definition, natural color, smile width
    
    **OTHER FACIAL FEATURES**: Ears (size, protrusion), neck (long/short/thick/slender), Adam's apple visibility
    
    **BODY**: Height (exact), body type (detailed), weight/build, posture
    
    **DISTINCTIVE MARKS**: Every scar, birthmark, tattoo, piercing, mole - exact location and description
    
    **AGE INDICATORS**: Wrinkles, crow's feet, laugh lines, gray hair, skin elasticity
    
    Think of it as creating a police sketch that must match perfectly across 100 different artists. EVERY detail matters for AI consistency.

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
    - First, define a **characters_roster** (2–5 characters) with EXTREMELY DETAILED descriptions for video generation consistency:
        * id (short unique tag like "hero1")
        * name
        * **Physical Appearance** (CRITICAL: Describe EVERY detail for perfect video consistency):
          - gender (male/female/non-binary - be explicit)
          - age (exact age like "28 years old" or narrow range "25-27")
          - height (exact measurement like "5'8\" / 173cm" or "6'2\" / 188cm")
          - weight_build (specific like "165 lbs, athletic build" or "180 lbs, muscular")
          - body_type (very specific: "lean athletic", "muscular mesomorph", "slim ectomorph", "curvy hourglass", etc.)
          - **SKIN DETAILS** (CRITICAL for consistency):
            * skin_tone (ultra-specific: "warm honey beige", "cool porcelain", "deep mahogany", "olive tan", "fair with pink undertones")
            * skin_texture (smooth/textured/freckled/clear/etc.)
            * skin_undertone (warm/cool/neutral - specify)
            * complexion_details (any blemishes, freckles, beauty marks - exact locations)
            * skin_condition (matte/dewy/oily/dry appearance)
          - **FACE STRUCTURE** (measure every feature):
            * face_shape (oval/round/square/heart/diamond/oblong - be precise)
            * forehead (high/medium/low, wide/narrow, any lines)
            * eyebrows (exact shape: "thick straight", "arched thin", "bushy natural", color, thickness)
            * eyes_detailed (CRITICAL):
              - eye_color (ultra-specific: "hazel with gold flecks", "steel blue-gray", "warm chocolate brown")
              - eye_shape (almond/round/hooded/monolid/deep-set/protruding)
              - eye_size (large/medium/small relative to face)
              - eyelid_type (single/double/hooded)
              - eyelashes (long/short/thick/sparse, natural/mascara)
              - eye_spacing (close-set/wide-set/average)
              - under_eye (bags/dark circles/smooth - describe)
            * nose_detailed:
              - nose_shape (straight/aquiline/button/roman/snub/bulbous)
              - nose_size (small/medium/large relative to face)
              - nose_bridge (high/low/wide/narrow)
              - nostrils (flared/narrow/round)
            * cheeks_detailed:
              - cheekbone_prominence (high/low/prominent/subtle)
              - cheek_fullness (full/hollow/average)
              - dimples (yes/no, location if yes)
            * mouth_lips_detailed:
              - lip_shape (full/thin/bow-shaped/heart-shaped/wide)
              - lip_size (upper and lower - be specific)
              - lip_color (natural pink/rose/brown/red tones)
              - mouth_width (wide/narrow/proportionate)
              - teeth (visible/hidden, straight/gap/etc.)
              - smile_type (wide/subtle/crooked/symmetric)
            * jaw_chin_detailed:
              - jawline (sharp/soft/square/rounded/defined)
              - jaw_width (wide/narrow/proportionate)
              - chin_shape (pointed/rounded/square/cleft)
              - chin_prominence (receding/prominent/average)
            * ears (if visible):
              - ear_size (small/medium/large)
              - ear_shape (attached/detached lobes, etc.)
          - **HEAD & SKULL SHAPE** (CRITICAL - describe structure):
            * head_size (large/medium/small relative to body)
            * head_shape (round/oval/square/long/etc.)
            * skull_prominence (flat back/rounded/prominent occipital bone)
            * cranium_height (high/medium/low crown)
          - **HAIR DETAILS** (CRITICAL - describe completely, including baldness):
            * hair_presence (full head of hair/thinning/balding/completely bald)
            * baldness_pattern (if applicable: "male pattern baldness with receding temples", "bald crown with side hair", "completely smooth bald", "thinning on top", "no baldness")
            * hair_density (thick coverage/normal/sparse/very thin/bald patches)
            * hair_color (ultra-specific: "ash blonde with platinum highlights", "jet black with blue undertones", "auburn with copper tones", "silver-gray", "salt and pepper", "dyed vs natural")
            * hair_color_variations (roots showing, highlights, lowlights, gray streaks, fading)
            * hair_length (exact: "shoulder-length", "mid-back", "chin-length bob", "buzz cut 1/4 inch", "completely shaved/bald")
            * hair_texture (straight/wavy/curly/coily - specify curl pattern like 2A, 3B, 4C, or "no hair/bald")
            * hair_thickness (fine/medium/thick/coarse strands, or "no hair")
            * hair_volume (flat/voluminous/medium, or "bald/no volume")
            * hair_style (exact description: "center-parted long layers", "side-swept bangs with ponytail", "slicked back undercut", "buzz cut", "completely bald and shaved", "bald with horseshoe pattern")
            * hair_condition (shiny/matte/frizzy/sleek/greasy/dry, or "smooth bald scalp")
            * hairline (straight/widow's peak/receding/high/low/completely receded/no hairline if bald)
            * hair_part (center/side/no part/zigzag, or "no part - bald")
            * scalp_visibility (scalp showing through hair/no scalp visible/completely visible if bald)
            * scalp_condition (if visible or bald: smooth/textured/shiny/matte/freckled/scarred)
            * facial_hair (if applicable - exact style: "full beard", "goatee", "mustache", "stubble", "clean shaven", length, color, coverage, thickness, grooming style)
            * facial_hair_pattern (even/patchy/sparse/thick, exact areas covered)
            * eyebrow_hair (already covered above but ensure consistency with head hair color)
          - **NECK & SHOULDERS**:
            * neck_length (long/short/average)
            * neck_width (thin/thick/proportionate)
            * shoulder_width (broad/narrow/average)
            * shoulder_shape (rounded/square/sloped)
          - **HANDS & ARMS** (if visible):
            * arm_length (long/short/proportionate)
            * arm_musculature (toned/soft/muscular/thin)
            * hand_size (large/small/proportionate)
            * finger_length (long/short/average)
            * nails (short/long, manicured/natural, color)
          - distinctive_marks (EXACT locations and descriptions):
            * scars (location, size, shape, color)
            * tattoos (exact design, location, size, colors)
            * birthmarks (location, size, shape, color)
            * moles/beauty marks (exact facial/body locations)
            * piercings (type, location, jewelry description)
            * any other unique identifiers
        * **Clothing & Style** (ULTRA-DETAILED for perfect consistency):
          - **PRIMARY OUTFIT** (describe every layer and piece):
            * top_garment (exact type, fit, fabric, color, pattern, condition)
            * bottom_garment (exact type, fit, fabric, color, pattern, length)
            * outerwear (jacket/coat/cape - exact style, length, color, material)
            * footwear (exact type, color, material, condition, heel height if applicable)
            * undergarments_visible (if any parts visible - straps, waistbands, etc.)
          - **CLOTHING DETAILS**:
            * fabric_type (cotton/silk/leather/denim/wool - be specific)
            * fabric_texture (smooth/rough/shiny/matte/textured)
            * fit_style (tight/loose/fitted/oversized/tailored)
            * clothing_condition (new/worn/vintage/distressed/pristine)
            * layering (describe each visible layer from inner to outer)
            * closures (buttons/zippers/laces - describe)
            * pockets (visible pockets, flaps, etc.)
            * seams_stitching (visible details, decorative stitching)
          - **COLOR PALETTE** (exact colors for each item):
            * primary_colors (exact shades: "navy blue #001f3f", "burgundy red", "forest green")
            * secondary_colors (accent colors, patterns)
            * color_combinations (how colors work together)
            * color_wear_patterns (fading, stains, variations)
          - **ACCESSORIES** (describe each item in detail):
            * jewelry (exact pieces: "silver chain necklace 18 inches", "gold hoop earrings 1 inch diameter")
            * watches_timepieces (brand style, wrist, exact appearance)
            * bags_carried (type, size, color, material, how carried)
            * belts (width, color, buckle style, material)
            * hats_headwear (exact style, color, how worn)
            * scarves_neckwear (material, color, how tied/worn)
            * glasses_eyewear (frame style, color, lens type)
            * gloves (if worn - material, length, color)
            * weapons_tools (exact type, how carried/worn, condition)
          - **STYLE CHARACTERISTICS**:
            * overall_aesthetic (modern/vintage/fantasy/professional/casual/etc.)
            * fashion_era (if period-specific - exact era and region)
            * cultural_influences (specific cultural elements in clothing)
            * personal_style_markers (signature pieces, unique combinations)
            * formality_level (very formal/business/casual/athletic/etc.)
            * weather_appropriateness (summer/winter/all-season wear)
          - **CLOTHING CONSISTENCY NOTES**:
            * which_items_never_change (core pieces that appear in every segment)
            * which_items_might_vary (accessories that can change)
            * how_clothing_moves (flow, drape, restriction of movement)
            * clothing_sounds (rustling, jingling, creaking leather, etc.)
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
          "video_prompt_description": "..." # ULTRA-COMPLETE description combining ALL above details in a single paragraph for video generation - must include EVERY physical feature, skin detail, facial feature, hair characteristic, and clothing item to ensure ZERO variation between segments
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

def get_outline_for_story_segments_chunked(idea: str, num_segments: int, no_narrations: bool, narration_only_first: bool, cliffhanger_interval: int, adult_story: bool, custom_character_roster: list = None, content_type: str = "movie") -> str:
    """
    Generate the prompt for creating a story outline and metadata for chunked segment generation.
    
    Args:
        content_type: Type of content - "short_film" or "movie" (default: "movie")
    This is the first step in the chunked generation process for large stories (100+ segments).
    
    Args:
        idea: The story idea/concept
        num_segments: Total number of segments for the complete story
        no_narrations: Whether narrations are completely disabled
        narration_only_first: Whether only the first segment can have narration
        cliffhanger_interval: Interval at which to add cliffhangers (e.g., every 150 segments)
        adult_story: Whether this is adult content vs family-friendly
        custom_character_roster: Optional user-provided character roster that MUST be used
        
    Returns:
        str: The formatted prompt for generating story outline and metadata
    """
    
    # Build custom character roster instruction if provided
    custom_roster_instruction = ""
    if custom_character_roster and len(custom_character_roster) > 0:
        import json
        roster_json = json.dumps(custom_character_roster, indent=2)
        custom_roster_instruction = f"""
    
    **CRITICAL REQUIREMENT - MANDATORY CHARACTER ROSTER**:
    You MUST use the following pre-defined character roster in your story outline. These are the MAIN CHARACTERS that the user has specifically requested. DO NOT create new main characters - use ONLY these characters as the primary cast:
    
    {roster_json}
    
    **RULES FOR USING CUSTOM CHARACTER ROSTER**:
    - These characters MUST appear in the story as the main cast
    - Use the EXACT character descriptions, names, IDs, and details provided
    - You can add minor supporting characters if needed, but the custom roster characters are the STARS
    - Ensure these characters drive the plot and appear throughout the story
    - Maintain ALL the physical appearance, clothing, and personality details exactly as specified
    - The story MUST revolve around these characters - they are not optional
    """
    
    # Determine the content type description
    content_description = "Short Films" if content_type == "short_film" else "viral Movies"
    
    # Add cinematic camera instructions for movies
    camera_instruction = ""
    if content_type == "movie":
        camera_instruction = """
      
      **CRITICAL CINEMATIC CAMERA REQUIREMENT FOR MOVIES**:
      ALL camera movements and angles MUST be CINEMATIC and PROFESSIONAL. Use:
      - Cinematic movements: dolly, tracking, crane, steadicam, orbital shots
      - Professional angles: Dutch, low/high angles, over-the-shoulder
      - Dynamic shots: whip pans, rack focus, push-in, pull-out
      - Establishing shots: wide, aerial, sweeping panoramas
      - Intimate moments: close-ups with shallow depth of field
      - Action sequences: handheld, slow-motion, varied angles
      
      Make every camera movement CINEMATIC and PURPOSEFUL, not just "medium shot" or "close-up".
      """
    
    return f"""
      You are a professional Humanised Script-writer for {content_description}.
      {custom_roster_instruction}
      {camera_instruction}
      
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
    adult_story: bool,
    existing_metadata: dict = None,
    custom_character_roster: list = None,
    content_type: str = "movie"
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
        content_type: Type of content - "short_film" or "movie" (default: "movie")
        total_segments: Total number of segments in the complete story
        segments_per_set: Number of segments per set
        actual_segments_in_set: Actual number of segments in this specific set
        start_segment: Starting segment number (1-based)
        end_segment: Ending segment number (1-based)
        no_narrations: Whether narrations are completely disabled
        narration_only_first: Whether only the first segment can have narration
        cliffhanger_segments: List of segment numbers that should have cliffhangers
        adult_story: Whether this is adult content vs family-friendly
        existing_metadata: Optional dict with title, characters_roster, narrator_voice, etc. from first set
        custom_character_roster: Optional user-provided character roster that MUST be used
        
    Returns:
        str: The formatted prompt for generating this set with metadata
    """
    
    # Build custom character roster instruction if provided (only for set 1)
    custom_roster_instruction = ""
    if custom_character_roster and len(custom_character_roster) > 0 and set_number == 1:
        import json
        roster_json = json.dumps(custom_character_roster, indent=2)
        custom_roster_instruction = f"""
    
    **CRITICAL REQUIREMENT - MANDATORY CHARACTER ROSTER**:
    You MUST use the following pre-defined character roster in your story. These are the MAIN CHARACTERS that the user has specifically requested. DO NOT create new main characters - use ONLY these characters as the primary cast:
    
    {roster_json}
    
    **RULES FOR USING CUSTOM CHARACTER ROSTER**:
    - These characters MUST appear in the story as the main cast
    - Use the EXACT character descriptions, names, IDs, and details provided
    - You can add minor supporting characters if needed, but the custom roster characters are the STARS
    - Ensure these characters drive the plot and appear in multiple segments
    - Maintain ALL the physical appearance, clothing, and personality details exactly as specified
    - The story MUST revolve around these characters - they are not optional
    """
    
    # If we have existing metadata (from set 1), use it to ensure consistency
    if existing_metadata and set_number > 1:
        import json
        metadata_instruction = f"""
    
    **CRITICAL CONSISTENCY REQUIREMENT FOR SET {set_number}**:
    You MUST use the EXACT SAME metadata from Set 1. DO NOT create new title, characters, or narrator voice.
    Use these EXACT values:
    
    - Title: "{existing_metadata.get('title', '')}"
    - Short Summary: "{existing_metadata.get('short_summary', '')}"
    - Description: "{existing_metadata.get('description', '')}"
    - Hashtags: {json.dumps(existing_metadata.get('hashtags', []))}
    - Narrator Voice: {json.dumps(existing_metadata.get('narrator_voice', {}))}
    - Characters Roster: {json.dumps(existing_metadata.get('characters_roster', []))}
    
    **YOU MUST COPY THESE EXACTLY - DO NOT MODIFY OR CREATE NEW ONES!**
    The characters MUST look identical to Set 1. Use the EXACT SAME character descriptions.
    """
    else:
        metadata_instruction = ""
    
    # Determine the content type description
    content_description = "Short Films" if content_type == "short_film" else "viral Movies"
    
    # Add cinematic camera instructions for movies
    camera_instruction = ""
    if content_type == "movie":
        camera_instruction = """
    
    **CRITICAL CINEMATIC CAMERA REQUIREMENT FOR MOVIES**:
    ALL camera movements and angles MUST be CINEMATIC and PROFESSIONAL. Use:
    - **Cinematic Movements**: Slow dolly in/out, smooth tracking shots, crane shots, steadicam follows, orbital shots
    - **Professional Angles**: Dutch angles, low angles for power, high angles for vulnerability, over-the-shoulder for dialogue
    - **Dynamic Shots**: Whip pans for energy, rack focus for emphasis, push-in for intensity, pull-out for revelation
    - **Establishing Shots**: Wide establishing shots, aerial views, sweeping panoramas
    - **Intimate Moments**: Close-ups with shallow depth of field, extreme close-ups for emotion
    - **Action Sequences**: Handheld for intensity, slow-motion for impact, quick cuts with varied angles
    
    Examples of CINEMATIC camera descriptions:
    - "Slow dolly in on character's face as realization dawns, shallow depth of field"
    - "Sweeping crane shot rising from ground level to reveal the vast landscape"
    - "Steadicam tracking shot following character through crowded street"
    - "Low angle shot looking up at character, emphasizing power and dominance"
    - "Orbital shot circling the couple as they embrace, golden hour lighting"
    - "Extreme close-up of eyes with rack focus to background action"
    - "Wide establishing shot with slow pan across the cityscape at sunset"
    
    DO NOT use simple descriptions like "medium shot" or "close-up" - make every camera movement CINEMATIC and PURPOSEFUL.
    """
    
    return f"""
    You are a professional Humanised Script-writer for {content_description}.
    you can add more custom fields for generating the best results as i am gonna feed your generated output into veo3 video generation model.
{custom_roster_instruction}
{camera_instruction}
{metadata_instruction}
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
  
      