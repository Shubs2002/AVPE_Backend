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
        character = next((c for c in characters_roster if c['id'] == char_id), None)
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
        character = next((c for c in characters_roster if c['id'] == char_id), None)
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