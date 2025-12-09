"""
Cloudinary Service for Character Image Storage

Handles uploading, managing, and deleting character images in Cloudinary.
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
import uuid
from typing import Optional, Dict
import base64
from io import BytesIO
from PIL import Image


class CloudinaryService:
    """Service for managing character images in Cloudinary"""
    
    def __init__(self):
        """Initialize Cloudinary with credentials from environment"""
        cloudinary.config(
            cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
            api_key=os.getenv("CLOUDINARY_API_KEY"),
            api_secret=os.getenv("CLOUDINARY_API_SECRET"),
            secure=True
        )
        
        # Verify configuration
        if not all([
            os.getenv("CLOUDINARY_CLOUD_NAME"),
            os.getenv("CLOUDINARY_API_KEY"),
            os.getenv("CLOUDINARY_API_SECRET")
        ]):
            print("⚠️  WARNING: Cloudinary credentials not fully configured!")
            print("⚠️  Set CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET in .env")
    
    def upload_character_image(
        self,
        image_data: str,
        character_name: str,
        folder: str = "characters"
    ) -> Dict:
        """
        Upload character image to Cloudinary
        
        Args:
            image_data: Base64 encoded image data (without data URI prefix)
            character_name: Name of the character (used in public_id)
            folder: Cloudinary folder (default: "characters")
            
        Returns:
            dict: Upload result with url, public_id, etc.
        """
        try:
            # Generate unique public_id
            unique_id = str(uuid.uuid4())[:8]
            safe_name = character_name.replace(" ", "_").lower()
            public_id = f"{folder}/character_{safe_name}_{unique_id}"
            
            # Format base64 data as data URI for Cloudinary
            # Cloudinary expects: "data:image/png;base64,iVBORw0KGgo..."
            if not image_data.startswith("data:"):
                # Detect image format from base64 header
                if image_data.startswith("/9j/"):
                    image_format = "jpeg"
                elif image_data.startswith("iVBORw0"):
                    image_format = "png"
                elif image_data.startswith("R0lGOD"):
                    image_format = "gif"
                elif image_data.startswith("UklGR"):
                    image_format = "webp"
                else:
                    image_format = "png"  # Default to PNG
                
                image_data = f"data:image/{image_format};base64,{image_data}"
            
            # Upload with transformations
            result = cloudinary.uploader.upload(
                image_data,
                folder=folder,
                public_id=public_id,
                transformation=[
                    {
                        "width": 1024,
                        "height": 1024,
                        "crop": "limit",
                        "quality": "auto:good"
                    }
                ],
                eager=[
                    {
                        "width": 256,
                        "height": 256,
                        "crop": "fill",
                        "gravity": "auto",
                        "quality": "auto:good"
                    }
                ],
                eager_async=False,
                resource_type="image"
            )
            
            # Get thumbnail URL
            thumbnail_url = None
            if result.get('eager'):
                thumbnail_url = result['eager'][0].get('secure_url')
            
            cloudinary_public_id = result.get("public_id")
            print(f"☁️  Uploaded to Cloudinary: {character_name}")
            
            return {
                "success": True,
                "url": result.get("secure_url"),
                "public_id": cloudinary_public_id,
                "thumbnail_url": thumbnail_url,
                "width": result.get("width"),
                "height": result.get("height"),
                "format": result.get("format"),
                "resource_type": result.get("resource_type"),
                "created_at": result.get("created_at")
            }
            
        except Exception as e:
            print(f"❌ Cloudinary upload error: {str(e)}")
            raise ValueError(f"Failed to upload image to Cloudinary: {str(e)}")
    
    def delete_character_image(self, public_id: str) -> Dict:
        """
        Delete character image from Cloudinary
        
        Args:
            public_id: Cloudinary public_id of the image
            
        Returns:
            dict: Deletion result
        """
        try:
            print(f"🗑️  Deleting image from Cloudinary: {public_id}")
            
            result = cloudinary.uploader.destroy(
                public_id,
                resource_type="image"
            )
            
            if result.get("result") == "ok":
                print(f"✅ Image deleted successfully!")
                return {"success": True, "message": "Image deleted"}
            else:
                print(f"⚠️  Image deletion result: {result.get('result')}")
                return {"success": False, "message": result.get("result")}
                
        except Exception as e:
            print(f"❌ Cloudinary deletion error: {str(e)}")
            raise ValueError(f"Failed to delete image from Cloudinary: {str(e)}")
    
    def get_image_url(self, public_id: str, transformation: Optional[Dict] = None) -> str:
        """
        Get Cloudinary URL for an image with optional transformation
        
        Args:
            public_id: Cloudinary public_id
            transformation: Optional transformation parameters
            
        Returns:
            str: Cloudinary URL
        """
        try:
            if transformation:
                url, _ = cloudinary.utils.cloudinary_url(
                    public_id,
                    transformation=transformation,
                    secure=True
                )
            else:
                url, _ = cloudinary.utils.cloudinary_url(
                    public_id,
                    secure=True
                )
            
            return url
            
        except Exception as e:
            print(f"❌ Error generating Cloudinary URL: {str(e)}")
            return ""
    
    def update_character_image(
        self,
        old_public_id: str,
        new_image_data: str,
        character_name: str,
        folder: str = "characters"
    ) -> Dict:
        """
        Update character image (delete old, upload new)
        
        Args:
            old_public_id: Public ID of old image to delete
            new_image_data: New image data to upload
            character_name: Character name
            folder: Cloudinary folder
            
        Returns:
            dict: Upload result for new image
        """
        try:
            # Delete old image
            if old_public_id:
                print(f"🗑️  Deleting old image: {old_public_id}")
                self.delete_character_image(old_public_id)
            
            # Upload new image
            return self.upload_character_image(new_image_data, character_name, folder)
            
        except Exception as e:
            print(f"❌ Error updating character image: {str(e)}")
            raise ValueError(f"Failed to update character image: {str(e)}")


# Global instance
cloudinary_service = CloudinaryService()


if __name__ == "__main__":
    print("☁️  Cloudinary Service initialized")
    print(f"📁 Cloud Name: {os.getenv('CLOUDINARY_CLOUD_NAME', 'Not set')}")
    print(f"🔑 API Key: {'Set' if os.getenv('CLOUDINARY_API_KEY') else 'Not set'}")
    print(f"🔐 API Secret: {'Set' if os.getenv('CLOUDINARY_API_SECRET') else 'Not set'}")
