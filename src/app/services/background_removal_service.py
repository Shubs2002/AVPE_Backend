"""
Background Removal Service

This module provides background removal functionality for character images.
"""

from rembg import remove
from PIL import Image
from io import BytesIO
from typing import Optional


def remove_background(image_data: bytes) -> bytes:
    """
    Remove background from an image
    
    Args:
        image_data: Image data as bytes
    
    Returns:
        bytes: Image with background removed (PNG with transparency)
    """
    try:
        print("🎨 Removing background from image...")
        
        # Load image
        input_image = Image.open(BytesIO(image_data))
        
        # Remove background
        output_image = remove(input_image)
        
        # Convert to bytes
        output_buffer = BytesIO()
        output_image.save(output_buffer, format="PNG")
        output_bytes = output_buffer.getvalue()
        
        print(f"✅ Background removed successfully")
        
        return output_bytes
    
    except Exception as e:
        error_msg = f"Failed to remove background: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)


def remove_background_from_file(input_path: str, output_path: str) -> bool:
    """
    Remove background from an image file
    
    Args:
        input_path: Path to input image
        output_path: Path to save output image
    
    Returns:
        bool: Success status
    """
    try:
        print(f"🎨 Removing background from: {input_path}")
        
        # Read input image
        with open(input_path, 'rb') as f:
            input_data = f.read()
        
        # Remove background
        output_data = remove_background(input_data)
        
        # Save output image
        with open(output_path, 'wb') as f:
            f.write(output_data)
        
        print(f"✅ Background removed and saved to: {output_path}")
        return True
    
    except Exception as e:
        print(f"❌ Failed to remove background: {str(e)}")
        return False
