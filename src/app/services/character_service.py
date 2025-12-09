"""
Character Service

Handles character management including AI analysis, storage, and retrieval.
"""

import json
import uuid
import base64
from datetime import datetime
from typing import Optional, Dict, List
from fastapi import UploadFile
from PIL import Image
from io import BytesIO

from app.services.encryption_service import encryption_service
from app.services.cloudinary_service import cloudinary_service
from app.connectors.mongodb_connector import get_collection
from app.data.prompts.analyze_character_prompt import get_character_analysis_prompt


class CharacterService:
    """Service for managing characters with AI analysis and encrypted storage"""
    
    def __init__(self):
        self.collection_name = "characters"
    
    async def analyze_character_image(
        self,
        image: UploadFile,
        character_name: str,
        can_speak: bool
    ) -> Dict:
        """
        Analyze character image using AI to suggest voice type and keywords
        
        Args:
            image: Uploaded image file
            character_name: Name of the character
            can_speak: Whether character can speak human language (guides voice description format)
            
        Returns:
            dict: Analysis results with suggestions
        """
        try:
            print(f"\n🔍 Analyzing character: {character_name}")
            print(f"🗣️  Speech capability: {'Enabled (can speak words)' if can_speak else 'Disabled (creature sounds only)'}")
            
            # Read image data
            image_data = await image.read()
            image_base64 = base64.b64encode(image_data).decode()
            
            # Use Gemini to analyze the character
            from app.services.genai_service import analyze_image_with_gemini
            
            # Pass can_speak to prompt so AI knows how to format voice_description
            prompt = get_character_analysis_prompt(
                character_count=1,
                character_name=character_name,
                can_speak=can_speak
            )
            
            analysis_result = analyze_image_with_gemini(
                image_data=image_base64,
                prompt=prompt
            )
            
            # Parse the analysis result
            if isinstance(analysis_result, str):
                analysis_data = json.loads(analysis_result)
            else:
                analysis_data = analysis_result
            
            # Generate character_id with format: char_charactername_uuid
            # Clean character name for ID (lowercase, remove spaces/special chars)
            clean_name = character_name.lower().replace(" ", "").replace("-", "").replace("_", "")
            # Take first 8 characters of UUID for shorter ID
            short_uuid = str(uuid.uuid4()).split('-')[0]
            character_id = f"char_{clean_name}_{short_uuid}"
            
            print(f"🆔 Generated character ID: {character_id}")
            
            # Extract the fields directly
            name = analysis_data.get("name", character_name)
            gender = analysis_data.get("gender", "undefined")
            keywords = analysis_data.get("keywords", "")  # Now a string, not array
            voice_description = analysis_data.get("voice_description", "")
            
            # Ensure keywords is within 500 character limit
            if len(keywords) > 500:
                keywords = keywords[:497] + "..."
            
            print(f"✅ Analysis complete: {name} ({gender})")
            
            # Build simplified response - ONLY essential data
            response = {
                "character_id": character_id,
                "character_name": name,
                "gender": gender,
                "voice_description": voice_description,
                "keywords": keywords,  # String of comma-separated keywords (max 500 chars)
                "can_speak": can_speak  # Boolean: true if can speak, false if only creature sounds
            }
            
            return response
            
        except Exception as e:
            print(f"❌ Analysis failed: {str(e)}")
            raise ValueError(f"Failed to analyze character: {str(e)}")
    
    def _map_speaking_style_to_voice(self, speaking_style: str, character_data: dict) -> str:
        """Map speaking style and character data to voice type"""
        
        # Get all relevant data
        appearance = character_data.get("physical_appearance", {})
        personality = character_data.get("personality", "").lower()
        
        # Get height/size info
        height = appearance.get("height", "").lower()
        
        # Get gender (can influence voice)
        gender = appearance.get("gender", "").lower()
        
        # Get skin tone (sometimes correlates with character type)
        skin_details = appearance.get("skin_details", {})
        
        # Combine all text for analysis
        all_text = f"{speaking_style} {personality} {height}".lower()
        
        print(f"🔍 Analyzing voice from: '{all_text[:100]}'")
        
        # Score each voice type
        soft_score = 0
        deep_score = 0
        magical_score = 0
        
        # Soft and High-Pitched indicators
        soft_keywords = ["shy", "soft", "gentle", "playful", "cute", "small", "young", 
                        "child", "friendly", "sweet", "light", "cheerful", "bubbly",
                        "feminine", "delicate", "timid", "nervous", "high"]
        for keyword in soft_keywords:
            if keyword in all_text:
                soft_score += 1
        
        # Deep and Grumbly indicators
        deep_keywords = ["confident", "authoritative", "deep", "serious", "strong", 
                        "powerful", "commanding", "bold", "gruff", "rough", "tough",
                        "masculine", "large", "tall", "big", "muscular", "heavy",
                        "intimidating", "stern", "firm", "low"]
        for keyword in deep_keywords:
            if keyword in all_text:
                deep_score += 1
        
        # Magical or Otherworldly indicators
        magical_keywords = ["mysterious", "ethereal", "magical", "mystical", "enchanting",
                           "otherworldly", "supernatural", "spiritual", "cosmic", "divine",
                           "ancient", "wise", "enigmatic", "arcane", "celestial"]
        for keyword in magical_keywords:
            if keyword in all_text:
                magical_score += 1
        
        print(f"📊 Voice scores - Soft: {soft_score}, Deep: {deep_score}, Magical: {magical_score}")
        
        # Return the highest scoring voice type
        if magical_score > 0 and magical_score >= soft_score and magical_score >= deep_score:
            return "Magical or Otherworldly"
        elif deep_score > soft_score:
            return "Deep and Grumbly"
        elif soft_score > 0:
            return "Soft and High-Pitched"
        else:
            # Default based on gender if no clear indicators
            if "male" in gender and "female" not in gender:
                return "Deep and Grumbly"
            else:
                return "Soft and High-Pitched"
    
    def _extract_keywords(self, character_data: dict) -> List[str]:
        """Extract keywords from character analysis"""
        
        keywords = []
        
        # From personality
        personality = character_data.get("personality", "")
        if personality:
            keywords.extend([trait.strip() for trait in personality.split(",")])
        
        # From appearance
        appearance = character_data.get("physical_appearance", {})
        if isinstance(appearance, dict):
            # Add size
            if "height" in appearance:
                height = appearance["height"].lower()
                if "small" in height or "short" in height:
                    keywords.append("small")
                elif "tall" in height or "large" in height:
                    keywords.append("large")
            
            # Add skin tone descriptors
            skin_details = appearance.get("skin_details", {})
            if isinstance(skin_details, dict) and "skin_tone" in skin_details:
                tone_words = skin_details["skin_tone"].split()
                keywords.extend(tone_words[:2])  # First 2 words
        
        # From clothing
        clothing = character_data.get("clothing_style", {})
        if isinstance(clothing, dict):
            style_chars = clothing.get("style_characteristics", {})
            if isinstance(style_chars, dict):
                aesthetic = style_chars.get("overall_aesthetic", "")
                if aesthetic:
                    keywords.extend(aesthetic.split("/"))
        
        # Clean and deduplicate
        keywords = [k.strip().lower() for k in keywords if k.strip()]
        keywords = list(dict.fromkeys(keywords))  # Remove duplicates while preserving order
        
        return keywords
    
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
        Create a new character with encrypted storage
        
        Args:
            image: Uploaded image file
            character_id: Character ID from analyze step (char_xxx)
            character_name: Name of the character
            gender: Gender (male/female/non-binary/creature/undefined)
            voice_description: Voice description with accent (and-separated)
            keywords: Comma-separated keywords string
            is_private: Private (true) or public (false)
            can_speak: Can speak human language (true) or only creature sounds (false)
            user_id: Optional user ID for multi-user support
            
        Returns:
            dict: Created character data
        """
        try:
            print(f"\n💾 Creating character: {character_name} (ID: {character_id})")
            
            # Read image data
            image_data = await image.read()
            image_base64 = base64.b64encode(image_data).decode()
            
            # Upload image to Cloudinary
            cloudinary_result = cloudinary_service.upload_character_image(
                image_data=image_base64,
                character_name=character_name
            )
            
            cloudinary_url = cloudinary_result["url"]
            cloudinary_public_id = cloudinary_result["public_id"]
            thumbnail_url = cloudinary_result.get("thumbnail_url")
            
            # Encrypt sensitive Cloudinary data only
            encrypted_public_id = encryption_service.encrypt(cloudinary_public_id)
            encrypted_url = encryption_service.encrypt(cloudinary_url)
            encrypted_thumbnail = encryption_service.encrypt(thumbnail_url) if thumbnail_url else None
            
            # Prepare character document
            character_doc = {
                "character_id": character_id,  # NOT encrypted - used for lookups
                "character_name": character_name,
                "gender": gender,
                "voice_description": voice_description,
                "keywords": keywords,  # String, not array
                "is_private": is_private,
                "can_speak": can_speak,  # Speech capability
                "cloudinary_public_id": encrypted_public_id,  # Encrypted
                "cloudinary_url": encrypted_url,  # Encrypted
                "thumbnail_url": encrypted_thumbnail,  # Encrypted
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            if user_id:
                character_doc["user_id"] = user_id
            
            # Save to MongoDB
            collection = get_collection(self.collection_name)
            result = collection.insert_one(character_doc)
            
            print(f"✅ Character created: {character_name} ({'Private' if is_private else 'Public'})")
            
            # Return response (with decrypted IDs for client)
            return {
                "success": True,
                "character_id": character_id,  # Already has char_ prefix
                "character_name": character_name,
                "gender": gender,
                "voice_description": voice_description,
                "keywords": keywords,  # String, not array
                "cloudinary_url": cloudinary_url,
                "thumbnail_url": thumbnail_url,
                "created_at": character_doc["created_at"].isoformat()
            }
            
        except Exception as e:
            print(f"❌ Creation failed: {str(e)}")
            raise ValueError(f"Failed to create character: {str(e)}")
    
    def get_all_characters(
        self,
        skip: int = 0,
        limit: int = 100,
        user_id: Optional[str] = None,
        current_user_id: Optional[str] = None
    ) -> Dict:
        """Get all characters with pagination and privacy filtering
        
        Args:
            skip: Number of records to skip
            limit: Max records to return
            user_id: Filter by specific user (optional)
            current_user_id: Current authenticated user (for privacy filtering)
        """
        try:
            collection = get_collection(self.collection_name)
            
            # Build query with privacy logic
            query = {}
            
            if user_id:
                # Specific user requested - show their characters only
                query["user_id"] = user_id
            elif current_user_id:
                # Show: user's own characters + all public characters
                query = {
                    "$or": [
                        {"user_id": current_user_id},  # User's own characters
                        {"is_private": False}  # Public characters
                    ]
                }
            else:
                # No user context - show only public characters
                query["is_private"] = False
            
            # Get total count
            total = collection.count_documents(query)
            
            # Get characters
            cursor = collection.find(query).skip(skip).limit(limit).sort("created_at", -1)
            characters = list(cursor)
            
            # Decrypt and format
            formatted_characters = []
            for char in characters:
                try:
                    formatted_char = self._format_character(char)
                    formatted_characters.append(formatted_char)
                except Exception as e:
                    print(f"⚠️  Error formatting character: {str(e)}")
                    continue
            
            return {
                "characters": formatted_characters,
                "total": total,
                "skip": skip,
                "limit": limit
            }
            
        except Exception as e:
            print(f"❌ Error getting characters: {str(e)}")
            raise ValueError(f"Failed to get characters: {str(e)}")
    
    def get_character_by_id(self, character_id: str) -> Dict:
        """Get a specific character by ID"""
        try:
            collection = get_collection(self.collection_name)
            
            # character_id is NOT encrypted in database, search directly
            character = collection.find_one({"character_id": character_id})
            
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            return self._format_character(character)
            
        except Exception as e:
            print(f"❌ Error getting character: {str(e)}")
            raise ValueError(f"Failed to get character: {str(e)}")
    
    def _format_character(self, char_doc: dict) -> dict:
        """Format character document for response (decrypt Cloudinary fields)"""
        
        # Decrypt Cloudinary fields only
        cloudinary_public_id = encryption_service.decrypt(char_doc["cloudinary_public_id"])
        cloudinary_url = encryption_service.decrypt(char_doc["cloudinary_url"])
        thumbnail_url = encryption_service.decrypt(char_doc["thumbnail_url"]) if char_doc.get("thumbnail_url") else None
        
        return {
            "character_id": char_doc["character_id"],  # Already unencrypted
            "character_name": char_doc["character_name"],
            "gender": char_doc.get("gender", "undefined"),
            "voice_description": char_doc.get("voice_description", ""),
            "keywords": char_doc["keywords"],
            "is_private": char_doc.get("is_private", False),
            "can_speak": char_doc.get("can_speak", False),  # Speech capability
            "cloudinary_url": cloudinary_url,  # Decrypted
            "cloudinary_public_id": cloudinary_public_id,  # Decrypted
            "thumbnail_url": thumbnail_url,  # Decrypted
            "user_id": char_doc.get("user_id"),
            "created_at": char_doc["created_at"].isoformat(),
            "updated_at": char_doc["updated_at"].isoformat()
        }


# Global instance
character_service = CharacterService()
