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
            "clothing_consistency_notes": "which items never change, which might vary, h ow clothing moves"
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
