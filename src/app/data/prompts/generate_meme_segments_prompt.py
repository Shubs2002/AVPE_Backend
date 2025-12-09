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


def get_meme_segments_prompt(idea: str, num_segments: int, custom_character_roster: list = None) -> str:
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
        custom_character_roster: Optional user-provided character roster that MUST be used
        
    Returns:
        str: The formatted prompt for generating meme segments
    """
    
    # Build custom character roster instruction if provided
    custom_roster_instruction = ""
    if custom_character_roster and len(custom_character_roster) > 0:
        import json
        roster_json = json.dumps(custom_character_roster, indent=2)
        custom_roster_instruction = f"""
    
    **CRITICAL REQUIREMENT - MANDATORY CHARACTER ROSTER**:
    You MUST use the following pre-defined character roster in your meme. These are the MAIN CHARACTERS that the user has specifically requested. DO NOT create new main characters - use ONLY these characters as the primary cast:
    
    {roster_json}
    
    **RULES FOR USING CUSTOM CHARACTER ROSTER**:
    - These characters MUST appear in the meme as the main cast
    - Use the EXACT character descriptions, names, IDs, and details provided
    - You can add minor supporting characters if needed, but the custom roster characters are the STARS
    - Ensure these characters drive the comedy and appear in multiple segments
    - Maintain ALL the physical appearance, clothing, and personality details exactly as specified
    - The meme MUST revolve around these characters - they are not optional
    - Use their personalities and traits to enhance the comedic effect
    """
    
    return f"""
    You are a professional Humanised meme creator and viral content specialist.
    you can add more custom fields for generating the best results as i am gonna feed your generated output into veo3 video generation model.
    {custom_roster_instruction}

    **CRITICAL CONSISTENCY REQUIREMENT - ULTRA-DETAILED CHARACTER DESCRIPTIONS**:
    The video generation model (Veo3) creates each segment independently. To ensure the SAME character appears identically across ALL segments, you MUST provide EXTREMELY DETAILED character descriptions covering EVERY visible feature.
    
    **MANDATORY CHARACTER DETAIL REQUIREMENTS FOR MEMES**:
    
    **SKIN**: Exact skin tone with undertones, texture, features (freckles, moles, dimples, laugh lines)
    
    **FACE**: Exact face shape, forehead, cheekbones, jawline, chin shape
    
    **HAIR - COMPLETE DETAILS**: 
    - Exact color with undertones/highlights
    - Precise length and style
    - Texture (thick/fine/coarse/silky, straight/wavy/curly)
    - Hairline description
    - **BALDNESS STAGE**: Norwood Scale if applicable (e.g., "No baldness", "Norwood 2 - temple recession", "Norwood 4 - crown thinning", "Completely bald", "Thinning at crown")
    - Facial hair: exact style, length, grooming
    
    **EYES**: Exact color with flecks/rings, shape, size, spacing, eyelashes, eyebrows (thickness, arch, color)
    
    **NOSE**: Bridge height, width, tip shape, nostril details
    
    **LIPS**: Fullness, cupid's bow, natural color, smile width
    
    **OTHER**: Ears, neck, body type, height, posture
    
    **DISTINCTIVE MARKS**: Every scar, birthmark, tattoo, piercing, mole with exact location
    
    **AGE INDICATORS**: Wrinkles, gray hair, skin elasticity
    
    For memes, facial expressions are CRITICAL - describe how features change during reactions (eyes widen, eyebrows raise, mouth opens, etc.)

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
    - Define **characters_roster** (1-4 characters) with EXTREMELY DETAILED descriptions for video generation consistency:
        * id (short tag like "main", "friend1")
        * name (can be generic like "Main Character", "Best Friend")
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
            * outerwear (jacket/coat - exact style, length, color, material)
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
          - **STYLE CHARACTERISTICS**:
            * overall_aesthetic (modern/vintage/trendy/casual/quirky/etc.)
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
        "voice_id": "...",
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
            "voice_id": "...", # MUST be same as main narrator_voice selection
            "comedic_delivery_variation": "...", # slight delivery adjustment (more_sarcastic, extra_bubbly, deadpan_timing, etc.)
            "pace_variation": "...", # slight pace adjustment for comedic timing (punch_line_pause, quick_setup, etc.)
            "energy_adjustment": "...", # slight energy change (build_up_energy, peak_energy, calm_delivery)
            "joke_timing": "...", # how to time this segment's comedy
            "consistency_note": "Same narrator voice as previous segments, only comedic timing varies"
          }}}},
          "characters_present": ["main", "friend1"],
           "dialogue": [
            {{"character": "main", "text": "...", "duration": "6s", "fade_out":"2s", "total_time":"8s", "word_count":"...", "pace":"..."}},
            {{"character": "friend", "text": "...", "duration": "6s", "fade_out":"2s", "total_time":"8s", "word_count":"...", "pace":"..."}}
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
          "background_music":  {{{{
          "present": true,
          "track_type": "suspenseful strings",
          "start_time": "0s",
          "end_time": "continuous/6s/4s/2s",
          "fade_in": "1s",
          "fade_out": "none/time in seconds",
          "volume": "low/high/medium",
          "mood": "tense, peace, etc",
          "continues_to_next_segment": true/false
          }}}}, 
          "sound_effects": [
            {{{{
            "sound_effect_id":"...",
            "type": "footsteps, thunder,etc",
            "start_time": "time in seconds",
            "duration": "time in seconds or continuos",
            "volume": "low/medium/high",
            "description": "echoing footsteps in hallway, thunder in mountains,etc"
            }}}}
          ],
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
