"""
Prompts for AI free/viral content generation services

This module contains prompts used for generating free, engaging viral content.
Free content focuses on providing value while being entertaining and shareable:
- Educational and how-to content
- Life hacks and practical tips
- Seasonal and festival-specific content
- Value-driven content (60% useful, 40% entertaining)
- Strong engagement hooks and CTAs

Functions:
1. get_free_content_prompt:
   - Used for generating viral free content (educational, lifestyle, tips)
   - Creates segments optimized for value delivery and shareability
   - Includes seasonal/festival awareness for timely content
   - Focuses on practical value with entertainment factor
"""


def get_free_content_prompt(idea: str, num_segments: int, custom_character_roster: list = None) -> str:
    """
    Generate the prompt for creating viral free content segments.
    
    Free content differs from stories and memes:
    - Primary focus on delivering value (60%) with entertainment (40%)
    - Educational, how-to, or practical tips format
    - Strong seasonal and festival awareness
    - Engagement-driven with clear CTAs
    - Narrator voices optimized for teaching/explaining
    
    Args:
        idea: The content concept/topic
        num_segments: Number of segments to generate (typically 5-10)
        custom_character_roster: Optional user-provided character roster that MUST be used
        
    Returns:
        str: The formatted prompt for generating free content segments
    """
    
    # Build custom character roster instruction if provided
    custom_roster_instruction = ""
    if custom_character_roster and len(custom_character_roster) > 0:
        import json
        roster_json = json.dumps(custom_character_roster, indent=2)
        custom_roster_instruction = f"""
    
    **CRITICAL REQUIREMENT - MANDATORY CHARACTER ROSTER**:
    You MUST use the following pre-defined character roster in your content. These are the MAIN CHARACTERS that the user has specifically requested. DO NOT create new main characters - use ONLY these characters as the primary cast:
    
    {roster_json}
    
    **RULES FOR USING CUSTOM CHARACTER ROSTER**:
    - These characters MUST appear in the content as the main presenters/hosts
    - Use the EXACT character descriptions, names, IDs, and details provided
    - You can add minor supporting characters if needed, but the custom roster characters are the STARS
    - Ensure these characters present the content and appear in multiple segments
    - Maintain ALL the physical appearance, clothing, and personality details exactly as specified
    - The content MUST feature these characters - they are not optional
    - Use their personalities and traits to enhance the content delivery
    """
    
    return f"""
    You are a Humanised viral content strategist and creator specializing in free, engaging content that gets millions of views.
    you can add more custom fields for generating the best results as i am gonna feed your generated output into veo3 video generation model.
    {custom_roster_instruction}

    **CRITICAL CONSISTENCY REQUIREMENT**:
    The video generation model (Veo3) creates each segment independently. To ensure the SAME character appears identically across ALL segments, you MUST provide EXTREMELY DETAILED character descriptions covering EVERY visible feature. Even slight variations in description will result in different-looking characters between segments. Describe characters with forensic-level detail - every skin tone nuance, every facial feature measurement, every clothing item specification. Think of it as creating a police sketch that must match perfectly across 100 different artists.

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
    - Define **characters_roster** (1-3 characters) with EXTREMELY DETAILED descriptions for video generation consistency:
        * id (short tag like "host", "expert", "friend")
        * name (can be generic like "Content Creator", "Expert", "Friend")
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
            * overall_aesthetic (professional/casual/trendy/educational/etc.)
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
    {{{{
      "title": "...",
      "short_summary": "...",
      "description": "...",
      "hashtags": ["...", "...", "..."],
      "content_type": "...", # educational, entertainment, lifestyle, etc.
      "target_audience": "...",
      "value_proposition": "...",
      "engagement_strategy": "...",
      "viral_potential": "...", # 1-10 rating
      "narrator_voice": {{{{
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
      "content_elements": {{{{
        "hook_factor": "...", # what grabs attention
        "shareability": "...", # why people will share
        "save_factor": "...", # why people will save
        "comment_bait": "...", # what will make people comment
        "trending_elements": ["..."], # current trends incorporated
        "seasonal_relevance": "...", # how it connects to current season
        "festival_connection": "...", # relevant festivals or celebrations
        "cultural_elements": ["..."], # Indian/regional cultural aspects
        "timing_strategy": "..." # best time to post for maximum reach
      }}}},
      "segments": [
        {{{{
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
          "narrator_voice_for_segment": {{{{  # for educational narration
            "voice_type": "...", # MUST be same as main narrator_voice selection
            "tone_variation": "...", # slight tone adjustment (more_encouraging, extra_professional, warmer, etc.)
            "pace_variation": "...", # slight pace adjustment (slightly_slower_for_complex_info, normal, etc.)
            "emphasis_style": "...", # how to emphasize key points in this segment
            "teaching_approach": "...", # instructional style for this specific segment
            "consistency_note": "Same narrator voice as previous segments, only teaching emphasis varies"
          }}}},
          "characters_present": ["host", "expert"], # characters in this segment
          "camera": "...",
          "clip_duration": 8, # always 8 seconds
          "word_count": "...", # actual word count to verify 8-second limit
          "estimated_speech_time": "...", # estimated seconds (should be ≤8)
          "background_definition": {{{{
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
          }}}},
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
        }}}}
      ]
    }}}}
    """

