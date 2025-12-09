"""
Imagen Service (Nano Banana Model)

This module provides image generation using Google's Imagen model.
"""

import os
from PIL import Image
from io import BytesIO
from typing import Optional
from google.genai import types
from app.connectors.genai_connector import get_genai_client


def generate_first_frame_with_imagen(
    character_image_url: str = None,
    frame_description: str = None,
    aspect_ratio: str = "9:16",
    output_dir: str = "frames",
    additional_reference_images: list = None,
    image_model: str = "gemini-2.5-flash-image",
    character_image_urls: list = None  # NEW: Support multiple character URLs
) -> tuple[Image.Image, str]:
    """
    Generate the first frame using Imagen (nano banana model).
    Downloads the generated frame to the frames folder.
    
    Args:
        character_image_url: URL of the character image (single character - deprecated, use character_image_urls)
        frame_description: Description of the scene, pose, environment
        aspect_ratio: Aspect ratio for the generated frame (default: "9:16")
        output_dir: Directory to save the frame (default: "frames")
        additional_reference_images: Optional list of additional reference image data (bytes or PIL Images)
        image_model: Image generation model to use
        character_image_urls: List of character image URLs (for multi-character support)
    
    Returns:
        tuple: (PIL.Image, filepath) - Generated image and path where it was saved
    """
    import requests
    from datetime import datetime
    
    print(f"🎨 Generating first frame with Imagen (nano banana)...")
    print(f"📝 Description: {frame_description[:100]}...")
    
    # Create frames directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Handle both old (single URL) and new (multiple URLs) formats
    urls_to_download = []
    if character_image_urls:
        # New format: list of URLs
        urls_to_download = character_image_urls if isinstance(character_image_urls, list) else [character_image_urls]
        print(f"👥 Loading {len(urls_to_download)} character image(s)...")
    elif character_image_url:
        # Old format: single URL (backward compatibility)
        urls_to_download = [character_image_url]
        print(f"👤 Loading 1 character image...")
    else:
        raise ValueError("Either character_image_url or character_image_urls must be provided")
    
    # Download all character images
    character_images = []
    for idx, url in enumerate(urls_to_download, 1):
        if url.startswith("http://") or url.startswith("https://"):
            print(f"📥 Downloading character {idx}/{len(urls_to_download)} from: {url[:50]}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            character_images.append(img)
            print(f"✅ Character {idx} loaded: {img.size}")
        else:
            raise ValueError(f"Unsupported URL format: {url}")
    
    # Map aspect ratio to dimensions
    aspect_ratio_dimensions = {
        "9:16": (720, 1280),   # Vertical (Instagram/TikTok)
        "16:9": (1280, 720),   # Horizontal (YouTube)
        "1:1": (1024, 1024),   # Square (Instagram)
        "4:5": (1024, 1280),   # Vertical (Instagram)
    }
    
    target_size = aspect_ratio_dimensions.get(aspect_ratio, (720, 1280))
    
    # Build prompt for Imagen with proper character reference handling
    num_chars = len(character_images)
    char_refs_text = "characters" if num_chars > 1 else "character"
    
    prompt = f"""Create a high-quality image.

Scene: {frame_description}

⚠️ CRITICAL CHARACTER CONSISTENCY RULE:
Use the reference image(s) EXACTLY as provided. DO NOT change, modify, or reinterpret the {char_refs_text}:
- Keep the EXACT same species/type (if it's a fluffy creature, keep it fluffy; if it's a robot, keep it a robot)
- Keep the EXACT same colors, patterns, and markings
- Keep the EXACT same body shape, size, and proportions
- Keep the EXACT same facial features and expressions style
- Keep the EXACT same clothing, accessories, or distinctive features
- DO NOT make the character more realistic, cartoonish, or change its art style
- DO NOT add or remove any features from the character

Style: Maintain the exact appearance of ALL {char_refs_text} from the reference image(s). Focus on the pose, environment, and background described. Keep each character's colors, features, and style consistent.

Requirements:
- High quality, detailed rendering
- ZERO changes to character appearance - use reference images AS-IS
- Each character should be clearly visible and distinct
- Clear, vibrant colors
- Professional composition"""
    
    print(f"🎨 Generating frame with Imagen...")
    print(f"📐 Aspect ratio: {aspect_ratio}")
    print(f"👥 Using {num_chars} character reference(s)")
    
    try:
        # Get Gemini client
        client = get_genai_client()
        
        # Prepare contents with ALL character images first, then additional references
        contents = [prompt] + character_images
        
        # Add additional reference images if provided
        if additional_reference_images:
            print(f"🖼️ Adding {len(additional_reference_images)} additional reference images...")
            for idx, ref_img_data in enumerate(additional_reference_images):
                try:
                    # Convert bytes to PIL Image if needed
                    if isinstance(ref_img_data, bytes):
                        ref_img = Image.open(BytesIO(ref_img_data))
                    elif isinstance(ref_img_data, Image.Image):
                        ref_img = ref_img_data
                    else:
                        print(f"⚠️ Skipping reference image {idx+1}: unsupported type")
                        continue
                    
                    contents.append(ref_img)
                    print(f"✅ Reference image {idx+1} added: {ref_img.size}")
                except Exception as e:
                    print(f"⚠️ Failed to add reference image {idx+1}: {str(e)}")
        
        # Use specified image generation model
        total_refs = len(character_images) + (len(additional_reference_images) if additional_reference_images else 0)
        print(f"🎨 Generating image with {image_model} ({total_refs} reference images)...")
        
        response = client.models.generate_content(
            model=image_model,
            contents=contents,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )
            )
        )
        
        # Extract generated image from response
        generated_image = None
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(f"📋 AI Response: {part.text[:100]}...")
            elif part.inline_data is not None:
                # Found the generated image
                generated_image = Image.open(BytesIO(part.inline_data.data))
                print(f"✅ Image generated by Gemini: {generated_image.size}")
                break
        
        if generated_image is None:
            # No image generated, use character image as fallback
            print(f"⚠️ No image generated in response, using character image as fallback")
            generated_image = _resize_to_aspect_ratio(character_image, aspect_ratio, target_size)
        
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
        print(f"⚠️ Frame generation failed: {str(e)}")
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


def generate_last_frame_with_imagen(
    character_image_url: str = None,
    first_frame_path: str = None,
    last_frame_description: str = None,
    aspect_ratio: str = "9:16",
    output_dir: str = "frames",
    additional_reference_images: list = None,
    image_model: str = "gemini-2.5-flash-image",
    character_image_urls: list = None  # NEW: Support multiple character URLs
) -> tuple[Image.Image, str]:
    """
    Generate the last frame using Imagen with BOTH character reference and first frame reference.
    This ensures character consistency AND environment/lighting consistency.
    
    Args:
        character_image_url: URL of the character image (single character - deprecated, use character_image_urls)
        first_frame_path: Path to the first frame of this segment (for environment consistency)
        last_frame_description: Description of the ending pose, position, environment
        aspect_ratio: Aspect ratio for the generated frame (default: "9:16")
        output_dir: Directory to save the frame (default: "frames")
        additional_reference_images: Optional list of additional reference image data (bytes or PIL Images)
        image_model: Image generation model to use
        character_image_urls: List of character image URLs (for multi-character support)
    
    Returns:
        tuple: (PIL.Image, filepath) - Generated image and path where it was saved
    """
    import requests
    from datetime import datetime
    
    print(f"🎨 Generating last frame with Imagen (nano banana)...")
    print(f"📝 Description: {last_frame_description[:100]}...")
    
    # Create frames directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Handle both old (single URL) and new (multiple URLs) formats
    urls_to_download = []
    if character_image_urls:
        # New format: list of URLs
        urls_to_download = character_image_urls if isinstance(character_image_urls, list) else [character_image_urls]
        print(f"👥 Loading {len(urls_to_download)} character image(s)...")
    elif character_image_url:
        # Old format: single URL (backward compatibility)
        urls_to_download = [character_image_url]
        print(f"👤 Loading 1 character image...")
    else:
        raise ValueError("Either character_image_url or character_image_urls must be provided")
    
    # Download all character images
    character_images = []
    for idx, url in enumerate(urls_to_download, 1):
        if url.startswith("http://") or url.startswith("https://"):
            print(f"📥 Downloading character {idx}/{len(urls_to_download)} from: {url[:50]}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            character_images.append(img)
            print(f"✅ Character {idx} loaded: {img.size}")
        else:
            raise ValueError(f"Unsupported URL format: {url}")
    
    # Use first character as primary
    character_image = character_images[0]
    
    # Load first frame
    first_frame_image = Image.open(first_frame_path)
    print(f"✅ First frame loaded: {first_frame_image.size}")
    
    # Map aspect ratio to dimensions
    aspect_ratio_dimensions = {
        "9:16": (720, 1280),   # Vertical (Instagram/TikTok)
        "16:9": (1280, 720),   # Horizontal (YouTube)
        "1:1": (1024, 1024),   # Square (Instagram)
        "4:5": (1024, 1280),   # Vertical (Instagram)
    }
    
    target_size = aspect_ratio_dimensions.get(aspect_ratio, (720, 1280))
    
    # Build prompt for Imagen with ALL character references
    num_chars = len(character_images)
    char_refs_text = "character references" if num_chars > 1 else "character reference"
    
    prompt = f"""Create a high-quality image.

Scene: {last_frame_description}

⚠️ CRITICAL CHARACTER CONSISTENCY RULE:
Use the FIRST {num_chars} reference image(s) EXACTLY as provided. DO NOT change, modify, or reinterpret ANY character:
- Keep the EXACT same species/type for each character (if it's a fluffy creature, keep it fluffy; if it's a robot, keep it a robot)
- Keep the EXACT same colors, patterns, and markings for each character
- Keep the EXACT same body shape, size, and proportions for each character
- Keep the EXACT same facial features and expressions style for each character
- Keep the EXACT same clothing, accessories, or distinctive features for each character
- DO NOT make any character more realistic, cartoonish, or change its art style
- DO NOT add or remove any features from any character
- Each character must remain COMPLETELY IDENTICAL to their reference image

CRITICAL REQUIREMENTS:
1. Character Appearance: Use the FIRST {num_chars} reference image(s) ({char_refs_text}) AS-IS with ZERO modifications
2. Environment & Lighting: Use the NEXT reference image (first frame) to maintain consistent environment, lighting, and background
3. Pose & Position: Follow the scene description for the character's final pose and position

ALL characters should look EXACTLY like in their respective character reference images, but in the environment and lighting from the first frame reference image, with the poses described in the scene.

Style: High quality, detailed rendering with consistent characters and environment.

Requirements:
- ALL characters MUST be fully visible (whole body in frame)
- ZERO changes to any character's appearance - use reference images AS-IS
- Maintain environment/lighting from first frame reference
- Clear, vibrant colors
- Professional composition"""
    
    print(f"🎨 Generating last frame with Imagen...")
    print(f"📐 Aspect ratio: {aspect_ratio}")
    print(f"🖼️ Using {num_chars} character reference(s) + first frame reference")
    
    try:
        # Get Gemini client
        client = get_genai_client()
        
        # Prepare contents with ALL character images, first frame, and additional references
        contents = [prompt] + character_images + [first_frame_image]
        
        # Add additional reference images if provided
        if additional_reference_images:
            print(f"🖼️ Adding {len(additional_reference_images)} additional reference images...")
            for idx, ref_img_data in enumerate(additional_reference_images):
                try:
                    # Convert bytes to PIL Image if needed
                    if isinstance(ref_img_data, bytes):
                        ref_img = Image.open(BytesIO(ref_img_data))
                    elif isinstance(ref_img_data, Image.Image):
                        ref_img = ref_img_data
                    else:
                        print(f"⚠️ Skipping reference image {idx+1}: unsupported type")
                        continue
                    
                    contents.append(ref_img)
                    print(f"✅ Reference image {idx+1} added: {ref_img.size}")
                except Exception as e:
                    print(f"⚠️ Failed to add reference image {idx+1}: {str(e)}")
        
        # Use specified image generation model with ALL references
        total_refs = len(character_images) + 1 + (len(additional_reference_images) if additional_reference_images else 0)
        print(f"🎨 Generating image with {image_model} ({total_refs} reference images)...")
        
        response = client.models.generate_content(
            model=image_model,
            contents=contents,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )
            )
        )
        
        # Extract generated image from response
        generated_image = None
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(f"📋 AI Response: {part.text[:100]}...")
            elif part.inline_data is not None:
                # Found the generated image
                generated_image = Image.open(BytesIO(part.inline_data.data))
                print(f"✅ Image generated by Gemini: {generated_image.size}")
                break
        
        if generated_image is None:
            # No image generated, use first frame as fallback
            print(f"⚠️ No image generated in response, using first frame as fallback")
            generated_image = _resize_to_aspect_ratio(first_frame_image, aspect_ratio, target_size)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"last_frame_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        # Save the frame
        generated_image.save(filepath, "PNG")
        print(f"💾 Last frame saved: {filepath}")
        print(f"📊 Size: {generated_image.size}")
        
        return generated_image, filepath
    
    except Exception as e:
        print(f"⚠️ Last frame generation failed: {str(e)}")
        print(f"⚠️ Using first frame as fallback")
        
        # Fallback: Use first frame
        fallback_image = _resize_to_aspect_ratio(first_frame_image, aspect_ratio, target_size)
        
        # Save fallback frame
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"last_frame_fallback_{timestamp}.png"
        filepath = os.path.join(output_dir, filename)
        
        fallback_image.save(filepath, "PNG")
        print(f"💾 Fallback frame saved: {filepath}")
        
        return fallback_image, filepath


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
        
        # Generate image with Gemini 2.5 Flash Image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=contents,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    image_size="4K"
                )
            )
        )
        
        # Extract image
        generated_image = None
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(f"📋 AI Response: {part.text[:100]}...")
            elif part.inline_data is not None:
                generated_image = Image.open(BytesIO(part.inline_data.data))
                print(f"✅ Image generated: {generated_image.size}")
                break
        
        if generated_image is None:
            raise ValueError("No image generated in response")
        
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
