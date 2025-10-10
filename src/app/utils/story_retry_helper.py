"""
Utility functions for retrying failed story generation sets.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def find_story_metadata(title: str, base_dir: str = "generated_movie_script") -> Optional[str]:
    """
    Find the metadata file for a story by its title.
    
    Args:
        title: The story title (e.g., "Midnight Protocol")
        base_dir: Base directory where stories are saved
        
    Returns:
        Path to the metadata file if found, None otherwise
    """
    # Normalize title for filename matching
    normalized_title = title.replace(" ", "_")
    
    # Look for metadata file
    metadata_filename = f"{normalized_title}_metadata.json"
    metadata_path = os.path.join(base_dir, metadata_filename)
    
    if os.path.exists(metadata_path):
        return metadata_path
    
    # Try case-insensitive search
    if os.path.exists(base_dir):
        for filename in os.listdir(base_dir):
            if filename.lower() == metadata_filename.lower():
                return os.path.join(base_dir, filename)
    
    return None


def load_story_metadata(metadata_path: str) -> Dict:
    """
    Load story metadata from a JSON file.
    
    Args:
        metadata_path: Path to the metadata file
        
    Returns:
        Dictionary containing the metadata
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        json.JSONDecodeError: If the file is not valid JSON
    """
    with open(metadata_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_failed_sets(title: str, base_dir: str = "generated_movie_script") -> Tuple[Optional[Dict], List[int]]:
    """
    Find failed sets for a story by analyzing which set files are missing.
    
    Args:
        title: The story title
        base_dir: Base directory where stories are saved
        
    Returns:
        Tuple of (metadata_dict, list_of_failed_set_numbers)
        Returns (None, []) if metadata not found
    """
    # Find and load metadata
    metadata_path = find_story_metadata(title, base_dir)
    if not metadata_path:
        return None, []
    
    metadata = load_story_metadata(metadata_path)
    
    # Get total sets from metadata
    gen_info = metadata.get('generation_info', {})
    total_sets = gen_info.get('total_sets', 30)
    
    # Check which set files exist
    normalized_title = title.replace(" ", "_")
    failed_sets = []
    
    for set_num in range(1, total_sets + 1):
        set_filename = f"{normalized_title}_set_{set_num:02d}.json"
        set_path = os.path.join(base_dir, set_filename)
        
        if not os.path.exists(set_path):
            failed_sets.append(set_num)
    
    return metadata, failed_sets


def construct_retry_payload(
    title: str,
    metadata: Dict,
    failed_sets: List[int],
    max_retries: int = 3,
    base_dir: str = "generated_movie_script"
) -> Dict:
    """
    Construct the payload for retrying failed story sets.
    
    Args:
        title: Story title
        metadata: Story metadata dictionary
        failed_sets: List of failed set numbers
        max_retries: Maximum retry attempts per set
        base_dir: Base directory where stories are saved
        
    Returns:
        Dictionary payload ready for the retry endpoint
    """
    # Calculate successful sets
    gen_info = metadata.get('generation_info', {})
    total_sets = gen_info.get('total_sets', 30)
    segments_per_set = gen_info.get('segments_per_set', 10)
    
    successful_sets = total_sets - len(failed_sets)
    total_segments_generated = successful_sets * segments_per_set
    
    # Construct the sets array that the retry service expects
    normalized_title = title.replace(" ", "_")
    sets_array = []
    
    for set_num in range(1, total_sets + 1):
        if set_num in failed_sets:
            # Failed set
            sets_array.append({
                'set_number': set_num,
                'status': 'failed',
                'file_path': None,
                'set_data': None,
                'error': 'Set file not found - needs retry'
            })
        else:
            # Successful set - load the file path
            set_filename = f"{normalized_title}_set_{set_num:02d}.json"
            set_path = os.path.join(base_dir, set_filename)
            
            # Try to load the set data to get segment count
            segments_count = segments_per_set
            set_data = None
            try:
                with open(set_path, 'r', encoding='utf-8') as f:
                    set_data = json.load(f)
                    segments_count = len(set_data.get('segments', []))
            except:
                pass  # If we can't load it, use default segment count
            
            sets_array.append({
                'set_number': set_num,
                'segments_count': segments_count,
                'file_path': set_path,
                'set_data': set_data,
                'status': 'success'
            })
    
    previous_result = {
        "story_title": title,
        "story_metadata": metadata,
        "sets": sets_array,
        "files_saved": True,
        "output_directory": base_dir,
        "generation_summary": {
            "successful_sets": successful_sets,
            "failed_sets": len(failed_sets),
            "total_segments_generated": total_segments_generated,
            "failed_set_numbers": failed_sets,
            "total_sets_requested": total_sets,
            "segments_per_set": segments_per_set
        }
    }
    
    return {
        "previous_result": previous_result,
        "max_retries": max_retries
    }


def get_retry_info_by_title(
    title: str,
    base_dir: str = "generated_movie_script"
) -> Dict:
    """
    Get comprehensive retry information for a story by its title.
    
    Args:
        title: Story title
        base_dir: Base directory where stories are saved
        
    Returns:
        Dictionary with story info and failed sets, or error info
    """
    metadata, failed_sets = find_failed_sets(title, base_dir)
    
    if metadata is None:
        return {
            "success": False,
            "error": f"Story '{title}' not found in {base_dir}",
            "title": title
        }
    
    if not failed_sets:
        gen_info = metadata.get('generation_info', {})
        return {
            "success": True,
            "title": title,
            "failed_sets": [],
            "message": "All sets completed successfully!",
            "total_sets": gen_info.get('total_sets', 0),
            "metadata": metadata
        }
    
    gen_info = metadata.get('generation_info', {})
    total_sets = gen_info.get('total_sets', 30)
    successful_sets = total_sets - len(failed_sets)
    
    return {
        "success": True,
        "title": title,
        "failed_sets": failed_sets,
        "total_sets": total_sets,
        "successful_sets": successful_sets,
        "failed_count": len(failed_sets),
        "metadata": metadata,
        "message": f"Found {len(failed_sets)} failed sets out of {total_sets} total sets"
    }
