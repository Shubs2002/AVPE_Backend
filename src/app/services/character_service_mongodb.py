"""
Character Service - MongoDB Implementation

This module provides character management functions using MongoDB instead of local files.
"""

from typing import Optional, Dict, Any
from app.services.character_repository import CharacterRepository

# Initialize repository
_character_repo = None


def get_character_repository() -> CharacterRepository:
    """Get or create character repository instance"""
    global _character_repo
    if _character_repo is None:
        _character_repo = CharacterRepository()
    return _character_repo


def save_character_to_mongodb(character_data: dict, character_name: str = None) -> dict:
    """
    Save character data to MongoDB
    
    Args:
        character_data: Character data from analysis
        character_name: Optional custom name for the character
    
    Returns:
        dict: Save result with character ID
    """
    try:
        repo = get_character_repository()
        
        # Get character name
        if character_name:
            name = character_name
        else:
            # Try to get name from character data
            if isinstance(character_data, dict) and 'name' in character_data:
                name = character_data['name']
            elif isinstance(character_data, dict) and 'characters_roster' in character_data:
                # Get first character's name
                roster = character_data['characters_roster']
                if roster and len(roster) > 0:
                    name = roster[0].get('name', 'unnamed_character')
                else:
                    name = 'unnamed_character'
            else:
                name = 'unnamed_character'
        
        # Save to MongoDB
        result = repo.create(character_data, name)
        
        return result
    
    except Exception as e:
        error_msg = f"Failed to save character to MongoDB: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }


def save_multiple_characters_to_mongodb(characters_list: list, character_names: list = None) -> dict:
    """
    Save multiple characters to MongoDB
    
    Args:
        characters_list: List of character data dictionaries
        character_names: Optional list of character names
    
    Returns:
        dict: Batch save result
    """
    try:
        repo = get_character_repository()
        
        # Prepare characters data
        characters_data = []
        for i, character in enumerate(characters_list):
            name = character_names[i] if character_names and i < len(character_names) else character.get('name', f'character_{i+1}')
            characters_data.append({
                'character_data': character,
                'character_name': name
            })
        
        # Bulk save to MongoDB
        result = repo.bulk_create(characters_data)
        
        return result
    
    except Exception as e:
        error_msg = f"Failed to save multiple characters to MongoDB: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }


def get_all_characters(skip: int = 0, limit: int = 100) -> dict:
    """
    Get list of all saved characters from MongoDB
    
    Args:
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
    
    Returns:
        dict: List of characters with metadata
    """
    try:
        repo = get_character_repository()
        return repo.get_all(skip, limit)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to retrieve characters: {str(e)}"
        }


def get_character_by_id(character_id: str) -> dict:
    """
    Get a specific character by MongoDB ID
    
    Args:
        character_id: MongoDB ObjectId as string
    
    Returns:
        dict: Character data
    """
    try:
        repo = get_character_repository()
        return repo.get_by_id(character_id)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to retrieve character: {str(e)}"
        }


def update_character(character_id: str, updated_data: dict) -> dict:
    """
    Update a saved character in MongoDB
    
    Args:
        character_id: MongoDB ObjectId as string
        updated_data: Updated character data
    
    Returns:
        dict: Update result
    """
    try:
        repo = get_character_repository()
        return repo.update(character_id, updated_data)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to update character: {str(e)}"
        }


def delete_character(character_id: str) -> dict:
    """
    Delete a saved character from MongoDB
    
    Args:
        character_id: MongoDB ObjectId as string
    
    Returns:
        dict: Delete result
    """
    try:
        repo = get_character_repository()
        return repo.delete(character_id)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to delete character: {str(e)}"
        }


def search_characters(
    query: Optional[str] = None,
    gender: Optional[str] = None,
    age_range: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> dict:
    """
    Search characters by name or other criteria in MongoDB
    
    Args:
        query: Search query string (searches in name)
        gender: Filter by gender
        age_range: Filter by age range
        skip: Number of records to skip (pagination)
        limit: Maximum number of records to return
    
    Returns:
        dict: Search results
    """
    try:
        repo = get_character_repository()
        return repo.search(query, gender, age_range, skip, limit)
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to search characters: {str(e)}"
        }
