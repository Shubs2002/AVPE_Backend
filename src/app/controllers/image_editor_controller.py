"""
Image Editor Controller

Handles image generation and editing operations with authentication.
"""

from typing import Dict, List, Optional
from app.services.image_edit_service import get_image_edit_service


class ImageEditorController:
    """Controller for image editing and generation operations"""
    
    def __init__(self):
        self.service = None
    
    def _get_service(self, model: str = "gemini-2.5-flash-image"):
        """Get or create image edit service"""
        if self.service is None:
            self.service = get_image_edit_service(model=model)
        return self.service
    
    def generate_single_image(
        self,
        prompt: str,
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        use_google_search: bool = False,
        model: str = "gemini-2.5-flash-image",
        current_user_id: Optional[str] = None
    ) -> Dict:
        """
        Generate a single image from a text prompt.
        
        Args:
            prompt: Text description of the image to generate
            aspect_ratio: Image aspect ratio
            resolution: Image resolution
            use_google_search: Enable Google Search for current information
            model: Gemini model to use
            current_user_id: Authenticated user ID (required)
            
        Returns:
            dict: Generation result with image path
        """
        if not current_user_id:
            return {
                "success": False,
                "error": "Authentication required"
            }
        
        try:
            service = self._get_service(model=model)
            
            image, image_path, text_response = service.generate_single_image(
                prompt=prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                use_google_search=use_google_search
            )
            
            return {
                "success": True,
                "image_path": image_path,
                "text_response": text_response,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "user_id": current_user_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }
    
    def generate_bulk_images(
        self,
        prompts: List[str],
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        use_google_search: bool = False,
        output_dir: str = "generated_images",
        delay_between_requests: float = 2.0,
        model: str = "gemini-2.5-flash-image",
        current_user_id: Optional[str] = None
    ) -> Dict:
        """
        Generate multiple images iteratively.
        
        Args:
            prompts: List of text prompts
            aspect_ratio: Image aspect ratio
            resolution: Image resolution
            use_google_search: Enable Google Search
            output_dir: Directory to save images
            delay_between_requests: Delay in seconds between requests
            model: Gemini model to use
            current_user_id: Authenticated user ID (required)
            
        Returns:
            dict: Bulk generation results
        """
        if not current_user_id:
            return {
                "success": False,
                "error": "Authentication required",
                "total_images": len(prompts)
            }
        
        try:
            service = self._get_service(model=model)
            
            results = service.generate_bulk_images(
                prompts=prompts,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                use_google_search=use_google_search,
                output_dir=output_dir,
                delay_between_requests=delay_between_requests
            )
            
            success_count = sum(1 for r in results if r["status"] == "completed")
            failed_count = sum(1 for r in results if r["status"] == "failed")
            
            return {
                "success": True,
                "total_images": len(prompts),
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results,
                "output_dir": output_dir,
                "user_id": current_user_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total_images": len(prompts)
            }
    
    def edit_single_image(
        self,
        image_path: str,
        edit_prompt: str,
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        model: str = "gemini-2.5-flash-image",
        current_user_id: Optional[str] = None
    ) -> Dict:
        """
        Edit an existing image using a text prompt.
        
        Args:
            image_path: Path to the image to edit
            edit_prompt: Text description of the edit
            aspect_ratio: Output aspect ratio
            resolution: Output resolution
            model: Gemini model to use
            current_user_id: Authenticated user ID (required)
            
        Returns:
            dict: Edit result with output path
        """
        if not current_user_id:
            return {
                "success": False,
                "error": "Authentication required",
                "input_image": image_path
            }
        
        import os
        
        # Validate image exists
        if not os.path.exists(image_path):
            return {
                "success": False,
                "error": f"Image not found: {image_path}",
                "input_image": image_path
            }
        
        try:
            service = self._get_service(model=model)
            
            edited_image, output_path, text_response = service.edit_image_with_prompt(
                image_path=image_path,
                edit_prompt=edit_prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution
            )
            
            return {
                "success": True,
                "input_image": image_path,
                "output_path": output_path,
                "text_response": text_response,
                "edit_prompt": edit_prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "user_id": current_user_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "input_image": image_path,
                "edit_prompt": edit_prompt
            }
    
    def edit_bulk_images(
        self,
        image_paths: List[str],
        edit_prompts: List[str],
        aspect_ratio: str = "16:9",
        resolution: str = "2K",
        output_dir: str = "edited_images",
        delay_between_requests: float = 2.0,
        model: str = "gemini-2.5-flash-image",
        current_user_id: Optional[str] = None
    ) -> Dict:
        """
        Edit multiple images iteratively.
        
        Args:
            image_paths: List of paths to images to edit
            edit_prompts: List of edit prompts (one per image, or single prompt for all)
            aspect_ratio: Output aspect ratio
            resolution: Output resolution
            output_dir: Directory to save edited images
            delay_between_requests: Delay in seconds between requests
            model: Gemini model to use
            current_user_id: Authenticated user ID (required)
            
        Returns:
            dict: Bulk edit results
        """
        if not current_user_id:
            return {
                "success": False,
                "error": "Authentication required",
                "total_images": len(image_paths)
            }
        
        import os
        
        # Validate all images exist
        missing_images = [path for path in image_paths if not os.path.exists(path)]
        if missing_images:
            return {
                "success": False,
                "error": f"Images not found: {', '.join(missing_images)}",
                "total_images": len(image_paths)
            }
        
        # Validate prompt count
        if len(edit_prompts) != 1 and len(edit_prompts) != len(image_paths):
            return {
                "success": False,
                "error": f"Number of prompts ({len(edit_prompts)}) must be 1 or match number of images ({len(image_paths)})",
                "total_images": len(image_paths)
            }
        
        try:
            service = self._get_service(model=model)
            
            results = service.edit_bulk_images(
                image_paths=image_paths,
                edit_prompts=edit_prompts,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                output_dir=output_dir,
                delay_between_requests=delay_between_requests
            )
            
            success_count = sum(1 for r in results if r["status"] == "completed")
            failed_count = sum(1 for r in results if r["status"] == "failed")
            
            return {
                "success": True,
                "total_images": len(image_paths),
                "success_count": success_count,
                "failed_count": failed_count,
                "results": results,
                "output_dir": output_dir,
                "user_id": current_user_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total_images": len(image_paths)
            }
    
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
        skip_on_error: bool = True,
        model: str = "gemini-2.5-flash-image",
        current_user_id: Optional[str] = None
    ) -> Dict:
        """
        Apply the same style to multiple images (batch style transfer).
        
        Args:
            image_paths: List of paths to images to transform
            style_prompt: Single style prompt to apply to ALL images
            aspect_ratio: Output aspect ratio
            resolution: Output resolution
            output_dir: Directory to save styled images
            delay_between_requests: Delay in seconds between requests
            variations_per_image: Number of variations to generate per image
            timeout_per_image: Timeout in seconds for each image
            skip_on_error: If True, skip failed images and continue
            model: Gemini model to use
            current_user_id: Authenticated user ID (required)
            
        Returns:
            dict: Batch style transfer results
        """
        if not current_user_id:
            return {
                "success": False,
                "error": "Authentication required",
                "total_images": len(image_paths)
            }
        
        import os
        
        # Validate all images exist
        missing_images = [path for path in image_paths if not os.path.exists(path)]
        if missing_images:
            return {
                "success": False,
                "error": f"Images not found: {', '.join(missing_images[:5])}{'...' if len(missing_images) > 5 else ''}",
                "total_images": len(image_paths),
                "missing_count": len(missing_images)
            }
        
        try:
            service = self._get_service(model=model)
            
            results = service.batch_style_transfer(
                image_paths=image_paths,
                style_prompt=style_prompt,
                aspect_ratio=aspect_ratio,
                resolution=resolution,
                output_dir=output_dir,
                delay_between_requests=delay_between_requests,
                variations_per_image=variations_per_image,
                timeout_per_image=timeout_per_image,
                skip_on_error=skip_on_error
            )
            
            success_count = sum(1 for r in results if r["status"] == "completed")
            failed_count = sum(1 for r in results if r["status"] == "failed")
            total_operations = len(image_paths) * variations_per_image
            
            return {
                "success": True,
                "total_images": len(image_paths),
                "total_operations": total_operations,
                "success_count": success_count,
                "failed_count": failed_count,
                "variations_per_image": variations_per_image,
                "style_prompt": style_prompt,
                "results": results,
                "output_dir": output_dir,
                "user_id": current_user_id
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "total_images": len(image_paths)
            }


# Singleton instance
image_editor_controller = ImageEditorController()
