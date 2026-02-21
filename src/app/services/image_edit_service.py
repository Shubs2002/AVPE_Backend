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


def get_genai_client():
    """Get configured GenAI client"""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")
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
            for part in response.parts:
                if part.text is not None:
                    text_response = part.text
                    print(f"📝 Text response: {text_response[:200]}...")
                elif image := part.as_image():
                    generated_image = image
                    
                    # Save image if output path provided
                    if output_path:
                        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
                        image.save(output_path, "PNG")
                        saved_path = output_path
                        print(f"✅ Image saved to: {output_path}")
                    else:
                        # Auto-generate filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        auto_path = f"generated_images/image_{timestamp}.png"
                        os.makedirs("generated_images", exist_ok=True)
                        image.save(auto_path, "PNG")
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
        output_path: Optional[str] = None
    ) -> Tuple[Optional[Image.Image], Optional[str], Optional[str]]:
        """
        Edit an existing image using a text prompt.
        
        Args:
            image_path: Path to the image to edit
            edit_prompt: Text description of the edit to make
            aspect_ratio: Output aspect ratio
            resolution: Output resolution
            output_path: Optional path to save edited image
            
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
        
        # Create chat session for editing
        chat = self.client.chats.create(
            model=self.model,
            config=types.GenerateContentConfig(
                response_modalities=['TEXT', 'IMAGE']
            )
        )
        
        try:
            # Send image with edit prompt
            response = chat.send_message(
                [input_image, edit_prompt],
                config=types.GenerateContentConfig(
                    image_config=types.ImageConfig(
                        aspect_ratio=aspect_ratio,
                        image_size=resolution
                    )
                )
            )
            
            edited_image = None
            text_response = None
            saved_path = None
            
            # Extract edited image and text
            for part in response.parts:
                if part.text is not None:
                    text_response = part.text
                    print(f"📝 Text response: {text_response[:200]}...")
                elif image := part.as_image():
                    edited_image = image
                    
                    # Save edited image
                    if output_path:
                        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
                        image.save(output_path, "PNG")
                        saved_path = output_path
                        print(f"✅ Edited image saved to: {output_path}")
                    else:
                        # Auto-generate filename
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        auto_path = f"edited_images/edited_{timestamp}.png"
                        os.makedirs("edited_images", exist_ok=True)
                        image.save(auto_path, "PNG")
                        saved_path = auto_path
                        print(f"✅ Edited image saved to: {auto_path}")
            
            return edited_image, saved_path, text_response
            
        except Exception as e:
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


# Singleton instance
_image_edit_service = None


def get_image_edit_service(model: str = "gemini-2.5-flash-image") -> ImageEditService:
    """Get or create the image edit service singleton"""
    global _image_edit_service
    if _image_edit_service is None:
        _image_edit_service = ImageEditService(model=model)
    return _image_edit_service
