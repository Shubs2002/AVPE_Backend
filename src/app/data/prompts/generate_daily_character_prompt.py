"""
Daily Character Life Content Generation

Simple service for creating engaging daily life moments of a character.
Perfect for Instagram pages showcasing character personality and behavior.
Maximum 10 segments per generation.
"""

def get_daily_character_prompt(idea: str, character_name: str, creature_language: str, character_subject: str = "creature", num_segments: int = None, allow_dialogue: bool = False, num_characters: int = 1) -> str:
    """
    Generate prompt for daily character life content using keyframes.
    
    Args:
        idea: The daily life moment/situation (e.g., "character sees his reflection and gets scared")
        character_name: Name of the character(s) - comma-separated for multiple
        creature_language: Voice type(s) - comma-separated for multiple characters
        character_subject: What the character is (e.g., "fluffy pink creature, small robot")
        num_segments: Number of segments. If None, Gemini decides automatically based on story needs.
        allow_dialogue: Allow human dialogue/narration (default: False - creature sounds only)
        num_characters: Number of characters (1-5, default: 1)
        
    Returns:
        str: The formatted prompt
    """
    
    # Parse multiple characters if provided
    character_names = [name.strip() for name in character_name.split(',')]
    creature_languages = [lang.strip() for lang in creature_language.split(',')]
    
    # Ensure we have enough languages for all characters
    while len(creature_languages) < len(character_names):
        creature_languages.append(creature_languages[0] if creature_languages else "Soft and High-Pitched")
    
    # Build character info
    is_multi_character = num_characters > 1 or len(character_names) > 1
    
    creature_sound_guide = {
        "Soft and High-Pitched": "cute, gentle squeaks and chirps - like a small friendly creature",
        "Magical or Otherworldly": "mystical, ethereal sounds with echo effects - otherworldly and enchanting",
        "Muffled and Low": "deep, grumbly sounds - like a gentle giant or sleepy creature"
    }
    
    # Build character descriptions
    if is_multi_character:
        character_info = []
        for i, (name, lang) in enumerate(zip(character_names, creature_languages)):
            sound_desc = creature_sound_guide.get(lang, f"creature sounds that are {lang}")
            character_info.append(f"**{name}**: {sound_desc}")
        characters_section = "\n    ".join(character_info)
        sound_description = "Each character has unique sounds as described above"
    else:
        sound_description = creature_sound_guide.get(creature_languages[0], f"creature sounds that are {creature_languages[0]}")
    
    # Build dialogue rules based on allow_dialogue parameter
    if allow_dialogue:
        dialogue_rules = f"""
    **DIALOGUE ALLOWED**:
    - Character CAN speak human language if needed
    - Can include narration or voiceover
    - Still use creature sounds ({sound_description}) for emotional moments
    - Balance dialogue with visual storytelling
    - Keep dialogue natural and engaging
        """
    else:
        dialogue_rules = f"""
    **CRITICAL RULES**:
    - **NO DIALOGUE** - Character cannot speak human language
    - **NO NARRATION** - Pure visual storytelling only
    - **ONLY CREATURE SOUNDS** - {sound_description}
    - **KEYFRAME-BASED** - User will provide character image as keyframe to Veo3
    - **VISUAL COMEDY** - Show emotions and reactions through actions, not words
        """
    
    # Build character section with subject handling
    # Parse character subjects for multi-character
    character_subjects = [subj.strip() for subj in character_subject.split(',')]
    while len(character_subjects) < len(character_names):
        character_subjects.append(character_subjects[0] if character_subjects else "creature")
    
    if is_multi_character:
        # Build detailed character descriptions with name, appearance, and voice
        character_details = []
        for name, subj, lang in zip(character_names, character_subjects, creature_languages):
            sound_desc = creature_sound_guide.get(lang, f"creature sounds that are {lang}")
            character_details.append(f"**{name}**: Appearance: {subj} | Voice: {sound_desc}")
        character_details_section = "\n    ".join(character_details)
        
        character_section = f"""
    **CHARACTERS** ({num_characters} characters):
    {characters_section}
    
    **CHARACTER DETAILS** (appearance + voice for each character):
    {character_details_section}
    
    **MULTI-CHARACTER RULES**:
    - Each character has unique sounds as described above
    - Characters can interact, play together, or appear separately
    - Track which characters appear in each segment using "characters_present" field
    - Each character's sounds should match their personality
    - Frame descriptions must specify each character's position when multiple are present
    
    **SUBJECT FIELD FOR VEO_PROMPT** (CRITICAL - Include name, appearance AND voice):
    - In EVERY veo_prompt, include a detailed subject description for EACH character present
    - Format: "[Name] ([appearance description]) with [voice description]"
    - Example for 2 characters: "Floof (fluffy pink creature with big curious eyes) with soft high-pitched chirps, and Poof (small blue robot with glowing antenna) with mechanical beeping sounds"
    - This helps Veo understand WHO each character is, what they LOOK like, and how they SOUND
    - Include voice descriptions so Veo can generate appropriate audio for each character
    """
    else:
        character_section = f"""
    **CHARACTER**: {character_names[0]}
    **CHARACTER APPEARANCE**: {character_subjects[0]}
    **CHARACTER VOICE**: {creature_languages[0]} ({sound_description})
    
    **SUBJECT FIELD FOR VEO_PROMPT** (CRITICAL - Include name, appearance AND voice):
    - In EVERY veo_prompt, include the character's name, appearance, and voice description
    - Format: "{character_names[0]} ([appearance]) with [voice description]"
    - Example: "{character_names[0]} ({character_subjects[0]}) with {sound_description}"
    - This helps Veo understand WHO the character is, what they LOOK like, and how they SOUND
    - Include voice description so Veo can generate appropriate audio
    """
    
    # Build segment count instruction
    if num_segments is None:
        segment_instruction = """
    **SEGMENT COUNT**: Determine the optimal number of segments (2-10) based on the story.
    - Simple moments: 2-3 segments
    - Standard stories: 4-7 segments  
    - Complex narratives: 8-10 segments
    - Each segment is 8 seconds
    - Choose the count that best serves the story without padding or rushing"""
        total_duration_text = "varies based on segment count"
    else:
        segment_instruction = f"""
    **SEGMENT COUNT - CRITICAL REQUIREMENT**: 
    - You MUST generate EXACTLY {num_segments} segments - NO MORE, NO LESS
    - This is a STRICT requirement - do NOT generate fewer segments
    - If the story feels too short, expand scenes with more detail and moments
    - If the story feels too long, that's fine - use all {num_segments} segments
    - Each segment is 8 seconds
    - Total video: ~{num_segments * 8} seconds (~{num_segments * 8 / 60:.1f} minutes)
    - VALIDATION: Your response MUST contain exactly {num_segments} segment objects in the segments array"""
        total_duration_text = f"~{num_segments * 8} seconds (~{num_segments * 8 / 60:.1f} minutes)"
    
    return f"""
    You are a viral content creator specializing in VISUAL storytelling for Instagram cute creature character content.
    
    {character_section}
    {dialogue_rules}
    
    Your specialty is creating SHORT, PUNCHY daily life content using ONLY visuals and creature sounds.
    {segment_instruction}

    **CONTENT STYLE - INSTAGRAM VIRAL**:
    - **Relatable**: Everyday situations people recognize
    - **Funny**: Comedic timing and reactions through actions
    - **Character-Driven**: Personality shines through body language and sounds
    - **100% Visual**: NO dialogue, NO narration - only creature sounds
    - **Engaging**: Hook in first 2 seconds with visual action
    - **Shareable**: Makes people tag friends ("This is so cute!")
    - **FAST-PACED**: Quick, energetic movements with snappy transitions - NO slow motion unless for comedic effect
    - **DYNAMIC**: Active, lively character movements - avoid slow, sluggish actions
    
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
    
    **VIRAL HOOK STRATEGY** (CRITICAL FOR ENGAGEMENT):
    - **First 2 Seconds = EVERYTHING**: 90% of viewers decide to watch or scroll in 2 seconds
    - **Hook Types**:
      * **Curiosity Hook**: "What's going to happen?" (character about to do something unexpected)
      * **Relatable Hook**: "That's so me!" (everyday situation viewers recognize instantly)
      * **Surprise Hook**: Unexpected visual that makes viewers go "Wait, what?"
      * **Cute Hook**: Immediate "awww" moment that stops the scroll
      * **Comedy Hook**: Instant visual gag that makes viewers laugh
    - **Hook Formula**: Show the MOST interesting moment first, then build to it
    - **Pattern Interrupt**: Do something visually unexpected in first frame
    
    **INSTAGRAM OPTIMIZATION**:
    - **First 2 Seconds**: HOOK - grab attention with immediate visual action (use hook strategies above)
    - **Pure Visual Storytelling**: Actions and reactions tell the whole story
    - **NO Dialogue/Narration**: Only creature sounds and music
    - **Relatable Moments**: Situations viewers recognize ("This is literally me")
    - **Comedic Timing**: Perfect pacing for laughs through visuals
    - **Shareable**: "This is so cute!" and "Tag someone who does this" vibes
    - **Emotional Payoff**: Make viewers feel something (laugh, aww, relate)
    
    **SEGMENT STRUCTURE** (8 seconds each):
    1. **Hook** (First 1-2 segments): Grab attention IMMEDIATELY, set up situation with intrigue
       - Start with the most interesting visual
       - Create curiosity: "What will happen next?"
       - Make it relatable or surprising
    2. **Build** (Middle segments): Develop the moment, escalate tension/comedy
       - Add complications or obstacles
       - Show character's reactions and emotions
       - Keep energy high, don't let it drag
    3. **Payoff** (Final segments): Satisfying punchline, resolution, or twist
       - Deliver on the hook's promise
       - End with a memorable moment
       - Leave viewers wanting to share or rewatch
    
    **ENGAGEMENT PRINCIPLES**:
    - **Every Second Counts**: No boring moments, every frame should be interesting
    - **Escalation**: Each segment should be more interesting than the last
    - **Surprise**: Include unexpected moments that break viewer expectations
    - **Emotion**: Make viewers FEEL something (laugh, relate, go "aww")
    - **Rewatch Value**: Include details viewers will notice on second watch
    
    **CRITICAL: CONTINUOUS STORYTELLING**:
    - **ALL segments MUST be a CONTINUOUS series of events**
    - **Segments flow in CHRONOLOGICAL ORDER from first to last**
    - **Each segment picks up EXACTLY where the previous ended**
    - **NO time jumps, NO scene changes, NO disconnected moments**
    - **ONE continuous story from start to finish**
    - **Character's position/pose at END of segment N = START of segment N+1**
    - **Think of it as ONE video split into multiple parts, NOT separate videos**
    
    **Continuity Examples**:
    - ✅ GOOD: Seg 1 ends with character reaching for object → Seg 2 starts with character touching object
    - ✅ GOOD: Seg 3 ends with character falling → Seg 4 starts with character on ground
    - ✅ GOOD: Seg 5 ends with character looking left → Seg 6 starts with character still looking left
    - ❌ BAD: Seg 1 in cave → Seg 2 suddenly in forest (scene jump)
    - ❌ BAD: Seg 2 ends standing → Seg 3 starts sitting (position jump)
    - ❌ BAD: Seg 4 ends scared → Seg 5 starts happy with no transition (emotion jump)
    
    **CAMERA POSITIONING AND MOTION** (CRITICAL FOR CINEMATIC STORYTELLING):
    
    Create smooth, cinematic camera movements that enhance the visual narrative. Use descriptive, flowing language.
    
    **Camera Positioning (Shot Types)**:
    - **Aerial view**: Bird's eye perspective from above
    - **Eye-level**: Neutral, relatable perspective at character's eye height
    - **Top-down shot**: Directly overhead, looking straight down
    - **Low angle / Worm's eye**: Looking up from ground level (makes subject appear powerful/imposing)
    - **High angle**: Looking down at subject (makes subject appear small/vulnerable)
    - **Close-up shot**: Tight framing on face or specific detail
    - **Medium shot**: Waist-up or upper body framing
    - **Wide shot**: Full body and environment visible
    - **Extreme close-up**: Macro detail (eyes, water drops, textures)
    - **Over-the-shoulder**: POV perspective from behind character
    - **POV shot**: First-person view from character's perspective
    - **Tracking drone view**: Following subject from aerial perspective
    
    **Camera Movements (Cinematic Techniques)**:
    - **Dolly in/out**: Camera moves forward toward or backward away from subject
      Example: "The camera dollies in, revealing the tension in his jaw and desperation etched on his face"
    - **Pull back**: Camera slowly moves backward to reveal more of the scene
      Example: "The camera slowly pulls back to a medium-wide shot, revealing the breathtaking scene"
    - **Pan**: Smooth horizontal sweep across the scene
      Example: "The camera slowly pans across the whimsical, sunlit scene"
    - **Tilt**: Vertical movement up or down
    - **Zoom in/out**: Lens zooms to change focal length
      Example: "Zoomed in maintaining close-up detail of water drips"
    - **Tracking shot**: Camera follows subject's movement smoothly
    - **Orbiting**: Camera circles around the subject
    - **Crane shot**: Camera moves up or down on a vertical axis
    - **Handheld**: Slight natural camera shake for realism
    - **Smooth glide**: Steady, flowing camera movement
    - **Static hold**: Camera remains still, letting action unfold
    
    **Cinematic Camera Description Format**:
    Write camera movements as flowing, descriptive sentences that paint the visual:
    
    ✅ GOOD Examples:
    - "The camera slowly pulls back to a medium-wide shot, revealing the breathtaking scene as the dress's long train glides and floats gracefully on the water's surface behind her"
    - "The camera slowly pans across the whimsical, sunlit scene as the miniature figures expertly carve the turquoise water"
    - "Close up shot of melting icicles on a frozen rock wall with cool blue tones, zoomed in maintaining close-up detail of water drips"
    - "The camera dollies to show a close up of a desperate man in a green trench coat"
    - "The camera dollies in, revealing the tension in his jaw and the desperation etched on his face as he struggles to make the call"
    - "Aerial view tracking the character as they run through the forest, camera smoothly following from above"
    - "Eye-level shot with camera slowly circling around the character, revealing their surroundings"
    - "Low angle worm's eye view as the camera tilts up, making the character appear towering and powerful"
    
    ❌ BAD Examples (too simple):
    - "Camera moves"
    - "Close up"
    - "Wide shot"
    
    **Camera Guidelines for Veo Prompt**:
    1. **Be Descriptive**: Use flowing, cinematic language
    2. **Specify Movement**: Describe HOW the camera moves (slowly pulls back, smoothly pans, dollies in)
    3. **Include Framing**: Mention shot composition (close-up, wide shot, medium shot)
    4. **Add Context**: Explain what the camera movement reveals or emphasizes
    5. **Smooth Transitions**: Camera movements should feel natural and purposeful
    6. **Match Emotion**: Camera movement should enhance the mood (slow for dramatic, quick for energetic)
    
    **Camera Tips for Viral Content**:
    - **Vary camera work** - Don't use same angle/movement for every segment
    - **Dynamic movement** - Use camera motion to add energy and visual interest
    - **Match emotion** - Close-ups for reactions, wide shots for action, dollies for reveals
    - **Cinematic flow** - Smooth, professional camera movements enhance production value
    - **POV immersion** - First-person shots make viewers feel present in the scene
    
    **ACTION PACING** (CRITICAL FOR VIRAL CONTENT):
    - **FAST & ENERGETIC**: Character movements should be quick, lively, and dynamic
    - **SNAPPY TRANSITIONS**: Actions should flow rapidly from one to the next
    - **NO SLUGGISH MOVEMENTS**: Avoid slow, dragging actions unless for specific comedic effect
    - **QUICK REACTIONS**: Character should react quickly and expressively
    - **DYNAMIC ENERGY**: Keep the energy high and movements active throughout
    - **Example**: Instead of "slowly walks" → use "quickly scurries" or "bounces over"
    - **Example**: Instead of "gradually turns" → use "whips around" or "spins quickly"
    
    **AUDIO TIMING** (CRITICAL):
    - **NO Dialogue/Narration** - Character cannot speak human language
    - **Creature Sounds**: Precise timing for emotional sounds (e.g., "2.5s - happy chirp", "5s - confused grunt")
    - **Background Music**: Exact start/end times, volume levels
    - **Sound Effects**: Environmental sounds with precise timing (e.g., "2.5s - door creak", "7s - splash")
    
    Task:
    Create a viral Instagram character moment based on: "{idea}"
    
    **FIRST: Analyze the idea to determine scene structure:**
    - Does the idea mention "different scenes", "various locations", "multiple places"?
      → YES: Each segment is a SEPARATE scene (all need first_frame_description)
      → NO: Segments are CONTINUOUS in one location (only segment 1 needs first_frame_description)
    
    **SEGMENT COUNT**:
    {f"- Generate exactly {num_segments} segments" if num_segments else "- Determine optimal segment count (2-10) based on story complexity"}
    - Each segment is 8 seconds
    - Total video: {total_duration_text}
    - **IF CONTINUOUS**: All segments flow seamlessly in chronological order
    - **IF SEPARATE SCENES**: Each segment is a different location/moment (like a montage)
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
    
    **FRAME DESCRIPTIONS - ULTRA-DETAILED REQUIREMENTS**:
    
    Frame descriptions are used by Imagen AI to generate actual images, so they must be EXTREMELY detailed.
    
    **Required Elements in EVERY Frame Description**:
    1. **Camera Angle**: Exact angle and distance
       - Examples: "Low angle wide shot", "Eye-level close-up", "High angle medium shot", "Over-the-shoulder view"
    
    2. **Character Position & Pose**: Precise body position
       - Examples: "Standing upright with arms at sides", "Crouching with paws on ground", "Mid-jump with legs bent"
    
    3. **Full Body Visibility Rule** (FLEXIBLE based on action):
       - **At least ONE frame per segment** MUST show full body ("Full body visible from head to toe")
       - **Can be in FIRST frame, LAST frame, or BOTH** - depends on the action
       - **Guideline**: Alternate between frames for variety
         - Segment 1: Full body in FIRST or LAST (or both)
         - Segment 2: Full body in the OTHER frame (or both)
         - Continue alternating for visual variety
       - **Action-dependent**: If action requires close-up (facial reaction), put full body in the other frame
       - **Scene changes**: When first_frame_description exists, ensure at least one frame has full body
    
    4. **Objects & Props**: Specific items and their positions
       - Examples: "Blue plastic sled 2 feet to the left", "Red toy car parked behind", "Snow-covered pine trees in background"
    
    5. **Lighting Details**: Light source, direction, quality
       - Examples: "Bright morning sunlight from upper right", "Soft golden hour glow", "Dramatic shadows cast to the left"
    
    6. **Environment Specifics**: Background details
       - Examples: "Snowy hilltop with visible footprints", "Wooden cabin 20 feet behind", "Clear blue sky with few clouds"
    
    7. **Spatial Relationships**: How elements relate
       - Examples: "Character centered in frame", "Trees framing the sides", "Horizon line at upper third"
    
    **Frame Description Examples**:
    
    ✅ GOOD - Full body in FIRST frame (wide establishing shot):
    "Low angle wide shot. {character_name} standing fully visible from head to toe in center of snowy hilltop, wearing oversized black sunglasses and tiny red scarf, arms crossed confidently. Blue plastic sled lying 3 feet to his right. Snow-covered pine trees line the background 15 feet away. Wooden cabin visible on left side in distance. Bright morning sunlight from upper right creating long shadows to the left. Clear blue sky. Fresh snow with few footprints around character."
    
    ✅ GOOD - Full body in LAST frame (action shot):
    "Eye-level medium shot. {character_name} sitting on blue sled, full body visible from head to toe, leaning forward with paws gripping the sides, eyes wide with excitement. Camera positioned at character's eye level. Red toy car visible 5 feet behind in soft focus. Snow texture detailed in foreground. Pine trees blurred in background. Bright sunlight creating sparkles on snow surface. Character's shadow visible beneath sled."
    
    ✅ GOOD - Close-up in FIRST, full body in LAST (reaction then action):
    FIRST: "Close-up shot. {character_name}'s face filling frame, eyes widening in surprise, mouth forming an 'O' shape. Whiskers visible. Soft focus background."
    LAST: "Wide shot. {character_name} jumping backwards, full body visible from head to toe, arms flailing, landing on snow. Complete environment visible."
    
    ❌ BAD (Too vague):
    "{character_name} standing in snow looking cool"
    
    **Minimum Length**: Each frame description must be at least 30 words to ensure sufficient detail for Imagen.
    
    **FIRST FRAME DESCRIPTION LOGIC** (CRITICAL):
    
    **Analyze the user's idea carefully to determine if scenes should be continuous or separate:**
    
    **Keywords indicating SEPARATE SCENES** (each segment needs first_frame_description):
    - "different scenes", "various locations", "multiple places", "different settings"
    - "cuts to", "switches to", "moves to different", "in various"
    - "montage", "compilation", "different moments"
    
    **Keywords indicating CONTINUOUS SCENE** (only segment 1 needs first_frame_description):
    - "continuous", "one scene", "same location", "stays in"
    - "throughout", "entire time", "without leaving"
    
    **Rules:**
    - **Segment 1**: ALWAYS include detailed first_frame_description (starting frame)
    - **If idea mentions "different scenes/locations"**: EVERY segment gets first_frame_description (new scene each time)
    - **If idea is continuous story in one place**: Only segment 1 gets first_frame_description, others set to null
    - **Scene change mid-story**: Include first_frame_description when location/setting changes
    
    **Examples:**
    
    Idea: "Floof dancing in different different scenes"
    → Each segment = different location → ALL segments get first_frame_description
    
    Idea: "Floof sees reflection and gets scared"  
    → One continuous scene → Only segment 1 gets first_frame_description
    
    Idea: "Floof explores house, then goes outside"
    → Segment 1-3 inside (only seg 1 has desc), Segment 4+ outside (seg 4 has desc for scene change)
    
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
          "characters_present": ["Character1", "Character2"],
          "veo_prompt": "CRITICAL - VEO 3 DESCRIPTIVE PROMPT FORMAT. Write as a flowing, descriptive paragraph with keyword tags in parentheses. Include ALL these elements naturally woven together:\\n\\n**FORMAT**: Write a single flowing description with (keyword tags) like this example:\\n'Close up shot (composition) of Floof (fluffy pink creature with big curious eyes) with soft high-pitched chirps (subject) bouncing happily toward a puddle (action) in a sunlit forest clearing (context) with warm golden tones (ambiance), the camera slowly dollies forward (camera motion) tracking the movement as Floof stops at the water's edge (action), soft morning light filtering through trees (lighting), cute character animation style (style), shallow focus on character (focus), at 1.0s playful high-pitched chirps expressing curiosity (audio/sfx), at 4.0s soft surprised squeak as seeing reflection (audio/sfx), gentle forest ambiance with rustling leaves and distant bird calls (ambient audio).'\\n\\n**SUBJECT FORMAT** (CRITICAL - Include name, appearance AND voice):\\n- For SINGLE character: '[Name] ([appearance description]) with [voice description]'\\n- Example: 'Floof (fluffy pink creature with big curious eyes) with soft high-pitched chirps'\\n- For MULTIPLE characters: '[Name1] ([appearance1]) with [voice1], and [Name2] ([appearance2]) with [voice2]'\\n- Example: 'Floof (fluffy pink creature with big curious eyes) with soft high-pitched chirps, and Poof (small blue robot with glowing antenna) with mechanical beeping sounds'\\n- This helps Veo understand WHO each character is, what they LOOK like, and how they SOUND\\n\\n**REQUIRED ELEMENTS** (include keyword tag in parentheses):\\n- (subject): Character name + appearance + voice description (see format above)\\n- (action): What the subject is doing - movements, events, interactions\\n- (context): The setting/environment where action takes place\\n- (composition): Shot framing - wide shot, close-up, medium shot, two-shot, single-shot, extreme close-up\\n- (camera motion): How camera moves - dollies in/out, pulls back, pans across, tilts, zooms, tracking, orbiting, static hold\\n- (camera position): Where camera is - aerial view, eye-level, low angle, high angle, top-down, worm's eye, POV shot\\n- (style): Visual style - cute character animation, cinematic, film noir, sci-fi, horror film, animated, Instagram vertical\\n- (ambiance): Color and light mood - warm tones, cool blue tones, golden hour, night, dramatic shadows\\n- (lighting): Light source and quality - soft morning sunlight, dramatic backlighting, dappled light, neon glow\\n- (focus): Lens effects - shallow focus, deep focus, soft focus, macro lens, wide-angle lens\\n- (audio/sfx): Creature sounds and sound effects with timing - 'at 2.0s playful chirps expressing excitement (audio/sfx)', 'at 5.0s splash sound as hitting water (audio/sfx)'\\n- (dialogue): Character speech in quotes with timing (ONLY if allow_dialogue=True) - 'at 3.0s Floof chirps softly \"Wow!\" (dialogue)'\\n- (ambient audio): Environmental soundscape - 'forest ambiance with bird calls (ambient audio)', 'city traffic hum (ambient audio)'\\n- (overlay_text): Text to display on screen - ONLY include if there's actual text to show, otherwise OMIT entirely\\n- (overlay_position): Where text appears - top, center, bottom, top-left, bottom-right - ONLY include if overlay_text exists\\n- (overlay_type): Type of text - title, subtitle, caption, description - ONLY include if overlay_text exists\\n\\n**AUDIO IN VEO_PROMPT** (CRITICAL - All audio goes IN the veo_prompt):\\n- **Creature Sounds**: Include timing for character sounds - 'at 1.0s playful high-pitched chirps (audio/sfx)', 'at 4.0s surprised squeak (audio/sfx)'\\n- **Dialogue** (only if allow_dialogue=True): Include speech with timing - 'at 3.0s Floof trills softly \"This is amazing!\" (dialogue)'\\n- **Sound Effects**: Environmental sounds with timing - 'at 2.5s splash sound (audio/sfx)', 'at 6.0s door creaking (audio/sfx)'\\n- **Ambient Audio**: Background soundscape - 'gentle forest ambiance with rustling leaves (ambient audio)'\\n- **Voice Matching**: Match sounds to character voice - 'Floof chirps happily in soft high-pitched tones (audio/sfx)'\\n\\n**EXAMPLE VEO_PROMPT (Single Character - NO dialogue)**:\\n'Medium wide shot (composition) of Floof (fluffy pink creature with big curious eyes and soft fur) with playful high-pitched chirps and squeaks (subject) bouncing excitedly toward a shimmering puddle on a mossy forest path (action) in a magical woodland clearing (context), the camera smoothly tracks alongside at eye-level (camera position) then slowly dollies in (camera motion) as Floof stops at the water's edge and peers down curiously (action), cute character animation style with vibrant saturated colors (style), warm golden morning light filtering through tall pine trees creating dappled patterns on the moss (lighting) with soft natural tones and slight mist (ambiance), deep focus keeping both character and environment sharp (focus), at 1.0s playful high-pitched chirping sounds expressing happiness (audio/sfx), at 4.0s soft curious cooing as investigating the reflection (audio/sfx), at 6.0s surprised squeak seeing own reflection (audio/sfx), gentle forest ambiance with rustling leaves and distant bird calls throughout (ambient audio).'\\n\\n**EXAMPLE VEO_PROMPT (Single Character - WITH dialogue allowed)**:\\n'Medium shot (composition) of Floof (fluffy pink creature with big curious eyes) with soft high-pitched chirps (subject) sitting at a tiny desk looking at a computer screen (action) in a cozy bedroom at night (context), the camera slowly dollies in (camera motion) from eye-level (camera position) as Floof's eyes widen at something on screen (action), cute character animation style (style), warm lamp light casting soft shadows (lighting) with cozy amber tones (ambiance), at 1.0s soft lo-fi music playing in background (ambient audio), at 2.0s Floof chirps curiously (audio/sfx), at 4.0s Floof gasps and squeaks excitedly \"No way!\" (dialogue), at 6.0s happy bouncing chirps (audio/sfx), keyboard clicking sounds (ambient audio).'\\n\\n**EXAMPLE VEO_PROMPT (Multiple Characters)**:\\n'Wide two-shot (composition) of Floof (fluffy pink creature with big curious eyes) with soft high-pitched chirps, and Poof (small blue robot with glowing antenna) with mechanical beeping sounds (subject) walking together through a snowy meadow (action) in a winter wonderland at sunset (context), the camera slowly pulls back (camera motion) from eye-level (camera position) revealing the vast snowy landscape (action), cute character animation style (style), warm orange sunset light casting long shadows on pristine snow (lighting) with cool blue tones in shadows (ambiance), at 1.0s crunching footsteps in snow (audio/sfx), at 2.0s Floof makes excited chirping sounds (audio/sfx), at 4.0s Poof responds with happy beeping (audio/sfx), at 6.0s both characters make joyful sounds together (audio/sfx), peaceful winter ambiance with gentle wind (ambient audio).'\\n\\n**OVERLAY TEXT EXAMPLE** (when needed):\\n'...the creature looks up with wonder (action), \"Chapter 1: The Discovery\" (overlay_text) appearing at the top of frame (overlay_position) as a title (overlay_type)...'\\n\\n**AUDIO PROMPTING RULES**:\\n- **ALL audio goes IN the veo_prompt** - no separate audio fields\\n- **Creature Sounds**: Always include with timing - 'at 2.0s happy chirps (audio/sfx)'\\n- **Dialogue**: ONLY if allow_dialogue=True - 'at 3.0s Floof says \"Wow!\" (dialogue)'\\n- **Sound Effects**: Environmental sounds - 'at 5.0s splash (audio/sfx)'\\n- **Ambient**: Background soundscape - 'forest ambiance (ambient audio)'\\n- **Timing Format**: Use 'at X.Xs' format for precise timing",
          "first_frame_description": "**CONDITIONAL FIELD - NOT ALWAYS REQUIRED**\\n\\n**WHEN TO INCLUDE** (provide detailed description):\\n- Segment 1: ALWAYS include (establishes the starting scene)\\n- Scene change: Include when location/setting changes from previous segment\\n- Different scenes idea: Include for EVERY segment if idea mentions 'different scenes/locations'\\n\\n**WHEN TO SET TO NULL** (consecutive/continuous scenes):\\n- Set to null when scene continues from previous segment without location change\\n- Set to null when action flows directly from previous segment's ending\\n- Example: If segment 2 continues in same room as segment 1, set to null\\n\\n**WHEN INCLUDED** (minimum 30 words):\\nULTRA-DETAILED frame description with: Camera angle, Character's exact pose (specify position for EACH character if multiple), Full body visibility (include 'Full body visible from head to toe' in EITHER first or last frame), Specific objects, Lighting details, Environment specifics. For multi-character: specify each character's position (e.g., 'Floof on left, Poof on right').",
          "last_frame_description": "**ALWAYS REQUIRED** - Never set to null.\\n\\nULTRA-DETAILED frame description (minimum 30 words) including: Camera angle (e.g., 'Close-up from front', 'Wide shot from behind'), Character's exact final pose (e.g., 'leaning forward with paws on ground'), Full body visibility (at least ONE frame per segment must show full body), Specific objects and positions, Lighting details, Environmental details. For multi-character: specify each character's position and action. This frame will be generated by Imagen.",
          "scene": "What's happening visually",
          "action": "Specific character action (for multi-character: describe each character's action)",
          "reaction": "Character's reaction/emotion (for multi-character: each character's reaction)",
          "camera": "Specific camera angle and movement (e.g., 'Close-up on face, slow zoom in', 'Wide shot, tracking left', 'Low angle, static')",
          "visual_focus": "What viewers should notice",
          "overlay_text": "Text to display on screen - OMIT this field entirely if no overlay needed",
          "overlay_position": "top/center/bottom/top-left/top-right/bottom-left/bottom-right - OMIT if no overlay",
          "overlay_type": "title/subtitle/caption/description - OMIT if no overlay",
          "background": {{
            "location": "Specific location",
            "setting": "Detailed setting description",
            "time_of_day": "morning/afternoon/evening/night",
            "lighting": "natural/artificial/dramatic",
            "props": ["key props in scene"],
            "atmosphere": "mood and vibe",
            "video_prompt_background": "Complete background description for AI"
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
    
    **FIRST AND LAST FRAME DESCRIPTIONS** (CRITICAL FOR IMAGEN GENERATION):
    
    **First Frame Description** (ALL SEGMENTS):
    - Describe the STARTING FRAME: character's initial pose, position, environment
    - Character appearance STAYS THE SAME (from user's keyframe image)
    - Only describe: pose, body position, surroundings, background, lighting
    - **MUST show character FULLY VISIBLE** (whole body in frame)
    - This will be generated with Imagen (Nano Banana) using user's character image as reference
    - Example: "{character_name} standing at cave entrance, looking curious, surrounded by icy rocks and snow, soft moonlight from above, full body visible"
    
    **Last Frame Description** (ALL SEGMENTS):
    - Describe the ENDING FRAME: character's final pose, position at segment end
    - This frame will be generated with Imagen using BOTH:
      1. User's character image (for character consistency)
      2. The first frame of this segment (for environment/lighting consistency)
    - **MUST show character FULLY VISIBLE** (whole body in frame)
    - This becomes the FIRST FRAME of the NEXT segment (ensures perfect continuity)
    - Example: "{character_name} bent over puddle, eyes wide in surprise, same cave environment, full body visible"
    
    **Character Visibility Rule**:
    - Character MUST be fully visible (whole body) in BOTH first AND last frame
    - This ensures character consistency across all generated frames
    - Avoid close-ups that crop the character in frame descriptions
    - Full body visibility = better Imagen generation with character reference
    
    **REMEMBER**:
    - Maximum {num_segments} segments (each 8 seconds)
    - **CONTINUOUS STORY**: Segments 1→{num_segments} must flow as ONE unbroken sequence
    - **NO JUMPS**: Each segment picks up exactly where previous ended
    - **SAME LOCATION**: All segments in same environment (no scene changes)
    - 100% VISUAL storytelling - NO dialogue, NO narration
    - ONLY creature sounds: {sound_description}
    - Character appearance defined by keyframe image
    - **ALL SEGMENTS**: Include BOTH "first_frame_description" AND "last_frame_description"
    - **FRAME CHAINING**: Last frame of segment N = First frame of segment N+1
    - **CHARACTER VISIBILITY**: Character MUST be fully visible (whole body) in BOTH first and last frames
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
    
    {f"**FINAL REMINDER - CRITICAL**: Your JSON response MUST contain EXACTLY {num_segments} segments in the segments array. Count them before responding. If you have fewer than {num_segments}, add more segments to reach exactly {num_segments}. This is a STRICT requirement." if num_segments else ""}
    """
