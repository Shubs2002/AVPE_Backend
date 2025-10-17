"""
Utility functions for retrying failed story generation sets.
"""
import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from app.services.file_storage_manager import storage_manager


def find_story_metadata(title: str, content_type: str = "movies") -> Optional[str]:
    """
    Find the metadata file for a story by its title using file storage manager.
    
    Args:
        title: The story title (e.g., "Midnight Protocol")
        content_type: Type of content (movies, stories, anime, etc.)
        
    Returns:
        Path to the metadata file if found, None otherwise
    """
    content_dir = storage_manager.get_content_directory(content_type, title, create=False)
    metadata_path = os.path.join(content_dir, "metadata.json")
    
    if os.path.exists(metadata_path):
        return metadata_path
    
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


def find_failed_sets(title: str, content_type: str = "movies") -> Tuple[Optional[Dict], List[int]]:
    """
    Find failed sets for a story by analyzing which set files are missing.
    
    Args:
        title: The story title
        content_type: Type of content (movies, stories, anime, etc.)
        
    Returns:
        Tuple of (metadata_dict, list_of_failed_set_numbers)
        Returns (None, []) if metadata not found
    """
    # Load metadata using storage manager
    metadata = storage_manager.load_metadata(content_type, title)
    if not metadata:
        return None, []
    
    # Get total sets from metadata
    gen_info = metadata.get('generation_info', {})
    total_sets = gen_info.get('total_sets', 30)
    
    # Find missing sets using storage manager
    failed_sets = storage_manager.find_missing_sets(content_type, title, total_sets)
    
    return metadata, failed_sets


def construct_retry_payload(
    title: str,
    content_type: str,
    metadata: Dict,
    failed_sets: List[int],
    max_retries: int = 3
) -> Dict:
    """
    Construct the payload for retrying failed story sets.
    
    Args:
        title: Story title
        content_type: Type of content (movies, stories, anime, etc.)
        metadata: Story metadata dictionary
        failed_sets: List of failed set numbers
        max_retries: Maximum retry attempts per set
        
    Returns:
        Dictionary payload ready for the retry endpoint
    """
    # Calculate successful sets
    gen_info = metadata.get('generation_info', {})
    total_sets = gen_info.get('total_sets', 30)
    segments_per_set = gen_info.get('segments_per_set', 10)
    
    successful_sets = total_sets - len(failed_sets)
    total_segments_generated = successful_sets * segments_per_set
    
    # Get content directory
    content_dir = storage_manager.get_content_directory(content_type, title, create=False)
    
    # Construct the sets array that the retry service expects
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
            # Successful set - load using storage manager
            set_data = storage_manager.load_set(content_type, title, set_num)
            set_path = os.path.join(content_dir, f"set_{set_num:02d}.json")
            
            segments_count = segments_per_set
            if set_data:
                segments_count = len(set_data.get('segments', []))
            
            sets_array.append({
                'set_number': set_num,
                'segments_count': segments_count,
                'file_path': set_path,
                'set_data': set_data,
                'status': 'success'
            })
    
    previous_result = {
        "story_title": title,
        "content_type": content_type,
        "story_metadata": metadata,
        "sets": sets_array,
        "files_saved": True,
        "content_directory": content_dir,
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
    content_type: str = "movies"
) -> Dict:
    """
    Get comprehensive retry information for a story by its title.
    
    Args:
        title: Story title
        content_type: Type of content (movies, stories, anime, etc.)
        
    Returns:
        Dictionary with story info and failed sets, or error info
    """
    metadata, failed_sets = find_failed_sets(title, content_type)
    
    if metadata is None:
        return {
            "success": False,
            "error": f"Story '{title}' not found in {content_type}",
            "title": title,
            "content_type": content_type
        }
    
    if not failed_sets:
        gen_info = metadata.get('generation_info', {})
        return {
            "success": True,
            "title": title,
            "content_type": content_type,
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
        "content_type": content_type,
        "failed_sets": failed_sets,
        "total_sets": total_sets,
        "successful_sets": successful_sets,
        "failed_count": len(failed_sets),
        "metadata": metadata,
        "message": f"Found {len(failed_sets)} failed sets out of {total_sets} total sets"
    }
