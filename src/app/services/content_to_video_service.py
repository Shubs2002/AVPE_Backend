"""
Unified service to convert any content type (story, meme, free content) to video generation prompts
"""
import json
import re
import time


def clean_json_string(text: str) -> str:
    """Clean JSON string by replacing problematic characters"""
    # Replace en-dash and em-dash with regular dash
    text = text.replace('‑', '-').replace('—', '-').replace('–', '-')
    
    # Replace smart quotes with regular quotes
    text = text.replace('"', '"').replace('"', '"').replace(''', "'").replace(''', "'")
    
    # Remove other problematic Unicode characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    
    return text


def detect_content_type(content_data: dict) -> str:
    """
    Detect the type of content (story, meme, or free_content)
    
    Args:
        content_data: The content data dictionary
    
    Returns:
        str: Content type ('story', 'meme', 'free_content')
    """
    # Check for story-specific fields
    if 'characters_roster' in content_data and 'segments' in content_data:
        return 'story'
    
    # Check for meme-specific fields
    if 'meme_type' in content_data or 'characters_roster' in content_data:
        return 'meme'
    
    # Check for free content-specific fields
    if 'content_type' in content_data or 'value_proposition' in content_data:
        return 'free_content'
    
    # Default fallback - check segments structure
    segments = content_data.get('segments', [])
    if segments:
        first_segment = segments[0]
        if 'visual_comedy' in first_segment:
            return 'meme'
        elif 'value_content' in first_segment:
            return 'free_content'
        else:
            return 'story'
    
    return 'story'  # Default fallback


def extract_video_prompt_from_content_segment(content_data: dict, segment_number: int, content_type: str = None) -> dict:
    """
    Extract a clean video generation prompt from any content type segment
    
    Args:
        content_data: The complete content data
        segment_number: Which segment to extract (1-based indexing)
        content_type: Override content type detection
    
    Returns:
        dict: Clean prompt data for video generation
    """
    if content_type is None:
        content_type = detect_content_type(content_data)
    
    try:
        # Get the specific segment
        segments = content_data.get('segments', [])
        if segment_number < 1 or segment_number > len(segments):
            raise ValueError(f"Segment {segment_number} not found. Available segments: 1-{len(segments)}")
        
        segment = segments[segment_number - 1]  # Convert to 0-based indexing
        
        # Extract based on content type
        if content_type == 'story':
            return extract_story_segment_prompt(content_data, segment, segment_number)
        elif content_type == 'meme':
            return extract_meme_segment_prompt(content_data, segment, segment_number)
        elif content_type == 'free_content':
            return extract_free_content_segment_prompt(content_data, segment, segment_number)
        else:
            raise ValueError(f"Unknown content type: {content_type}")
            
    except Exception as e:
        raise ValueError(f"Error extracting video prompt: {str(e)}")


def extract_story_segment_prompt(content_data: dict, segment: dict, segment_number: int) -> dict:
    """Extract video prompt from story segment"""
    characters_roster = content_data.get('characters_roster', [])
    main_narrator_voice = content_data.get('narrator_voice', {})
    
    # Build character descriptions for this segment
    characters_present = segment.get('characters_present', [])
    character_descriptions = []
    
    for char_id in characters_present:
        character = next((c for c in characters_roster if c.get('id') == char_id), None)
        if character:
            char_desc = character.get('video_prompt_description', '')
            if char_desc:
                character_descriptions.append(f"{character['name']}: {char_desc}")
    
    # Get background description
    background_def = segment.get('background_definition', {})
    background_prompt = background_def.get('video_prompt_background', background_def.get('setting_description', ''))
    
    # Build the main prompt with validation
    scene_description = segment.get('scene', '').strip()
    if not scene_description:
        scene_description = f"Scene from {content_data.get('title', 'story')} segment {segment_number}"
    
    # Get content (narration or dialogue) with validation
    content_type = segment.get('content_type', 'narration')
    content_text = ""
    narrator_info = ""
    
    if content_type == 'narration':
        content_text = segment.get('narration', '').strip()
        if not content_text:
            content_text = f"Narration for segment {segment_number} of the story"
            
        # Add narrator voice information for narration segments - ENSURE CONSISTENCY
        segment_narrator = segment.get('narrator_voice_for_segment', {})
        if segment_narrator or main_narrator_voice:
            # ALWAYS use main narrator voice type for consistency
            voice_type = main_narrator_voice.get('voice_type', 'neutral')
            base_tone = main_narrator_voice.get('tone', 'neutral')
            base_pace = main_narrator_voice.get('speaking_pace', 'moderate')
            
            # Allow only minor variations per segment
            tone_variation = segment_narrator.get('tone_variation', base_tone)
            pace_variation = segment_narrator.get('pace_variation', 'same')
            emotion = segment_narrator.get('emotion', 'neutral')
            emphasis = segment_narrator.get('emphasis', '')
            
            narrator_info = f"Narrator Voice: CONSISTENT {voice_type} (same as all segments) with {tone_variation} tone variation, {pace_variation} pace, {emotion} emotion"
            if emphasis:
                narrator_info += f", emphasizing {emphasis}"
            
    elif content_type == 'dialogue':
        dialogue_lines = segment.get('dialogue', [])
        dialogue_text = []
        for line in dialogue_lines:
            char_name = line.get('character', 'Character').strip()
            char_line = line.get('line', '').strip()
            if char_name and char_line:
                dialogue_text.append(f"{char_name}: \"{char_line}\"")
        content_text = " ".join(dialogue_text) if dialogue_text else f"Dialogue for segment {segment_number}"
    
    # Build the complete prompt
    prompt_parts = []
    
    if scene_description:
        prompt_parts.append(f"Scene: {scene_description}")
    
    if background_prompt:
        prompt_parts.append(f"Background: {background_prompt}")
    
    if character_descriptions:
        prompt_parts.append(f"Characters: {'; '.join(character_descriptions)}")
    
    if content_text:
        prompt_parts.append(f"Action/Dialogue: {content_text}")
    
    if narrator_info:
        prompt_parts.append(narrator_info)
    
    # Add visual style elements
    camera = segment.get('camera', '')
    lighting = segment.get('lighting', '')
    color_palette = segment.get('color_palette', '')
    mood = segment.get('mood', '')
    
    if camera:
        prompt_parts.append(f"Camera: {camera}")
    if lighting:
        prompt_parts.append(f"Lighting: {lighting}")
    if color_palette:
        prompt_parts.append(f"Colors: {color_palette}")
    if mood:
        prompt_parts.append(f"Mood: {mood}")
    
    # Add critical video production instructions
    production_notes = []
    
    # Narration instructions
    if content_type == 'narration':
        production_notes.append("NARRATION: External voiceover only - characters do NOT speak the narration text. Narration is overlay audio, not character dialogue")
    
    # Timing and pacing instructions
    production_notes.append(f"TIMING: Adjust narration/dialogue speed to fit exactly {segment.get('clip_duration', 8)} seconds. Keep dialogue and narration concise and complete")
    
    # Text overlay instructions
    text_overlays = segment.get('text_overlays', [])
    if text_overlays:
        production_notes.append(f"TEXT OVERLAYS: Display on screen: {', '.join(text_overlays)}")
    
    # Transition instructions
    transition = segment.get('transition', '')
    if transition:
        production_notes.append(f"TRANSITION: {transition}")
    else:
        production_notes.append("TRANSITION: Smooth fade or cut to maintain story flow")
    
    # Completeness instruction
    production_notes.append("COMPLETENESS: Ensure video segment feels complete within duration - no abrupt cuts or incomplete actions")
    
    # Add production notes to prompt
    if production_notes:
        prompt_parts.append(f"PRODUCTION NOTES: {'; '.join(production_notes)}")
    
    # Join all parts
    final_prompt = ". ".join(prompt_parts)
    final_prompt = clean_json_string(final_prompt)
    
    return {
        "prompt": final_prompt,
        "segment_number": segment_number,
        "content_type": content_type,
        "duration_seconds": segment.get('clip_duration', 8),
        "characters_present": characters_present,
        "background_type": background_def.get('environment_type', 'realistic'),
        "mood": mood,
        "camera_style": camera,
        "lighting": lighting,
        "color_palette": color_palette,
        "narrator_voice": main_narrator_voice,
        "segment_narrator": segment.get('narrator_voice_for_segment', {}),
        "original_content_type": "story"
    }


def extract_meme_segment_prompt(content_data: dict, segment: dict, segment_number: int) -> dict:
    """Extract video prompt from meme segment"""
    characters_roster = content_data.get('characters_roster', [])
    main_narrator_voice = content_data.get('narrator_voice', {})
    meme_type = content_data.get('meme_type', 'comedy')
    
    # Build character descriptions for this segment
    characters_present = segment.get('characters_present', [])
    character_descriptions = []
    
    for char_id in characters_present:
        character = next((c for c in characters_roster if c.get('id') == char_id), None)
        if character:
            char_desc = character.get('video_prompt_description', '')
            if char_desc:
                character_descriptions.append(f"{character['name']}: {char_desc}")
    
    # Build the main prompt for meme
    scene_description = segment.get('scene', '')
    visual_comedy = segment.get('visual_comedy', '')
    
    # Add narrator voice information for meme commentary - ENSURE CONSISTENCY
    narrator_info = ""
    segment_narrator = segment.get('narrator_voice_for_segment', {})
    if segment_narrator or main_narrator_voice:
        # ALWAYS use main narrator voice type for consistency
        voice_type = main_narrator_voice.get('voice_type', '')
        base_comedic_style = main_narrator_voice.get('comedic_style', '')
        base_pace = main_narrator_voice.get('speaking_pace', '')
        
        # Allow only minor variations per segment
        delivery_variation = segment_narrator.get('comedic_delivery_variation', base_comedic_style)
        pace_variation = segment_narrator.get('pace_variation', 'same')
        energy_adjustment = segment_narrator.get('energy_adjustment', 'same')
        joke_timing = segment_narrator.get('joke_timing', '')
        
        narrator_info = f"Meme Narrator: CONSISTENT {voice_type} (same as all segments) with {delivery_variation} delivery variation, {pace_variation} pace for {meme_type} meme"
        if joke_timing:
            narrator_info += f", {joke_timing} timing"
    
    # Get dialogue/reactions
    dialogue_lines = segment.get('dialogue', [])
    reactions = segment.get('reactions', [])
    
    dialogue_text = []
    for line in dialogue_lines:
        char_name = line.get('character', 'Unknown')
        char_line = line.get('line', '')
        dialogue_text.append(f"{char_name}: \"{char_line}\"")
    
    reaction_text = []
    for reaction in reactions:
        char_name = reaction.get('character', 'Unknown')
        char_reaction = reaction.get('reaction', '')
        reaction_text.append(f"{char_name} reacts: {char_reaction}")
    
    # Build the complete prompt
    prompt_parts = []
    
    if scene_description:
        prompt_parts.append(f"Scene: {scene_description}")
    
    if visual_comedy:
        prompt_parts.append(f"Visual Comedy: {visual_comedy}")
    
    if character_descriptions:
        prompt_parts.append(f"Characters: {'; '.join(character_descriptions)}")
    
    if dialogue_text:
        prompt_parts.append(f"Dialogue: {'; '.join(dialogue_text)}")
    
    if reaction_text:
        prompt_parts.append(f"Reactions: {'; '.join(reaction_text)}")
    
    if narrator_info:
        prompt_parts.append(narrator_info)
    
    # Add meme-specific elements
    meme_format = segment.get('meme_format', '')
    facial_expressions = segment.get('facial_expressions', [])
    visual_gags = segment.get('visual_gags', [])
    
    if meme_format:
        prompt_parts.append(f"Meme Format: {meme_format}")
    if facial_expressions:
        prompt_parts.append(f"Expressions: {', '.join(facial_expressions)}")
    if visual_gags:
        prompt_parts.append(f"Visual Gags: {', '.join(visual_gags)}")
    
    # Add style elements
    camera = segment.get('camera', '')
    mood = segment.get('mood', 'comedic')
    
    if camera:
        prompt_parts.append(f"Camera: {camera}")
    
    prompt_parts.append(f"Style: Comedic meme video, {mood} mood")
    
    # Add critical video production instructions for memes
    production_notes = []
    
    # Meme-specific narration instructions
    production_notes.append("NARRATION: Meme commentary is external voiceover - characters do NOT speak narrator text. Commentary overlays the visual action")
    
    # Timing and pacing instructions for comedy
    production_notes.append(f"TIMING: Adjust dialogue/reactions/commentary speed to fit exactly {segment.get('clip_duration', 8)} seconds. Keep comedic timing tight and complete")
    
    # Text overlay instructions for memes
    text_overlays = segment.get('text_overlays', [])
    meme_text = segment.get('meme_text', [])
    all_text = text_overlays + meme_text
    if all_text:
        production_notes.append(f"TEXT OVERLAYS: Display meme text on screen: {', '.join(all_text)}")
    
    # Transition instructions for comedy flow
    transition = segment.get('transition', '')
    if transition:
        production_notes.append(f"TRANSITION: {transition}")
    else:
        production_notes.append("TRANSITION: Quick cut or comedic transition to maintain meme pacing")
    
    # Completeness instruction for memes
    production_notes.append("COMPLETENESS: Ensure meme segment delivers complete joke/gag within duration - no incomplete punchlines")
    
    # Add production notes to prompt
    if production_notes:
        prompt_parts.append(f"PRODUCTION NOTES: {'; '.join(production_notes)}")
    
    # Join all parts
    final_prompt = ". ".join(prompt_parts)
    final_prompt = clean_json_string(final_prompt)
    
    return {
        "prompt": final_prompt,
        "segment_number": segment_number,
        "content_type": "meme",
        "duration_seconds": segment.get('clip_duration', 8),
        "characters_present": characters_present,
        "meme_type": content_data.get('meme_type', 'comedy'),
        "comedy_style": segment.get('comedy_style', 'visual'),
        "mood": mood,
        "camera_style": camera,
        "narrator_voice": main_narrator_voice,
        "segment_narrator": segment.get('narrator_voice_for_segment', {}),
        "original_content_type": "meme"
    }


def extract_free_content_segment_prompt(content_data: dict, segment: dict, segment_number: int) -> dict:
    """Extract video prompt from free content segment"""
    main_narrator_voice = content_data.get('narrator_voice', {})
    content_type = content_data.get('content_type', 'educational')
    target_audience = content_data.get('target_audience', 'general')
    
    # Build the main prompt for free content
    scene_description = segment.get('scene', '')
    key_message = segment.get('key_message', '')
    value_content = segment.get('value_content', '')
    entertainment_element = segment.get('entertainment_element', '')
    visual_demonstration = segment.get('visual_demonstration', '')
    
    # Add narrator voice information for educational content - ENSURE CONSISTENCY
    narrator_info = ""
    segment_narrator = segment.get('narrator_voice_for_segment', {})
    if segment_narrator or main_narrator_voice:
        # ALWAYS use main narrator voice type for consistency
        voice_type = main_narrator_voice.get('voice_type', '')
        base_tone = main_narrator_voice.get('tone', '')
        base_pace = main_narrator_voice.get('speaking_pace', '')
        authority = main_narrator_voice.get('authority_level', '')
        
        # Allow only minor variations per segment
        tone_variation = segment_narrator.get('tone_variation', base_tone)
        pace_variation = segment_narrator.get('pace_variation', 'same')
        emphasis_style = segment_narrator.get('emphasis_style', '')
        teaching_approach = segment_narrator.get('teaching_approach', '')
        
        narrator_info = f"Educational Narrator: CONSISTENT {voice_type} (same as all segments) with {tone_variation} tone variation, {pace_variation} pace, {authority} authority for {content_type} content targeting {target_audience}"
        if emphasis_style:
            narrator_info += f", {emphasis_style} emphasis"
    
    # Build the complete prompt
    prompt_parts = []
    
    if scene_description:
        prompt_parts.append(f"Scene: {scene_description}")
    
    if key_message:
        prompt_parts.append(f"Key Message: {key_message}")
    
    if value_content:
        prompt_parts.append(f"Educational Content: {value_content}")
    
    if entertainment_element:
        prompt_parts.append(f"Entertainment: {entertainment_element}")
    
    if visual_demonstration:
        prompt_parts.append(f"Visual Demo: {visual_demonstration}")
    
    if narrator_info:
        prompt_parts.append(narrator_info)
    
    # Add content-specific elements
    engagement_hook = segment.get('engagement_hook', '')
    call_to_action = segment.get('call_to_action', '')
    text_overlays = segment.get('text_overlays', [])
    
    if engagement_hook:
        prompt_parts.append(f"Engagement: {engagement_hook}")
    
    if call_to_action:
        prompt_parts.append(f"CTA: {call_to_action}")
    
    if text_overlays:
        prompt_parts.append(f"Text Overlays: {', '.join(text_overlays)}")
    
    # Add style elements
    camera = segment.get('camera', '')
    lighting = segment.get('lighting', 'bright, natural')
    color_scheme = segment.get('color_scheme', 'vibrant')
    
    if camera:
        prompt_parts.append(f"Camera: {camera}")
    
    prompt_parts.append(f"Style: Educational content video, {lighting} lighting, {color_scheme} colors")
    
    # Add critical video production instructions for educational content
    production_notes = []
    
    # Educational narration instructions
    production_notes.append("NARRATION: Educational voiceover is external - presenter/characters do NOT speak narrator text unless specifically presenting. Narration overlays visual demonstrations")
    
    # Timing and pacing instructions for education
    production_notes.append(f"TIMING: Adjust narration/presentation speed to fit exactly {segment.get('clip_duration', 8)} seconds. Keep educational content clear and complete")
    
    # Text overlay instructions for educational content
    text_overlays = segment.get('text_overlays', [])
    key_points = segment.get('key_points', [])
    all_text = text_overlays + key_points
    if all_text:
        production_notes.append(f"TEXT OVERLAYS: Display educational text on screen: {', '.join(all_text)}")
    
    # Transition instructions for educational flow
    transition = segment.get('transition', '')
    if transition:
        production_notes.append(f"TRANSITION: {transition}")
    else:
        production_notes.append("TRANSITION: Smooth educational transition to maintain learning flow")
    
    # Completeness instruction for educational content
    production_notes.append("COMPLETENESS: Ensure educational segment delivers complete concept/lesson within duration - no incomplete explanations")
    
    # Add production notes to prompt
    if production_notes:
        prompt_parts.append(f"PRODUCTION NOTES: {'; '.join(production_notes)}")
    
    # Join all parts
    final_prompt = ". ".join(prompt_parts)
    final_prompt = clean_json_string(final_prompt)
    
    return {
        "prompt": final_prompt,
        "segment_number": segment_number,
        "content_type": "free_content",
        "duration_seconds": segment.get('clip_duration', 8),
        "content_category": content_data.get('content_type', 'educational'),
        "target_audience": content_data.get('target_audience', 'general'),
        "value_proposition": content_data.get('value_proposition', ''),
        "mood": "engaging",
        "camera_style": camera,
        "lighting": lighting,
        "color_scheme": color_scheme,
        "narrator_voice": main_narrator_voice,
        "segment_narrator": segment.get('narrator_voice_for_segment', {}),
        "original_content_type": "free_content"
    }


def extract_all_content_video_prompts(content_data: dict, content_type: str = None) -> list:
    """
    Extract video prompts for all segments in any content type
    
    Args:
        content_data: The complete content data
        content_type: Override content type detection
    
    Returns:
        list: List of video prompt dictionaries
    """
    if content_type is None:
        content_type = detect_content_type(content_data)
    
    segments = content_data.get('segments', [])
    prompts = []
    
    for i in range(1, len(segments) + 1):
        try:
            prompt_data = extract_video_prompt_from_content_segment(content_data, i, content_type)
            prompts.append(prompt_data)
        except Exception as e:
            print(f"Error extracting segment {i}: {str(e)}")
            continue
    
    return prompts


def content_segment_to_video_request(content_data: dict, segment_number: int, content_type: str = None, **video_options) -> dict:
    """
    Convert any content segment to a video generation request
    
    Args:
        content_data: The complete content data
        segment_number: Which segment to convert
        content_type: Override content type detection
        **video_options: Additional video generation options
    
    Returns:
        dict: Ready-to-use video generation request
    """
    if content_type is None:
        content_type = detect_content_type(content_data)
    
    prompt_data = extract_video_prompt_from_content_segment(content_data, segment_number, content_type)
    
    # Default video options
    video_request = {
        "prompt": prompt_data["prompt"],
        "durationSeconds": prompt_data.get("duration_seconds", 8),
        "resolution": video_options.get("resolution", "720p"),
        "aspectRatio": video_options.get("aspectRatio", "9:16"),
        "download": video_options.get("download", False),
        "filename": video_options.get("filename", f"{content_type}_segment_{segment_number}")
    }
    
    # Add any additional options
    video_request.update(video_options)
    
    return video_request


def generate_full_content_videos(content_data: dict, content_type: str = None, video_options: dict = None) -> dict:
    """
    Generate videos for all segments in any content type sequentially
    
    Args:
        content_data: The complete content data
        content_type: Override content type detection
        video_options: Video generation options
    
    Returns:
        dict: Results for all generated segments
    """
    if content_type is None:
        content_type = detect_content_type(content_data)
    
    if video_options is None:
        video_options = {}
    
    segments = content_data.get('segments', [])
    
    if not segments:
        raise ValueError("No segments found in content data")
    
    # Prepare results structure
    results = {
        "content_title": content_data.get('title', 'Untitled Content'),
        "content_type": content_type,
        "total_segments": len(segments),
        "segments_results": [],
        "success_count": 0,
        "error_count": 0,
        "video_urls": [],
        "downloaded_files": []
    }
    
    print(f"🎬 Starting video generation for {content_type}: {results['content_title']}")
    print(f"📊 Total segments to process: {len(segments)}")
    
    # Process each segment sequentially
    for i, segment in enumerate(segments, 1):
        print(f"\n🎯 Processing {content_type.title()} Segment {i}/{len(segments)}")
        
        try:
            # Extract video prompt for this segment
            prompt_data = extract_video_prompt_from_content_segment(content_data, i, content_type)
            
            # Create video request
            video_request = content_segment_to_video_request(
                content_data, 
                i, 
                content_type,
                **video_options
            )
            
            print(f"📝 Prompt: {video_request['prompt'][:100]}...")
            
            # Store segment info
            segment_result = {
                "segment_number": i,
                "content_type": content_type,
                "video_request": video_request,
                "status": "processing",
                "video_url": None,
                "downloaded_file": None,
                "error": None
            }
            
            results["segments_results"].append(segment_result)
            
            print(f"✅ {content_type.title()} Segment {i} prepared successfully")
            
        except Exception as e:
            error_msg = f"Error processing {content_type} segment {i}: {str(e)}"
            print(f"❌ {error_msg}")
            
            segment_result = {
                "segment_number": i,
                "status": "error",
                "error": error_msg,
                "video_url": None,
                "downloaded_file": None
            }
            
            results["segments_results"].append(segment_result)
            results["error_count"] += 1
    
    print(f"\n📋 Preparation Summary:")
    print(f"✅ Successfully prepared: {len(segments) - results['error_count']} segments")
    print(f"❌ Errors: {results['error_count']} segments")
    
    return results


def execute_content_video_generation(content_data: dict, content_type: str = None, video_options: dict = None, generate_videos: bool = True):
    """
    Complete pipeline: prepare segments and optionally execute video generation for any content type
    
    Args:
        content_data: Complete content data
        content_type: Override content type detection
        video_options: Video generation options
        generate_videos: Whether to actually generate videos or just prepare
    
    Returns:
        dict: Complete results with video generation status
    """
    # First, prepare all segments
    results = generate_full_content_videos(content_data, content_type, video_options)
    
    if not generate_videos:
        print("🔄 Preparation complete. Set generate_videos=True to execute video generation.")
        return results
    
    print(f"\n🚀 Starting video generation for {results['total_segments']} {results['content_type']} segments...")
    
    # Import here to avoid circular imports
    from app.services.genai_service import generate_video_from_payload, download_video
    
    # Execute video generation for each prepared segment
    for segment_result in results["segments_results"]:
        if segment_result["status"] != "processing":
            continue
        
        segment_num = segment_result["segment_number"]
        video_request = segment_result["video_request"]
        
        print(f"\n🎬 Generating video for {results['content_type'].title()} Segment {segment_num}...")
        
        # Retry logic for failed segments
        max_retries = 3
        retry_delay = 30  # seconds
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 Retry attempt {attempt + 1}/{max_retries} for Segment {segment_num}")
                    print(f"⏳ Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                
                # Generate video
                video_response = generate_video_from_payload(video_request)
                
                if isinstance(video_response, list) and len(video_response) > 0:
                    video_url = video_response[0]
                    segment_result["video_url"] = video_url
                    segment_result["status"] = "completed"
                    results["video_urls"].append(video_url)
                    results["success_count"] += 1
                    
                    print(f"✅ Segment {segment_num} video generated: {video_url[:50]}...")
                    
                    # Download if requested
                    if video_request.get("download", False):
                        try:
                            filename = video_request.get("filename", f"segment_{segment_num}")
                            filepath = download_video(video_url, filename)
                            segment_result["downloaded_file"] = filepath
                            results["downloaded_files"].append(filepath)
                            print(f"📥 Downloaded: {filepath}")
                        except Exception as e:
                            print(f"⚠️ Download failed for segment {segment_num}: {str(e)}")
                    
                    break  # Success, exit retry loop
                    
                else:
                    raise Exception("No video URL returned from generation")
                    
            except Exception as e:
                error_msg = f"Video generation failed for segment {segment_num} (attempt {attempt + 1}): {str(e)}"
                print(f"❌ {error_msg}")
                
                if attempt == max_retries - 1:  # Last attempt failed
                    segment_result["status"] = "failed"
                    segment_result["error"] = error_msg
                    segment_result["retry_attempts"] = max_retries
                    results["error_count"] += 1
                else:
                    # Check if it's a temporary error (overload, rate limit, internal server errors, etc.)
                    error_str = str(e).lower()
                    is_temporary_error = (
                        "overloaded" in error_str or 
                        "rate" in error_str or 
                        "quota" in error_str or
                        "internal server" in error_str or
                        "'code': 13" in str(e) or
                        "server issue" in error_str or
                        "try again" in error_str
                    )
                    
                    if is_temporary_error:
                        print(f"🔄 Temporary error detected, will retry...")
                        continue
                    else:
                        # Permanent error, don't retry
                        segment_result["status"] = "failed"
                        segment_result["error"] = error_msg
                        segment_result["retry_attempts"] = attempt + 1
                        results["error_count"] += 1
                        break
    
    # Final summary
    print(f"\n🎉 {results['content_type'].title()} Video Generation Complete!")
    print(f"✅ Successfully generated: {results['success_count']} videos")
    print(f"❌ Failed: {results['error_count']} videos")
    print(f"📥 Downloaded: {len(results['downloaded_files'])} files")
    
    return results



def execute_daily_character_video_generation(content_data: dict, video_options: dict = None):
    """
    Generate videos for daily character content using keyframes with CHAT-BASED frame generation.
    Uses chat sessions to maintain continuity across continuous segments.
    
    Args:
        content_data: Daily character content data with segments
        video_options: Video generation options including character_keyframe_uri
    
    Returns:
        dict: Complete results with video generation status
    """
    import time
    import requests
    from io import BytesIO
    from PIL import Image
    from app.services.genai_service import generate_video_with_keyframes
    from app.services.imagen_chat_service import FrameGenerationChat
    
    if video_options is None:
        video_options = {}
    
    character_keyframe_uri = video_options.get("character_keyframe_uri")
    if not character_keyframe_uri:
        return {"error": "character_keyframe_uri is required in video_options"}
    
    # Extract segments
    segments = content_data.get("segments", [])
    if not segments:
        return {"error": "No segments found in content_data"}
    
    character_name = content_data.get("character_name", "Character")
    title = content_data.get("title", "Daily Character Content")
    
    # Extract character metadata for multi-character support
    character_metadata = content_data.get("character_metadata", {})
    characters = character_metadata.get("characters", [])
    
    # Extract visual style from content_data (vibe for daily character, genre for short films)
    content_style = content_data.get("vibe") or content_data.get("genre") or content_data.get("style") or "cute character animation"
    
    # Build character names and subjects lists for Imagen
    character_names_list = []
    character_subjects_list = []
    character_url_to_info = {}  # Map URL to character info
    
    # Get character URLs list
    character_keyframe_uris = video_options.get("character_keyframe_uris", [character_keyframe_uri])
    
    if characters:
        for char in characters:
            char_name = char.get("character_name", "Character")
            char_subject = char.get("subject", "creature")  # Get subject description from database
            char_url = char.get("cloudinary_url", "")
            
            character_names_list.append(char_name)
            character_subjects_list.append(char_subject)
            
            if char_url:
                character_url_to_info[char_url] = {
                    "name": char_name,
                    "subject": char_subject
                }
        
        print(f"📋 Character metadata loaded:")
        for name, subject in zip(character_names_list, character_subjects_list):
            print(f"   - {name}: {subject[:50]}...")
    else:
        # Fallback for single character without metadata
        character_names_list = [character_name]
        character_subjects_list = [content_data.get("creature_sound_description", "creature")]
    
    # Download character images once for chat service
    print(f"📥 Downloading character images for chat service...")
    character_images = []
    for idx, url in enumerate(character_keyframe_uris, 1):
        if url.startswith("http://") or url.startswith("https://"):
            print(f"   Downloading character {idx}/{len(character_keyframe_uris)}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            character_images.append(img)
            print(f"   ✅ Character {idx} loaded: {img.size}")
    
    print(f"\n🎬 Starting daily character video generation for: {title}")
    print(f"👤 Character(s): {', '.join(character_names_list)}")
    print(f"🎭 Style: {content_style}")
    print(f"🖼️ Keyframe: {character_keyframe_uri}")
    print(f"📊 Total segments: {len(segments)}")
    print(f"🔄 Using CHAT-BASED frame generation for continuity")
    
    # Initialize results
    results = {
        "success": False,
        "content_type": "daily_character",
        "character_name": character_name,
        "title": title,
        "total_segments": len(segments),
        "success_count": 0,
        "error_count": 0,
        "video_urls": [],
        "downloaded_files": [],
        "segments_results": [],
        "frame_chain": []  # Track frame chaining
    }
    
    # Initialize chat session for frame generation (will be reused for continuous segments)
    frame_chat = None
    
    # Process each segment
    for idx, segment in enumerate(segments):
        segment_num = segment.get("segment", 0)
        duration = segment.get("duration", 8)
        is_first_segment = (idx == 0)
        is_last_segment = (idx == len(segments) - 1)
        
        # Check for Veo 3 structured prompt first
        veo_prompt = segment.get("veo_prompt")
        
        if veo_prompt:
            # Use the new Veo 3 structured prompt with audio cues
            prompt = veo_prompt
            print(f"✅ Using Veo 3 structured prompt with integrated audio")
        else:
            # Fallback: Build prompt from individual fields (old method)
            scene = segment.get("scene", "")
            action = segment.get("action", "")
            reaction = segment.get("reaction", "")
            camera = segment.get("camera", "")
            visual_focus = segment.get("visual_focus", "")
            
            # Get background details
            background = segment.get("background", {})
            video_prompt_background = background.get("video_prompt_background", "")
            
            # Combine all visual elements into prompt
            prompt_parts = []
            if scene:
                prompt_parts.append(scene)
            if action:
                prompt_parts.append(action)
            if reaction:
                prompt_parts.append(f"Character shows {reaction}.")
            if visual_focus:
                prompt_parts.append(f"Focus on: {visual_focus}.")
            if camera:
                prompt_parts.append(f"Camera: {camera}.")
            if video_prompt_background:
                prompt_parts.append(f"Background: {video_prompt_background}")
            
            prompt = " ".join(prompt_parts)
            print(f"⚠️  Using legacy prompt format (no integrated audio)")
        
        segment_result = {
            "segment_number": segment_num,
            "duration": duration,
            "prompt": prompt,
            "status": "processing",
            "video_url": None,
            "error": None,
            "first_frame_source": None,
            "last_frame_extracted": None
        }
        
        results["segments_results"].append(segment_result)
        
        print(f"\n🎬 Generating video for Segment {segment_num}/{len(segments)}...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Determine first frame for this segment using CHAT-BASED generation
        first_frame_to_use = None
        first_frame_desc = segment.get("first_frame_description")
        last_frame_desc = segment.get("last_frame_description")
        
        # Get character info for this segment
        segment_char_names = []
        segment_char_subjects = []
        characters_present = segment.get("characters_present", [])
        
        if characters_present and characters:
            # Match characters_present to character metadata
            for char_name in characters_present:
                for char in characters:
                    if char.get("character_name") == char_name:
                        segment_char_names.append(char_name)
                        segment_char_subjects.append(char.get("subject", "creature"))
                        break
        else:
            # Fallback to all characters
            segment_char_names = character_names_list
            segment_char_subjects = character_subjects_list
        
        # CHAT-BASED FRAME GENERATION LOGIC
        try:
            if first_frame_desc:
                # NEW SCENE - Create new chat session
                print(f"🆕 Segment {segment_num}: NEW SCENE detected (has first_frame_description)")
                print(f"   Creating new chat session for frame generation...")
                
                frame_chat = FrameGenerationChat(
                    model=video_options.get("image_model", "gemini-2.5-flash-image")
                )
                
                # Generate first frame with new chat
                print(f"🎨 Generating first frame with new chat session...")
                generated_image, first_frame_path = frame_chat.generate_first_frame(
                    character_images=character_images,
                    frame_description=first_frame_desc,
                    character_names=segment_char_names,
                    character_subjects=segment_char_subjects,
                    style=content_style,
                    aspect_ratio=video_options.get("aspect_ratio", "9:16"),
                    resolution="2K",
                    output_dir="frames"
                )
                
                first_frame_to_use = first_frame_path
                segment_result["first_frame_source"] = "chat_new_scene"
                segment_result["first_frame_path"] = first_frame_path
                print(f"✅ First frame generated (new scene): {first_frame_path}")
                
            elif frame_chat is not None:
                # CONTINUOUS SEGMENT - Reuse existing chat session
                print(f"🔄 Segment {segment_num}: CONTINUOUS from previous (no first_frame_description)")
                print(f"   Reusing existing chat session for continuity...")
                
                # The last frame from previous segment becomes the first frame
                # We don't need to generate a new first frame - just use the last one
                if hasattr(frame_chat, 'current_frame') and frame_chat.current_frame:
                    # Save the current frame as first frame for this segment
                    import os
                    from datetime import datetime
                    os.makedirs("frames", exist_ok=True)
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    first_frame_path = os.path.join("frames", f"first_frame_continuous_{timestamp}.png")
                    frame_chat.current_frame.save(first_frame_path, "PNG")
                    
                    first_frame_to_use = first_frame_path
                    segment_result["first_frame_source"] = "chat_continuous"
                    segment_result["first_frame_path"] = first_frame_path
                    print(f"✅ Using previous last frame as first frame: {first_frame_path}")
                else:
                    # Fallback to character keyframe
                    first_frame_to_use = character_keyframe_uri
                    segment_result["first_frame_source"] = "character_keyframe_fallback"
                    print(f"⚠️ No previous frame available, using character keyframe")
            else:
                # First segment without first_frame_description - use character keyframe
                first_frame_to_use = character_keyframe_uri
                segment_result["first_frame_source"] = "character_keyframe"
                print(f"🖼️ Segment {segment_num}: Using character keyframe as first frame")
            
            # Generate LAST FRAME using chat (if description provided)
            last_frame_to_use = None
            if last_frame_desc and frame_chat is not None:
                print(f"🎨 Generating last frame with chat session...")
                generated_image, last_frame_path = frame_chat.generate_last_frame(
                    last_frame_description=last_frame_desc,
                    aspect_ratio=video_options.get("aspect_ratio", "9:16"),
                    resolution="2K",
                    output_dir="frames"
                )
                
                last_frame_to_use = last_frame_path
                segment_result["last_frame_generated"] = last_frame_path
                print(f"✅ Last frame generated: {last_frame_path}")
                print(f"   → Will be used as first frame for next continuous segment")
            else:
                print(f"⚠️ No last_frame_description provided for segment {segment_num}")
                
        except Exception as e:
            print(f"⚠️ Chat-based frame generation failed: {str(e)}")
            print(f"   Falling back to character keyframe")
            first_frame_to_use = character_keyframe_uri
            last_frame_to_use = None
            segment_result["first_frame_source"] = "character_keyframe_fallback"
            segment_result["frame_generation_error"] = str(e)
        
        # Retry logic
        max_retries = 3
        retry_delay = 30
        
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    print(f"🔄 Retry attempt {attempt + 1}/{max_retries} for Segment {segment_num}")
                    print(f"⏳ Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                
                # Generate video with keyframe chaining and character reference (Veo 3.1)
                video_urls = generate_video_with_keyframes(
                    prompt=prompt,
                    first_frame=first_frame_to_use,  # Chat-generated or character keyframe
                    last_frame=last_frame_to_use,  # Chat-generated last frame (if available)
                    duration=duration,
                    resolution=video_options.get("resolution", "720p"),
                    aspect_ratio=video_options.get("aspect_ratio", "9:16"),
                    reference_image_urls=[character_keyframe_uri]  # Character as reference for consistency
                )
                
                if video_urls and len(video_urls) > 0:
                    video_url = video_urls[0]
                    segment_result["video_url"] = video_url
                    segment_result["status"] = "completed"
                    results["video_urls"].append(video_url)
                    results["success_count"] += 1
                    
                    print(f"✅ Segment {segment_num} video generated: {video_url[:50]}...")
                    
                    # Download video to content directory
                    try:
                        from app.services.genai_service import download_video
                        from app.services.file_storage_manager import storage_manager, ContentType
                        import os
                        
                        # Get content directory from file storage manager
                        content_dir = storage_manager.get_content_directory(ContentType.DAILY_CHARACTER, title)
                        
                        # Create subdirectories
                        videos_dir = os.path.join(content_dir, "videos")
                        os.makedirs(videos_dir, exist_ok=True)
                        
                        # Download video to content directory
                        temp_filename = f"{character_name}_segment_{segment_num}"
                        temp_video_path = download_video(video_url, temp_filename, download_dir=videos_dir)
                        print(f"📥 Downloaded to: {temp_video_path}")
                        
                        # Also save to downloads folder if requested
                        if video_options.get("download", False):
                            downloads_path = download_video(video_url, temp_filename, download_dir="downloads")
                            segment_result["downloaded_file"] = downloads_path
                            results["downloaded_files"].append(downloads_path)
                            print(f"💾 Also saved to downloads: {downloads_path}")
                        
                        segment_result["video_file"] = temp_video_path
                        print(f"📁 Content directory: {content_dir}")
                        
                    except Exception as e:
                        print(f"⚠️ Video download failed for segment {segment_num}: {str(e)}")
                    
                    break  # Success, exit retry loop
                    
                else:
                    raise Exception("No video URL returned from generation")
                    
            except Exception as e:
                error_msg = f"Video generation failed for segment {segment_num} (attempt {attempt + 1}): {str(e)}"
                print(f"❌ {error_msg}")
                
                if attempt == max_retries - 1:  # Last attempt failed
                    segment_result["status"] = "failed"
                    segment_result["error"] = error_msg
                    segment_result["retry_attempts"] = max_retries
                    results["error_count"] += 1
                else:
                    # Check if it's a temporary error
                    error_str = str(e).lower()
                    is_temporary_error = (
                        "overloaded" in error_str or 
                        "rate" in error_str or 
                        "quota" in error_str or
                        "internal server" in error_str or
                        "'code': 13" in str(e) or
                        "server issue" in error_str or
                        "try again" in error_str
                    )
                    
                    if is_temporary_error:
                        print(f"🔄 Temporary error detected, will retry...")
                        continue
                    else:
                        # Permanent error, don't retry
                        segment_result["status"] = "failed"
                        segment_result["error"] = error_msg
                        segment_result["retry_attempts"] = attempt + 1
                        results["error_count"] += 1
                        break
        
        # Small delay between segments to avoid rate limits
        if segment_num < len(segments):
            time.sleep(2)
    
    # Update final status
    results["success"] = results["error_count"] == 0
    
    # Summary
    print(f"\n{'='*60}")
    print(f"🎉 Daily Character Video Generation Complete!")
    print(f"✅ Successful: {results['success_count']}/{results['total_segments']}")
    print(f"❌ Failed: {results['error_count']}/{results['total_segments']}")
    
    if results["error_count"] > 0:
        failed_segments = [s["segment_number"] for s in results["segments_results"] if s["status"] == "failed"]
        print(f"⚠️ Failed segments: {failed_segments}")
        print(f"💡 You can retry failed segments using the retry endpoint")
    
    # Clean up extracted frames (no longer needed after all videos are generated)
    if results["frame_chain"]:
        print(f"\n🧹 Cleaning up extracted frames...")
        import os
        from app.services.file_storage_manager import storage_manager, ContentType
        
        try:
            content_dir = storage_manager.get_content_directory(ContentType.DAILY_CHARACTER, title, create=False)
            frames_dir = os.path.join(content_dir, "frames")
            
            if os.path.exists(frames_dir):
                # Delete all frame files EXCEPT the last one
                frame_chain = results["frame_chain"]
                last_frame_path = frame_chain[-1].get("last_frame") if frame_chain else None
                
                for frame_info in frame_chain:
                    frame_path = frame_info.get("last_frame")
                    if frame_path and os.path.exists(frame_path):
                        # Keep the last frame, delete all others
                        if frame_path != last_frame_path:
                            os.remove(frame_path)
                            print(f"🗑️ Deleted: {os.path.basename(frame_path)}")
                        else:
                            print(f"💾 Kept last frame: {os.path.basename(frame_path)}")
                
                # Don't remove frames directory since we're keeping the last frame
                remaining_files = os.listdir(frames_dir)
                if not remaining_files:
                    os.rmdir(frames_dir)
                    print(f"🗑️ Removed empty frames directory")
                else:
                    print(f"📁 Frames directory kept with {len(remaining_files)} file(s)")
                
                print(f"✅ Cleanup complete")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {str(e)}")
    
    print(f"{'='*60}\n")
    
    return results



def build_daily_character_video_prompt(segment: dict) -> str:
    """
    Build a video prompt from daily character segment data.
    
    Args:
        segment: Daily character segment with scene, action, reaction, etc.
    
    Returns:
        str: Complete video prompt for generation
    """
    prompt_parts = []
    
    # Scene description
    scene = segment.get('scene', '')
    if scene:
        prompt_parts.append(f"Scene: {scene}")
    
    # Action
    action = segment.get('action', '')
    if action:
        prompt_parts.append(f"Action: {action}")
    
    # Reaction
    reaction = segment.get('reaction', '')
    if reaction:
        prompt_parts.append(f"Reaction: {reaction}")
    
    # Visual focus
    visual_focus = segment.get('visual_focus', '')
    if visual_focus:
        prompt_parts.append(f"Visual Focus: {visual_focus}")
    
    # Background
    background = segment.get('background', {})
    if background:
        bg_prompt = background.get('video_prompt_background', '')
        if bg_prompt:
            prompt_parts.append(f"Background: {bg_prompt}")
    
    # Camera
    camera = segment.get('camera', '')
    if camera:
        prompt_parts.append(f"Camera: {camera}")
    
    # Comedy element
    comedy = segment.get('comedy_element', '')
    if comedy:
        prompt_parts.append(f"Comedy: {comedy}")
    
    # Add pacing instruction for faster, more dynamic videos
    prompt_parts.append("Pacing: Fast-paced, energetic movement with quick transitions. Dynamic and snappy action")
    
    # Join all parts
    return ". ".join(prompt_parts) if prompt_parts else "Daily character moment"


def execute_daily_character_video_generation(content_data: dict, video_options: dict = None):
    """
    Generate videos for daily character content using keyframes (original mode).
    Uses character image as first frame and previous frame as image parameter.
    
    Args:
        content_data: Daily character content data
        video_options: Video generation options including character_keyframe_uri
    
    Returns:
        dict: Complete results with video generation status
    """
    if video_options is None:
        video_options = {}
    
    character_keyframe_uri = video_options.get("character_keyframe_uri")
    if not character_keyframe_uri:
        raise ValueError("character_keyframe_uri is required in video_options")
    
    segments = content_data.get('segments', [])
    
    if not segments:
        raise ValueError("No segments found in content data")
    
    # Extract character metadata for multi-character support
    character_metadata = content_data.get("character_metadata", {})
    characters = character_metadata.get("characters", [])
    
    # Extract visual style from content_data (vibe for daily character, genre for short films)
    content_style = content_data.get("vibe") or content_data.get("genre") or content_data.get("style") or "cute character animation"
    
    # Build character names and subjects lists for Imagen
    character_names_list = []
    character_subjects_list = []
    
    if characters:
        for char in characters:
            char_name = char.get("character_name", "Character")
            char_subject = char.get("subject", "creature")  # Get subject description from database
            character_names_list.append(char_name)
            character_subjects_list.append(char_subject)
        
        print(f"📋 Character metadata loaded:")
        for name, subject in zip(character_names_list, character_subjects_list):
            print(f"   - {name}: {subject[:50]}...")
    else:
        # Fallback for single character without metadata
        character_names_list = [content_data.get('character_name', 'Character')]
        character_subjects_list = [content_data.get("creature_sound_description", "creature")]
    
    # Prepare results structure
    results = {
        "content_title": content_data.get('title', 'Daily Character Video'),
        "character_name": content_data.get('character_name', 'Character'),
        "content_type": "daily_character",
        "total_segments": len(segments),
        "segments_results": [],
        "success_count": 0,
        "error_count": 0,
        "video_urls": [],
        "character_keyframe_uri": character_keyframe_uri
    }
    
    print(f"🎬 Starting daily character video generation for: {results['content_title']}")
    print(f"👤 Character(s): {', '.join(character_names_list)}")
    print(f"🎭 Style: {content_style}")
    print(f"🖼️ Keyframe: {character_keyframe_uri}")
    print(f"📊 Total segments: {len(segments)}")
    
    # Import here to avoid circular imports
    from app.services.genai_service import generate_video_with_keyframes
    from app.services.imagen_service import generate_first_frame_with_imagen
    
    previous_frame = None  # Track previous frame for continuity
    
    # Process each segment sequentially
    for i, segment in enumerate(segments, 1):
        print(f"\n🎬 Generating video for Segment {i}/{len(segments)}...")
        
        segment_result = {
            "segment_number": i,
            "status": "processing",
            "video_url": None,
            "error": None
        }
        
        try:
            # Extract or build prompt from segment
            # Check for Veo 3 structured prompt first (veo_prompt), then fallback to video_prompt
            prompt = segment.get('veo_prompt', '') or segment.get('video_prompt', '')
            if prompt:
                print(f"✅ Using Veo 3 structured prompt with integrated audio")
            else:
                # Build prompt from segment fields for daily character content
                prompt = build_daily_character_video_prompt(segment)
                print(f"⚠️  Using legacy prompt format (no integrated audio)")
            
            if not prompt or prompt == "Daily character moment":
                raise ValueError(f"Could not build video prompt for segment {i}")
            
            print(f"📝 Prompt: {prompt[:100]}...")
            
            # Setup organized directories using file_storage_manager
            from app.services.file_storage_manager import storage_manager, ContentType
            import os
            
            title = content_data.get('title', 'Untitled')
            content_dir = storage_manager.get_content_directory(ContentType.DAILY_CHARACTER, title)
            frames_dir = os.path.join(content_dir, "frames")
            videos_dir = os.path.join(content_dir, "videos")
            os.makedirs(frames_dir, exist_ok=True)
            os.makedirs(videos_dir, exist_ok=True)
            
            is_last_segment = (i == len(segments))
            
            # STEP 1: Determine IMAGE parameter (first frame for video)
            # Logic:
            # - If first_frame_description exists (scene change): Generate new frame with Imagen
            # - If no first_frame_description (continuous scene): Use previous segment's last frame
            # - Segment 1 always needs a first frame (either generated or character keyframe)
            first_frame = None
            first_frame_description = segment.get('first_frame_description')
            
            # Check if first_frame_description is provided and not empty
            has_first_frame_desc = first_frame_description and first_frame_description.strip()
            
            if has_first_frame_desc:
                # Scene change detected: Generate new first frame with Imagen
                print(f"🎨 Segment {i}: Scene change detected - Generating first frame with Imagen...")
                print(f"📝 Frame description: {first_frame_description[:100]}...")
                try:
                    # Get character URLs for this segment (support multi-character)
                    segment_char_urls = segment.get("character_keyframe_uris")
                    if not segment_char_urls:
                        segment_char_urls = [segment.get("character_keyframe_uri", character_keyframe_uri)]
                    
                    # Get character names and subjects for this segment's characters
                    segment_char_names = []
                    segment_char_subjects = []
                    characters_present = segment.get("characters_present", [])
                    
                    if characters_present and characters:
                        # Match characters_present to character metadata
                        for char_name in characters_present:
                            for char in characters:
                                if char.get("character_name") == char_name:
                                    segment_char_names.append(char_name)
                                    segment_char_subjects.append(char.get("subject", "creature"))
                                    break
                    else:
                        # Fallback to all characters
                        segment_char_names = character_names_list
                        segment_char_subjects = character_subjects_list
                    
                    generated_image, frame_path = generate_first_frame_with_imagen(
                        character_image_urls=segment_char_urls,
                        frame_description=first_frame_description,
                        aspect_ratio=video_options.get("aspect_ratio", "9:16"),
                        output_dir=frames_dir,
                        additional_reference_images=video_options.get("reference_images"),
                        image_model=video_options.get("image_model", "gemini-2.5-flash-image"),
                        character_names=segment_char_names,
                        character_subjects=segment_char_subjects,
                        style=content_style
                    )
                    first_frame = frame_path
                    segment_result["first_frame_generated"] = frame_path
                    segment_result["scene_change"] = True
                    print(f"✅ First frame generated for scene change: {frame_path}")
                except Exception as e:
                    print(f"⚠️ Imagen generation failed: {str(e)}, using fallback")
                    # Fallback: use previous frame if available, otherwise character keyframe
                    first_frame = previous_frame if previous_frame else character_keyframe_uri
            else:
                # Continuous scene: Use previous segment's last frame
                if i == 1:
                    # First segment with no description: use character keyframe
                    first_frame = character_keyframe_uri
                    print(f"📸 Segment 1: Using character keyframe as first frame")
                elif previous_frame:
                    # Continuous scene: use previous last frame
                    first_frame = previous_frame
                    segment_result["scene_change"] = False
                    print(f"🔗 Segment {i}: Continuous scene - Using previous segment's last frame")
                    print(f"🔗 Segment {i}: Using generated last frame from previous segment: {first_frame}")
                else:
                    # Fallback: Use character keyframe
                    print(f"⚠️ Segment {i}: Previous frame not available, using character keyframe")
                    first_frame = character_keyframe_uri
            
            # STEP 2: Generate LAST_FRAME parameter with Imagen (for ALL segments)
            last_frame = None
            last_frame_description = segment.get('last_frame_description')
            
            if last_frame_description:
                print(f"🎨 Segment {i}: Generating last frame with Imagen (dual reference)...")
                print(f"📝 Last frame description: {last_frame_description[:100]}...")
                try:
                    from app.services.imagen_service import generate_last_frame_with_imagen
                    
                    # Get character URLs for this segment (support multi-character)
                    segment_char_urls = segment.get("character_keyframe_uris")
                    if not segment_char_urls:
                        segment_char_urls = [segment.get("character_keyframe_uri", character_keyframe_uri)]
                    
                    # Get character names and subjects for this segment's characters
                    segment_char_names = []
                    segment_char_subjects = []
                    characters_present = segment.get("characters_present", [])
                    
                    if characters_present and characters:
                        # Match characters_present to character metadata
                        for char_name in characters_present:
                            for char in characters:
                                if char.get("character_name") == char_name:
                                    segment_char_names.append(char_name)
                                    segment_char_subjects.append(char.get("subject", "creature"))
                                    break
                    else:
                        # Fallback to all characters
                        segment_char_names = character_names_list
                        segment_char_subjects = character_subjects_list
                    
                    generated_image, last_frame_path = generate_last_frame_with_imagen(
                        character_image_urls=segment_char_urls,
                        first_frame_path=first_frame,
                        last_frame_description=last_frame_description,
                        aspect_ratio=video_options.get("aspect_ratio", "9:16"),
                        output_dir=frames_dir,
                        additional_reference_images=video_options.get("reference_images"),
                        image_model=video_options.get("image_model", "gemini-2.5-flash-image"),
                        character_names=segment_char_names,
                        character_subjects=segment_char_subjects,
                        style=content_style
                    )
                    last_frame = last_frame_path
                    segment_result["last_frame_generated"] = last_frame_path
                    print(f"✅ Last frame generated: {last_frame_path}")
                    
                    # Store generated last frame for next segment (no extraction needed!)
                    if not is_last_segment:
                        previous_frame = last_frame_path
                        print(f"   → Will be used as first frame for segment {i+1}")
                    else:
                        print(f"   → Last segment: Frame used for video interpolation only")
                    
                except Exception as e:
                    print(f"⚠️ Last frame generation failed: {str(e)}")
                    last_frame = None
            else:
                print(f"⚠️ No last_frame_description provided for segment {i}")
            
            # Generate video with BOTH first and last frames (Veo 3.1 interpolation)
            print(f"🎬 Generating video with first frame{' and last frame' if last_frame else ''}...")
            video_urls = generate_video_with_keyframes(
                prompt=prompt,
                first_frame=first_frame,
                last_frame=last_frame,  # Use generated last frame if available
                duration=segment.get('clip_duration', 8),
                resolution=video_options.get("resolution", "720p"),
                aspect_ratio=video_options.get("aspect_ratio", "9:16"),
                reference_image_urls=None,  # No reference images in this mode
                use_frames_as_references=False  # Use frames as image parameter
            )
            
            if video_urls and len(video_urls) > 0:
                video_url = video_urls[0]
                segment_result["video_url"] = video_url
                segment_result["status"] = "completed"
                results["video_urls"].append(video_url)
                results["success_count"] += 1
                
                # STEP 3: Download video (NO extraction - using generated frames!)
                try:
                    from app.services.genai_service import download_video
                    
                    # Download video to content directory
                    character_name = content_data.get('character_name', 'character')
                    safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).strip().replace(' ', '_').lower()
                    filename = f"{safe_name}_segment_{i}"
                    video_path = download_video(video_url, filename, download_dir=videos_dir)
                    segment_result["video_file"] = video_path
                    print(f"📥 Downloaded to: {video_path}")
                    
                    # Also save to downloads folder if explicitly requested
                    if video_options.get("download", False):
                        downloads_path = download_video(video_url, filename, download_dir="downloads")
                        segment_result["downloaded_file"] = downloads_path
                        if "downloaded_files" not in results:
                            results["downloaded_files"] = []
                        results["downloaded_files"].append(downloads_path)
                        print(f"💾 Also saved to downloads: {downloads_path}")
                    
                except Exception as download_error:
                    print(f"⚠️ Download failed for segment {i}: {str(download_error)}")
                    segment_result["download_error"] = str(download_error)
                
                print(f"✅ Segment {i} completed: {video_url}")
            else:
                raise ValueError("No video URL returned from generation")
                
        except Exception as e:
            error_msg = f"Video generation failed for segment {i}: {str(e)}"
            print(f"❌ {error_msg}")
            segment_result["status"] = "failed"
            segment_result["error"] = error_msg
            results["error_count"] += 1
        
        results["segments_results"].append(segment_result)
    
    print(f"\n{'='*60}")
    print(f"🎉 Daily Character Video Generation Complete!")
    print(f"✅ Successful: {results['success_count']}/{results['total_segments']}")
    print(f"❌ Failed: {results['error_count']}/{results['total_segments']}")
    
    if results['error_count'] > 0:
        failed_segments = [r['segment_number'] for r in results['segments_results'] if r['status'] == 'failed']
        print(f"⚠️ Failed segments: {failed_segments}")
        print(f"💡 You can retry failed segments using the retry endpoint")
    
    # NOTE: Frame cleanup is now handled AFTER thumbnail generation in the merge pipeline
    # Frames are kept here so thumbnail can use them as reference
    print(f"\nℹ️ Frames kept for thumbnail generation (will be cleaned up after merge)")
    results["frames_cleaned"] = False
    
    print(f"{'='*60}")
    
    return results


def execute_daily_character_video_generation_with_references(content_data: dict, video_options: dict = None):
    """
    Generate videos for daily character content using REFERENCE IMAGES (new mode).
    Uses both previous frame AND character keyframe as reference images for character consistency.
    
    Args:
        content_data: Daily character content data
        video_options: Video generation options including character_keyframe_uri and use_frames_as_references=True
    
    Returns:
        dict: Complete results with video generation status
    """
    if video_options is None:
        video_options = {}
    
    character_keyframe_uri = video_options.get("character_keyframe_uri")
    if not character_keyframe_uri:
        raise ValueError("character_keyframe_uri is required in video_options")
    
    segments = content_data.get('segments', [])
    
    if not segments:
        raise ValueError("No segments found in content data")
    
    # Extract character metadata for multi-character support
    character_metadata = content_data.get("character_metadata", {})
    characters = character_metadata.get("characters", [])
    
    # Build character names and subjects lists for Imagen
    character_names_list = []
    character_subjects_list = []
    
    if characters:
        for char in characters:
            char_name = char.get("character_name", "Character")
            char_subject = char.get("subject", "creature")  # Get subject description from database
            character_names_list.append(char_name)
            character_subjects_list.append(char_subject)
        
        print(f"📋 Character metadata loaded:")
        for name, subject in zip(character_names_list, character_subjects_list):
            print(f"   - {name}: {subject[:50]}...")
    else:
        # Fallback for single character without metadata
        character_names_list = [content_data.get('character_name', 'Character')]
        character_subjects_list = [content_data.get("creature_sound_description", "creature")]
    
    # Extract visual style from content_data (vibe for daily character, genre for short films)
    content_style = content_data.get("vibe") or content_data.get("genre") or content_data.get("style") or "cute character animation"
    
    # Prepare results structure
    results = {
        "content_title": content_data.get('title', 'Daily Character Video'),
        "character_name": content_data.get('character_name', 'Character'),
        "content_type": "daily_character",
        "mode": "reference_images",
        "total_segments": len(segments),
        "segments_results": [],
        "success_count": 0,
        "error_count": 0,
        "video_urls": [],
        "character_keyframe_uri": character_keyframe_uri
    }
    
    print(f"🎬 Starting daily character video generation (REFERENCE MODE) for: {results['content_title']}")
    print(f"👤 Character(s): {', '.join(character_names_list)}")
    print(f"🎭 Style: {content_style}")
    print(f"🖼️ Character Keyframe: {character_keyframe_uri}")
    print(f"🎨 Mode: Using frames as REFERENCE IMAGES for character consistency")
    print(f"📊 Total segments: {len(segments)}")
    
    # Import here to avoid circular imports
    from app.services.genai_service import generate_video_with_keyframes
    from app.services.imagen_service import generate_first_frame_with_imagen
    
    previous_frame = None  # Track previous frame for continuity
    
    # Process each segment sequentially
    for i, segment in enumerate(segments, 1):
        print(f"\n🎬 Generating video for Segment {i}/{len(segments)}...")
        
        segment_result = {
            "segment_number": i,
            "status": "processing",
            "video_url": None,
            "error": None
        }
        
        try:
            # Extract or build prompt from segment
            # Check for Veo 3 structured prompt first (veo_prompt), then fallback to video_prompt
            prompt = segment.get('veo_prompt', '') or segment.get('video_prompt', '')
            if prompt:
                print(f"✅ Using Veo 3 structured prompt with integrated audio")
            else:
                # Build prompt from segment fields for daily character content
                prompt = build_daily_character_video_prompt(segment)
                print(f"⚠️  Using legacy prompt format (no integrated audio)")
            
            if not prompt or prompt == "Daily character moment":
                raise ValueError(f"Could not build video prompt for segment {i}")
            
            print(f"📝 Prompt: {prompt[:100]}...")
            
            # Generate first frame with Imagen if frame description exists
            first_frame = None
            frame_description = segment.get('first_frame_description')
            
            if frame_description and i == 1:  # Only for first segment
                print(f"🎨 Segment {i}: Generating custom first frame with Imagen (nano banana)...")
                print(f"📝 Frame description: {frame_description[:100]}...")
                try:
                    # Create frames directory in workspace
                    import os
                    frames_dir = "frames"
                    os.makedirs(frames_dir, exist_ok=True)
                    
                    # Get character URLs for this segment (support multi-character)
                    segment_char_urls = segment.get("character_keyframe_uris")
                    if not segment_char_urls:
                        segment_char_urls = [segment.get("character_keyframe_uri", character_keyframe_uri)]
                    
                    # Get character names and subjects for this segment's characters
                    segment_char_names = []
                    segment_char_subjects = []
                    characters_present = segment.get("characters_present", [])
                    
                    if characters_present and characters:
                        # Match characters_present to character metadata
                        for char_name in characters_present:
                            for char in characters:
                                if char.get("character_name") == char_name:
                                    segment_char_names.append(char_name)
                                    segment_char_subjects.append(char.get("subject", "creature"))
                                    break
                    else:
                        # Fallback to all characters
                        segment_char_names = character_names_list
                        segment_char_subjects = character_subjects_list
                    
                    generated_image, frame_path = generate_first_frame_with_imagen(
                        character_image_urls=segment_char_urls,
                        frame_description=frame_description,
                        aspect_ratio=video_options.get("aspect_ratio", "9:16"),
                        output_dir=frames_dir,
                        image_model=video_options.get("image_model", "gemini-2.5-flash-image"),
                        character_names=segment_char_names,
                        character_subjects=segment_char_subjects,
                        style=content_style
                    )
                    # Use the saved frame path as first_frame (will be used as reference)
                    first_frame = frame_path
                    print(f"✅ First frame generated and saved to: {frame_path}")
                except Exception as e:
                    print(f"⚠️ Imagen generation failed: {str(e)}, using character keyframe")
                    first_frame = character_keyframe_uri
            elif previous_frame:
                # Use previous frame for continuity
                first_frame = previous_frame
                print(f"🔗 Segment {i}: Using previous frame as reference")
            else:
                # Use character keyframe as fallback
                first_frame = character_keyframe_uri
                print(f"⚠️ Segment {i}: Previous frame not available, using character keyframe")
            
            # NEW MODE: Generate video with REFERENCE IMAGES
            # Both previous frame and character keyframe are used as references
            video_urls = generate_video_with_keyframes(
                prompt=prompt,
                first_frame=first_frame,  # Will be used as reference image
                duration=segment.get('clip_duration', 8),
                resolution=video_options.get("resolution", "720p"),
                aspect_ratio=video_options.get("aspect_ratio", "9:16"),
                reference_image_urls=[character_keyframe_uri],  # Character keyframe as reference
                use_frames_as_references=True  # NEW: Use frames as reference images
            )
            
            if video_urls and len(video_urls) > 0:
                video_url = video_urls[0]
                segment_result["video_url"] = video_url
                segment_result["status"] = "completed"
                results["video_urls"].append(video_url)
                results["success_count"] += 1
                
                print(f"✅ Segment {i} completed: {video_url}")
                
                # Extract last frame from generated video for next segment
                # This will be used as a reference image for the next segment
                if i < len(segments):  # Not the last segment
                    try:
                        print(f"🎞️ Extracting last frame from segment {i} for next segment...")
                        from app.services.genai_service import download_video
                        import os
                        
                        # Create frames directory in the workspace (not temp)
                        frames_dir = "frames"
                        os.makedirs(frames_dir, exist_ok=True)
                        
                        # Download video to frames directory
                        video_filename = f"segment_{i}_temp.mp4"
                        video_path = download_video(video_url, video_filename, frames_dir)
                        
                        # Extract last frame to frames directory
                        from app.services.video_frame_extractor import extract_last_frame_from_video
                        frame_filename = f"segment_{i}_last_frame.png"
                        frame_path = os.path.join(frames_dir, frame_filename)
                        extract_last_frame_from_video(video_path, frame_path)
                        
                        # Use this frame for next segment
                        previous_frame = frame_path
                        print(f"✅ Last frame extracted and will be used as reference for segment {i+1}")
                        
                        # Clean up downloaded video (keep frame for next segment)
                        if os.path.exists(video_path):
                            os.remove(video_path)
                            print(f"🗑️ Cleaned up temporary video file")
                            
                    except Exception as e:
                        print(f"⚠️ Failed to extract last frame: {str(e)}")
                        print(f"⚠️ Next segment will use character keyframe instead")
                        previous_frame = None
            else:
                raise ValueError("No video URL returned from generation")
                
        except Exception as e:
            error_msg = f"Video generation failed for segment {i} (attempt 1): {str(e)}"
            print(f"❌ {error_msg}")
            segment_result["status"] = "failed"
            segment_result["error"] = error_msg
            results["error_count"] += 1
        
        results["segments_results"].append(segment_result)
    
    print(f"\n{'='*60}")
    print(f"🎉 Daily Character Video Generation Complete!")
    print(f"✅ Successful: {results['success_count']}/{results['total_segments']}")
    print(f"❌ Failed: {results['error_count']}/{results['total_segments']}")
    
    if results['error_count'] > 0:
        failed_segments = [r['segment_number'] for r in results['segments_results'] if r['status'] == 'failed']
        print(f"⚠️ Failed segments: {failed_segments}")
        print(f"💡 You can retry failed segments using the retry endpoint")
    
    print(f"{'='*60}")
    
    return results
