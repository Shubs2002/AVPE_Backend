"""
Character Model for MongoDB

This module defines the Character data model and provides
database operations for character management.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from bson import ObjectId


class Character:
    """
    Character model for MongoDB storage
    """
    
    # Collection name in MongoDB
    COLLECTION_NAME = "characters"
    
    def __init__(
        self,
        character_data: Dict[str, Any],
        character_name: str,
        _id: Optional[ObjectId] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
        version: str = "1.0"
    ):
        """
        Initialize a Character instance
        
        Args:
            character_data: Complete character analysis data
            character_name: Name of the character
            _id: MongoDB ObjectId (auto-generated if not provided)
            created_at: Creation timestamp
            updated_at: Last update timestamp
            version: Data version
        """
        self._id = _id
        self.character_data = character_data
        self.character_name = character_name
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()
        self.version = version
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert Character instance to dictionary for MongoDB storage
        
        Returns:
            dict: Character data as dictionary
        """
        data = {
            "character_data": self.character_data,
            "character_name": self.character_name,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "version": self.version
        }
        
        if self._id:
            data["_id"] = self._id
        
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Character':
        """
        Create Character instance from dictionary
        
        Args:
            data: Dictionary from MongoDB
        
        Returns:
            Character: Character instance
        """
        return cls(
            _id=data.get("_id"),
            character_data=data.get("character_data", {}),
            character_name=data.get("character_name", "Unknown"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at"),
            version=data.get("version", "1.0")
        )
    
    def to_response(self) -> Dict[str, Any]:
        """
        Convert Character to API response format
        
        Returns:
            dict: Character data for API response
        """
        return {
            "id": str(self._id) if self._id else None,
            "character_name": self.character_name,
            "character_data": self.character_data,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "version": self.version
        }
    
    @staticmethod
    def get_searchable_fields() -> List[str]:
        """
        Get list of fields that can be searched
        
        Returns:
            list: Searchable field names
        """
        return [
            "character_name",
            "character_data.name",
            "character_data.physical_appearance.gender",
            "character_data.physical_appearance.estimated_age",
            "character_data.role",
            "character_data.personality"
        ]
    
    @staticmethod
    def create_indexes(collection) -> None:
        """
        Create indexes for the characters collection
        
        Args:
            collection: MongoDB collection
        """
        # Index on character_name for fast lookups
        collection.create_index("character_name")
        
        # Index on character_data.name for searching
        collection.create_index("character_data.name")
        
        # Index on created_at for sorting
        collection.create_index("created_at")
        
        # Text index for full-text search
        collection.create_index([
            ("character_name", "text"),
            ("character_data.name", "text"),
            ("character_data.personality", "text"),
            ("character_data.role", "text")
        ])
        
        print("✅ Character collection indexes created")
