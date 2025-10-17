"""
Character Image Service

This module provides complete character creation from images:
- Image analysis with Gemini
- Background removal
- Cloudinary upload
- MongoDB storage
"""

import json
from typing import Dict, Any, Optional
from io import BytesIO
from PIL import Image

from app.services.background_removal_service import remove_background
from app.services.cloudinary_service import upload_image_to_cloudinary
from app.services.character_repository import CharacterRepository
from app.connectors.genai_connector import get_genai_client
from app.data.prompts.analyze_character_prompt import get_character_analysis_prompt


def analyze_image_with_gemini(image_data: bytes, character_name: Optional[str] = None) -> Dict[str, Any]:
    """
    Analyze an image using Gemini to extract detailed character information
    
    Args:
        image_data: Image data as bytes
        character_name: Optional character name to use
    
    Returns:
        dict: Character analysis data
    """
    try:
        print("🔍 Analyzing image with Gemini...")
        
        # Get Gemini client
        client = get_genai_client()
        
        # Load image
        image = Image.open(BytesIO(image_data))
        print(f"📸 Image loaded: {image.size} {image.mode}")
        
        # Get analysis prompt
        prompt = get_character_analysis_prompt(
            character_count=1,
            character_name=character_name
        )
        
        # Analyze with Gemini
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=[prompt, image]
        )
        
        # Extract text response
        response_text = response.text.strip()
        
        # Clean up response (remove markdown code blocks if present)
        if response_text.startswith("```json"):
            response_text = response_text[7:]
        if response_text.startswith("```"):
            response_text = response_text[3:]
        if response_text.endswith("```"):
            response_text = response_text[:-3]
        response_text = response_text.strip()
        
        # Parse JSON
        character_data = json.loads(response_text)
        
        print(f"✅ Character analysis complete")
        
        return {
            "success": True,
            "character_data": character_data
        }
    
    except json.JSONDecodeError as e:
        error_msg = f"Failed to parse Gemini response as JSON: {str(e)}"
        print(f"❌ {error_msg}")
        print(f"Response text: {response_text[:500]}")
        return {
            "success": False,
            "error": error_msg
        }
    
    except Exception as e:
        error_msg = f"Failed to analyze image with Gemini: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }


def create_character_from_image(
    image_data: bytes,
    character_name: str,
    remove_bg: bool = True,
    upload_to_cloudinary: bool = True
) -> Dict[str, Any]:
    """
    Complete character creation pipeline from image:
    1. Analyze image with Gemini
    2. Remove background (optional)
    3. Upload to Cloudinary (optional)
    4. Save to MongoDB
    
    Args:
        image_data: Image data as bytes
        character_name: Name for the character
        remove_bg: Whether to remove background (default: True)
        upload_to_cloudinary: Whether to upload to Cloudinary (default: True)
    
    Returns:
        dict: Complete character creation result
    """
    try:
        print(f"\n🎭 Creating character: {character_name}")
        print("=" * 60)
        
        # Step 1: Analyze image with Gemini
        print("\n📋 Step 1: Analyzing image with Gemini...")
        analysis_result = analyze_image_with_gemini(image_data, character_name)
        
        if not analysis_result["success"]:
            return analysis_result
        
        character_data = analysis_result["character_data"]
        
        # Step 2: Remove background (if requested)
        processed_image_data = image_data
        if remove_bg:
            print("\n🎨 Step 2: Removing background...")
            try:
                processed_image_data = remove_background(image_data)
            except Exception as e:
                print(f"⚠️ Background removal failed: {str(e)}")
                print("⚠️ Continuing with original image...")
                processed_image_data = image_data
        else:
            print("\n⏭️ Step 2: Skipping background removal")
        
        # Step 3: Upload to Cloudinary (if requested)
        image_url = None
        cloudinary_public_id = None
        
        if upload_to_cloudinary:
            print("\n☁️ Step 3: Uploading to Cloudinary...")
            
            # Create safe public ID from character name
            safe_name = "".join(c for c in character_name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_').lower()
            
            upload_result = upload_image_to_cloudinary(
                image_data=processed_image_data,
                folder="characters",
                public_id=safe_name,
                tags=["character", character_name]
            )
            
            if upload_result["success"]:
                image_url = upload_result["url"]
                cloudinary_public_id = upload_result["public_id"]
            else:
                print(f"⚠️ Cloudinary upload failed: {upload_result.get('error')}")
                print("⚠️ Continuing without image URL...")
        else:
            print("\n⏭️ Step 3: Skipping Cloudinary upload")
        
        # Step 4: Save to MongoDB
        print("\n💾 Step 4: Saving to MongoDB...")
        repo = CharacterRepository()
        
        save_result = repo.create(
            character_data=character_data,
            character_name=character_name,
            image_url=image_url,
            cloudinary_public_id=cloudinary_public_id
        )
        
        if not save_result["success"]:
            return save_result
        
        print("\n" + "=" * 60)
        print(f"✅ Character created successfully!")
        print(f"📝 Name: {character_name}")
        print(f"🆔 ID: {save_result['character_id']}")
        if image_url:
            print(f"🖼️ Image: {image_url}")
        print("=" * 60 + "\n")
        
        return {
            "success": True,
            "character_id": save_result["character_id"],
            "character_name": character_name,
            "character_data": character_data,
            "image_url": image_url,
            "cloudinary_public_id": cloudinary_public_id,
            "created_at": save_result["created_at"]
        }
    
    except Exception as e:
        error_msg = f"Failed to create character from image: {str(e)}"
        print(f"❌ {error_msg}")
        return {
            "success": False,
            "error": error_msg
        }
