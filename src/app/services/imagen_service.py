"""
Imagen Service (Nano Banana Model)

This module provides image generation using Google's Imagen model.
"""

import os
from PIL import Image
from io import BytesIO
from typing import Optional
from app.connectors.genai_connector import get_genai_client


def generate_first_frame_with_imagen(
    character_image_url: str,
    frame_description: str,
    aspect_ratio: str = "9:16",
    output_dir: str = "frames"
) -> tuple[Image.Image, str]:
    """
    Generate the first frame using Imagen (nano banana model).
    Downloads the generated frame to the frames folder.
    
    Args:
        character_image_url: URL of the character image
        frame_description: Description of the scene, pose, environment
        aspect_ratio: Aspect ratio for the generated frame (default: "9:16")
        output_dir: Directory to save the frame (default: "frames")
    
    Returns:
        tuple: (PIL.Image, filepath) - Generated image and path where it was saved
    """
    import requests
    from datetime import datetime
    
    print(f"🎨 Generating first frame with Imagen (nano banana)...")
    print(f"📝 Description: {frame_description[:100]}...")
    
    # Create frames directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Download character image if it's a URL
    character_image = None
    if character_image_url.startswith("http://") or character_image_url.startswith("https://"):
        print(f"📥 Downloading character image from: {character_image_url[:50]}...")
        response = requests.get(character_image_url, timeout=30)
        response.raise_for_status()
        character_image = Image.open(BytesIO(response.content))
        print(f"✅ Character image loaded: {character_image.size}")
    else:
        raise ValueError(f"Unsupported character_image_url format: {character_image_url}")
    
    # Map aspect ratio to dimensions
    aspect_ratio_dimensions = {
        "9:16": (720, 1280),   # Vertical (Instagram/TikTok)
        "16:9": (1280, 720),   # Horizontal (YouTube)
        "1:1": (1024, 1024),   # Square (Instagram)
        "4:5": (1024, 1280),   # Vertical (Instagram)
    }
    
    target_size = aspect_ratio_dimensions.get(aspect_ratio, (720, 1280))
    
    # Build prompt for Imagen
    prompt = f"""Create a high-quality image in {aspect_ratio} aspect ratio ({target_size[0]}x{target_size[1]} pixels).

Scene: {frame_description}

Style: Maintain the character's exact appearance from the reference image. Focus on the pose, environment, and background described. Keep the character's colors, features, and style consistent.

Requirements:
- Aspect ratio: {aspect_ratio}
- High quality, detailed rendering
- Consistent character appearance
- Clear, vibrant colors
- Professional composition"""
    
    print(f"🎨 Generating frame with Imagen...")
    print(f"📐 Target size: {target_size[0]}x{target_size[1]} ({aspect_ratio})")
    
    try:
        # Get Gemini client (Imagen uses same client)
        client = get_genai_client()
        
        # Generate image with Imagen
        # Note: Using Gemini's image generation capability (nano banana)
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",  # Supports image generation
            contents=[prompt, character_image]
        )
        
        # Extract generated image from response
        generated_image = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                # Found the generated image
                generated_image = Image.open(BytesIO(part.inline_data.data))
                print(f"✅ Image generated: {generated_image.size}")
                break
        
        if generated_image is None:
            # Fallback: Use character image with proper aspect ratio
            print(f"⚠️ No image generated, using character image as fallback")
            generated_image = _resize_to_aspect_ratio(character_image, aspect_ratio, target_size)
        
        # Ensure correct size
        if generated_image.size != target_size:
            print(f"📐 Resizing from {generated_image.size} to {target_size}")
            generated_image = generated_image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"first_frame_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        # Save the frame
        generated_image.save(filepath, "PNG")
        print(f"💾 First frame saved: {filepath}")
        print(f"📊 Size: {generated_image.size}")
        
        return generated_image, filepath
    
    except Exception as e:
        print(f"⚠️ Imagen generation failed: {str(e)}")
        print(f"⚠️ Using character image as fallback")
        
        # Fallback: Use character image with proper aspect ratio
        fallback_image = _resize_to_aspect_ratio(character_image, aspect_ratio, target_size)
        
        # Save fallback frame
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"first_frame_fallback_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        fallback_image.save(filepath, "PNG")
        print(f"💾 Fallback frame saved: {filepath}")
        
        return fallback_image, filepath


def _resize_to_aspect_ratio(
    image: Image.Image,
    aspect_ratio: str,
    target_size: Optional[tuple] = None
) -> Image.Image:
    """
    Resize an image to match the specified aspect ratio.
    
    Args:
        image: PIL Image to resize
        aspect_ratio: Target aspect ratio (e.g., "9:16", "16:9", "1:1")
        target_size: Optional target size (width, height)
    
    Returns:
        PIL.Image: Resized image
    """
    # Parse aspect ratio
    try:
        width_ratio, height_ratio = map(int, aspect_ratio.split(':'))
    except:
        print(f"⚠️ Invalid aspect ratio '{aspect_ratio}', using original image")
        return image
    
    # Calculate target dimensions
    original_width, original_height = image.size
    target_aspect = width_ratio / height_ratio
    current_aspect = original_width / original_height
    
    if abs(target_aspect - current_aspect) < 0.01 and target_size is None:
        # Already correct aspect ratio
        return image
    
    # Determine new dimensions (maintain quality, crop if needed)
    if current_aspect > target_aspect:
        # Image is too wide, crop width
        new_height = original_height
        new_width = int(new_height * target_aspect)
    else:
        # Image is too tall, crop height
        new_width = original_width
        new_height = int(new_width / target_aspect)
    
    # Center crop
    left = (original_width - new_width) // 2
    top = (original_height - new_height) // 2
    right = left + new_width
    bottom = top + new_height
    
    cropped_image = image.crop((left, top, right, bottom))
    
    # Resize to target size if specified
    if target_size:
        cropped_image = cropped_image.resize(target_size, Image.Resampling.LANCZOS)
    
    print(f"✅ Resized from {image.size} to {cropped_image.size} ({aspect_ratio})")
    
    return cropped_image


def generate_frame_from_description(
    description: str,
    aspect_ratio: str = "9:16",
    output_dir: str = "frames",
    reference_image: Optional[Image.Image] = None
) -> tuple[Image.Image, str]:
    """
    Generate a frame from text description only (no character reference).
    
    Args:
        description: Scene description
        aspect_ratio: Aspect ratio (default: "9:16")
        output_dir: Directory to save the frame
        reference_image: Optional reference image for style
    
    Returns:
        tuple: (PIL.Image, filepath)
    """
    from datetime import datetime
    
    print(f"🎨 Generating frame from description...")
    print(f"📝 Description: {description[:100]}...")
    
    # Create frames directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Map aspect ratio to dimensions
    aspect_ratio_dimensions = {
        "9:16": (720, 1280),
        "16:9": (1280, 720),
        "1:1": (1024, 1024),
        "4:5": (1024, 1280),
    }
    
    target_size = aspect_ratio_dimensions.get(aspect_ratio, (720, 1280))
    
    # Build prompt
    prompt = f"""Create a high-quality image in {aspect_ratio} aspect ratio ({target_size[0]}x{target_size[1]} pixels).

{description}

Requirements:
- Aspect ratio: {aspect_ratio}
- High quality, detailed rendering
- Clear, vibrant colors
- Professional composition"""
    
    try:
        client = get_genai_client()
        
        # Prepare contents
        contents = [prompt]
        if reference_image:
            contents.append(reference_image)
        
        # Generate image
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=contents
        )
        
        # Extract image
        generated_image = None
        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                generated_image = Image.open(BytesIO(part.inline_data.data))
                break
        
        if generated_image is None:
            raise ValueError("No image generated")
        
        # Resize to target size
        if generated_image.size != target_size:
            generated_image = generated_image.resize(target_size, Image.Resampling.LANCZOS)
        
        # Save
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"frame_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        generated_image.save(filepath, "PNG")
        print(f"💾 Frame saved: {filepath}")
        
        return generated_image, filepath
    
    except Exception as e:
        print(f"❌ Frame generation failed: {str(e)}")
        raise
