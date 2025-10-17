"""
Cloudinary Service

This module provides image upload and management functionality using Cloudinary.
"""

import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional, Dict, Any
from PIL import Image
from io import BytesIO
from app.config.settings import settings


def initialize_cloudinary():
    """Initialize Cloudinary configuration"""
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True
    )
    print("✅ Cloudinary initialized")


def upload_image_to_cloudinary(
    image_data: bytes,
    folder: str = "characters",
    public_id: Optional[str] = None,
    tags: Optional[list] = None
) -> Dict[str, Any]:
    """
    Upload an image to Cloudinary
    
    Args:
        image_data: Image data as bytes
        folder: Cloudinary folder to store the image
        public_id: Optional custom public ID for the image
        tags: Optional list of tags for the image
    
    Returns:
        dict: Upload result with URL and metadata
    """
    try:
        # Initialize Cloudinary if not already done
        initialize_cloudinary()
        
        # Prepare upload options
        upload_options = {
            "folder": folder,
            "resource_type": "image",
            "format": "png",
            "quality": "auto:best"
        }
        
        if public_id:
            upload_options["public_id"] = public_id
        
        if tags:
            upload_options["tags"] = tags
        
        # Upload to Cloudinary
        print(f"📤 Uploading image to Cloudinary folder: {folder}")
        result = cloudinary.uploader.upload(image_data, **upload_options)
        
        print(f"✅ Image uploaded successfully: {result['secure_url']}")
        
        return {
            "success": True,
            "url": result["secure_url"],
            "public_id": result["public_id"],
            "width": result["width"],
            "height": result["height"],
            "format": result["format"],
            "resource_type": result["resource_type"],
            "created_at": result["created_at"]
        }
    
    except Exception as e:
        error_msg = f"Failed to upload image to Cloudinary: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }


def delete_image_from_cloudinary(public_id: str) -> Dict[str, Any]:
    """
    Delete an image from Cloudinary
    
    Args:
        public_id: Cloudinary public ID of the image
    
    Returns:
        dict: Delete result
    """
    try:
        initialize_cloudinary()
        
        result = cloudinary.uploader.destroy(public_id)
        
        if result.get("result") == "ok":
            print(f"✅ Image deleted from Cloudinary: {public_id}")
            return {
                "success": True,
                "message": f"Image deleted: {public_id}"
            }
        else:
            return {
                "success": False,
                "error": f"Failed to delete image: {result}"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Failed to delete image: {str(e)}"
        }


def get_cloudinary_url(public_id: str, transformations: Optional[Dict] = None) -> str:
    """
    Get Cloudinary URL for an image with optional transformations
    
    Args:
        public_id: Cloudinary public ID
        transformations: Optional transformations (width, height, crop, etc.)
    
    Returns:
        str: Cloudinary URL
    """
    try:
        initialize_cloudinary()
        
        if transformations:
            url = cloudinary.CloudinaryImage(public_id).build_url(**transformations)
        else:
            url = cloudinary.CloudinaryImage(public_id).build_url()
        
        return url
    
    except Exception as e:
        print(f"❌ Failed to generate Cloudinary URL: {str(e)}")
        return ""
