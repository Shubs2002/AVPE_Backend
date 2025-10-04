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


def get_free_content_prompt(idea: str, num_segments: int) -> str:
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
        
    Returns:
        str: The formatted prompt for generating free content segments
    """
    
    return f"""
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
          "video_prompt_description": "..." # Complete description for video generation
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

