"""
Prompts for AI character analysis from images

This module contains prompts used for analyzing images to extract character information.
Used for creating detailed character rosters for video generation by:
- Analyzing character physical appearance
- Inferring personality traits from visual cues
- Generating consistent character descriptions
- Creating video generation prompts

Functions:
1. get_character_analysis_prompt:
   - Used for analyzing images to extract character details
   - Creates detailed character rosters for video generation
   - Maintains visual consistency across segments
   - Infers personality and voice characteristics
"""


def get_character_analysis_prompt(character_count: int, character_name: str = None) -> str:
    """
    Generate the prompt for analyzing characters from an image.
    
    This function creates a prompt for extracting detailed character information
    from images, which is essential for:
    - Creating consistent character descriptions for video generation
    - Maintaining visual continuity across multiple video segments
    - Inferring personality traits and voice characteristics
    - Generating complete character rosters
    
    Args:
        character_count: Number of characters to identify in the image
        character_name: Optional specific name to use for the main character
        
    Returns:
        str: The formatted prompt for character analysis
    """
    
    return f"""
    You are a professional character designer and visual analyst for film production.
    
    **CRITICAL CONSISTENCY REQUIREMENT**:
    The video generation model (Veo3) creates each segment independently. To ensure the SAME character appears identically across ALL segments, you MUST provide EXTREMELY DETAILED character descriptions covering EVERY visible feature. Even slight variations in description will result in different-looking characters between segments. Analyze and describe characters with forensic-level detail - every skin tone nuance, every facial feature measurement, every clothing item specification. Think of it as creating a police sketch that must match perfectly across 100 different artists.
    
    Task: Analyze this image and create detailed character roster(s) for video generation.
    
    Instructions:
    - Identify and analyze {character_count} character(s) in this image
    - If there are fewer than {character_count} characters visible, analyze all visible characters
    - If there are more than {character_count} characters, focus on the most prominent ones
    - Create detailed descriptions suitable for consistent video generation
    - Each character should be described in enough detail to maintain visual consistency across multiple video segments
    {f"- Use '{character_name}' as the character name for the main character" if character_name else ""}
    
    For each character, provide:
    - Unique character ID (short, like "char1", "hero", "villain", etc.)
    - Character name (can be descriptive like "Mysterious Woman", "Young Warrior", etc.)
    - Complete physical appearance details
    - Clothing and style information
    - Personality traits (inferred from appearance/pose)
    - Role suggestions (protagonist, antagonist, supporting, etc.)
    - Voice and mannerism suggestions
    - Complete video generation prompt description
    
    Return ONLY valid JSON with this EXACT structure:
    {{{{
      "analysis_summary": "Brief description of what you see in the image",
      "characters_detected": {character_count},
      "characters_roster": [
        {{{{
          "id": "char1",
          "name": "Character Name",
          "confidence_score": 0.95,
          "position_in_image": "center/left/right/background",
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
          "inferred_personality": {{{{
            "primary_traits": ["confident", "mysterious", "friendly", "etc."],
            "energy_level": "high/medium/low",
            "approachability": "very approachable/somewhat reserved/intimidating/etc.",
            "likely_role": "protagonist/antagonist/mentor/comic relief/etc."
          }}}},
          "suggested_voice_mannerisms": {{{{
            "speaking_style": "confident/shy/authoritative/playful/etc.",
            "likely_accent": "neutral/regional/foreign/etc.",
            "speech_pace": "fast/moderate/slow",
            "typical_expressions": "facial expressions and gestures they might use"
          }}}},
          "video_prompt_description": "ULTRA-COMPLETE description combining ALL above details in a single comprehensive paragraph for video generation - must include EVERY physical feature, skin detail, facial feature, hair characteristic, and clothing item to ensure ZERO variation between segments. This should be a complete, standalone description that can be used directly for video generation.",
          "character_backstory_suggestions": "Brief suggestions for potential character background",
          "scene_context": "What this character appears to be doing in the image"
        }}}}
      ],
      "image_context": {{{{
        "setting": "description of the background/environment",
        "lighting": "natural/artificial/dramatic/soft/etc.",
        "mood": "overall mood of the image",
        "style": "photographic/artistic/cartoon/realistic/etc.",
        "quality": "high/medium/low resolution and clarity"
      }}}},
      "video_generation_notes": "Additional notes for maintaining consistency in video generation"
    }}}}
    """
