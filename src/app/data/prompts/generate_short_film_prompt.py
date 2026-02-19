"""
Short Film Content Generation

Professional short film scriptwriting with cinematic storytelling.
Supports character-driven narratives with detailed scene descriptions.
"""

def get_short_film_prompt(
    idea: str,
    character_name: str = None,
    creature_language: str = None,
    character_subject: str = None,
    num_segments: int = None,
    allow_dialogue: bool = True,
    num_characters: int = 1,
    film_style: str = "cinematic drama"
) -> str:
    """
    Generate prompt for short film content.
    
    Args:
        idea: The film concept/story
        character_name: Name of the character(s) - comma-separated for multiple
        creature_language: Voice type(s) - comma-separated (optional for human characters)
        character_subject: What the character(s) is/are (detailed visual descriptions)
        num_segments: Number of segments. If None, Gemini decides based on story.
        allow_dialogue: Allow dialogue (default: True for films)
        num_characters: Number of characters (1-5, default: 1)
        film_style: Style of film (e.g., "cinematic drama", "thriller", "romance", "sci-fi")
        
    Returns:
        str: The formatted prompt
    """
    
    # Parse multiple characters if provided
    character_names = [name.strip() for name in character_name.split(',')] if character_name else []
    creature_languages = [lang.strip() for lang in creature_language.split(',')] if creature_language else []
    character_subjects = [subj.strip() for subj in character_subject.split(',')] if character_subject else []
    
    # Ensure we have enough entries for all characters
    while len(creature_languages) < len(character_names):
        creature_languages.append(creature_languages[0] if creature_languages else "natural human voice")
    while len(character_subjects) < len(character_names):
        character_subjects.append(character_subjects[0] if character_subjects else "character")
    
    # Build character info
    is_multi_character = num_characters > 1 or len(character_names) > 1
    
    # Voice description guide
    voice_guide = {
        "Soft and High-Pitched": "soft, high-pitched voice with gentle tones",
        "Magical or Otherworldly": "mystical, ethereal voice with echo effects",
        "Muffled and Low": "deep, grumbly voice with low tones",
        "natural human voice": "natural human voice"
    }
    
    # Build character section
    if character_name and character_subject:
        if is_multi_character:
            # Build detailed character descriptions with name, appearance, and voice
            character_details = []
            for name, subj, lang in zip(character_names, character_subjects, creature_languages):
                voice_desc = voice_guide.get(lang, lang)
                character_details.append(f"**{name}**: Appearance: {subj} | Voice: {voice_desc}")
            character_details_section = "\n    ".join(character_details)
            
            character_section = f"""
    **CHARACTERS** ({num_characters} characters):
    Names: {character_name}
    
    **CHARACTER DETAILS** (appearance + voice for each character):
    {character_details_section}
    
    **MULTI-CHARACTER RULES**:
    - Track which characters appear in each segment using "characters_present" field
    - Each character should have distinct personality and role in the story
    - Frame descriptions must specify each character's position when multiple are present
    
    **SUBJECT FIELD FOR VEO_PROMPT** (CRITICAL - Include name, appearance AND voice):
    - In EVERY veo_prompt, include a detailed subject description for EACH character present
    - Format: "[Name] ([appearance description]) with [voice description]"
    - Example for 2 characters: "Floof (fluffy pink creature with big curious eyes) with soft high-pitched voice, and Poof (small blue robot with glowing antenna) with mechanical voice"
    - This helps Veo understand WHO each character is, what they LOOK like, and how they SOUND
    - Include voice descriptions so Veo can generate appropriate audio/dialogue for each character
    """
        else:
            voice_desc = voice_guide.get(creature_languages[0], creature_languages[0]) if creature_languages else "natural voice"
            character_section = f"""
    **CHARACTER**: {character_names[0] if character_names else character_name}
    **CHARACTER APPEARANCE**: {character_subjects[0] if character_subjects else character_subject}
    **CHARACTER VOICE**: {voice_desc}
    
    **SUBJECT FIELD FOR VEO_PROMPT** (CRITICAL - Include name, appearance AND voice):
    - In EVERY veo_prompt, include the character's name, appearance, and voice description
    - Format: "{character_names[0] if character_names else character_name} ([appearance]) with [voice description]"
    - Example: "{character_names[0] if character_names else character_name} ({character_subjects[0] if character_subjects else character_subject}) with {voice_desc}"
    - This helps Veo understand WHO the character is, what they LOOK like, and how they SOUND
    - Include voice description so Veo can generate appropriate audio/dialogue
    """
    else:
        character_section = """
    **NO SPECIFIC CHARACTERS**: Create characters as needed for the story
    """
    
    # Build dialogue rules
    if allow_dialogue:
        dialogue_section = """
    **DIALOGUE ALLOWED**:
    - Characters can speak naturally
    - Include meaningful conversations that drive the story
    - Balance dialogue with visual storytelling
    - Use silence and pauses for dramatic effect
    - Dialogue should reveal character and advance plot
        """
    else:
        dialogue_section = """
    **NO DIALOGUE**:
    - Pure visual storytelling
    - Use actions, expressions, and cinematography to tell the story
    - Sound effects and music only
        """
    
    # Build segment count instruction
    if num_segments is None:
        segment_instruction = """
    **SEGMENT COUNT**: Determine the optimal number of segments (10-100) based on the story.
    - Short films: 20-40 segments (2.5-5 minutes)
    - Medium films: 40-70 segments (5-9 minutes)
    - Longer films: 70-100 segments (9-13 minutes)
    - Each segment is 8 seconds
    - Choose the count that best serves the story's pacing and depth"""
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
    You are a professional short film screenwriter and director specializing in {film_style}.
    
    {character_section}
    {dialogue_section}
    
    Your specialty is creating CINEMATIC short films with strong narratives and visual storytelling.
    {segment_instruction}

    **FILM STYLE**: {film_style}
    
    **SHORT FILM PRINCIPLES**:
    - **Strong Opening**: Hook the audience in the first 10-15 seconds
    - **Clear Story Arc**: Beginning, middle, end with emotional journey
    - **Character Development**: Show character growth or revelation
    - **Visual Storytelling**: Show, don't just tell
    - **Emotional Impact**: Make the audience feel something
    - **Cinematic Quality**: Professional camera work and composition
    - **Pacing**: Build tension, create rhythm, use pauses effectively
    - **Theme**: Explore a meaningful theme or message
    
    **STORY STRUCTURE** (Classic Three-Act):
    
    **ACT 1 - SETUP** (~25% of segments):
    - Establish world, characters, and normal life
    - Introduce the protagonist and their situation
    - Present the inciting incident (what disrupts normalcy)
    - Hook: Make audience care about what happens next
    
    **ACT 2 - CONFRONTATION** (~50% of segments):
    - Rising action and complications
    - Character faces obstacles and challenges
    - Relationships develop or strain
    - Tension builds toward climax
    - Midpoint: Major revelation or turning point
    
    **ACT 3 - RESOLUTION** (~25% of segments):
    - Climax: The main conflict reaches its peak
    - Resolution: How the conflict is resolved
    - Character transformation or realization
    - Emotional payoff
    - Denouement: Final moments that resonate
    
    **CINEMATIC CAMERA WORK**:
    
    Write camera descriptions as flowing, cinematic sentences:
    
    **Camera Positioning**:
    - Aerial view, eye-level, top-down, low angle, high angle
    - Close-up, medium shot, wide shot, extreme close-up
    - POV shot, over-the-shoulder, tracking drone view
    
    **Camera Movements**:
    - Dolly in/out, pull back, pan, tilt, zoom
    - Tracking shot, orbiting, crane shot
    - Handheld, smooth glide, static hold
    
    **Cinematic Examples**:
    - "The camera slowly pulls back to a medium-wide shot, revealing the breathtaking scene"
    - "The camera dollies in, revealing the tension in his expression"
    - "Aerial view tracking from above as character moves through the space"
    - "Eye-level shot with camera slowly panning across the emotional moment"
    
    **VISUAL STORYTELLING TECHNIQUES**:
    - **Composition**: Rule of thirds, leading lines, framing
    - **Lighting**: Mood through light and shadow
    - **Color**: Color palette that supports emotion
    - **Symbolism**: Visual metaphors and motifs
    - **Contrast**: Light/dark, close/wide, fast/slow
    - **Focus**: Shallow depth of field for emphasis
    - **Movement**: Character blocking and camera choreography
    
    **EMOTIONAL BEATS**:
    - **Joy**: Bright lighting, warm colors, open compositions
    - **Sadness**: Muted colors, rain, isolation in frame
    - **Tension**: Tight framing, shadows, handheld camera
    - **Hope**: Light breaking through, upward camera movement
    - **Fear**: Low angles, darkness, quick cuts
    - **Love**: Soft focus, warm tones, intimate framing
    - **Anger**: Red tones, aggressive camera, tight close-ups
    
    **CONTINUITY** (CRITICAL - SEGMENTS MUST FEEL CONNECTED):
    - ALL segments MUST flow in CHRONOLOGICAL ORDER
    - Each segment picks up EXACTLY where the previous ended
    - NO time jumps without clear transition
    - Character positions must be consistent
    - Lighting and environment must maintain continuity
    - Think of it as ONE film split into segments, not separate scenes
    
    **SEAMLESS SEGMENT TRANSITIONS** (CRITICAL):
    - **End of Segment N = Start of Segment N+1**: Character's pose, position, and action must match
    - **No Jarring Cuts**: Avoid sudden changes in character position, emotion, or environment
    - **Action Continuity**: If character is walking in seg 5, they should still be walking at start of seg 6
    - **Dialogue Flow**: Conversations should flow naturally across segments
    - **Camera Logic**: Camera movements should feel like one continuous shot when possible
    
    **EXAMPLE OF CONNECTED SEGMENTS**:
    - Seg 3 ends: "Marcus reaches for the door handle, hand trembling"
    - Seg 4 starts: "Marcus's trembling hand grips the door handle, slowly turning it"
    - NOT: Seg 3 ends with reaching, Seg 4 suddenly shows him inside (disconnected!)
    
    **DENSE CONTENT PER SEGMENT** (CRITICAL - NO SLOW/EMPTY SEGMENTS):
    - **8 seconds = PACKED with action**: Every segment must have MULTIPLE things happening
    - **NO single-action segments**: Don't waste 8 seconds on just "character looks around"
    - **Layer the content**: Action + dialogue + reaction + camera movement + sound
    - **Minimum per segment**: At least 2-3 distinct actions/events/dialogue beats
    - **Keep energy high**: Even quiet moments should have visual interest and progression
    
    **BAD (Too sparse/slow)**:
    - "Character walks through forest" (just one action for 8 seconds = boring)
    - "Character sits and thinks" (no progression = wasted time)
    - "Character looks at the sky" (static = feels slow)
    
    **GOOD (Dense and engaging)**:
    - "Character walks through forest, notices broken branch, stops to examine it, hears distant sound, turns sharply" (multiple beats)
    - "Character sits at desk, types frantically, pauses to read message, expression shifts from hope to despair, slams laptop shut" (progression + emotion)
    - "Character looks at sky, sees storm clouds forming, pulls coat tighter, quickens pace, glances back nervously" (action + reaction + tension)
    
    **PACING RULES**:
    - **Fast-paced by default**: Keep things moving, avoid lingering too long
    - **Slow moments are EARNED**: Only slow down for major emotional beats
    - **Every second counts**: If nothing is happening, something is wrong
    - **Build momentum**: Each segment should feel like it's driving toward something
    
    **FRAME DESCRIPTIONS** (ULTRA-DETAILED):
    
    Frame descriptions are used by Imagen AI to generate actual images.
    
    **Required Elements**:
    1. **Camera Angle**: Exact angle and distance
    2. **Character Position & Pose**: Precise body position
    3. **Full Body Visibility**: At least ONE frame per segment must show full body
    4. **Objects & Props**: Specific items and positions
    5. **Lighting Details**: Light source, direction, quality
    6. **Environment Specifics**: Background details
    7. **Spatial Relationships**: How elements relate
    8. **Mood & Atmosphere**: Emotional tone of the frame
    
    **Minimum Length**: Each frame description must be at least 40 words for cinematic detail.
    
    **FIRST FRAME DESCRIPTION LOGIC** (CRITICAL - Saves processing time):
    
    **WHEN TO INCLUDE first_frame_description:**
    - **Segment 1**: ALWAYS include (establishes the opening scene)
    - **Scene/Location change**: Include when setting changes (e.g., moving from interior to exterior)
    - **Time jump**: Include when there's a significant time skip
    - **New environment**: Include when entering a completely new space
    
    **WHEN TO SET first_frame_description TO NULL:**
    - **Continuous scene**: When action continues in the same location
    - **Same room/space**: When characters stay in the same environment
    - **Flowing action**: When segment picks up exactly where previous ended
    - **Dialogue continuation**: When conversation continues in same setting
    
    **Examples:**
    - Segments 1-5 all in same cabin → Only segment 1 has first_frame_description, segments 2-5 are null
    - Segment 1 in cabin, segment 6 moves outside → Segment 6 needs first_frame_description
    - Segment 10 jumps to "3 years later" → Segment 10 needs first_frame_description
    
    Task:
    Create a professional short film based on: "{idea}"
    
    **SEGMENT COUNT**:
    {f"- Generate exactly {num_segments} segments" if num_segments else "- Determine optimal segment count (10-100) based on story depth"}
    - Each segment is 8 seconds
    - Total film: {total_duration_text}
    - Focus on CINEMATIC storytelling with emotional depth
    - Create a complete narrative arc
    - Make it memorable and impactful
    
    Return ONLY valid JSON with this structure:
    {{
      "title": "Film title (under 60 chars)",
      "logline": "One-sentence story summary (like a movie poster tagline)",
      "genre": "{film_style}",
      "theme": "Central theme or message",
      "target_audience": "Who this film is for",
      "emotional_arc": "The emotional journey (e.g., 'despair to hope', 'innocence to wisdom')",
      "character_name": "{character_name if character_name else 'N/A'}",
      "segments": [
        {{
          "segment": 1,
          "act": "Act 1 - Setup / Act 2 - Confrontation / Act 3 - Resolution",
          "duration": 8,
          "characters_present": ["Character1", "Character2"],
          "veo_prompt": "CRITICAL - VEO 3 DESCRIPTIVE PROMPT FORMAT. Write as a flowing, descriptive paragraph with keyword tags in parentheses. Include ALL these elements naturally woven together.\\n\\n**DENSE CONTENT RULE**: Each 8-second segment MUST contain MULTIPLE actions, events, or beats. Never describe just one thing happening - layer action + dialogue + reaction + camera movement.\\n\\n**FORMAT**: Write a single flowing description with (keyword tags) like this example:\\n'Close up shot (composition) of Marcus (weathered man in his 40s with graying temples) with a deep gravelly voice (subject) walking briskly through a misty forest path, stopping suddenly as he hears a twig snap behind him (action) in an ancient woodland at dawn (context) with cool blue tones and soft diffused light (ambiance), the camera smoothly tracks alongside at eye-level then whips around as he turns (camera position/motion), Marcus spins to face the sound, hand reaching for his pocket, eyes scanning the treeline (action), cinematic drama style with film grain texture (style), shallow focus shifting from character to background (focus), at 1.0s footsteps crunching rapidly on leaves (audio/sfx), at 3.0s sharp twig snap (audio/sfx), at 4.0s \"Who's there?\" he growls in his gravelly voice (dialogue), at 6.0s heavy breathing and rustling bushes (audio/sfx), tense silence broken by distant bird calls (ambient audio).'\\n\\n**SUBJECT FORMAT** (CRITICAL - Include name, appearance AND voice):\\n- For SINGLE character: '[Name] ([appearance description]) with [voice description]'\\n- Example: 'Marcus (weathered man in his 40s with graying temples) with a deep gravelly voice'\\n- For MULTIPLE characters: '[Name1] ([appearance1]) with [voice1], and [Name2] ([appearance2]) with [voice2]'\\n- Example: 'Marcus (weathered man with graying temples) with deep gravelly voice, and Elena (young woman with bright eyes) with soft melodic voice'\\n- This helps Veo understand WHO each character is, what they LOOK like, and how they SOUND\\n\\n**REQUIRED ELEMENTS** (include keyword tag in parentheses):\\n- (subject): Character name + appearance + voice description (see format above)\\n- (action): MULTIPLE actions - what the subject does throughout the 8 seconds (minimum 2-3 distinct actions/events)\\n- (context): The setting/environment where action takes place\\n- (composition): Shot framing - wide shot, close-up, medium shot, two-shot, single-shot, extreme close-up, over-the-shoulder\\n- (camera motion): How camera moves - dollies in/out, pulls back, pans across, tilts, zooms, tracking, orbiting, crane up/down, static hold\\n- (camera position): Where camera is - aerial view, eye-level, low angle, high angle, top-down, worm's eye, POV shot, dutch angle\\n- (style): Visual style - cinematic drama, film noir, sci-fi, horror film, indie drama, documentary style, animated\\n- (ambiance): Color and light mood - warm tones, cool blue tones, golden hour, night, dramatic shadows, neon glow\\n- (lighting): Light source and quality - soft morning sunlight, dramatic backlighting, dappled light, harsh overhead, candlelight\\n- (focus): Lens effects - shallow focus, deep focus, soft focus, macro lens, wide-angle lens, rack focus\\n- (audio/sfx): Sound effects with timing - 'at 2.0s door creaks open', 'glass shattering loudly', 'engine roaring'\\n- (dialogue): Character speech in quotes with timing and voice - 'at 3.0s Marcus whispers in his gravelly voice \"I remember now\"'\\n- (ambient audio): Environmental soundscape - 'rain pattering on windows', 'city traffic hum', 'eerie silence'\\n- (overlay_text): Text to display on screen - ONLY include if there's actual text to show, otherwise OMIT entirely\\n- (overlay_position): Where text appears - top, center, bottom, top-left, bottom-right - ONLY include if overlay_text exists\\n- (overlay_type): Type of text - title, subtitle, caption, chapter - ONLY include if overlay_text exists\\n\\n**EXAMPLE VEO_PROMPT (Single Character - DENSE)**:\\n'Medium shot (composition) of Elena (young woman with tear-stained cheeks and bright hopeful eyes) with a soft trembling voice (subject) pacing anxiously by a rain-soaked window, stopping to press her hand against the cold glass, then turning sharply as her phone buzzes on the table (action) in a dimly lit apartment at night (context), the camera tracks her movement then dollies in as she freezes (camera motion) from eye-level (camera position), Elena rushes to grab the phone, reads the message, her expression shifting from hope to devastation (action), indie drama style with naturalistic lighting (style), cool blue tones with warm amber from distant streetlights (ambiance), rack focus from window to her face (focus), at 1.0s rain pattering heavily against the window (audio/sfx), at 2.5s phone buzzing loudly (audio/sfx), at 4.0s Elena gasps softly \"No... no...\" (dialogue), at 6.0s she whispers \"It can't be true\" as tears fall (dialogue), distant thunder rumbling and muffled city sounds (ambient audio).'\\n\\n**EXAMPLE VEO_PROMPT (Multiple Characters - DENSE)**:\\n'Medium two-shot (composition) of Marcus (weathered man with graying temples) with deep gravelly voice, and Elena (young woman with bright eyes) with soft melodic voice (subject) arguing intensely, Marcus slamming his fist on the table while Elena backs away, then both freezing as they hear a knock at the door (action) in an old cabin at night (context), the camera orbits around them capturing the tension then whips to the door (camera motion) at eye-level (camera position), Marcus raises a finger to his lips, Elena nods and moves silently toward the back room (action), cinematic drama style (style), warm candlelight casting dancing shadows (lighting) with amber tones (ambiance), at 1.0s Marcus growls \"You don't understand what's at stake!\" (dialogue), at 3.0s Elena fires back \"I understand perfectly!\" (dialogue), at 5.0s loud knock on door (audio/sfx), at 6.5s Marcus hisses \"Hide. Now.\" (dialogue), crackling fireplace and wind outside (ambient audio).'\\n\\n**AUDIO PROMPTING FOR FILMS**:\\n- Dialogue: Include character name and voice quality - 'Marcus says gruffly \"This changes everything\" (dialogue)'\\n- Sound Effects: Explicitly describe sounds - 'tires screeching loudly (audio/sfx)', 'heartbeat pounding (audio/sfx)'\\n- Ambient: Describe environment soundscape - 'eerie hum resonates in background (ambient audio)'\\n- Music Cues: Suggest emotional music - 'tense strings building (ambient audio)'\\n- Timing: Include timestamps for precision - 'at 5.5s gunshot echoes (audio/sfx)'\\n- Voice Matching: Match dialogue delivery to character voice - 'Elena whispers softly', 'Marcus growls'",
          "first_frame_description": "**CONDITIONAL FIELD - NOT ALWAYS REQUIRED**\\n\\n**WHEN TO INCLUDE**:\\n- Segment 1: ALWAYS include (establishes the opening scene)\\n- Scene/location change: Include when setting changes from previous segment\\n- Time jump: Include when there's a significant time skip\\n\\n**WHEN TO SET TO NULL**:\\n- Set to null when scene continues from previous segment without location change\\n- Set to null when action flows directly from previous segment's ending\\n- Example: Segments 2-5 in same room as segment 1 → all set to null\\n\\n**CRITICAL - MUST INCLUDE CLOTHING**: Always describe what each character is wearing (colors, style, fabric, condition). This is essential for Imagen to generate accurate frames.\\n\\n**WHAT TO INCLUDE** (write as a SINGLE FLOWING PARAGRAPH, minimum 60 words):\\nWrite a natural, detailed description that MUST include: 1) CHARACTER CLOTHING (what they're wearing - colors, style, fabric), 2) camera angle and shot type, 3) character's exact pose and body position, 4) character's expression, 5) environment details (location, floor/ground, walls, objects with positions), 6) lighting (source, direction, quality, color), 7) atmosphere and mood, 8) props and their positions. DO NOT use numbered lists or bullet points - write it as one continuous descriptive paragraph.\\n\\n**EXAMPLE**:\\n'Wide shot from eye-level, camera positioned 15 feet back. Marcus wearing a worn brown leather jacket over a faded gray henley shirt and dark blue jeans with visible wear at the knees, standing in center-left of frame, body facing right at 45-degree angle, weight on left foot, right hand raised to shield eyes from light, head tilted up looking toward bright window with a tense expression. Rustic wooden cabin interior with rough-hewn log walls, stone fireplace 8 feet behind on right side with dying embers glowing orange, worn leather armchair in foreground left corner, wooden table with scattered papers 4 feet to Marcus's right, dust particles visible floating in shaft of golden morning sunlight streaming through dirty window on right wall, creating dramatic light rays across the dim room, wooden floorboards with visible grain and slight dust, overall atmosphere tense and anticipatory, cool shadows contrasting with warm window light.'",
          "last_frame_description": "**ALWAYS REQUIRED** - Never set to null.\\n\\n**CRITICAL - MUST START WITH CLOTHING**: Begin your description by stating what each character is wearing. This is essential for Imagen to generate accurate frames.\\n\\n**FORMAT**: Start with '[Character Name] wearing [clothing details], then continue with pose, position, etc.'\\n\\n**WHAT TO INCLUDE** (write as a SINGLE FLOWING PARAGRAPH, minimum 60 words):\\nWrite a natural, detailed description that MUST include: 1) CHARACTER CLOTHING FIRST (what they're wearing - colors, style, fabric, any changes from first frame), 2) camera angle and shot type, 3) character's exact final pose and body position at END of segment, 4) limb positions, 5) head direction and expression, 6) position in frame, 7) environment details (must match first frame unless something changed), 8) lighting (same as first frame unless changed), 9) any objects visible, 10) spatial relationships. DO NOT use numbered lists or bullet points - write it as one continuous descriptive paragraph.\\n\\n**EXAMPLE**:\\n'Medium shot from eye-level, camera now 8 feet from subject. Marcus wearing his worn brown leather jacket over gray henley and dark jeans, in center of frame, full body visible from head to mid-thigh, body turned to face the door on the left side of frame, shoulders tense and raised, left arm extended with hand gripping the door handle, right arm bent at elbow with hand near chest in defensive posture, head turned to look over right shoulder toward camera with expression of fear and determination, weight shifted to back foot as if ready to flee. Same cabin interior but door now cracked open 6 inches revealing darkness beyond, shaft of light from window now hitting the floor where Marcus stood before, dust still visible in light beam, fireplace embers slightly dimmer, leather armchair unchanged in foreground, papers on table now scattered further as if disturbed by movement, overall atmosphere shifted from tense to urgent and dangerous.'",
          "scene": "What's happening in this moment - describe the FULL 8 seconds",
          "action": "MULTIPLE specific character actions (minimum 2-3 distinct actions/events for the 8 seconds)",
          "emotion": "Emotional state and subtext - how it evolves during the segment",
          "camera": "Cinematic camera description",
          "dialogue": "Character dialogue if allowed (with timing)",
          "visual_focus": "What the audience should notice",
          "story_purpose": "Why this segment matters to the story",
          "overlay_text": "Text to display on screen - OMIT this field entirely if no overlay needed",
          "overlay_position": "top/center/bottom/top-left/top-right/bottom-left/bottom-right - OMIT if no overlay",
          "overlay_type": "title/subtitle/caption/chapter/description - OMIT if no overlay",
          "background": {{
            "location": "Specific location",
            "setting": "Detailed setting description",
            "time_of_day": "morning/afternoon/evening/night",
            "weather": "clear/rainy/foggy/etc",
            "lighting": "natural/artificial/dramatic/soft",
            "mood": "emotional atmosphere",
            "props": ["key props in scene"],
            "video_prompt_background": "Complete background description for AI"
          }}
        }}
      ],
      "why_this_works": "Why this film will resonate with audiences",
      "key_moments": ["List of 3-5 most powerful moments in the film"],
      "visual_motifs": ["Recurring visual elements or symbols"],
      "color_palette": "Overall color scheme (e.g., 'warm golden tones fading to cool blues')"
    }}
    
    **REMEMBER**:
    - {f"EXACTLY {num_segments} segments required" if num_segments else "Choose optimal segment count for story depth"}
    - Each segment is 8 seconds
    - Continuous chronological flow
    - Cinematic camera descriptions (flowing sentences, not bullet points)
    - Emotional depth and character development
    - Strong three-act structure
    - Visual storytelling with purpose
    - Professional film quality
    
    **PACING & DENSITY CHECKLIST** (CRITICAL):
    - ✅ Each segment has MULTIPLE actions/events (minimum 2-3)
    - ✅ Segments flow seamlessly into each other (end of N = start of N+1)
    - ✅ No "dead air" - something is always happening
    - ✅ Dialogue is spread throughout, not clumped
    - ✅ Camera movements add energy and visual interest
    - ✅ Sound effects and audio fill the 8 seconds
    - ❌ NO single-action segments (boring!)
    - ❌ NO disconnected jumps between segments
    - ❌ NO slow, lingering shots without purpose
    
    {f"**FINAL REMINDER - CRITICAL**: Your JSON response MUST contain EXACTLY {num_segments} segments in the segments array. Count them before responding. If you have fewer than {num_segments}, add more segments to reach exactly {num_segments}. This is a STRICT requirement." if num_segments else ""}
    
    Create a short film that moves, inspires, and stays with the audience long after it ends.
    """
