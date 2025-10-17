"""
Character Repository

This module provides database operations for character management using MongoDB.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from bson import ObjectId
from pymongo.collection import Collection

from app.connectors.mongodb_connector import get_collection
from app.models.character import Character


class CharacterRepository:
    """
    Repository for character database operations
    """
    
    def __init__(self):
        """Initialize the repository with MongoDB collection"""
        self.collection: Collection = get_collection(Character.COLLECTION_NAME)
        # Ensure indexes are created
        Character.create_indexes(self.collection)
    
    def create(
        self, 
        character_data: Dict[str, Any], 
        character_name: str,
        image_url: Optional[str] = None,
        cloudinary_public_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new character in the database
        
        Args:
            character_data: Complete character analysis data
            character_name: Name of the character
            image_url: Optional Cloudinary URL of character image
            cloudinary_public_id: Optional Cloudinary public ID
        
        Returns:
            dict: Created character with ID
        """
        try:
            character = Character(
                character_data=character_data,
                character_name=character_name,
                image_url=image_url,
                cloudinary_public_id=cloudinary_public_id
            )
            
            result = self.collection.insert_one(character.to_dict())
            character._id = result.inserted_id
            
            print(f"💾 Character saved to MongoDB: {character_name} (ID: {result.inserted_id})")
            if image_url:
                print(f"🖼️ Character image URL: {image_url}")
            
            return {
                "success": True,
                "character_id": str(result.inserted_id),
                "character_name": character_name,
                "image_url": image_url,
                "created_at": character.created_at.isoformat()
            }
        
        except Exception as e:
            error_msg = f"Failed to create character: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    def get_all(self, skip: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        Get all characters with pagination
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            dict: List of characters
        """
        try:
            total_count = self.collection.count_documents({})
            
            cursor = self.collection.find().sort("created_at", -1).skip(skip).limit(limit)
            
            characters = []
            for doc in cursor:
                character = Character.from_dict(doc)
                
                # Extract character info from nested structure
                char_info = character.character_data
                if 'characters_roster' in char_info and char_info['characters_roster']:
                    # Data is in characters_roster format
                    first_char = char_info['characters_roster'][0]
                    char_id = first_char.get('id', 'unknown')
                    gender = first_char.get('physical_appearance', {}).get('gender', 'Unknown')
                    age = first_char.get('physical_appearance', {}).get('estimated_age', 'Unknown')
                else:
                    # Data is in direct format
                    char_id = char_info.get('id', 'unknown')
                    gender = char_info.get('physical_appearance', {}).get('gender', 'Unknown')
                    age = char_info.get('physical_appearance', {}).get('estimated_age', 'Unknown')
                
                characters.append({
                    "id": str(character._id),
                    "character_name": character.character_name,
                    "character_id": char_id,
                    "gender": gender,
                    "age": age,
                    "created_at": character.created_at.isoformat() if character.created_at else None,
                    "updated_at": character.updated_at.isoformat() if character.updated_at else None
                })
            
            return {
                "success": True,
                "total_characters": total_count,
                "returned_count": len(characters),
                "skip": skip,
                "limit": limit,
                "characters": characters
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to retrieve characters: {str(e)}"
            }
    
    def get_by_id(self, character_id: str) -> Dict[str, Any]:
        """
        Get a character by ID
        
        Args:
            character_id: MongoDB ObjectId as string
        
        Returns:
            dict: Character data
        """
        try:
            if not ObjectId.is_valid(character_id):
                return {
                    "success": False,
                    "error": "Invalid character ID format"
                }
            
            doc = self.collection.find_one({"_id": ObjectId(character_id)})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Character not found with ID: {character_id}"
                }
            
            character = Character.from_dict(doc)
            
            return {
                "success": True,
                "character": character.to_response()
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to retrieve character: {str(e)}"
            }
    
    def update(self, character_id: str, updated_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a character
        
        Args:
            character_id: MongoDB ObjectId as string
            updated_data: Data to update
        
        Returns:
            dict: Update result
        """
        try:
            if not ObjectId.is_valid(character_id):
                return {
                    "success": False,
                    "error": "Invalid character ID format"
                }
            
            # Get existing character
            doc = self.collection.find_one({"_id": ObjectId(character_id)})
            
            if not doc:
                return {
                    "success": False,
                    "error": f"Character not found with ID: {character_id}"
                }
            
            # Merge updated data with existing character_data
            existing_character_data = doc.get("character_data", {})
            existing_character_data.update(updated_data)
            
            # Update document
            update_result = self.collection.update_one(
                {"_id": ObjectId(character_id)},
                {
                    "$set": {
                        "character_data": existing_character_data,
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if update_result.modified_count > 0:
                print(f"✏️ Character updated: {character_id}")
                return {
                    "success": True,
                    "character_id": character_id,
                    "updated_at": datetime.utcnow().isoformat(),
                    "message": "Character updated successfully"
                }
            else:
                return {
                    "success": True,
                    "character_id": character_id,
                    "message": "No changes made (data was identical)"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to update character: {str(e)}"
            }
    
    def delete(self, character_id: str) -> Dict[str, Any]:
        """
        Delete a character
        
        Args:
            character_id: MongoDB ObjectId as string
        
        Returns:
            dict: Delete result
        """
        try:
            if not ObjectId.is_valid(character_id):
                return {
                    "success": False,
                    "error": "Invalid character ID format"
                }
            
            result = self.collection.delete_one({"_id": ObjectId(character_id)})
            
            if result.deleted_count > 0:
                print(f"🗑️ Character deleted: {character_id}")
                return {
                    "success": True,
                    "character_id": character_id,
                    "message": "Character deleted successfully"
                }
            else:
                return {
                    "success": False,
                    "error": f"Character not found with ID: {character_id}"
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to delete character: {str(e)}"
            }
    
    def search(
        self,
        query: Optional[str] = None,
        gender: Optional[str] = None,
        age_range: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Search characters with filters
        
        Args:
            query: Text search query
            gender: Filter by gender
            age_range: Filter by age range
            skip: Number of records to skip
            limit: Maximum number of records to return
        
        Returns:
            dict: Search results
        """
        try:
            # Build search filter
            search_filter = {}
            
            # Text search
            if query:
                search_filter["$text"] = {"$search": query}
            
            # Gender filter
            if gender:
                search_filter["character_data.physical_appearance.gender"] = {
                    "$regex": gender,
                    "$options": "i"
                }
            
            # Age range filter
            if age_range:
                search_filter["character_data.physical_appearance.estimated_age"] = {
                    "$regex": age_range,
                    "$options": "i"
                }
            
            # Count total matching documents
            total_count = self.collection.count_documents(search_filter)
            
            # Execute search
            cursor = self.collection.find(search_filter).sort("created_at", -1).skip(skip).limit(limit)
            
            results = []
            for doc in cursor:
                character = Character.from_dict(doc)
                
                # Extract character info from nested structure
                char_info = character.character_data
                if 'characters_roster' in char_info and char_info['characters_roster']:
                    # Data is in characters_roster format
                    first_char = char_info['characters_roster'][0]
                    char_id = first_char.get('id', 'unknown')
                    gender = first_char.get('physical_appearance', {}).get('gender', 'Unknown')
                    age = first_char.get('physical_appearance', {}).get('estimated_age', 'Unknown')
                    role = first_char.get('role', 'Unknown')
                else:
                    # Data is in direct format
                    char_id = char_info.get('id', 'unknown')
                    gender = char_info.get('physical_appearance', {}).get('gender', 'Unknown')
                    age = char_info.get('physical_appearance', {}).get('estimated_age', 'Unknown')
                    role = char_info.get('role', 'Unknown')
                
                results.append({
                    "id": str(character._id),
                    "character_name": character.character_name,
                    "character_id": char_id,
                    "gender": gender,
                    "age": age,
                    "role": role,
                    "created_at": character.created_at.isoformat() if character.created_at else None
                })
            
            return {
                "success": True,
                "total_results": total_count,
                "returned_count": len(results),
                "query": query,
                "filters": {
                    "gender": gender,
                    "age_range": age_range
                },
                "skip": skip,
                "limit": limit,
                "characters": results
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to search characters: {str(e)}"
            }
    
    def bulk_create(self, characters_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create multiple characters at once
        
        Args:
            characters_data: List of character data dictionaries
        
        Returns:
            dict: Bulk create result
        """
        try:
            documents = []
            for char_data in characters_data:
                character = Character(
                    character_data=char_data.get('character_data', {}),
                    character_name=char_data.get('character_name', 'Unknown')
                )
                documents.append(character.to_dict())
            
            result = self.collection.insert_many(documents)
            
            print(f"💾 Bulk save complete: {len(result.inserted_ids)} characters saved to MongoDB")
            
            return {
                "success": True,
                "total_created": len(result.inserted_ids),
                "character_ids": [str(id) for id in result.inserted_ids]
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to bulk create characters: {str(e)}"
            }
