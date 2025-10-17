"""
Daily Character Life Content Generation

Simple service for creating engaging daily life moments of a character.
Perfect for Instagram pages showcasing character personality and behavior.
Maximum 10 segments per generation.
"""

def get_daily_character_prompt(idea: str, character_name: str, creature_language: str, num_segments: int) -> str:
    """
    Generate prompt for daily character life content using keyframes.
    
    Args:
        idea: The daily life moment/situation (e.g., "character sees his reflection and gets scared")
        character_name: Name of the character
        creature_language: Voice type ("Soft and High-Pitched", "Magical or Otherworldly", "Muffled and Low")
        num_segments: Number of segments (max 10)
        
    Returns:
        str: The formatted prompt
    """
    
    # Limit segments to 10
    if num_segments > 10:
        num_segments = 10
    
    # Use the creature language description directly
    # If it's one of the common ones, provide more detail
    # Otherwise, use the user's description as-is
    creature_sound_guide = {
        "Soft and High-Pitched": "cute, gentle squeaks and chirps - like a small friendly creature",
        "Magical or Otherworldly": "mystical, ethereal sounds with echo effects - otherworldly and enchanting",
        "Muffled and Low": "deep, grumbly sounds - like a gentle giant or sleepy creature"
    }
    
    # Use predefined description if available, otherwise use user's custom description
    sound_description = creature_sound_guide.get(creature_language, f"creature sounds that are {creature_language}")
    
    return f"""
    You are a viral content creator specializing in VISUAL storytelling for Instagram cutte creature character content.
    
    **CHARACTER**: {character_name}
    **CREATURE LANGUAGE**: {creature_language} ({sound_description})
    
    **CRITICAL RULES**:
    - **NO DIALOGUE** - Character cannot speak human language
    - **NO NARRATION** - Pure visual storytelling only
    - **ONLY CREATURE SOUNDS** - {sound_description}
    - **KEYFRAME-BASED** - User will provide character image as keyframe to Veo3
    - **VISUAL COMEDY** - Show emotions and reactions through actions, not words
    
    Your specialty is creating SHORT, PUNCHY daily life content using ONLY visuals and creature sounds.
    Each video is ~1 minute total (8 seconds per segment × {num_segments} segments)

    **CONTENT STYLE - INSTAGRAM VIRAL**:
    - **Relatable**: Everyday situations people recognize
    - **Funny**: Comedic timing and reactions through actions
    - **Character-Driven**: Personality shines through body language and sounds
    - **100% Visual**: NO dialogue, NO narration - only creature sounds
    - **Engaging**: Hook in first 2 seconds with visual action
    - **Shareable**: Makes people tag friends ("This is so cute!")
    
    **DAILY LIFE CONTENT TYPES**:
    - Funny reactions (seeing reflection, hearing noise, etc.)
    - Relatable struggles (waking up, cooking fails, etc.)
    - Character quirks (weird habits, funny behaviors)
    - Everyday adventures (grocery shopping, commuting, etc.)
    - Emotional moments (happy, sad, confused, excited)
    - Random thoughts (internal monologue moments)
    
    **KEYFRAME USAGE**:
    - User will provide {character_name}'s image as the FIRST KEYFRAME to Veo3
    - Character appearance is ALREADY DEFINED by the keyframe image
    - Focus on ACTIONS, MOVEMENTS, and REACTIONS
    - Character will look consistent because of keyframe
    
    **CREATURE SOUNDS ONLY**:
    - {character_name} communicates through {creature_language} sounds
    - Sound types: {sound_description}
    - Use sounds to express emotions (happy chirps, confused grunts, scared squeaks, etc.)
    - Sounds should match the action and emotion
    - NO human words, NO narration, NO dialogue
    
    **INSTAGRAM OPTIMIZATION**:
    - **First 2 Seconds**: HOOK - grab attention with immediate visual action
    - **Pure Visual Storytelling**: Actions and reactions tell the whole story
    - **NO Dialogue/Narration**: Only creature sounds and music
    - **Relatable Moments**: Situations viewers recognize
    - **Comedic Timing**: Perfect pacing for laughs through visuals
    - **Shareable**: "This is so cute!" and "Tag someone" vibes
    
    **SEGMENT STRUCTURE** (8 seconds each):
    1. **Hook** (Seg 1-2): Grab attention, set up situation
    2. **Build** (Seg 3-6): Develop the moment, show reactions
    3. **Payoff** (Seg 7-{num_segments}): Punchline, resolution, or twist
    
    **CRITICAL: CONTINUOUS STORYTELLING**:
    - **ALL segments MUST be a CONTINUOUS series of events**
    - **Segments 1 → {num_segments} flow in CHRONOLOGICAL ORDER**
    - **Each segment picks up EXACTLY where the previous ended**
    - **NO time jumps, NO scene changes, NO disconnected moments**
    - **ONE continuous story from start to finish**
    - **Character's position/pose at END of segment N = START of segment N+1**
    - **Think of it as ONE video split into {num_segments} parts, NOT {num_segments} separate videos**
    
    **Continuity Examples**:
    - ✅ GOOD: Seg 1 ends with character reaching for object → Seg 2 starts with character touching object
    - ✅ GOOD: Seg 3 ends with character falling → Seg 4 starts with character on ground
    - ✅ GOOD: Seg 5 ends with character looking left → Seg 6 starts with character still looking left
    - ❌ BAD: Seg 1 in cave → Seg 2 suddenly in forest (scene jump)
    - ❌ BAD: Seg 2 ends standing → Seg 3 starts sitting (position jump)
    - ❌ BAD: Seg 4 ends scared → Seg 5 starts happy with no transition (emotion jump)
    
    **CAMERA WORK** (CRITICAL FOR VISUAL STORYTELLING):
    
    **Camera Angles**:
    - **Close-up**: Face/eyes for emotions and reactions (great for comedy)
    - **Medium shot**: Upper body, shows actions and gestures
    - **Wide shot**: Full body and environment, establishes scene
    - **Extreme close-up**: Specific detail (eyes widening, paw reaching, etc.)
    - **Over-the-shoulder**: POV perspective, immersive
    - **Low angle**: Looking up at character (makes them look bigger/powerful)
    - **High angle**: Looking down at character (makes them look small/vulnerable)
    - **Eye level**: Neutral, relatable perspective
    
    **Camera Movements**:
    - **Static**: No movement, stable shot (for calm moments)
    - **Pan**: Horizontal movement (following action)
    - **Tilt**: Vertical movement (up/down)
    - **Zoom in**: Moving closer (building tension/focus)
    - **Zoom out**: Moving away (revealing context)
    - **Tracking**: Following character movement
    - **Shaky cam**: Handheld feel (for chaos/excitement)
    - **Slow motion**: Dramatic emphasis
    - **Quick cuts**: Fast-paced energy
    
    **Camera Tips for Instagram**:
    - **Vary angles** - Don't use same shot for every segment
    - **Match emotion** - Close-ups for reactions, wide for action
    - **Dynamic movement** - Static shots can be boring
    - **POV shots** - Make viewers feel like they're there
    - **Comedic framing** - Unexpected angles enhance humor
    
    **AUDIO TIMING** (CRITICAL):
    - **NO Dialogue/Narration** - Character cannot speak human language
    - **Creature Sounds**: Precise timing for emotional sounds (e.g., "2.5s - happy chirp", "5s - confused grunt")
    - **Background Music**: Exact start/end times, volume levels
    - **Sound Effects**: Environmental sounds with precise timing (e.g., "2.5s - door creak", "7s - splash")
    
    Task:
    Create a viral Instagram character moment based on: "{idea}"
    
    - Generate {num_segments} segments (max 10)
    - Each segment is 8 seconds
    - Total video: ~{num_segments * 8} seconds (~1 minute)
    - **CRITICAL**: All segments MUST form ONE CONTINUOUS story in chronological order
    - **CRITICAL**: Each segment must flow seamlessly into the next (no jumps)
    - Focus on 100% VISUAL comedy and character personality
    - Make it RELATABLE and SHAREABLE
    - NO dialogue, NO narration - ONLY creature sounds and actions
    
    **CONTINUITY CHECKLIST** (MUST FOLLOW):
    1. ✅ Segment endings connect to next segment's beginning
    2. ✅ Character position flows naturally (no teleporting)
    3. ✅ Environment stays consistent (same location throughout)
    4. ✅ Emotions transition logically (scared → relieved, not scared → happy instantly)
    5. ✅ Actions complete across segments (start action in seg N, finish in seg N+1)
    6. ✅ Time flows forward continuously (no time jumps)
    7. ✅ Camera perspective maintains spatial continuity
    
    **CONTENT GUIDELINES**:
    - **Visual ONLY**: Actions and reactions tell the entire story
    - **Relatable**: Everyday situations everyone recognizes
    - **Funny**: Comedic reactions through body language and sounds
    - **Character**: Personality shines through movements and creature sounds
    - **Engaging**: Hook viewers with immediate visual action
    - **Clean**: Family-friendly content
    - **NO WORDS**: Character uses only creature sounds to communicate
    
    **CONTINUITY EXAMPLE** (How segments should connect):
    
    Segment 1: "{character_name} walks into cave, sees puddle, bends down to look"
    → Character ends: Bent over puddle, looking down
    
    Segment 2: "{character_name} peers into puddle, sees reflection, eyes widen"
    → Character starts: Already bent over puddle (same position as Seg 1 ended)
    → Character ends: Still bent over, but eyes wide, surprised
    
    Segment 3: "{character_name} jumps back in shock, covers eyes with paws"
    → Character starts: Bent over puddle, surprised (same as Seg 2 ended)
    → Character ends: Standing back from puddle, paws over eyes
    
    Segment 4: "{character_name} slowly peeks through paws, still scared"
    → Character starts: Standing with paws over eyes (same as Seg 3 ended)
    → Character ends: Paws slightly apart, peeking through
    
    **See the pattern?** Each segment's START = Previous segment's END
    This creates ONE continuous flowing story, not separate disconnected moments!
    
    Return ONLY valid JSON with this structure:
    {{
      "title": "Short catchy title (under 50 chars)",
      "hook": "First 2 seconds visual hook description",
      "concept": "One-line concept (e.g., '{character_name} sees reflection and freaks out')",
      "vibe": "funny/relatable/wholesome/chaotic/cute/etc.",
      "target_audience": "Instagram users who love cute character content",
      "hashtags": ["#CharacterContent", "#DailyLife", "#Relatable", "#Cute", "#Viral", "#{character_name}"],
      "character_name": "{character_name}",
      "creature_language": "{creature_language}",
      "creature_sound_description": "{sound_description}",
      "keyframe_note": "User will provide {character_name}'s image as first keyframe - character appearance is already defined",
      "segments": [
        {{
          "segment": 1,
          "duration": 8,
          "first_frame_description": "ONLY FOR SEGMENT 1: Detailed description of the starting frame - character pose, position, environment, lighting. Character appearance stays same (from keyframe), only describe pose, surroundings, and background.",
          "scene": "What's happening visually",
          "action": "Specific character action",
          "reaction": "Character's reaction/emotion",
          "camera": "Specific camera angle and movement (e.g., 'Close-up on face, slow zoom in', 'Wide shot, tracking left', 'Low angle, static')",
          "visual_focus": "What viewers should notice",
          "comedy_element": "What makes this funny/engaging",
          "creature_sounds": [
            {{
              "time": "exact second (e.g., '2.5s')",
              "sound_type": "happy chirp/confused grunt/scared squeak/excited trill/etc.",
              "emotion": "what emotion the sound conveys",
              "description": "detailed sound description matching {creature_language}"
            }}
          ],
          "background": {{
            "location": "Specific location",
            "setting": "Detailed setting description",
            "time_of_day": "morning/afternoon/evening/night",
            "lighting": "natural/artificial/dramatic",
            "props": ["key props in scene"],
            "atmosphere": "mood and vibe",
            "video_prompt_background": "Complete background description for AI"
          }},
          "audio_timing": {{
            "creature_sounds": {{
              "present": true/false,
              "sound_count": "number of creature sounds in this segment",
              "sounds": [
                {{
                  "time": "exact second",
                  "type": "sound type",
                  "emotion": "emotion conveyed"
                }}
              ]
            }},
            "background_music": {{
              "present": true/false,
              "track_type": "upbeat/comedic/chill/dramatic",
              "start_time": "0s",
              "end_time": "8s or continuous",
              "volume": "low/medium/high",
              "mood": "funny/relaxed/tense",
              "continues_to_next_segment": true/false
            }},
            "sound_effects": [
              {{
                "type": "specific sound effect",
                "start_time": "exact second (e.g., '2.5s')",
                "duration": "how long (e.g., '0.5s')",
                "volume": "subtle/medium/loud",
                "description": "detailed sound description"
              }}
            ]
          }},
          "instagram_note": "Why this moment works for Instagram"
        }}
      ],
      "why_this_works": "Why this content will go viral on Instagram",
      "tag_line": "Caption for Instagram post",
      "engagement_hook": "Call-to-action (e.g., 'Tag someone who does this!')"
    }}
    
    **CAMERA EXAMPLES FOR DIFFERENT MOMENTS**:
    - **Surprise/Shock**: "Extreme close-up on eyes, quick zoom in"
    - **Discovery**: "Wide shot, slow pan to reveal object"
    - **Confusion**: "Medium shot, camera tilts with character's head"
    - **Action/Chase**: "Tracking shot, following character movement"
    - **Reaction**: "Close-up on face, static to capture expression"
    - **Comedy Beat**: "Low angle looking up, static for comedic timing"
    - **Reveal**: "Start close-up, zoom out to show full scene"
    - **Chaos**: "Shaky cam, quick cuts between angles"
    - **Cute Moment**: "Soft close-up, slight slow motion"
    - **Ending**: "Wide shot, slow zoom out as character exits"
    
    **FIRST FRAME DESCRIPTION** (SEGMENT 1 ONLY):
    - For segment 1, include "first_frame_description" field
    - Describe the STARTING FRAME: character's initial pose, position, environment
    - Character appearance STAYS THE SAME (from keyframe image)
    - Only describe: pose, body position, surroundings, background, lighting
    - This will be used to generate the first frame with Imagen before video generation
    - Example: "{character_name} standing at cave entrance, looking curious, surrounded by icy rocks and snow, soft moonlight from above"
    
    **REMEMBER**:
    - Maximum {num_segments} segments (each 8 seconds)
    - **CONTINUOUS STORY**: Segments 1→{num_segments} must flow as ONE unbroken sequence
    - **NO JUMPS**: Each segment picks up exactly where previous ended
    - **SAME LOCATION**: All segments in same environment (no scene changes)
    - 100% VISUAL storytelling - NO dialogue, NO narration
    - ONLY creature sounds: {sound_description}
    - Character appearance defined by keyframe image
    - **SEGMENT 1**: Include "first_frame_description" for starting frame generation
    - **VARY CAMERA ANGLES** - Different shot for each segment (but maintain spatial continuity)
    - **MATCH CAMERA TO EMOTION** - Close for reactions, wide for action
    - Make it RELATABLE and SHAREABLE
    - Hook viewers in first 2 seconds with visual action
    - Keep it CLEAN and family-friendly
    - Focus on ACTIONS and REACTIONS
    - Perfect for Instagram's 1-minute format
    - {character_name} communicates through sounds and body language only
    - **THINK**: One continuous video split into {num_segments} parts, NOT {num_segments} separate videos
    
    Create content that makes people say "This is SO cute!" or "I love {character_name}!"
    """
