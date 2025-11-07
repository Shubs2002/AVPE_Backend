import json
from app.config.settings import settings
from app.connectors.openai_connector import get_openai_client
from app.data.prompts.generate_segmented_story_prompt import (
    get_story_segments_prompt,
    get_outline_for_story_segments_chunked,
    get_chunk_segments_prompt,
    get_story_segments_in_sets_prompt
)
from app.data.prompts.generate_meme_segments_prompt import get_meme_segments_prompt
from app.data.prompts.generate_free_content_prompt import get_free_content_prompt
from app.data.prompts.generate_whatsapp_story_prompt import get_whatsapp_story_prompt
from app.data.prompts.generate_music_video_prompt import get_music_video_prompt
from app.data.prompts.generate_anime_prompt import get_anime_story_prompt
from app.data.prompts.generate_daily_character_prompt import get_daily_character_prompt
from app.data.prompts.generate_trending_ideas_prompt import get_trending_ideas_prompt
from app.data.prompts.analyze_character_prompt import get_character_analysis_prompt
from app.utils.id_generator import generate_character_id


def ensure_character_ids(custom_character_roster: list) -> list:
    """
    Ensure all characters in the roster have unique IDs.
    ONLY generates IDs for characters that don't already have them.
    If user provides IDs, they are preserved.
    
    Args:
        custom_character_roster: List of character dictionaries
    
    Returns:
        list: Character roster with IDs (user-provided or auto-generated)
    """
    if not custom_character_roster:
        return custom_character_roster
    
    for character in custom_character_roster:
        # Only generate ID if character doesn't have one or has 'unknown'
        if not character.get('id') or character.get('id') == 'unknown':
            character['id'] = generate_character_id()
            print(f"🆔 Auto-generated ID for character '{character.get('name', 'Unknown')}': {character['id']}")
        else:
            # User provided an ID, keep it
            print(f"✅ Using user-provided ID for character '{character.get('name', 'Unknown')}': {character['id']}")
    
    return custom_character_roster


def generate_story_segments(idea: str, num_segments: int = 7, custom_character_roster: list = None):
    # Ensure all characters have IDs
    if custom_character_roster:
        custom_character_roster = ensure_character_ids(custom_character_roster)
    # For large segment counts, use chunked generation to avoid JSON parsing issues
    if num_segments > 20:
        return generate_story_segments_chunked(idea, num_segments, custom_character_roster)
    
    prompt = get_story_segments_prompt(idea, num_segments, custom_character_roster, content_type="short_film")
    raw_output = None
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

          # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        story_data = json.loads(raw_output)

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"  # Limit output length
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating story content: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

    return story_data

def generate_story_segments_chunked(idea: str, num_segments: int, custom_character_roster: list = None):
    """
    Generate story segments in chunks to handle large segment counts (100+)
    This prevents JSON parsing issues with very large responses
    """
    print(f"🔄 Generating {num_segments} segments in chunks to avoid JSON parsing issues...")
    
    # Ensure all characters have IDs
    if custom_character_roster:
        custom_character_roster = ensure_character_ids(custom_character_roster)
        print(f"✅ Using custom character roster with {len(custom_character_roster)} characters")
    
    # Parse special requirements from the idea
    idea_upper = idea.upper()
    no_narrations = 'NO NARRATION' in idea_upper
    narration_only_first = 'ONLY 1ST SEGMENT' in idea_upper or 'ONLY FIRST SEGMENT' in idea_upper
    adult_story = 'ADULT' in idea_upper
    
    # Look for cliffhanger patterns
    cliffhanger_interval = 0
    if '150TH SEGMENT' in idea_upper or 'EVERY 150' in idea_upper:
        cliffhanger_interval = 150
    elif 'CLIFFHANGER' in idea_upper:
        # Try to extract number
        import re
        match = re.search(r'EVERY (\d+)', idea_upper)
        if match:
            cliffhanger_interval = int(match.group(1))
    
    print(f"📋 Parsed requirements: no_narrations={no_narrations}, narration_only_first={narration_only_first}, cliffhanger_interval={cliffhanger_interval}, adult_story={adult_story}")
    
    # First, generate the story outline and metadata
    outline_prompt = get_outline_for_story_segments_chunked(idea, num_segments, no_narrations, narration_only_first, cliffhanger_interval, adult_story, custom_character_roster, content_type="movie")
    
    try:
        # Generate story outline and metadata
        print("📋 Generating story outline and metadata...")
        client = get_openai_client()
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": outline_prompt}],
        )
        
        raw_output = response.choices[0].message.content.strip()
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        story_outline = json.loads(raw_output)
        print(f"✅ Story outline generated: {story_outline['title']}")
        
        # Now generate segments in chunks
        chunk_size = 15  # Generate 15 segments at a time
        all_segments = []
        
        for chunk_start in range(0, num_segments, chunk_size):
            chunk_end = min(chunk_start + chunk_size, num_segments)
            chunk_segments = chunk_end - chunk_start
            
            print(f"🎬 Generating segments {chunk_start + 1}-{chunk_end}...")
            
            # Get the relevant plot points for this chunk
            plot_points = story_outline["story_outline"][chunk_start:chunk_end]
            
            # Check for special requirements
            special_reqs = story_outline.get("special_requirements", {})
            no_narrations = special_reqs.get("no_narrations", False)
            narration_only_first = special_reqs.get("narration_only_first", False)
            cliffhanger_interval = special_reqs.get("cliffhanger_intervals", 0)
            
            # Check if any segments in this chunk should have cliffhangers
            cliffhanger_segments = []
            if cliffhanger_interval > 0:
                for seg_num in range(chunk_start + 1, chunk_end + 1):
                    if seg_num % cliffhanger_interval == 0:
                        cliffhanger_segments.append(seg_num)
            
            # Build segment generation prompt using the prompt function
            segment_prompt = get_chunk_segments_prompt(
                chunk_segments=chunk_segments,
                chunk_start=chunk_start,
                chunk_end=chunk_end,
                story_title=story_outline['title'],
                story_summary=story_outline['short_summary'],
                character_names=[char['name'] for char in story_outline['characters_roster']],
                plot_points=plot_points,
                no_narrations=no_narrations,
                narration_only_first=narration_only_first,
                cliffhanger_interval=cliffhanger_interval,
                cliffhanger_segments=cliffhanger_segments
            )
            
            # Generate this chunk of segments
            client = get_openai_client()
            chunk_response = client.chat.completions.create(
                model=settings.SCRIPT_MODEL,
                messages=[{"role": "user", "content": segment_prompt}],
            )
            
            chunk_raw = chunk_response.choices[0].message.content.strip()
            if chunk_raw.startswith("```"):
                chunk_raw = chunk_raw.split("```json")[-1].split("```")[0].strip()
            
            chunk_segments_data = json.loads(chunk_raw)
            
            # Validate we got the right number of segments
            if len(chunk_segments_data) != chunk_segments:
                print(f"⚠️ Warning: Expected {chunk_segments} segments, got {len(chunk_segments_data)}")
                # Trim or pad as needed
                if len(chunk_segments_data) > chunk_segments:
                    chunk_segments_data = chunk_segments_data[:chunk_segments]
                    print(f"🔧 Trimmed to {chunk_segments} segments")
                elif len(chunk_segments_data) < chunk_segments:
                    print(f"🔧 Got fewer segments than expected, using {len(chunk_segments_data)}")
            
            all_segments.extend(chunk_segments_data)
            
            print(f"✅ Generated segments {chunk_start + 1}-{chunk_end} ({len(chunk_segments_data)} segments)")
            
            # Small delay to avoid rate limits
            import time
            time.sleep(1)
        
        # Combine everything into final story data
        final_story = {
            "title": story_outline["title"],
            "short_summary": story_outline["short_summary"],
            "description": story_outline["description"],
            "hashtags": story_outline["hashtags"],
            "narrator_voice": story_outline["narrator_voice"],
            "characters_roster": story_outline["characters_roster"],
            "segments": all_segments
        }
        
        print(f"🎉 Successfully generated {len(all_segments)} segments for '{final_story['title']}'")
        return final_story
        
    except Exception as e:
        error_msg = f"Chunked story generation failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise ValueError(error_msg)

def generate_story_segments_in_sets(idea: str, total_segments: int, segments_per_set: int = 10, set_number: int = 1, existing_metadata: dict = None, custom_character_roster: list = None, no_narration: bool = False, narration_only_first: bool = False, cliffhanger_interval: int = 0, content_rating: str = "U"):
    """
    Generate story segments in sets of 10 (or specified amount) with complete metadata
    
    Args:
        idea: Story idea with special requirements
        total_segments: Total number of segments for the complete story
        segments_per_set: Number of segments to generate per set (default: 10)
        set_number: Which set to generate (1-based indexing)
        existing_metadata: Optional metadata from first set to ensure consistency (title, characters, narrator_voice, etc.)
        custom_character_roster: User-provided character roster
        no_narration: If True, no narration in any segment
        narration_only_first: If True, narration only in first segment
        cliffhanger_interval: Add cliffhangers every N segments (0 = no cliffhangers)
        content_rating: Content rating - "U" (Universal), "U/A" (Parental Guidance), "A" (Adult)
    
    Returns:
        dict: Complete story data with metadata + only the requested set of segments
    """
    print(f"🎬 Generating set {set_number} ({segments_per_set} segments) of {total_segments} total segments...")
    print(f"📋 Settings: no_narration={no_narration}, narration_only_first={narration_only_first}, cliffhanger_interval={cliffhanger_interval}, content_rating={content_rating}")
    
    # Ensure all characters have IDs
    if custom_character_roster:
        custom_character_roster = ensure_character_ids(custom_character_roster)
    
    # Use provided parameters instead of parsing from idea
    no_narrations = no_narration
    adult_story = (content_rating == "A")  # Adult content only if rating is "A"
    
    # Calculate segment range for this set
    start_segment = (set_number - 1) * segments_per_set + 1
    end_segment = min(start_segment + segments_per_set - 1, total_segments)
    actual_segments_in_set = end_segment - start_segment + 1
    
    print(f"📊 Set {set_number}: Segments {start_segment}-{end_segment} ({actual_segments_in_set} segments)")
    print(f"📋 Requirements: no_narrations={no_narrations}, narration_only_first={narration_only_first}, cliffhanger_interval={cliffhanger_interval}, adult_story={adult_story}")
    
    # Check if any segments in this set should have cliffhangers
    cliffhanger_segments = []
    if cliffhanger_interval > 0:
        for seg_num in range(start_segment, end_segment + 1):
            if seg_num % cliffhanger_interval == 0:
                cliffhanger_segments.append(seg_num)
    
    # Generate the complete story with this specific set of segments using the prompt function
    prompt = get_story_segments_in_sets_prompt(
        idea=idea,
        set_number=set_number,
        total_segments=total_segments,
        segments_per_set=segments_per_set,
        actual_segments_in_set=actual_segments_in_set,
        start_segment=start_segment,
        end_segment=end_segment,
        no_narrations=no_narrations,
        narration_only_first=narration_only_first,
        cliffhanger_segments=cliffhanger_segments,
        adult_story=adult_story,
        existing_metadata=existing_metadata,
        custom_character_roster=custom_character_roster,
        content_type="movie"
    )
    
    raw_output = None
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        story_data = json.loads(raw_output)
        
        # Validate segment count
        generated_segments = story_data.get('segments', [])
        if len(generated_segments) != actual_segments_in_set:
            print(f"⚠️ Warning: Expected {actual_segments_in_set} segments, got {len(generated_segments)}")
            # Trim if too many segments
            if len(generated_segments) > actual_segments_in_set:
                story_data['segments'] = generated_segments[:actual_segments_in_set]
                print(f"🔧 Trimmed to {actual_segments_in_set} segments")
            # If too few, that's acceptable for the last set
            elif len(generated_segments) < actual_segments_in_set and set_number == ((total_segments + segments_per_set - 1) // segments_per_set):
                print(f"🔧 Last set has {len(generated_segments)} segments (acceptable)")
            else:
                print(f"🔧 Got fewer segments than expected: {len(generated_segments)}")
        
        final_segment_count = len(story_data.get('segments', []))
        print(f"✅ Successfully generated set {set_number} with {final_segment_count} segments")
        print(f"📖 Title: {story_data.get('title', 'N/A')}")
        print(f"👥 Characters: {len(story_data.get('characters_roster', []))}")
        
        return story_data

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed for set {set_number}: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating story set {set_number}: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

def generate_full_story_automatically(idea: str, total_segments: int = None, segments_per_set: int = 10, custom_character_roster: list = None, no_narration: bool = False, narration_only_first: bool = False, cliffhanger_interval: int = 0, content_rating: str = "U"):
    """
    Automatically generate a complete story by:
    1. Detecting the total segments needed from the idea
    2. Generating all sets automatically with retry logic
    3. Saving each set to JSON files using file storage manager
    4. Returning a summary of all generated content
    
    Args:
        no_narration: If True, no narration in any segment
        narration_only_first: If True, narration only in first segment
        cliffhanger_interval: Add cliffhangers every N segments (0 = no cliffhangers)
        content_rating: Content rating - "U" (Universal), "U/A" (Parental Guidance), "A" (Adult)
    """
    import os
    import json
    import time
    from datetime import datetime
    from app.services.file_storage_manager import storage_manager, ContentType
    
    print(f"🚀 Starting automatic full story generation...")
    print(f"💡 Idea: {idea}")
    
    # Step 1: Determine total segments needed
    if total_segments is None:
        # Auto-detect from the idea
        total_segments = detect_total_segments_from_idea(idea)
        print(f"📊 Auto-detected total segments needed: {total_segments}")
    else:
        # Use provided number
        print(f"📊 Using specified total segments: {total_segments}")
    
    # Step 2: Calculate how many sets we need
    total_sets = (total_segments + segments_per_set - 1) // segments_per_set
    print(f"📦 Will generate {total_sets} sets of {segments_per_set} segments each")
    
    # Step 4: Generate all sets with retry logic
    all_sets = []
    story_title = None
    story_metadata = None
    
    def generate_set_with_retry(set_number, max_retries=3):
        """Generate a single set with retry logic and exponential backoff"""
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    wait_time = 2 ** (attempt - 1)  # Exponential backoff: 2, 4, 8 seconds
                    print(f"🔄 Retry attempt {attempt}/{max_retries} for Set {set_number} (waiting {wait_time}s)...")
                    time.sleep(wait_time)
                else:
                    print(f"\n🎬 Generating Set {set_number}/{total_sets}...")
                
                # Generate this set - pass metadata from set 1 to ensure consistency
                story_set = generate_story_segments_in_sets(
                    idea, 
                    total_segments, 
                    segments_per_set, 
                    set_number,
                    existing_metadata=story_metadata if set_number > 1 else None,
                    custom_character_roster=custom_character_roster,
                    no_narration=no_narration,
                    narration_only_first=narration_only_first,
                    cliffhanger_interval=cliffhanger_interval,
                    content_rating=content_rating
                )
                
                # Success - return the generated set
                return story_set, None
                
            except Exception as e:
                error_msg = f"Attempt {attempt} failed for set {set_number}: {str(e)}"
                print(f"⚠️ {error_msg}")
                
                if attempt == max_retries:
                    # Final attempt failed
                    final_error = f"Failed to generate set {set_number} after {max_retries} attempts: {str(e)}"
                    print(f"❌ {final_error}")
                    return None, final_error
        
        return None, "Unknown error"
    
    for set_number in range(1, total_sets + 1):
        story_set, error = generate_set_with_retry(set_number)
        
        if story_set is not None:
            # Success - process the generated set
            
            # Store metadata from first set
            if set_number == 1:
                story_title = story_set.get('title', 'Untitled Story')
                story_metadata = {
                    'title': story_set.get('title'),
                    'short_summary': story_set.get('short_summary'),
                    'description': story_set.get('description'),
                    'hashtags': story_set.get('hashtags'),
                    'narrator_voice': story_set.get('narrator_voice'),
                    'characters_roster': story_set.get('characters_roster'),
                    'generation_info': {
                        'total_segments': total_segments,
                        'segments_per_set': segments_per_set,
                        'total_sets': total_sets,
                        'generated_at': datetime.now().isoformat(),
                        'idea': idea,
                        'no_narration': no_narration,
                        'narration_only_first': narration_only_first,
                        'cliffhanger_interval': cliffhanger_interval,
                        'content_rating': content_rating
                    }
                }
                print(f"✅ Stored metadata from Set 1 for consistency across all sets")
                
                # Save metadata using storage manager
                storage_manager.save_metadata(ContentType.MOVIE, story_title, story_metadata)
                print(f"📋 Saved story metadata using storage manager")
            else:
                print(f"♻️ Reusing metadata from Set 1 to ensure consistency")
            
            # Save set using storage manager
            filepath = storage_manager.save_set(ContentType.MOVIE, story_title, set_number, story_set)
            print(f"💾 Saved: {filepath}")
            
            all_sets.append({
                'set_number': set_number,
                'segments_count': len(story_set.get('segments', [])),
                'file_path': filepath,
                'set_data': story_set,
                'status': 'success'
            })
            
        else:
            # Failed after all retries
            all_sets.append({
                'set_number': set_number,
                'error': error,
                'file_path': None,
                'set_data': None,
                'status': 'failed'
            })
        
        # Small delay to avoid rate limits (only between sets, not retries)
        if set_number < total_sets:
            print("⏳ Waiting 2 seconds to avoid rate limits...")
            time.sleep(2)
    
    # Step 5: Get content directory for reference
    content_dir = None
    if story_title:
        content_dir = storage_manager.get_content_directory(ContentType.MOVIE, story_title, create=False)
    
    # Step 6: Create summary
    successful_sets = [s for s in all_sets if s.get('status') == 'success']
    failed_sets = [s for s in all_sets if s.get('status') == 'failed']
    
    total_segments_generated = sum(s.get('segments_count', 0) for s in successful_sets)
    
    # Check if we have any failed sets for retry information
    failed_set_numbers = [s['set_number'] for s in failed_sets]
    
    summary = {
        'success': len(failed_sets) == 0,  # Only fully successful if no failed sets
        'story_title': story_title,
        'story_metadata': story_metadata,
        'generation_summary': {
            'total_segments_requested': total_segments,
            'total_segments_generated': total_segments_generated,
            'total_sets_requested': total_sets,
            'successful_sets': len(successful_sets),
            'failed_sets': len(failed_sets),
            'segments_per_set': segments_per_set,
            'failed_set_numbers': failed_set_numbers
        },
        'files_saved': save_to_files,
        'content_type': ContentType.MOVIE,
        'content_directory': content_dir,
        'sets': all_sets,
        'retry_info': {
            'can_retry': len(failed_sets) > 0,
            'failed_sets': failed_set_numbers,
            'retry_endpoint': '/retry-failed-story-sets' if len(failed_sets) > 0 else None
        }
    }
    
    print(f"\n🎉 Story Generation Complete!")
    print(f"📖 Title: {story_title}")
    print(f"✅ Successfully generated: {len(successful_sets)}/{total_sets} sets")
    print(f"📊 Total segments: {total_segments_generated}/{total_segments}")
    if failed_sets:
        print(f"❌ Failed sets: {len(failed_sets)} - {failed_set_numbers}")
        print(f"🔄 You can retry failed sets using the retry endpoint")
    if content_dir:
        print(f"💾 Files saved to: {content_dir}")
    
    return summary

def retry_failed_story_sets(previous_result: dict, max_retries: int = 3):
    """
    Retry failed sets from a previous story generation attempt.
    
    Args:
        previous_result: The result from generate_full_story_automatically
        max_retries: Maximum retry attempts per failed set
    
    Returns:
        Updated result with retry attempts
    """
    import os
    import json
    import time
    from datetime import datetime
    
    print(f"🔄 Starting retry for failed story sets...")
    
    # Extract information from previous result
    if not previous_result.get('sets'):
        raise ValueError("No sets found in previous result")
    
    story_metadata = previous_result.get('story_metadata')
    if not story_metadata:
        raise ValueError("No story metadata found in previous result")
    
    # Get generation info
    gen_info = story_metadata.get('generation_info', {})
    idea = gen_info.get('idea')
    total_segments = gen_info.get('total_segments')
    segments_per_set = gen_info.get('segments_per_set', 10)
    no_narration = gen_info.get('no_narration', False)
    narration_only_first = gen_info.get('narration_only_first', False)
    cliffhanger_interval = gen_info.get('cliffhanger_interval', 0)
    content_rating = gen_info.get('content_rating', 'U')
    
    if not idea:
        raise ValueError("Original idea not found in metadata")
    
    # Find failed sets
    failed_sets = [s for s in previous_result['sets'] if s.get('status') == 'failed']
    if not failed_sets:
        print("✅ No failed sets found - nothing to retry")
        return previous_result
    
    print(f"🎯 Found {len(failed_sets)} failed sets to retry: {[s['set_number'] for s in failed_sets]}")
    
    # Get content type and directory
    from app.services.file_storage_manager import storage_manager, ContentType
    content_type = previous_result.get('content_type', ContentType.MOVIE)
    story_title = story_metadata.get('title', 'Untitled Story')
    
    def retry_single_set(set_number, max_retries=3):
        """Retry a single failed set with exponential backoff"""
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    wait_time = 2 ** (attempt - 1)  # Exponential backoff: 2, 4, 8 seconds
                    print(f"🔄 Retry attempt {attempt}/{max_retries} for Set {set_number} (waiting {wait_time}s)...")
                    time.sleep(wait_time)
                else:
                    print(f"🎬 Retrying Set {set_number}...")
                
                # Generate this set using existing metadata for consistency
                story_set = generate_story_segments_in_sets(
                    idea, 
                    total_segments, 
                    segments_per_set, 
                    set_number,
                    existing_metadata=story_metadata,
                    custom_character_roster=story_metadata.get('characters_roster'),
                    no_narration=no_narration,
                    narration_only_first=narration_only_first,
                    cliffhanger_interval=cliffhanger_interval,
                    content_rating=content_rating
                )
                
                # Success - return the generated set
                return story_set, None
                
            except Exception as e:
                error_msg = f"Retry attempt {attempt} failed for set {set_number}: {str(e)}"
                print(f"⚠️ {error_msg}")
                
                if attempt == max_retries:
                    # Final attempt failed
                    final_error = f"Failed to retry set {set_number} after {max_retries} attempts: {str(e)}"
                    print(f"❌ {final_error}")
                    return None, final_error
        
        return None, "Unknown error"
    
    # Retry each failed set
    updated_sets = previous_result['sets'].copy()
    retry_results = []
    
    for failed_set in failed_sets:
        set_number = failed_set['set_number']
        story_set, error = retry_single_set(set_number, max_retries)
        
        # Find the index of this set in the updated_sets list
        set_index = next(i for i, s in enumerate(updated_sets) if s['set_number'] == set_number)
        
        if story_set is not None:
            # Success - update the set using storage manager
            filepath = storage_manager.save_set(content_type, story_title, set_number, story_set)
            print(f"💾 Saved: {filepath}")
            
            updated_sets[set_index] = {
                'set_number': set_number,
                'segments_count': len(story_set.get('segments', [])),
                'file_path': filepath,
                'set_data': story_set,
                'status': 'success',
                'retry_info': {
                    'was_retried': True,
                    'retry_timestamp': datetime.now().isoformat()
                }
            }
            
            retry_results.append({
                'set_number': set_number,
                'status': 'success',
                'segments_generated': len(story_set.get('segments', []))
            })
            
        else:
            # Still failed after retry
            updated_sets[set_index]['retry_info'] = {
                'was_retried': True,
                'retry_failed': True,
                'retry_error': error,
                'retry_timestamp': datetime.now().isoformat()
            }
            
            retry_results.append({
                'set_number': set_number,
                'status': 'failed',
                'error': error
            })
        
        # Small delay between retries
        time.sleep(2)
    
    # Update summary
    successful_sets = [s for s in updated_sets if s.get('status') == 'success']
    still_failed_sets = [s for s in updated_sets if s.get('status') == 'failed']
    
    total_segments_generated = sum(s.get('segments_count', 0) for s in successful_sets)
    still_failed_set_numbers = [s['set_number'] for s in still_failed_sets]
    
    updated_result = previous_result.copy()
    updated_result.update({
        'success': len(still_failed_sets) == 0,
        'sets': updated_sets,
        'generation_summary': {
            **previous_result['generation_summary'],
            'total_segments_generated': total_segments_generated,
            'successful_sets': len(successful_sets),
            'failed_sets': len(still_failed_sets),
            'failed_set_numbers': still_failed_set_numbers
        },
        'retry_info': {
            'retry_performed': True,
            'retry_timestamp': datetime.now().isoformat(),
            'retry_results': retry_results,
            'can_retry': len(still_failed_sets) > 0,
            'failed_sets': still_failed_set_numbers,
            'retry_endpoint': '/retry-failed-story-sets' if len(still_failed_sets) > 0 else None
        }
    })
    
    successful_retries = [r for r in retry_results if r['status'] == 'success']
    failed_retries = [r for r in retry_results if r['status'] == 'failed']
    
    print(f"\n🎉 Retry Complete!")
    print(f"✅ Successfully retried: {len(successful_retries)} sets")
    print(f"❌ Still failed: {len(failed_retries)} sets")
    if still_failed_sets:
        print(f"🔄 Failed sets: {still_failed_set_numbers} - can retry again if needed")
    
    return updated_result

def detect_total_segments_from_idea(idea: str) -> int:
    """
    Analyze the idea to automatically detect how many segments are needed
    """
    idea_upper = idea.upper()
    
    # Look for explicit segment counts in the idea
    import re
    
    # Check for explicit numbers like "100 segments", "200 episodes", etc.
    segment_patterns = [
        r'(\d+)\s*SEGMENTS?',
        r'(\d+)\s*EPISODES?',
        r'(\d+)\s*PARTS?',
        r'(\d+)\s*CHAPTERS?'
    ]
    
    for pattern in segment_patterns:
        match = re.search(pattern, idea_upper)
        if match:
            segments = int(match.group(1))
            print(f"🔍 Found explicit segment count: {segments}")
            return segments
    
    # Look for story length indicators
    if any(word in idea_upper for word in ['SHORT STORY', 'BRIEF', 'QUICK']):
        return 20
    elif any(word in idea_upper for word in ['MEDIUM', 'MODERATE']):
        return 50
    elif any(word in idea_upper for word in ['LONG', 'EXTENDED', 'DETAILED', 'EPIC']):
        return 100
    elif any(word in idea_upper for word in ['SERIES', 'SEASON', 'FULL MOVIE', 'FEATURE']):
        return 150
    elif any(word in idea_upper for word in ['SAGA', 'TRILOGY', 'FRANCHISE']):
        return 200
    
    # Look for cliffhanger intervals to estimate length
    if 'EVERY 150' in idea_upper or '150TH' in idea_upper:
        return 300  # If cliffhangers every 150, story is probably 2x that
    elif 'EVERY 100' in idea_upper or '100TH' in idea_upper:
        return 200
    elif 'EVERY 50' in idea_upper or '50TH' in idea_upper:
        return 100
    
    # Check for adult/complex content (usually longer)
    if 'ADULT' in idea_upper:
        return 100
    
    # Default based on complexity
    word_count = len(idea.split())
    if word_count > 50:
        return 100  # Complex idea = longer story
    elif word_count > 20:
        return 50   # Medium idea = medium story
    else:
        return 30   # Simple idea = shorter story

def generate_meme_segments(idea: str, num_segments: int = 7, custom_character_roster: list = None):
    # Ensure all characters have IDs
    if custom_character_roster:
        custom_character_roster = ensure_character_ids(custom_character_roster)
    
    prompt = get_meme_segments_prompt(idea, num_segments, custom_character_roster)
    raw_output = None
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

          # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        meme_data = json.loads(raw_output)

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"  # Limit output length
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating meme content: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

    return meme_data

def generate_free_content(idea: str, num_segments: int = 7, custom_character_roster: list = None):
    # Ensure all characters have IDs
    if custom_character_roster:
        custom_character_roster = ensure_character_ids(custom_character_roster)
    
    prompt = get_free_content_prompt(idea, num_segments, custom_character_roster)
    raw_output = None
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

         # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        content_data = json.loads(raw_output)

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"  # Limit output length
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating free content: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

    return content_data

def generate_whatsapp_story(idea: str, num_segments: int = 7, custom_character_roster: list = None):
    """
    Generate WhatsApp AI story with beautiful sceneries and moments
    
    Args:
        idea: Story idea/concept
        num_segments: Number of segments (default 7 for WhatsApp stories)
        custom_character_roster: Optional user-provided character roster
    
    Returns:
        dict: WhatsApp story data with segments
    """
    # Ensure all characters have IDs
    if custom_character_roster:
        custom_character_roster = ensure_character_ids(custom_character_roster)
    
    prompt = get_whatsapp_story_prompt(idea, num_segments, custom_character_roster)
    raw_output = None
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        whatsapp_story_data = json.loads(raw_output)
        
        print(f"✅ Successfully generated WhatsApp story with {len(whatsapp_story_data.get('segments', []))} segments")

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed for WhatsApp story: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating WhatsApp story: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

    return whatsapp_story_data

def generate_music_video(song_lyrics: str, song_length: int, background_voice_needed: bool = False, additional_dialogues: list = None, custom_character_roster: list = None, music_genre: str = None, visual_theme: str = None):
    """
    Generate AI music video prompts from song lyrics
    
    Args:
        song_lyrics: The complete song lyrics
        song_length: Song length in seconds
        background_voice_needed: Whether background narration is needed
        additional_dialogues: Optional dialogues to add
        custom_character_roster: Optional character roster
        music_genre: Optional music genre
        visual_theme: Optional visual theme
    
    Returns:
        dict: Music video data with segments
    """
    # Ensure all characters have IDs
    if custom_character_roster:
        custom_character_roster = ensure_character_ids(custom_character_roster)
    
    prompt = get_music_video_prompt(
        song_lyrics, 
        song_length, 
        background_voice_needed, 
        additional_dialogues, 
        custom_character_roster,
        music_genre,
        visual_theme
    )
    
    raw_output = None
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

        # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        music_video_data = json.loads(raw_output)
        
        print(f"✅ Successfully generated music video with {len(music_video_data.get('segments', []))} segments")
        print(f"🎵 Song length: {song_length}s, Total segments: {music_video_data.get('total_segments', 'N/A')}")

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed for music video: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating music video: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

    return music_video_data
    
def generate_trending_ideas(content_type: str = "all", count: int = 5):
    """
    Generate trending, creative, and unique ideas for content creation
    
    Args:
        content_type: Type of content ("story", "meme", "free_content", or "all")
        count: Number of ideas to generate (default 5)
    
    Returns:
        dict: Generated ideas with metadata
    """
    
    if content_type == "all":
        content_types = ["story", "meme", "free_content"]
        ideas_per_type = max(1, count // 3)  # Distribute evenly
    else:
        content_types = [content_type]
        ideas_per_type = count

    prompt = get_trending_ideas_prompt(content_types, ideas_per_type)
    raw_output = None
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[{"role": "user", "content": prompt}],
        )

          # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        ideas_data = json.loads(raw_output)

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"  # Limit output length
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error generating trending ideas: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

    return ideas_data

def analyze_character_from_image(image_data: str, image_format: str = "jpeg", character_count: int = 1, character_name: str = None):
    """
    Analyze an image to generate detailed character roster for video generation.
    
    NOTE: This function is optimized for SINGLE CHARACTER analysis (character_count=1).
    For multiple characters, use separate images with the multiple images endpoint.
    
    Args:
        image_data: Base64 encoded image data
        image_format: Image format (jpeg, png, webp, etc.)
        character_count: Number of characters to identify (MUST be 1 for single image endpoint)
        character_name: Name to assign to the character
    
    Returns:
        dict: Character roster with detailed descriptions for video generation
    """
    print(f"🎭 Analyzing image for {character_count} character(s)...")
    
    prompt = get_character_analysis_prompt(character_count, character_name)
    
    raw_output = None
    try:
        # Prepare the message with image
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/{image_format};base64,{image_data}"
                        }
                    }
                ]
            }
        ]
        
        client = get_openai_client()
        
        # Token allocation optimized for single character analysis
        # For 1 character: 8000 tokens (sufficient for extremely detailed schema)
        # Note: This endpoint should only be used with character_count=1
        max_tokens = 8000 if character_count == 1 else 5000 + (character_count * 4000)
        
        response = client.chat.completions.create(
            model="meta-llama/llama-4-maverick:free",  # Using Grok vision model for image analysis
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7
        )

        # Validate response exists
        if response is None:
            raise ValueError("API returned None response")
        
        # Validate response structure
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        # Validate message content
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        # Validate content is not None or empty
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()

        # Remove code block wrappers
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        # Validate JSON is not empty after cleanup
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")

        character_data = json.loads(raw_output)
        
        # Character IDs are no longer auto-generated
        # Characters will use their names or client-provided IDs if needed
        
        characters_found = len(character_data.get('characters_roster', []))
        print(f"✅ Successfully analyzed {characters_found} character(s) from image")
        print(f"📊 Analysis summary: {character_data.get('analysis_summary', 'N/A')}")
        
        return character_data

    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed for character analysis: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Error analyzing character from image: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)

def analyze_multiple_character_images(image_list: list, character_count_per_image: int = 1):
    """
    Analyze multiple images to generate a combined character roster
    
    Args:
        image_list: List of dictionaries with 'image_data', 'image_format', and optional 'description'
        character_count_per_image: Number of characters to identify per image
    
    Returns:
        dict: Combined character roster from all images
    """
    print(f"🎭 Analyzing {len(image_list)} images for characters...")
    
    all_characters = []
    all_analyses = []
    
    for i, image_info in enumerate(image_list, 1):
        try:
            print(f"\n📸 Analyzing image {i}/{len(image_list)}...")
            
            image_data = image_info.get('image_data')
            image_format = image_info.get('image_format', 'jpeg')
            description = image_info.get('description', f'Image {i}')
            
            if not image_data:
                print(f"⚠️ Skipping image {i}: No image data provided")
                continue
            
            # Analyze this image
            analysis = analyze_character_from_image(
                image_data, 
                image_format, 
                character_count_per_image
            )
            
            # Add image info to each character
            for char in analysis.get('characters_roster', []):
                char['source_image'] = i
                char['source_description'] = description
                char['id'] = f"img{i}_{char['id']}"  # Make IDs unique across images
            
            all_characters.extend(analysis.get('characters_roster', []))
            all_analyses.append({
                'image_number': i,
                'description': description,
                'analysis': analysis
            })
            
        except Exception as e:
            print(f"❌ Failed to analyze image {i}: {str(e)}")
            all_analyses.append({
                'image_number': i,
                'description': image_info.get('description', f'Image {i}'),
                'error': str(e)
            })
    
    # Create combined result
    combined_result = {
        'total_images_analyzed': len(image_list),
        'successful_analyses': len([a for a in all_analyses if 'error' not in a]),
        'total_characters_found': len(all_characters),
        'characters_roster': all_characters,
        'individual_analyses': all_analyses,
        'combined_notes': f"Character roster combined from {len(image_list)} images. Each character ID is prefixed with 'img{i}_' to ensure uniqueness."
    }
    
    print(f"\n🎉 Multi-image analysis complete!")
    print(f"📊 Total characters found: {len(all_characters)}")
    print(f"✅ Successful analyses: {combined_result['successful_analyses']}/{len(image_list)}")
    
    return combined_result

def save_character_to_file(character_data: dict, character_name: str = None):
    """
    Save character data to a JSON file in the saved_characters folder
    
    Args:
        character_data: Character data from analysis
        character_name: Optional custom name for the file
    
    Returns:
        dict: Save result with file path
    """
    import os
    import json
    from datetime import datetime
    
    try:
        # Create saved_characters directory if it doesn't exist
        save_dir = "saved_characters"
        os.makedirs(save_dir, exist_ok=True)
        
        # Get character name for filename
        if character_name:
            filename_base = character_name
        else:
            # Try to get name from character data
            if isinstance(character_data, dict) and 'name' in character_data:
                filename_base = character_data['name']
            elif isinstance(character_data, dict) and 'characters_roster' in character_data:
                # Get first character's name
                roster = character_data['characters_roster']
                if roster and len(roster) > 0:
                    filename_base = roster[0].get('name', 'unnamed_character')
                else:
                    filename_base = 'unnamed_character'
            else:
                filename_base = 'unnamed_character'
        
        # Clean filename (remove invalid characters)
        safe_filename = "".join(c for c in filename_base if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_filename = safe_filename.replace(' ', '_')[:50]  # Limit length
        
        # Add timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_filename}_{timestamp}.json"
        filepath = os.path.join(save_dir, filename)
        
        # Add metadata to character data
        save_data = {
            "character_data": character_data,
            "metadata": {
                "saved_at": datetime.now().isoformat(),
                "character_name": character_name or filename_base,
                "filename": filename,
                "version": "1.0"
            }
        }
        
        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Character saved: {filepath}")
        
        return {
            "success": True,
            "filepath": filepath,
            "filename": filename,
            "character_name": character_name or filename_base,
            "saved_at": save_data["metadata"]["saved_at"]
        
        }
    except Exception as e:
        error_msg = f"Failed to save character: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }

def save_multiple_characters_to_files(characters_list: list, character_names: list = None):
    """
    Save multiple characters to separate JSON files
    
    Args:
        characters_list: List of character data
        character_names: List of character names (optional)
    
    Returns:
        dict: Save results for all characters
    """
    results = {
        "total_characters": len(characters_list),
        "successful_saves": 0,
        "failed_saves": 0,
        "save_results": []
    }
    
    for i, character_data in enumerate(characters_list):
        character_name = None
        if character_names and i < len(character_names):
            character_name = character_names[i]
        
        save_result = save_character_to_file(character_data, character_name)
        results["save_results"].append(save_result)
        
        if save_result["success"]:
            results["successful_saves"] += 1
        else:
            results["failed_saves"] += 1
    
    print(f"💾 Batch save complete: {results['successful_saves']}/{results['total_characters']} characters saved")
    
    return results


# ==================== CHARACTER MANAGEMENT (MONGODB-BASED) ====================

from app.services.character_repository import CharacterRepository

# Initialize repository
_character_repo = None

def get_character_repository() -> CharacterRepository:
    """Get or create character repository instance"""
    global _character_repo
    if _character_repo is None:
        _character_repo = CharacterRepository()
    return _character_repo

def get_all_characters():
    """
    Get list of all saved characters
    
    Returns:
        dict: List of characters with metadata
    """
    import os
    import json
    from datetime import datetime
    
    try:
        save_dir = "saved_characters"
        
        if not os.path.exists(save_dir):
            return {
                "success": True,
                "total_characters": 0,
                "characters": []
            }
        
        characters = []
        for filename in os.listdir(save_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(save_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # Extract character info
                    character_data = data.get('character_data', {})
                    metadata = data.get('metadata', {})
                    
                    characters.append({
                        "filename": filename,
                        "filepath": filepath,
                        "character_id": character_data.get('id', 'unknown'),
                        "character_name": character_data.get('name', metadata.get('character_name', 'Unknown')),
                        "saved_at": metadata.get('saved_at', 'Unknown'),
                        "file_size_bytes": os.path.getsize(filepath),
                        "has_image_data": 'source_image' in character_data
                    })
                except Exception as e:
                    print(f"⚠️ Error reading {filename}: {e}")
                    continue
        
        # Sort by saved_at (newest first)
        characters.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        
        return {
            "success": True,
            "total_characters": len(characters),
            "characters": characters
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to list characters: {str(e)}"
        }


def get_character_by_filename(filename: str):
    """
    Get a specific character by filename
    
    Args:
        filename: The filename of the saved character
    
    Returns:
        dict: Character data
    """
    import os
    import json
    
    try:
        save_dir = "saved_characters"
        filepath = os.path.join(save_dir, filename)
        
        if not os.path.exists(filepath):
            return {
                "success": False,
                "error": f"Character file not found: {filename}"
            }
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {
            "success": True,
            "filename": filename,
            "filepath": filepath,
            "character_data": data.get('character_data', {}),
            "metadata": data.get('metadata', {})
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to read character: {str(e)}"
        }


def update_character(filename: str, updated_data: dict):
    """
    Update a saved character
    
    Args:
        filename: The filename of the character to update
        updated_data: Updated character data
    
    Returns:
        dict: Update result
    """
    import os
    import json
    from datetime import datetime
    
    try:
        save_dir = "saved_characters"
        filepath = os.path.join(save_dir, filename)
        
        if not os.path.exists(filepath):
            return {
                "success": False,
                "error": f"Character file not found: {filename}"
            }
        
        # Read existing data
        with open(filepath, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
        
        # Update character data
        existing_data['character_data'].update(updated_data)
        
        # Update metadata
        if 'metadata' not in existing_data:
            existing_data['metadata'] = {}
        
        existing_data['metadata']['updated_at'] = datetime.now().isoformat()
        existing_data['metadata']['version'] = existing_data['metadata'].get('version', '1.0')
        
        # Save updated data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(existing_data, f, indent=2, ensure_ascii=False)
        
        print(f"✏️ Character updated: {filepath}")
        
        return {
            "success": True,
            "filename": filename,
            "filepath": filepath,
            "updated_at": existing_data['metadata']['updated_at'],
            "message": "Character updated successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update character: {str(e)}"
        }


def delete_character(filename: str):
    """
    Delete a saved character
    
    Args:
        filename: The filename of the character to delete
    
    Returns:
        dict: Delete result
    """
    import os
    
    try:
        save_dir = "saved_characters"
        filepath = os.path.join(save_dir, filename)
        
        if not os.path.exists(filepath):
            return {
                "success": False,
                "error": f"Character file not found: {filename}"
            }
        
        # Delete the file
        os.remove(filepath)
        
        print(f"🗑️ Character deleted: {filepath}")
        
        return {
            "success": True,
            "filename": filename,
            "message": "Character deleted successfully"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to delete character: {str(e)}"
        }


def search_characters(query: str = None, filters: dict = None):
    """
    Search characters by name or other criteria
    
    Args:
        query: Search query string (searches in name)
        filters: Additional filters (e.g., gender, age_range)
    
    Returns:
        dict: Search results
    """
    import os
    import json
    
    try:
        save_dir = "saved_characters"
        
        if not os.path.exists(save_dir):
            return {
                "success": True,
                "total_results": 0,
                "characters": []
            }
        
        results = []
        
        for filename in os.listdir(save_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(save_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    character_data = data.get('character_data', {})
                    metadata = data.get('metadata', {})
                    
                    # Apply query filter
                    if query:
                        character_name = character_data.get('name', '').lower()
                        if query.lower() not in character_name:
                            continue
                    
                    # Apply additional filters
                    if filters:
                        match = True
                        
                        # Filter by gender
                        if 'gender' in filters:
                            char_gender = character_data.get('physical_appearance', {}).get('gender', '').lower()
                            if char_gender != filters['gender'].lower():
                                match = False
                        
                        # Filter by age range
                        if 'age_range' in filters:
                            char_age = character_data.get('physical_appearance', {}).get('estimated_age', '')
                            if filters['age_range'] not in char_age:
                                match = False
                        
                        if not match:
                            continue
                    
                    results.append({
                        "filename": filename,
                        "filepath": filepath,
                        "character_id": character_data.get('id', 'unknown'),
                        "character_name": character_data.get('name', 'Unknown'),
                        "gender": character_data.get('physical_appearance', {}).get('gender', 'Unknown'),
                        "age": character_data.get('physical_appearance', {}).get('estimated_age', 'Unknown'),
                        "saved_at": metadata.get('saved_at', 'Unknown')
                    })
                
                except Exception as e:
                    print(f"⚠️ Error reading {filename}: {e}")
                    continue
        
        # Sort by saved_at (newest first)
        results.sort(key=lambda x: x.get('saved_at', ''), reverse=True)
        
        return {
            "success": True,
            "total_results": len(results),
            "query": query,
            "filters": filters,
            "characters": results
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to search characters: {str(e)}"
        }



def generate_anime_story_automatically(
    idea: str,
    total_segments: int = None,
    segments_per_set: int = 10,
    custom_character_roster: list = None,
    anime_style: str = "shonen",
    no_narration: bool = False,
    narration_only_first: bool = False,
    cliffhanger_interval: int = 0,
    content_rating: str = "U/A"
):
    """
    Automatically generate a complete Japanese anime story in English.
    
    Similar to generate_full_story_automatically but specifically for anime content.
    Files are automatically saved using the file storage manager.
    
    Args:
        idea: The anime story concept
        total_segments: Total number of segments (auto-detected if None)
        segments_per_set: Segments per set (default: 10)
        custom_character_roster: Optional pre-defined anime characters
        anime_style: Type of anime - "shonen", "shojo", "seinen", "slice_of_life", "mecha", "isekai"
        no_narration: If True, no narration in any segment
        narration_only_first: If True, narration only in first segment
        cliffhanger_interval: Add cliffhangers every N segments
        content_rating: "U" (Universal), "U/A" (Parental Guidance), "A" (Adult)
    
    Returns:
        dict: Complete anime generation results with metadata and segments
    """
    import os
    import json
    import time
    from datetime import datetime
    from app.services.file_storage_manager import storage_manager, ContentType
    
    print(f"🎌 Starting automatic anime generation...")
    print(f"💡 Anime Idea: {idea}")
    print(f"🎨 Anime Style: {anime_style}")
    
    # Step 1: Determine total segments needed
    if total_segments is None:
        total_segments = detect_total_segments_from_idea(idea)
        print(f"📊 Auto-detected total segments needed: {total_segments}")
    else:
        print(f"📊 Using specified total segments: {total_segments}")
    
    # Step 2: Calculate how many sets we need
    total_sets = (total_segments + segments_per_set - 1) // segments_per_set
    print(f"📦 Will generate {total_sets} sets of {segments_per_set} segments each")
    
    # Step 4: Generate all sets with retry logic
    all_sets = []
    anime_title = None
    anime_metadata = None
    
    def generate_set_with_retry(set_number, max_retries=3):
        """Generate a single anime set with retry logic"""
        nonlocal anime_title, anime_metadata
        
        for attempt in range(1, max_retries + 1):
            try:
                if attempt > 1:
                    wait_time = 2 ** (attempt - 1)
                    print(f"🔄 Retry attempt {attempt}/{max_retries} for Set {set_number} (waiting {wait_time}s)...")
                    time.sleep(wait_time)
                else:
                    print(f"\n🎬 Generating Anime Set {set_number}/{total_sets}...")
                
                # Calculate segment range for this set
                start_segment = (set_number - 1) * segments_per_set + 1
                end_segment = min(set_number * segments_per_set, total_segments)
                
                # Determine cliffhanger segments
                cliffhanger_segments = []
                if cliffhanger_interval > 0:
                    for seg_num in range(start_segment, end_segment + 1):
                        if seg_num % cliffhanger_interval == 0:
                            cliffhanger_segments.append(seg_num)
                
                # Build the prompt
                prompt = get_anime_story_prompt(
                    idea=idea,
                    num_segments=end_segment - start_segment + 1,
                    custom_character_roster=custom_character_roster,
                    anime_style=anime_style
                )
                
                # Add special instructions
                special_instructions = []
                if no_narration:
                    special_instructions.append("NO NARRATION in any segment - only dialogue and visual storytelling")
                elif narration_only_first and set_number == 1:
                    special_instructions.append("Include narration ONLY in the first segment for introduction")
                elif narration_only_first:
                    special_instructions.append("NO NARRATION - only dialogue")
                
                if cliffhanger_segments:
                    special_instructions.append(f"Add DRAMATIC ANIME CLIFFHANGERS at segments: {cliffhanger_segments}")
                
                special_instructions.append(f"Content Rating: {content_rating}")
                special_instructions.append(f"This is set {set_number} of {total_sets}, segments {start_segment}-{end_segment}")
                
                if anime_metadata and set_number > 1:
                    special_instructions.append("CRITICAL: Use the EXACT same character descriptions and anime style from previous sets")
                
                if special_instructions:
                    prompt += "\n\n**SPECIAL INSTRUCTIONS**:\n" + "\n".join(f"- {inst}" for inst in special_instructions)
                
                # Call OpenAI
                client = get_openai_client()
                response = client.chat.completions.create(
                    model=settings.SCRIPT_MODEL,
                    messages=[
                        {"role": "system", "content": "You are a professional Japanese anime scriptwriter creating anime content in English."},
                        {"role": "user", "content": prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.8
                )
                
                # Parse response
                anime_set = json.loads(response.choices[0].message.content)
                
                # Store metadata from first set
                if set_number == 1:
                    anime_title = anime_set.get("title", "Untitled Anime")
                    anime_metadata = {
                        "title": anime_title,
                        "anime_style": anime_style,
                        "short_summary": anime_set.get("short_summary", ""),
                        "description": anime_set.get("description", ""),
                        "hashtags": anime_set.get("hashtags", []),
                        "target_demographic": anime_set.get("target_demographic", ""),
                        "narrator_voice": anime_set.get("narrator_voice", {}),
                        "characters_roster": anime_set.get("characters_roster", []),
                        "anime_themes": anime_set.get("anime_themes", []),
                        "power_system": anime_set.get("power_system", ""),
                        "world_building": anime_set.get("world_building", ""),
                        "generation_info": {
                            "total_segments": total_segments,
                            "segments_per_set": segments_per_set,
                            "total_sets": total_sets,
                            "generated_at": datetime.now().isoformat(),
                            "idea": idea,
                            "anime_style": anime_style,
                            "no_narration": no_narration,
                            "narration_only_first": narration_only_first,
                            "cliffhanger_interval": cliffhanger_interval,
                            "content_rating": content_rating
                        }
                    }
                    print(f"🎌 Anime Title: {anime_title}")
                    print(f"🎨 Style: {anime_style}")
                
                # Save to file if requested
                filepath = None
                if save_to_files:
                    safe_title = "".join(c for c in anime_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_title = safe_title.replace(' ', '_')[:50]
                    
                    filename = f"{safe_title}_set_{set_number:02d}.json"
                    filepath = os.path.join(output_directory, filename)
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(anime_set, f, indent=2, ensure_ascii=False)
                    
                    print(f"💾 Saved: {filepath}")
                
                return {
                    'set_number': set_number,
                    'segments_count': len(anime_set.get('segments', [])),
                    'file_path': filepath,
                    'set_data': anime_set,
                    'status': 'success'
                }
                
            except Exception as e:
                error = str(e)
                print(f"❌ Error generating anime set {set_number} (attempt {attempt}/{max_retries}): {error}")
                if attempt == max_retries:
                    return {
                        'set_number': set_number,
                        'error': error,
                        'file_path': None,
                        'set_data': None,
                        'status': 'failed'
                    }
        
        return None
    
    # Generate all sets
    for set_num in range(1, total_sets + 1):
        result = generate_set_with_retry(set_num)
        if result:
            all_sets.append(result)
        
        # Small delay between sets
        if set_num < total_sets:
            print("⏳ Waiting 2 seconds...")
            time.sleep(2)
    
    # Step 5: Save complete anime metadata
    if save_to_files and anime_metadata:
        safe_title = "".join(c for c in anime_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:50]
        
        metadata_filename = f"{safe_title}_metadata.json"
        metadata_filepath = os.path.join(output_directory, metadata_filename)
        
        with open(metadata_filepath, 'w', encoding='utf-8') as f:
            json.dump(anime_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Saved anime metadata: {metadata_filepath}")
    
    # Step 6: Create summary
    successful_sets = [s for s in all_sets if s.get('status') == 'success']
    failed_sets = [s for s in all_sets if s.get('status') == 'failed']
    
    total_segments_generated = sum(s.get('segments_count', 0) for s in successful_sets)
    failed_set_numbers = [s['set_number'] for s in failed_sets]
    
    summary = {
        'success': len(failed_sets) == 0,
        'anime_title': anime_title,
        'anime_style': anime_style,
        'story_metadata': anime_metadata,
        'generation_summary': {
            'total_segments_requested': total_segments,
            'total_segments_generated': total_segments_generated,
            'total_sets_requested': total_sets,
            'successful_sets': len(successful_sets),
            'failed_sets': len(failed_sets),
            'segments_per_set': segments_per_set,
            'failed_set_numbers': failed_set_numbers
        },
        'files_saved': save_to_files,
        'output_directory': output_directory if save_to_files else None,
        'sets': all_sets,
        'retry_info': {
            'can_retry': len(failed_sets) > 0,
            'failed_sets': failed_set_numbers,
            'retry_endpoint': '/retry-failed-story-sets' if len(failed_sets) > 0 else None
        }
    }
    
    print(f"\n🎉 Anime Generation Complete!")
    print(f"🎌 Title: {anime_title}")
    print(f"🎨 Style: {anime_style}")
    print(f"✅ Successfully generated: {len(successful_sets)}/{total_sets} sets")
    print(f"📊 Total segments: {total_segments_generated}/{total_segments}")
    if failed_sets:
        print(f"❌ Failed sets: {len(failed_sets)} - {failed_set_numbers}")
        print(f"🔄 You can retry failed sets using the retry endpoint")
    if save_to_files:
        print(f"💾 Files saved to: {output_directory}")
    
    return summary



def generate_daily_character_content(
    idea: str,
    character_name: str,
    creature_language: str = "Soft and High-Pitched",
    num_segments: int = 7,
    allow_dialogue: bool = False
):
    """
    Generate daily character life content for Instagram using keyframes.
    
    Creates engaging daily moments. By default uses creature sounds only (NO dialogue/narration).
    Designed for use with character images as keyframes in Veo3.
    Maximum 10 segments per generation.
    
    Args:
        idea: The daily life moment/situation
        character_name: Name of the character
        creature_language: Voice type ("Soft and High-Pitched", "Magical or Otherworldly", "Muffled and Low")
        num_segments: Number of segments (max 10, default 7 for ~1 min video)
        allow_dialogue: Allow human dialogue/narration (default: False - creature sounds only)
    
    Returns:
        dict: Generated daily character content
    """
    import json
    from datetime import datetime
    
    # Limit to 10 segments
    if num_segments > 10:
        print(f"⚠️ Limiting segments to 10 (requested: {num_segments})")
        num_segments = 10
    
    if num_segments < 1:
        raise ValueError("Number of segments must be at least 1")
    
    print(f"🎬 Generating daily character content...")
    print(f"👤 Character: {character_name}")
    print(f"🗣️ Creature Language: {creature_language}")
    print(f"💡 Idea: {idea}")
    print(f"📊 Segments: {num_segments} (~{num_segments * 8} seconds)")
    
    # Build the prompt
    prompt = get_daily_character_prompt(idea, character_name, creature_language, num_segments, allow_dialogue)
    
    # Call OpenAI
    raw_output = None
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=settings.SCRIPT_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a viral Instagram content creator specializing in relatable character moments. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.9  # Higher creativity for fun content
        )
        
        # Validate response
        if response is None:
            raise ValueError("API returned None response")
        
        if not hasattr(response, 'choices') or not response.choices:
            raise ValueError(f"Invalid API response structure: {response}")
        
        if not hasattr(response.choices[0], 'message') or not hasattr(response.choices[0].message, 'content'):
            raise ValueError(f"Missing message content in response: {response.choices[0]}")
        
        raw_output = response.choices[0].message.content
        
        if not raw_output or raw_output.strip() == "":
            raise ValueError("API returned empty content")
        
        raw_output = raw_output.strip()
        
        # Remove code block wrappers if present
        if raw_output.startswith("```"):
            raw_output = raw_output.split("```json")[-1].split("```")[0].strip()
        
        if not raw_output:
            raise ValueError("Content became empty after removing code blocks")
        
        # Parse response
        content = json.loads(raw_output)
        
    except json.JSONDecodeError as e:
        error_msg = f"JSON parsing failed: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        raise ValueError(error_msg)
    
    except Exception as e:
        error_msg = f"Daily character content generation failed: {e}"
        if raw_output:
            error_msg += f"\n\nRaw output:\n{raw_output[:500]}"
        else:
            error_msg += "\n\nNo output received from API"
        raise ValueError(error_msg)
    
    # Add generation metadata
    content["generation_info"] = {
        "generated_at": datetime.now().isoformat(),
        "idea": idea,
        "num_segments": num_segments,
        "total_duration_seconds": num_segments * 8,
        "content_type": "daily_character_life",
        "platform": "instagram"
    }
    
    print(f"✅ Generated: {content.get('title', 'Untitled')}")
    print(f"🎭 Character: {content.get('character', {}).get('name', 'Unknown')}")
    print(f"📊 Segments: {len(content.get('segments', []))}")
    print(f"⏱️ Duration: ~{num_segments * 8} seconds")
    
    return content
