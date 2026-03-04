"""
Image Editing Service using Gemini Nano Banana Pro

Provides bulk image editing and generation capabilities with iterative processing
for free tier compatibility.
"""

import os
import time
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime
from PIL import Image
from io import BytesIO
import base64

from google import genai
from google.genai import types
from app.config.settings import settings


def get_genai_client():
    """Get configured GenAI client"""
    api_key = settings.GOOGLE_STUDIO_API_KEY
    if not api_key:
        raise ValueError("GOOGLE_STUDIO_API_KEY environment variable not set")
    return genai.Client(api_key=api_key)


class ImageEditService:
    """
    Service for editing and generating images using Gemini's image generation.
    Supports iterative processing for bulk operations on free tier.
    """
    
    def __init__(self, model: str = "gemini-2.5-flash-image"):
        """
        Initialize the image edit service.
        
        Args:
            model: Gemini model to use for image generation
        """
        self.model = model
        self.client = get_genai_client()
    
    def generate_single_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        use_google_search: bool = False,
        output_path: Optional[str] = None
    ) -> Tuple[Optional[Image.Image], Optional[str], Optional[str]]:
        """
        Generate a single image from a text prompt.
        
        Args:
            prompt: Text description of the image to generate
            aspect_ratio: Image aspect ratio (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)
            resolution: Image resolution (1K, 2K, 4K)
            use_google_search: Enable Google Search tool for current information
            output_path: Optional path to save the image
            
        Returns:
            Tuple of (PIL Image, saved file path, text response)
        """
        print(f"🎨 Generating image with prompt: {prompt[:100]}...")
        
        # Build config
        config_params = {
            'response_modalities': ['TEXT', 'IMAGE'],
            'image_config': types.ImageConfig(
                aspect_ratio=aspect_ratio,
                image_size=resolution
            )
        }
        
        if use_google_search:
            config_params['tools'] = [{"google_search": {}}]
        
        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=types.GenerateContentConfig(**config_params)
            )
            
            generated_image = None
            text_response = None
            saved_path = None
            
            # Extract image and text from response
            for part in response.candidates[0].content.parts:
                if part.text is not None:
                    text_response = part.text
                    print(f"📝 Text response: {text_response[:200]}...")
                elif part.inline_data is not None:
                    # Extract image from inline_data
                    generated_image = Image.open(BytesIO(part.inline_data.data))
                    print(f"✅ Image generated: {generated_image.size}")
                    
                    # Save image if output path provided
                    if output_path:
                        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
                        generated_image.save(output_path, "PNG")
                        saved_path = output_path
                        print(f"✅ Image saved to: {output_path}")
                    else:
                        # Auto-generate filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        auto_path = f"generated_images/image_{timestamp}.png"
                        os.makedirs("generated_images", exist_ok=True)
                        generated_image.save(auto_path, "PNG")
                        saved_path = auto_path
                        print(f"✅ Image saved to: {auto_path}")
            
            return generated_image, saved_path, text_response
            
        except Exception as e:
            print(f"❌ Image generation failed: {str(e)}")
            raise
    
    def generate_bulk_images(
        self,
        prompts: List[str],
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        use_google_search: bool = False,
        output_dir: str = "generated_images",
        delay_between_requests: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple images iteratively (free tier friendly).
        
        Args:
            prompts: List of text prompts for image generation
            aspect_ratio: Image aspect ratio
            resolution: Image resolution
            use_google_search: Enable Google Search tool
            output_dir: Directory to save generated images
            delay_between_requests: Delay in seconds between requests (for rate limiting)
            
        Returns:
            List of results with image paths, text responses, and status
        """
        print(f"🎨 Starting bulk image generation: {len(prompts)} images")
        print(f"⏱️  Delay between requests: {delay_between_requests}s")
        
        os.makedirs(output_dir, exist_ok=True)
        results = []
        
        for idx, prompt in enumerate(prompts, 1):
            print(f"\n📸 Generating image {idx}/{len(prompts)}...")
            
            result = {
                "index": idx,
                "prompt": prompt,
                "status": "processing",
                "image_path": None,
                "text_response": None,
                "error": None
            }
            
            try:
                # Generate filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(output_dir, f"image_{idx}_{timestamp}.png")
                
                # Generate image
                image, saved_path, text_response = self.generate_single_image(
                    prompt=prompt,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                    use_google_search=use_google_search,
                    output_path=output_path
                )
                
                result["status"] = "completed"
                result["image_path"] = saved_path
                result["text_response"] = text_response
                print(f"✅ Image {idx} completed")
                
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
                print(f"❌ Image {idx} failed: {str(e)}")
            
            results.append(result)
            
            # Delay before next request (except for last one)
            if idx < len(prompts):
                print(f"⏳ Waiting {delay_between_requests}s before next request...")
                time.sleep(delay_between_requests)
        
        # Summary
        success_count = sum(1 for r in results if r["status"] == "completed")
        failed_count = sum(1 for r in results if r["status"] == "failed")
        
        print(f"\n📊 Bulk generation complete:")
        print(f"   ✅ Success: {success_count}/{len(prompts)}")
        print(f"   ❌ Failed: {failed_count}/{len(prompts)}")
        
        return results
    
    def edit_image_with_prompt(
        self,
        image_path: str,
        edit_prompt: str,
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        output_path: Optional[str] = None,
        max_retries: int = 3,
        timeout_seconds: int = 120
    ) -> Tuple[Optional[Image.Image], Optional[str], Optional[str]]:
        """
        Edit an existing image using a text prompt with timeout and retry logic.
        
        Args:
            image_path: Path to the image to edit
            edit_prompt: Text description of the edit to make
            aspect_ratio: Output aspect ratio
            resolution: Output resolution
            output_path: Optional path to save edited image
            max_retries: Maximum number of retry attempts
            timeout_seconds: Timeout for API call in seconds
            
        Returns:
            Tuple of (PIL Image, saved file path, text response)
        """
        print(f"✏️ Editing image: {image_path}")
        print(f"📝 Edit prompt: {edit_prompt[:100]}...")
        
        # Load the image
        try:
            input_image = Image.open(image_path)
            print(f"✅ Image loaded: {input_image.size}")
        except Exception as e:
            print(f"❌ Failed to load image: {str(e)}")
            raise
        
        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait_time = 2 ** attempt  # Exponential backoff: 2, 4, 8 seconds
                    print(f"🔄 Retry attempt {attempt + 1}/{max_retries} after {wait_time}s...")
                    time.sleep(wait_time)
                
                print(f"⏱️  Sending request (attempt {attempt + 1}/{max_retries})...")
                
                # Create chat session for editing (like imagen_chat_service does)
                chat = self.client.chats.create(
                    model=self.model,
                    config=types.GenerateContentConfig(
                        response_modalities=['TEXT', 'IMAGE'],
                        image_config=types.ImageConfig(
                            aspect_ratio=aspect_ratio,
                            image_size=resolution
                        ),
                        tools=[{"google_search": {}}]  # Enable Google Search like imagen_chat_service
                    )
                )
                
                # Send message with image and prompt (like imagen_chat_service does)
                contents = [edit_prompt, input_image]
                response = chat.send_message(contents)
                
                edited_image = None
                text_response = None
                saved_path = None
                
                # Extract edited image and text (like imagen_chat_service does)
                for part in response.parts:
                    if part.text is not None:
                        text_response = part.text
                        print(f"📝 Text response: {text_response[:200]}...")
                    elif image := part.as_image():
                        # Store the image directly like imagen_chat_service does
                        edited_image = image
                        
                        # Debug: check what type of object we got
                        print(f"🔍 Image type: {type(edited_image)}")
                        print(f"🔍 Image attributes: {dir(edited_image)[:10]}")
                        
                        # Try to get size
                        try:
                            img_size = edited_image.size
                            print(f"✅ Image edited: {img_size}")
                        except AttributeError:
                            # If no size attribute, try to convert to PIL Image
                            print(f"⚠️ Converting to PIL Image...")
                            if hasattr(edited_image, '_pil_image'):
                                edited_image = edited_image._pil_image
                            elif hasattr(edited_image, 'data'):
                                edited_image = Image.open(BytesIO(edited_image.data))
                            else:
                                # Last resort: try to save and reload
                                import tempfile
                                with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
                                    edited_image.save(tmp.name)
                                    edited_image = Image.open(tmp.name)
                            print(f"✅ Image converted: {edited_image.size}")
                        
                        # Save edited image
                        if output_path:
                            os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
                            edited_image.save(output_path, "PNG")
                            saved_path = output_path
                            print(f"✅ Edited image saved to: {output_path}")
                        else:
                            # Auto-generate filename
                            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                            auto_path = f"edited_images/edited_{timestamp}.png"
                            os.makedirs("edited_images", exist_ok=True)
                            edited_image.save(auto_path, "PNG")
                            saved_path = auto_path
                            print(f"✅ Edited image saved to: {auto_path}")
                        break
                
                if edited_image is None:
                    raise ValueError("No image generated in response")
                
                return edited_image, saved_path, text_response
                
            except TimeoutError as e:
                print(f"⏱️ Timeout: {str(e)}")
                if attempt == max_retries - 1:
                    raise Exception(f"Request timed out after {max_retries} attempts")
                continue
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if it's a retryable error
                is_retryable = any(keyword in error_str for keyword in [
                    'timeout', 'timed out', 'deadline', 'unavailable',
                    'internal', 'server error', 'code 13', 'code 14',
                    'rate limit', 'quota', '429', '503', '500'
                ])
                
                if is_retryable and attempt < max_retries - 1:
                    print(f"⚠️ Retryable error: {str(e)}")
                    continue
                else:
                    print(f"❌ Image editing failed: {str(e)}")
                    raise
    
    def edit_bulk_images(
        self,
        image_paths: List[str],
        edit_prompts: List[str],
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        output_dir: str = "edited_images",
        delay_between_requests: float = 2.0
    ) -> List[Dict[str, Any]]:
        """
        Edit multiple images iteratively (free tier friendly).
        
        Args:
            image_paths: List of paths to images to edit
            edit_prompts: List of edit prompts (one per image, or single prompt for all)
            aspect_ratio: Output aspect ratio
            resolution: Output resolution
            output_dir: Directory to save edited images
            delay_between_requests: Delay in seconds between requests
            
        Returns:
            List of results with edited image paths, text responses, and status
        """
        print(f"✏️ Starting bulk image editing: {len(image_paths)} images")
        print(f"⏱️  Delay between requests: {delay_between_requests}s")
        
        os.makedirs(output_dir, exist_ok=True)
        
        # If single prompt provided, use it for all images
        if len(edit_prompts) == 1 and len(image_paths) > 1:
            edit_prompts = edit_prompts * len(image_paths)
        
        if len(edit_prompts) != len(image_paths):
            raise ValueError(f"Number of prompts ({len(edit_prompts)}) must match number of images ({len(image_paths)}) or be 1")
        
        results = []
        
        for idx, (image_path, edit_prompt) in enumerate(zip(image_paths, edit_prompts), 1):
            print(f"\n✏️ Editing image {idx}/{len(image_paths)}...")
            
            result = {
                "index": idx,
                "input_image": image_path,
                "edit_prompt": edit_prompt,
                "status": "processing",
                "output_path": None,
                "text_response": None,
                "error": None
            }
            
            try:
                # Generate output filename
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = os.path.join(output_dir, f"edited_{idx}_{timestamp}.png")
                
                # Edit image
                edited_image, saved_path, text_response = self.edit_image_with_prompt(
                    image_path=image_path,
                    edit_prompt=edit_prompt,
                    aspect_ratio=aspect_ratio,
                    resolution=resolution,
                    output_path=output_path
                )
                
                result["status"] = "completed"
                result["output_path"] = saved_path
                result["text_response"] = text_response
                print(f"✅ Image {idx} edited successfully")
                
            except Exception as e:
                result["status"] = "failed"
                result["error"] = str(e)
                print(f"❌ Image {idx} editing failed: {str(e)}")
            
            results.append(result)
            
            # Delay before next request (except for last one)
            if idx < len(image_paths):
                print(f"⏳ Waiting {delay_between_requests}s before next request...")
                time.sleep(delay_between_requests)
        
        # Summary
        success_count = sum(1 for r in results if r["status"] == "completed")
        failed_count = sum(1 for r in results if r["status"] == "failed")
        
        print(f"\n📊 Bulk editing complete:")
        print(f"   ✅ Success: {success_count}/{len(image_paths)}")
        print(f"   ❌ Failed: {failed_count}/{len(image_paths)}")
        
        return results
    
    def batch_style_transfer(
        self,
        image_paths: List[str],
        style_prompt: str,
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        output_dir: str = "styled_images",
        delay_between_requests: float = 2.0,
        variations_per_image: int = 1,
        timeout_per_image: int = 120,
        skip_on_error: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Apply the same style/transformation to multiple images (batch style transfer).
        Perfect for converting 50+ images to the same style efficiently.
        
        Args:
            image_paths: List of paths to images to transform
            style_prompt: Single style prompt to apply to ALL images
                         Example: "Convert to anime style with vibrant colors"
                         Example: "Make it look like a watercolor painting"
                         Example: "Transform into pixel art style"
            aspect_ratio: Output aspect ratio
            resolution: Output resolution
            output_dir: Directory to save styled images
            delay_between_requests: Delay in seconds between requests
            variations_per_image: Number of variations to generate per image (default: 1)
            timeout_per_image: Timeout in seconds for each image processing
            skip_on_error: If True, skip failed images and continue; if False, stop on error
            
        Returns:
            List of results with styled image paths, text responses, and status
            
        Example:
            # Convert 50 images to anime style
            service.batch_style_transfer(
                image_paths=["img1.png", "img2.png", ..., "img50.png"],
                style_prompt="Convert to anime style with vibrant colors and bold outlines",
                variations_per_image=1
            )
        """
        print(f"🎨 Starting batch style transfer: {len(image_paths)} images")
        print(f"🖌️  Style: {style_prompt[:80]}...")
        print(f"🔢 Variations per image: {variations_per_image}")
        print(f"⏱️  Delay between requests: {delay_between_requests}s")
        print(f"⏱️  Timeout per image: {timeout_per_image}s")
        print(f"🔄 Skip on error: {skip_on_error}")
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = []
        total_operations = len(image_paths) * variations_per_image
        operation_count = 0
        
        start_time = time.time()
        
        for img_idx, image_path in enumerate(image_paths, 1):
            elapsed = time.time() - start_time
            avg_time_per_image = elapsed / img_idx if img_idx > 1 else 0
            remaining_images = len(image_paths) - img_idx
            eta_seconds = avg_time_per_image * remaining_images if avg_time_per_image > 0 else 0
            
            print(f"\n🖼️ Processing image {img_idx}/{len(image_paths)}: {os.path.basename(image_path)}")
            print(f"   ⏱️  Elapsed: {elapsed/60:.1f}m | ETA: {eta_seconds/60:.1f}m | Avg: {avg_time_per_image:.1f}s/image")
            
            # Generate variations for this image
            for var_idx in range(variations_per_image):
                operation_count += 1
                
                if variations_per_image > 1:
                    print(f"   Variation {var_idx + 1}/{variations_per_image}...")
                
                result = {
                    "index": img_idx,
                    "variation": var_idx + 1,
                    "input_image": image_path,
                    "style_prompt": style_prompt,
                    "status": "processing",
                    "output_path": None,
                    "text_response": None,
                    "error": None
                }
                
                try:
                    # Generate output filename
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                    base_name = os.path.splitext(os.path.basename(image_path))[0]
                    
                    if variations_per_image > 1:
                        filename = f"{base_name}_styled_v{var_idx + 1}_{timestamp}.png"
                    else:
                        filename = f"{base_name}_styled_{timestamp}.png"
                    
                    output_path = os.path.join(output_dir, filename)
                    
                    # Apply style transformation with timeout
                    styled_image, saved_path, text_response = self.edit_image_with_prompt(
                        image_path=image_path,
                        edit_prompt=style_prompt,
                        aspect_ratio=aspect_ratio,
                        resolution=resolution,
                        output_path=output_path,
                        max_retries=2,
                        timeout_seconds=timeout_per_image
                    )
                    
                    result["status"] = "completed"
                    result["output_path"] = saved_path
                    result["text_response"] = text_response
                    
                    if variations_per_image > 1:
                        print(f"   ✅ Variation {var_idx + 1} completed: {saved_path}")
                    else:
                        print(f"   ✅ Styled image saved: {saved_path}")
                    
                except Exception as e:
                    result["status"] = "failed"
                    result["error"] = str(e)
                    print(f"   ❌ Failed: {str(e)}")
                    
                    if not skip_on_error:
                        print(f"   🛑 Stopping batch processing due to error")
                        results.append(result)
                        return results
                
                results.append(result)
                
                # Delay before next request (except for last one)
                if operation_count < total_operations:
                    print(f"   ⏳ Waiting {delay_between_requests}s...")
                    time.sleep(delay_between_requests)
        
        # Summary
        success_count = sum(1 for r in results if r["status"] == "completed")
        failed_count = sum(1 for r in results if r["status"] == "failed")
        total_time = time.time() - start_time
        
        print(f"\n📊 Batch style transfer complete:")
        print(f"   ✅ Success: {success_count}/{total_operations}")
        print(f"   ❌ Failed: {failed_count}/{total_operations}")
        print(f"   ⏱️  Total time: {total_time/60:.1f} minutes")
        print(f"   📁 Output directory: {output_dir}")
        
        return results


# Singleton instance
_image_edit_service = None


def get_image_edit_service(model: str = "gemini-2.5-flash-image") -> ImageEditService:
    """Get or create the image edit service singleton"""
    global _image_edit_service
    if _image_edit_service is None:
        _image_edit_service = ImageEditService(model=model)
    return _image_edit_service
