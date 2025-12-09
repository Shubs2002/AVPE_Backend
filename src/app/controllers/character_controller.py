"""
Character Controller

Handles HTTP request/response logic for character management endpoints.
"""

from typing import Optional, Dict, List
from fastapi import UploadFile

from app.services.character_service import character_service


class CharacterController:
    """Controller for character management operations"""
    
    async def analyze_character_image(
        self,
        image: UploadFile,
        character_name: str,
        can_speak: bool
    ) -> Dict:
        """
        Analyze character image and return AI suggestions
        
        Args:
            image: Uploaded image file
            character_name: Name of the character
            can_speak: Whether character can speak human language (guides voice description)
            
        Returns:
            dict: Analysis results with voice and keyword suggestions
        """
        try:
            result = await character_service.analyze_character_image(
                image=image,
                character_name=character_name,
                can_speak=can_speak
            )
            
            return {
                "success": True,
                **result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def create_character(
        self,
        image: UploadFile,
        character_id: str,
        character_name: str,
        gender: str,
        voice_description: str,
        keywords: str,
        is_private: bool,
        can_speak: bool,
        user_id: Optional[str] = None
    ) -> Dict:
        """
        Create a new character
        
        Args:
            image: Uploaded image file
            character_id: Character ID from analyze step (char_xxx)
            character_name: Name of the character
            gender: Gender (male/female/non-binary/creature/undefined)
            voice_description: Voice description (and-separated)
            keywords: Comma-separated keywords string
            is_private: Private (true) or public (false)
            user_id: Optional user ID
            
        Returns:
            dict: Created character data
        """
        try:
            result = await character_service.create_character(
                image=image,
                character_id=character_id,
                character_name=character_name,
                gender=gender,
                voice_description=voice_description,
                keywords=keywords,
                is_private=is_private,
                can_speak=can_speak,
                user_id=user_id
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_all_characters(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
        current_user_id: Optional[str] = None
    ) -> Dict:
        """
        Get all characters with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            user_id: Optional user ID filter
            current_user_id: Optional current authenticated user ID (for privacy filtering)
            
        Returns:
            dict: List of characters with pagination info
        """
        try:
            return character_service.get_all_characters(
                skip=skip,
                limit=limit,
                user_id=user_id,
                current_user_id=current_user_id
            )
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "characters": [],
                "total": 0
            }
    
    def get_character_by_id(self, character_id: str) -> Dict:
        """
        Get a specific character by ID
        
        Args:
            character_id: Character ID
            
        Returns:
            dict: Character data
        """
        try:
            result = character_service.get_character_by_id(character_id)
            
            return {
                "success": True,
                **result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def update_character(
        self,
        character_id: str,
        updated_data: Dict
    ) -> Dict:
        """
        Update a character
        
        Args:
            character_id: Character ID
            updated_data: Data to update
            
        Returns:
            dict: Updated character data
        """
        try:
            # TODO: Implement update logic in character_service
            return {
                "success": False,
                "error": "Update functionality not yet implemented"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def delete_character(self, character_id: str) -> Dict:
        """
        Delete a character
        
        Args:
            character_id: Character ID
            
        Returns:
            dict: Deletion result
        """
        try:
            # TODO: Implement delete logic in character_service
            return {
                "success": False,
                "error": "Delete functionality not yet implemented"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def search_characters(
        self,
        query: Optional[str] = None,
        voice_type: Optional[str] = None,
        keywords: Optional[List[str]] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict:
        """
        Search characters by various criteria
        
        Args:
            query: Text search query
            voice_type: Filter by voice type
            keywords: Filter by keywords
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            dict: Search results
        """
        try:
            # TODO: Implement search logic in character_service
            return {
                "success": False,
                "error": "Search functionality not yet implemented",
                "characters": [],
                "total": 0
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "characters": [],
                "total": 0
            }


# Global instance
character_controller = CharacterController()
