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
from app.data.prompts.generate_trending_ideas_prompt import get_trending_ideas_prompt
from app.data.prompts.analyze_character_prompt import get_character_analysis_prompt
from app.utils.id_generator import generate_character_id


def ensure_character_ids(custom_character_roster: list) -> list:
    """
    Ensure all characters in the roster have unique IDs.
    Generates UUIDs for characters missing IDs.
    
    Args:
        custom_character_roster: List of character dictionaries
    
    Returns:
        list: Character roster with guaranteed IDs
    """
    if not custom_character_roster:
        return custom_character_roster
    
    for character in custom_character_roster:
        if not character.get('id') or character.get('id') == 'unknown':
            # Generate a unique ID using the centralized utility
            character['id'] = generate_character_id()
            print(f"🆔 Generated ID for character '{character.get('name', 'Unknown')}': {character['id']}")
    
    return custom_character_roster


def generate_story_segments(idea: str, num_segments: int = 7, custom_character_roster: list = None):
    # Ensure all characters have IDs
    if custom_character_roster:
        custom_character_roster = ensure_character_ids(custom_character_roster)
    # For large segment counts, use chunked generation to avoid JSON parsing issues
    if num_segments > 20:
        return generate_story_segments_chunked(idea, num_segments, custom_character_roster)
    
    prompt = get_story_segments_prompt(idea, num_segments, custom_character_roster)
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
    outline_prompt = get_outline_for_story_segments_chunked(idea, num_segments, no_narrations, narration_only_first, cliffhanger_interval, adult_story, custom_character_roster)
    
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

def generate_story_segments_in_sets(idea: str, total_segments: int, segments_per_set: int = 10, set_number: int = 1, existing_metadata: dict = None, custom_character_roster: list = None):
    """
    Generate story segments in sets of 10 (or specified amount) with complete metadata
    
    Args:
        idea: Story idea with special requirements
        total_segments: Total number of segments for the complete story
        segments_per_set: Number of segments to generate per set (default: 10)
        set_number: Which set to generate (1-based indexing)
        existing_metadata: Optional metadata from first set to ensure consistency (title, characters, narrator_voice, etc.)
    
    Returns:
        dict: Complete story data with metadata + only the requested set of segments
    """
    print(f"🎬 Generating set {set_number} ({segments_per_set} segments) of {total_segments} total segments...")
    
    # Ensure all characters have IDs
    if custom_character_roster:
        custom_character_roster = ensure_character_ids(custom_character_roster)
    
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
        import re
        match = re.search(r'EVERY (\d+)', idea_upper)
        if match:
            cliffhanger_interval = int(match.group(1))
    
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
        custom_character_roster=custom_character_roster
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

def generate_full_story_automatically(idea: str, total_segments: int = None, segments_per_set: int = 10, save_to_files: bool = True, output_directory: str = "generated_stories", custom_character_roster: list = None):
    """
    Automatically generate a complete story by:
    1. Detecting the total segments needed from the idea
    2. Generating all sets automatically
    3. Saving each set to JSON files
    4. Returning a summary of all generated content
    """
    import os
    import json
    import time
    from datetime import datetime
    
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
    
    # Step 3: Create output directory if saving to files
    if save_to_files:
        os.makedirs(output_directory, exist_ok=True)
        print(f"📁 Output directory: {output_directory}")
    
    # Step 4: Generate all sets
    all_sets = []
    story_title = None
    story_metadata = None
    
    for set_number in range(1, total_sets + 1):
        try:
            print(f"\n🎬 Generating Set {set_number}/{total_sets}...")
            
            # Generate this set - pass metadata from set 1 to ensure consistency
            story_set = generate_story_segments_in_sets(
                idea, 
                total_segments, 
                segments_per_set, 
                set_number,
                existing_metadata=story_metadata if set_number > 1 else None,
                custom_character_roster=custom_character_roster
            )
            
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
                        'idea': idea
                    }
                }
                print(f"✅ Stored metadata from Set 1 for consistency across all sets")
            else:
                print(f"♻️ Reusing metadata from Set 1 to ensure consistency")
            
            # Save to file if requested
            if save_to_files:
                # Clean title for filename
                safe_title = "".join(c for c in story_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                safe_title = safe_title.replace(' ', '_')[:50]  # Limit length
                
                filename = f"{safe_title}_set_{set_number:02d}.json"
                filepath = os.path.join(output_directory, filename)
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(story_set, f, indent=2, ensure_ascii=False)
                
                print(f"💾 Saved: {filepath}")
            
            all_sets.append({
                'set_number': set_number,
                'segments_count': len(story_set.get('segments', [])),
                'file_path': filepath if save_to_files else None,
                'set_data': story_set
            })
            
            # Small delay to avoid rate limits
            if set_number < total_sets:
                print("⏳ Waiting 2 seconds to avoid rate limits...")
                time.sleep(2)
                
        except Exception as e:
            error_msg = f"Failed to generate set {set_number}: {str(e)}"
            print(f"❌ {error_msg}")
            all_sets.append({
                'set_number': set_number,
                'error': error_msg,
                'file_path': None,
                'set_data': None
            })
    
    # Step 5: Save complete story metadata
    if save_to_files and story_metadata:
        safe_title = "".join(c for c in story_title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_title = safe_title.replace(' ', '_')[:50]
        
        metadata_filename = f"{safe_title}_metadata.json"
        metadata_filepath = os.path.join(output_directory, metadata_filename)
        
        with open(metadata_filepath, 'w', encoding='utf-8') as f:
            json.dump(story_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"📋 Saved story metadata: {metadata_filepath}")
    
    # Step 6: Create summary
    successful_sets = [s for s in all_sets if s.get('set_data') is not None]
    failed_sets = [s for s in all_sets if s.get('error') is not None]
    
    total_segments_generated = sum(s['segments_count'] for s in successful_sets)
    
    summary = {
        'success': True,
        'story_title': story_title,
        'story_metadata': story_metadata,
        'generation_summary': {
            'total_segments_requested': total_segments,
            'total_segments_generated': total_segments_generated,
            'total_sets_requested': total_sets,
            'successful_sets': len(successful_sets),
            'failed_sets': len(failed_sets),
            'segments_per_set': segments_per_set
        },
        'files_saved': save_to_files,
        'output_directory': output_directory if save_to_files else None,
        'sets': all_sets
    }
    
    print(f"\n🎉 Story Generation Complete!")
    print(f"📖 Title: {story_title}")
    print(f"✅ Successfully generated: {len(successful_sets)}/{total_sets} sets")
    print(f"📊 Total segments: {total_segments_generated}/{total_segments}")
    if failed_sets:
        print(f"❌ Failed sets: {len(failed_sets)}")
    if save_to_files:
        print(f"💾 Files saved to: {output_directory}")
    
    return summary

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
            model=settings.SCRIPT_MODEL,  # Using Grok vision model for image analysis
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
        
        # Generate unique IDs for characters using centralized utility
        if 'characters_roster' in character_data:
            for character in character_data['characters_roster']:
                # Always generate a new UUID for character ID
                character['id'] = generate_character_id()
                print(f"🆔 Generated ID for character '{character.get('name', 'Unknown')}': {character['id']}")
        
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
