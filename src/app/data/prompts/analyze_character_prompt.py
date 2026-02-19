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


def get_character_analysis_prompt(character_count: int, character_name: str = None, can_speak: bool = False) -> str:
    """
    Generate a prompt for analyzing characters from an image.
    
    Returns character data in the exact format needed:
    - Character name
    - Subject (what the character is - AI-detected from image)
    - Gender
    - Keywords (descriptive traits)
    - Voice description (creative, detailed sound description)
    
    Args:
        character_count: Number of characters to identify in the image
        character_name: Optional specific name to use for the main character
        can_speak: Whether character can speak human language (guides voice description format)
        
    Returns:
        str: The formatted prompt for character analysis
    """
    
    # Determine voice description instructions based on can_speak
    if can_speak:
        voice_instruction = """
    **VOICE DESCRIPTION FORMAT (can_speak = TRUE):**
    This character CAN SPEAK human language, so voice_description MUST include accent!
    Format: "[tone] and [ACCENT] and [quality] and [characteristic]"
    
    Examples:
    - "Deep resonant and British accent and powerful commanding and authoritative bass"
    - "Sweet melodic and American accent and cheerful high-pitched and innocent"
    - "Gentle aged and Scottish accent and warm grandfatherly and comforting wisdom"
    
    CRITICAL: MUST include accent (British, American, French, Scottish, Irish, etc.)
    """
    else:
        voice_instruction = """
    **VOICE DESCRIPTION FORMAT (can_speak = FALSE):**
    This character CANNOT SPEAK human language, only makes creature sounds!
    Format: "[sound type] and [quality] and [characteristic] and [emotion]"
    
    Examples:
    - "Cute creature vocalization and baby animal cooing and high-pitched fantasy squeak"
    - "Guttural roar and primal growling and savage snarling and beast-like rumbling"
    - "Mechanical beeps and boops and robotic monotone and electronic processing"
    
    CRITICAL: NO accent! Only describe sounds (roars, chirps, beeps, meows, etc.)
    """
    
    return f"""
    You are a character analyst. Analyze this image and provide character information.
    
    Task: Analyze this image for {character_count} character(s).
    
    {f"Use '{character_name}' as the character name." if character_name else ""}
    
    {voice_instruction}
    
    For the character, provide:
    1. **name** - Character name
    2. **subject** - DETAILED description of how the character looks (appearance, colors, features, style)
    3. **gender** - male/female/non-binary/creature/undefined
    4. **keywords** - Comprehensive string of descriptive keywords (max 500 characters)
    5. **can_speak** - Boolean: true if character can speak human language, false if only creature sounds
    6. **voice_description** - Creative, detailed voice/sound description (format depends on can_speak)
    
    **SPEECH DETECTION (can_speak) - CRITICAL:**
    Analyze the character and determine if they can speak human language:
    
    **can_speak = TRUE** (Can speak words/dialogue):
    - ✅ Humans (any age, gender, ethnicity)
    - ✅ Humanoids (elves, dwarves, orcs, aliens with human-like features)
    - ✅ Anthropomorphic characters (if they look like they can talk)
    - ✅ Robots/AI with speaking capability (if they have speakers/mouth)
    - ✅ Magical beings that appear intelligent (wizards, witches, fairies)
    - ✅ Any character that looks like they could have conversations
    
    **can_speak = FALSE** (Only creature sounds/noises):
    - ❌ Animals (dogs, cats, birds, fish, etc.)
    - ❌ Monsters (beasts, dragons, demons without human features)
    - ❌ Creatures (fantasy creatures, mythical beasts)
    - ❌ Non-speaking robots (R2-D2 style, only beeps)
    - ❌ Babies/infants (only crying/cooing)
    - ❌ Any character that would only make sounds, not words
    
    **When in doubt:** If the character has a human-like mouth/face and appears intelligent → can_speak = true
    
    **Keywords Guidelines:**
    Analyze the image and generate a comprehensive keyword string covering ALL relevant aspects:
    - **Species/Type**: human, monster, dragon, cat, dog, robot, alien, fairy, demon, angel, etc.
    - **Colors**: red, blue, green, golden, silver, black, white, rainbow, multicolored, etc.
    - **Size**: tiny, small, medium, large, huge, gigantic, towering, etc.
    - **Nature/Personality**: friendly, aggressive, playful, serious, mysterious, cheerful, grumpy, wise, etc.
    - **Physical Traits**: fluffy, scaly, furry, smooth, spiky, soft, rough, shiny, etc.
    - **Appearance**: cute, scary, elegant, rugged, beautiful, ugly, majestic, adorable, etc.
    - **Age**: young, old, ancient, baby, child, adult, elderly, etc.
    - **Style**: fantasy, modern, futuristic, medieval, tribal, magical, technological, etc.
    - **Special Features**: winged, horned, tailed, armored, glowing, transparent, etc.
    
    Create a comma-separated string with ALL relevant keywords you observe (max 500 characters).
    Example: "human, male, warrior, tall, muscular, brown-hair, blue-eyes, armored, medieval, brave, strong, confident, battle-worn, scarred, experienced, adult, serious, determined"
    
    **Voice Description Guidelines:**
    The format DEPENDS on can_speak value:
    
    **IF can_speak = TRUE (Speaking Characters):**
    - Format: "[tone] and [ACCENT] and [quality] and [characteristic]"
    - MUST include accent (British, American, French, Scottish, Irish, Australian, etc.)
    - Use " and " to separate phrases (NOT commas)
    - Include 4-6 descriptive phrases
    - Focus on how they would SPEAK words
    
    Examples:
    - Male Hero: "Deep resonant and British accent and powerful commanding and authoritative bass"
    - Young Girl: "Sweet melodic and American accent and cheerful high-pitched and innocent"
    - Wise Elder: "Gentle aged and Scottish accent and warm grandfatherly and comforting wisdom"
    - Villain: "Sinister raspy and German accent and menacing low growl and dark threatening"
    - Princess: "Elegant refined and French accent and soft melodic and graceful"
    - Warrior: "Strong confident and Irish accent and bold assertive and battle-hardened"
    - Scientist: "Intelligent precise and German accent and analytical methodical and calm"
    
    **IF can_speak = FALSE (Non-Speaking Characters):**
    - Format: "[sound type] and [quality] and [characteristic] and [emotion]"
    - NO accent needed (they don't speak human language)
    - Use " and " to separate phrases (NOT commas)
    - Include 4-6 descriptive phrases
    - Focus on SOUNDS they make (roars, chirps, beeps, etc.)
    
    Examples:
    - Cute Creature: "Cute creature vocalization and baby animal cooing and high-pitched fantasy squeak and soft melodic chirp"
    - Monster: "Guttural roar and primal growling and savage snarling and beast-like rumbling"
    - Robot: "Mechanical synthesized and digital beeps and boops and robotic monotone and electronic processing"
    - Dragon: "Deep thunderous roar and ancient rumbling and powerful echoing and majestic beast sounds"
    - Cat: "Soft meowing and gentle purring and playful chirping and contented trilling"
    - Dog: "Excited barking and happy panting and playful yipping and friendly woofing"
    
    **Subject Guidelines - DETAILED APPEARANCE DESCRIPTION:**
    The subject field should be a DETAILED description of how the character looks, including:
    - **Type/Species**: What kind of character (human, creature, robot, animal, fantasy being, etc.)
    - **Physical Features**: Size, body shape, distinctive features
    - **Colors**: Main colors, patterns, color combinations
    - **Style/Aesthetic**: Overall visual style (cute, scary, elegant, futuristic, etc.)
    - **Key Visual Elements**: Most noticeable visual characteristics
    
    **Length**: 10-30 words (detailed but concise)
    
    **Examples:**
    - "A fluffy pink creature with big round eyes, small body, soft fur, and adorable innocent expression"
    - "A tall muscular human warrior with brown hair, blue eyes, wearing medieval armor with battle scars"
    - "A sleek silver humanoid robot with glowing blue circuits, mechanical joints, and futuristic design"
    - "A majestic red dragon with golden scales, large wings, sharp claws, and fierce yellow eyes"
    - "A small orange tabby cat with white paws, green eyes, fluffy tail, and playful demeanor"
    - "An ethereal fairy with translucent wings, flowing white dress, glowing aura, and delicate features"
    
    Focus on VISUAL APPEARANCE that helps identify and describe the character for video generation.
    
    Return ONLY valid JSON with this EXACT structure:
    {{{{
      "name": "Character Name",
      "subject": "A fluffy pink creature with big round eyes, small body, soft fur, and adorable innocent expression",
      "gender": "male",
      "keywords": "human, male, warrior, tall, muscular, brown-hair, blue-eyes, armored, medieval, brave, strong, confident",
      "voice_description": "{('Deep resonant and British accent and powerful commanding and authoritative bass' if can_speak else 'Cute creature vocalization and baby animal cooing and high-pitched fantasy squeak')}"
    }}}}
    
    CRITICAL RULES: 
    1. **subject** - MUST be a DETAILED visual description (10-30 words) of how the character looks, including type, features, colors, and style
    
    2. **voice_description** - Format based on can_speak parameter (already provided):
       - Follow the format instructions above
       - Always use " and " to separate phrases (NOT commas)
       - Include 4-6 descriptive phrases
    
    3. **keywords** - SINGLE STRING (not array) with comma-separated descriptors, max 500 characters
       - Include ALL relevant aspects: species, colors, size, nature, traits, appearance, age, style, features
    
    4. **JSON format** - Do NOT return "characters_roster" array, just return the single character object
    
    5. **Do NOT include can_speak in response** - It's already provided as input parameter
    """
