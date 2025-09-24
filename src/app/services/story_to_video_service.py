"""
Service to convert story segments into video generation prompts
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


def extract_video_prompt_from_segment(story_data: dict, segment_number: int) -> dict:
    """
    Extract a clean video generation prompt from a specific story segment
    
    Args:
        story_data: The complete story data from story generation
        segment_number: Which segment to extract (1-based indexing)
    
    Returns:
        dict: Clean prompt data for video generation
    """
    try:
        # Get the specific segment
        segments = story_data.get('segments', [])
        if segment_number < 1 or segment_number > len(segments):
            raise ValueError(f"Segment {segment_number} not found. Available segments: 1-{len(segments)}")
        
        segment = segments[segment_number - 1]  # Convert to 0-based indexing
        characters_roster = story_data.get('characters_roster', [])
        
        # Build character descriptions for this segment
        characters_present = segment.get('characters_present', [])
        character_descriptions = []
        
        for char_id in characters_present:
            # Find character in roster
            character = next((c for c in characters_roster if c['id'] == char_id), None)
            if character:
                char_desc = character.get('video_prompt_description', '')
                if char_desc:
                    character_descriptions.append(f"{character['name']}: {char_desc}")
        
        # Get background description
        background_def = segment.get('background_definition', {})
        background_prompt = background_def.get('video_prompt_background', background_def.get('setting_description', ''))
        
        # Build the main prompt
        scene_description = segment.get('scene', '')
        
        # Get content (narration or dialogue)
        content_type = segment.get('content_type', 'narration')
        content_text = ""
        
        if content_type == 'narration':
            content_text = segment.get('narration', '')
        elif content_type == 'dialogue':
            dialogue_lines = segment.get('dialogue', [])
            dialogue_text = []
            for line in dialogue_lines:
                char_name = line.get('character', 'Unknown')
                char_line = line.get('line', '')
                dialogue_text.append(f"{char_name}: \"{char_line}\"")
            content_text = " ".join(dialogue_text)
        
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
        
        # Clean the prompt
        final_prompt = clean_json_string(final_prompt)
        
        # Return structured data
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
            "color_palette": color_palette
        }
        
    except Exception as e:
        raise ValueError(f"Error extracting video prompt: {str(e)}")


def extract_all_video_prompts(story_data: dict) -> list:
    """
    Extract video prompts for all segments in a story
    
    Args:
        story_data: The complete story data from story generation
    
    Returns:
        list: List of video prompt dictionaries
    """
    segments = story_data.get('segments', [])
    prompts = []
    
    for i in range(1, len(segments) + 1):
        try:
            prompt_data = extract_video_prompt_from_segment(story_data, i)
            prompts.append(prompt_data)
        except Exception as e:
            print(f"Error extracting segment {i}: {str(e)}")
            continue
    
    return prompts


def story_segment_to_video_request(story_data: dict, segment_number: int, **video_options) -> dict:
    """
    Convert a story segment to a video generation request
    
    Args:
        story_data: The complete story data
        segment_number: Which segment to convert
        **video_options: Additional video generation options (resolution, aspectRatio, etc.)
    
    Returns:
        dict: Ready-to-use video generation request
    """
    prompt_data = extract_video_prompt_from_segment(story_data, segment_number)
    
    # Default video options
    video_request = {
        "prompt": prompt_data["prompt"],
        "durationSeconds": prompt_data.get("duration_seconds", 8),
        "resolution": video_options.get("resolution", "720p"),
        "aspectRatio": video_options.get("aspectRatio", "9:16"),
        "download": video_options.get("download", False),
        "filename": video_options.get("filename", f"story_segment_{segment_number}")
    }
    
    # Add any additional options
    video_request.update(video_options)
    
    return video_request

def generate_full_story_videos(story_data: dict, video_options: dict = None) -> dict:
    """
    Generate videos for all segments in a story sequentially
    
    Args:
        story_data: The complete story data from story generation
        video_options: Video generation options (resolution, aspectRatio, download, etc.)
    
    Returns:
        dict: Results for all generated segments
    """
    if video_options is None:
        video_options = {}
    
    segments = story_data.get('segments', [])
    characters_roster = story_data.get('characters_roster', [])
    
    if not segments:
        raise ValueError("No segments found in story data")
    
    # Prepare results structure
    results = {
        "story_title": story_data.get('title', 'Untitled Story'),
        "total_segments": len(segments),
        "characters_roster": characters_roster,
        "segments_results": [],
        "success_count": 0,
        "error_count": 0,
        "video_urls": [],
        "downloaded_files": []
    }
    
    print(f"🎬 Starting video generation for story: {results['story_title']}")
    print(f"📊 Total segments to process: {len(segments)}")
    print(f"👥 Characters in story: {len(characters_roster)}")
    
    # Process each segment sequentially
    for i, segment in enumerate(segments, 1):
        print(f"\n🎯 Processing Segment {i}/{len(segments)}")
        
        try:
            # Extract video prompt for this segment
            prompt_data = extract_video_prompt_from_segment(story_data, i)
            
            # Create video request with character consistency
            video_request = create_consistent_video_request(
                prompt_data, 
                characters_roster, 
                i, 
                video_options
            )
            
            print(f"📝 Prompt: {video_request['prompt'][:100]}...")
            
            # Store segment info
            segment_result = {
                "segment_number": i,
                "content_type": prompt_data["content_type"],
                "characters_present": prompt_data["characters_present"],
                "video_request": video_request,
                "status": "processing",
                "video_url": None,
                "downloaded_file": None,
                "error": None
            }
            
            results["segments_results"].append(segment_result)
            
            print(f"✅ Segment {i} prepared successfully")
            
        except Exception as e:
            error_msg = f"Error processing segment {i}: {str(e)}"
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


def create_consistent_video_request(prompt_data: dict, characters_roster: list, segment_number: int, video_options: dict) -> dict:
    """
    Create a video request with enhanced character consistency
    
    Args:
        prompt_data: Extracted prompt data for the segment
        characters_roster: Complete character roster for consistency
        segment_number: Current segment number
        video_options: Video generation options
    
    Returns:
        dict: Enhanced video request with character consistency
    """
    # Get characters present in this segment
    characters_present = prompt_data.get("characters_present", [])
    
    # Build detailed character descriptions
    character_details = []
    for char_id in characters_present:
        character = next((c for c in characters_roster if c['id'] == char_id), None)
        if character:
            # Get detailed description
            video_desc = character.get('video_prompt_description', '')
            if video_desc:
                character_details.append(f"Character {character['name']}: {video_desc}")
    
    # Enhance the prompt with character consistency
    base_prompt = prompt_data["prompt"]
    
    # Add character consistency instructions
    consistency_prompt = ""
    if character_details:
        consistency_prompt = f" IMPORTANT: Maintain exact character appearance consistency: {'; '.join(character_details)}."
    
    # Add visual continuity instructions
    continuity_prompt = f" This is segment {segment_number} of a continuous story - maintain visual style and character consistency with previous segments."
    
    # Combine all prompts
    enhanced_prompt = base_prompt + consistency_prompt + continuity_prompt
    
    # Create video request
    video_request = {
        "prompt": enhanced_prompt,
        "durationSeconds": prompt_data.get("duration_seconds", 8),
        "resolution": video_options.get("resolution", "720p"),
        "aspectRatio": video_options.get("aspectRatio", "9:16"),
        "download": video_options.get("download", False),
        "filename": video_options.get("filename", f"story_segment_{segment_number}")
    }
    
    # Add segment-specific filename if downloading
    if video_request["download"] and not video_options.get("filename"):
        story_title = video_options.get("story_title", "story")
        safe_title = "".join(c for c in story_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        video_request["filename"] = f"{safe_title}_segment_{segment_number}"
    
    return video_request


def execute_story_video_generation(story_data: dict, video_options: dict = None, generate_videos: bool = True):
    """
    Complete pipeline: prepare segments and optionally execute video generation
    
    Args:
        story_data: Complete story data
        video_options: Video generation options
        generate_videos: Whether to actually generate videos or just prepare
    
    Returns:
        dict: Complete results with video generation status
    """
    # First, prepare all segments
    results = generate_full_story_videos(story_data, video_options)
    
    if not generate_videos:
        print("🔄 Preparation complete. Set generate_videos=True to execute video generation.")
        return results
    
    print(f"\n🚀 Starting video generation for {results['total_segments']} segments...")
    
    # Import here to avoid circular imports
    from app.services.genai_service import generate_video_from_payload, download_video
    
    # Execute video generation for each prepared segment
    for segment_result in results["segments_results"]:
        if segment_result["status"] != "processing":
            continue
        
        segment_num = segment_result["segment_number"]
        video_request = segment_result["video_request"]
        
        print(f"\n🎬 Generating video for Segment {segment_num}...")
        
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
    print(f"\n🎉 Story Video Generation Complete!")
    print(f"✅ Successfully generated: {results['success_count']} videos")
    print(f"❌ Failed: {results['error_count']} videos")
    print(f"📥 Downloaded: {len(results['downloaded_files'])} files")
    
    return results
    
def retry_failed_segments(previous_results: dict, video_options: dict = None) -> dict:
    """
    Retry generating videos for failed segments
    
    Args:
        previous_results: Results from previous generation attempt
        video_options: Video generation options
    
    Returns:
        dict: Updated results with retry attempts
    """
    if video_options is None:
        video_options = {}
    
    # Import here to avoid circular imports
    from app.services.genai_service import generate_video_from_payload, download_video
    
    failed_segments = [seg for seg in previous_results.get("segments_results", []) if seg.get("status") == "failed"]
    
    if not failed_segments:
        print("✅ No failed segments to retry!")
        return previous_results
    
    print(f"🔄 Retrying {len(failed_segments)} failed segments...")
    
    # Update counters
    retry_success_count = 0
    
    for segment_result in failed_segments:
        segment_num = segment_result["segment_number"]
        video_request = segment_result.get("video_request", {})
        
        print(f"\n🎬 Retrying Segment {segment_num}...")
        
        max_retries = 3
        retry_delay = 45  # Longer delay for retry attempts
        
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
                    segment_result["retry_success"] = True
                    
                    # Update main results
                    previous_results["video_urls"].append(video_url)
                    previous_results["success_count"] += 1
                    previous_results["error_count"] -= 1
                    retry_success_count += 1
                    
                    print(f"✅ Segment {segment_num} retry successful: {video_url[:50]}...")
                    
                    # Download if requested
                    if video_request.get("download", False):
                        try:
                            filename = video_request.get("filename", f"segment_{segment_num}")
                            filepath = download_video(video_url, filename)
                            segment_result["downloaded_file"] = filepath
                            previous_results["downloaded_files"].append(filepath)
                            print(f"📥 Downloaded: {filepath}")
                        except Exception as e:
                            print(f"⚠️ Download failed for segment {segment_num}: {str(e)}")
                    
                    break  # Success, exit retry loop
                    
                else:
                    raise Exception("No video URL returned from generation")
                    
            except Exception as e:
                error_msg = f"Retry failed for segment {segment_num} (attempt {attempt + 1}): {str(e)}"
                print(f"❌ {error_msg}")
                
                if attempt == max_retries - 1:  # Last attempt failed
                    segment_result["retry_error"] = error_msg
                    segment_result["retry_attempts"] = max_retries
                    print(f"💀 Segment {segment_num} failed after {max_retries} retry attempts")
                else:
                    # Wait before next retry
                    continue
    
    print(f"\n🎉 Retry Complete!")
    print(f"✅ Successfully retried: {retry_success_count} segments")
    print(f"❌ Still failed: {len(failed_segments) - retry_success_count} segments")
    
    return previous_results


def get_failed_segments_info(results: dict) -> dict:
    """
    Get information about failed segments for easy retry
    
    Args:
        results: Results from video generation
    
    Returns:
        dict: Information about failed segments
    """
    failed_segments = [seg for seg in results.get("segments_results", []) if seg.get("status") == "failed"]
    
    return {
        "total_failed": len(failed_segments),
        "failed_segment_numbers": [seg["segment_number"] for seg in failed_segments],
        "failed_segments": failed_segments,
        "can_retry": len(failed_segments) > 0
    }