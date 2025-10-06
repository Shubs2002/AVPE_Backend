from fastapi import HTTPException, status, UploadFile
from app.services import openai_service
import random

def build_story(idea: str, segments: int = 5, custom_character_roster: list = None):
    """Generate story segments from an idea using ChatGPT."""
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing story idea"
        )
    try:
        story = openai_service.generate_story_segments(idea, segments, custom_character_roster)
        return {"story": story}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Story generation failed: {str(e)}"
        )

def build_story_set(idea: str, total_segments: int, segments_per_set: int = 10, set_number: int = 1, custom_character_roster: list = None):
    """Generate a specific set of story segments with complete metadata."""
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing story idea"
        )
    
    if total_segments <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Total segments must be greater than 0"
        )
    
    if segments_per_set <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Segments per set must be greater than 0"
        )
    
    if set_number <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Set number must be greater than 0"
        )
    
    # Calculate max possible sets
    max_sets = (total_segments + segments_per_set - 1) // segments_per_set
    if set_number > max_sets:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Set number {set_number} exceeds maximum possible sets ({max_sets}) for {total_segments} total segments"
        )
    
    try:
        story_set = openai_service.generate_story_segments_in_sets(
            idea, total_segments, segments_per_set, set_number, custom_character_roster
        )
        return {"story_set": story_set}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Story set generation failed: {str(e)}"
        )

def build_full_story_auto(idea: str, total_segments: int = None, segments_per_set: int = 10, save_to_files: bool = True, output_directory: str = "generated_stories", custom_character_roster: list = None):
    """Generate a complete story automatically in sets and save to JSON files."""
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing story idea"
        )
    
    if segments_per_set <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Segments per set must be greater than 0"
        )
    
    try:
        result = openai_service.generate_full_story_automatically(
            idea, total_segments, segments_per_set, save_to_files, output_directory, custom_character_roster
        )
        return {"result": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Automatic story generation failed: {str(e)}"
        )

def build_meme(idea: str = None, segments: int = 5, custom_character_roster: list = None):
    """Generate meme segments from an idea using ChatGPT."""
    # Generate random meme idea if not provided
    if not idea:
        import random
        random_meme_ideas = [
            "When you're trying to look busy at work",
            "Me explaining why I need another streaming subscription", 
            "When your friend says they're 5 minutes away",
            "Trying to act normal after googling your symptoms",
            "When you see your ex with someone uglier than you",
            "Me pretending to understand what my boss just said",
            "When you're an adult but still ask your parents for advice",
            "Me trying to save money vs me seeing something I want",
            "When someone asks if you're okay but you're clearly not",
            "Me at 3 AM wondering why I'm like this"
        ]
        idea = random.choice(random_meme_ideas)
        print(f"🎲 Generated random meme idea: {idea}")
    
    try:
        meme = openai_service.generate_meme_segments(idea, segments, custom_character_roster)
        return {"meme": meme}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meme generation failed: {str(e)}"
        )

def build_free_content(idea: str = None, segments: int = 5, custom_character_roster: list = None):
    """Generate viral free content segments from an idea using ChatGPT."""
    # Generate random content idea if not provided
    if not idea:
        import random
        random_content_ideas = [
            "5 morning habits that changed my life",
            "How to learn any skill in 30 days",
            "Money mistakes I wish I knew at 20",
            "Phone tricks everyone should know",
            "Cleaning hacks that actually work",
            "Study techniques that got me straight A's",
            "Productivity tips for busy people",
            "Healthy meal prep ideas for beginners",
            "Time management secrets of successful people",
            "Simple exercises you can do anywhere",
            "Budget-friendly home organization tips",
            "Essential life skills they don't teach in school"
        ]
        idea = random.choice(random_content_ideas)
        print(f"🎲 Generated random content idea: {idea}")
    
    try:
        content = openai_service.generate_free_content(idea, segments, custom_character_roster)
        return {"content": content}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Free content generation failed: {str(e)}"
        )
        
def generate_trending_ideas(content_type: str = "all", count: int = 5):
    """Generate trending, creative, and unique content ideas."""
    try:
        ideas = openai_service.generate_trending_ideas(content_type, count)
        return ideas
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Trending ideas generation failed: {str(e)}"
        )

def retry_failed_story_sets(previous_result: dict, max_retries: int = 3):
    """Retry failed sets from a previous story generation attempt."""
    if not previous_result:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Previous result is required"
        )
    
    if max_retries <= 0 or max_retries > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Max retries must be between 1 and 10"
        )
    
    try:
        result = openai_service.retry_failed_story_sets(previous_result, max_retries)
        return {"result": result}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retry story sets: {str(e)}"
        )



def analyze_character_image_file(image: UploadFile, character_name: str, save_character: bool = False):
    """Analyze an uploaded image file to generate detailed character roster.
    
    NOTE: This endpoint analyzes SINGLE CHARACTER only (1 person per image).
    For multiple characters, use /analyze-multiple-character-images-files with separate images.
    """
    import base64
    
    # Validate file
    if not image:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image file provided"
        )
    
    # Validate character name
    if not character_name or character_name.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character name is required"
        )
    
    # Check file size (limit to 10MB)
    max_size = 10 * 1024 * 1024  # 10MB
    if hasattr(image, 'size') and image.size > max_size:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image file too large. Maximum size is 10MB"
        )
    
    try:
        # Read and encode the image
        image_content = image.file.read()
        image_data = base64.b64encode(image_content).decode('utf-8')
        
        # Detect image format from multiple sources
        image_format = None
        
        # Try to detect from content type first
        if image.content_type and image.content_type != 'application/octet-stream':
            if 'jpeg' in image.content_type or 'jpg' in image.content_type:
                image_format = 'jpeg'
            elif 'png' in image.content_type:
                image_format = 'png'
            elif 'webp' in image.content_type:
                image_format = 'webp'
            elif 'gif' in image.content_type:
                image_format = 'gif'
        
        # If not detected, try from filename
        if not image_format and image.filename:
            file_ext = image.filename.split('.')[-1].lower()
            if file_ext in ['jpg', 'jpeg', 'heic', 'heif']:
                image_format = 'jpeg'
            elif file_ext in ['png', 'webp', 'gif', 'bmp']:
                image_format = file_ext
        
        # If still not detected, try to detect from image content (magic bytes)
        if not image_format:
            # Check magic bytes
            if image_content[:2] == b'\xff\xd8':
                image_format = 'jpeg'
            elif image_content[:8] == b'\x89PNG\r\n\x1a\n':
                image_format = 'png'
            elif image_content[:4] == b'RIFF' and image_content[8:12] == b'WEBP':
                image_format = 'webp'
            elif image_content[:6] in (b'GIF87a', b'GIF89a'):
                image_format = 'gif'
        
        # Default to jpeg if still not detected
        if not image_format:
            image_format = 'jpeg'
            print(f"⚠️ Could not detect image format, defaulting to jpeg")
        
        # Analyze the image (always 1 character for this endpoint)
        character_analysis = openai_service.analyze_character_from_image(
            image_data, image_format, 1, character_name.strip()
        )
        
        # Update character name in the roster
        if 'characters_roster' in character_analysis and character_analysis['characters_roster']:
            character_analysis['characters_roster'][0]['name'] = character_name.strip()
        
        # Add file info to response
        character_analysis['file_info'] = {
            'filename': image.filename,
            'content_type': image.content_type,
            'detected_format': image_format,
            'file_size_bytes': len(image_content)
        }
        
        # Save character if requested (to MongoDB)
        save_result = None
        if save_character:
            save_result = character_service_mongodb.save_character_to_mongodb(character_analysis, character_name.strip())
        
        response = {"character_analysis": character_analysis}
        if save_result:
            response["save_result"] = save_result
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Character image file analysis failed: {str(e)}"
        )

def analyze_multiple_character_images_files(images: list, character_names: str, save_characters: bool = False):
    """Analyze multiple uploaded image files to generate a combined character roster.
    
    NOTE: Each image should contain ONLY 1 character.
    Provide one image per character you want to analyze.
    """
    import base64
    
    # Validate inputs
    if not images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No image files provided"
        )
    
    if not character_names or character_names.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character names are required (comma-separated)"
        )
    
    # Parse character names
    names_list = [name.strip() for name in character_names.split(',') if name.strip()]
    if len(names_list) != len(images):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Number of character names ({len(names_list)}) must match number of images ({len(images)})"
        )
    
    # Check number of images (limit to 10)
    if len(images) > 10:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Too many images. Maximum is 10 images per request"
        )
    
    try:
        processed_images = []
        
        for i, image in enumerate(images, 1):
            if not image:
                continue
                
            # Check file size (limit to 10MB per image)
            max_size = 10 * 1024 * 1024  # 10MB
            if hasattr(image, 'size') and image.size > max_size:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Image {i} too large. Maximum size is 10MB per image"
                )
            
            # Read and encode the image
            image_content = image.file.read()
            image_data = base64.b64encode(image_content).decode('utf-8')
            
            # Detect image format from multiple sources
            image_format = None
            
            # Try to detect from content type first
            if image.content_type and image.content_type != 'application/octet-stream':
                if 'jpeg' in image.content_type or 'jpg' in image.content_type:
                    image_format = 'jpeg'
                elif 'png' in image.content_type:
                    image_format = 'png'
                elif 'webp' in image.content_type:
                    image_format = 'webp'
                elif 'gif' in image.content_type:
                    image_format = 'gif'
            
            # If not detected, try from filename
            if not image_format and image.filename:
                file_ext = image.filename.split('.')[-1].lower()
                if file_ext in ['jpg', 'jpeg', 'heic', 'heif']:
                    image_format = 'jpeg'
                elif file_ext in ['png', 'webp', 'gif', 'bmp']:
                    image_format = file_ext
            
            # If still not detected, try to detect from image content (magic bytes)
            if not image_format:
                # Check magic bytes
                if image_content[:2] == b'\xff\xd8':
                    image_format = 'jpeg'
                elif image_content[:8] == b'\x89PNG\r\n\x1a\n':
                    image_format = 'png'
                elif image_content[:4] == b'RIFF' and image_content[8:12] == b'WEBP':
                    image_format = 'webp'
                elif image_content[:6] in (b'GIF87a', b'GIF89a'):
                    image_format = 'gif'
            
            # Default to jpeg if still not detected
            if not image_format:
                image_format = 'jpeg'
                print(f"⚠️ Image {i}: Could not detect format, defaulting to jpeg")
            
            processed_images.append({
                'image_data': image_data,
                'image_format': image_format,
                'description': names_list[i-1],  # Use provided character name
                'character_name': names_list[i-1],
                'file_info': {
                    'filename': image.filename,
                    'content_type': image.content_type,
                    'detected_format': image_format,
                    'file_size_bytes': len(image_content)
                }
            })
        
        if not processed_images:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No valid image files found"
            )
        
        # Analyze all images (1 character per image)
        combined_analysis = openai_service.analyze_multiple_character_images(
            processed_images, 1
        )
        
        # Update character names in the roster based on source_description
        # This ensures that if an image fails, the correct name is still used
        if 'characters_roster' in combined_analysis:
            for character in combined_analysis['characters_roster']:
                # The source_description contains the original character name
                source_desc = character.get('source_description', '')
                # Find the matching name from the original names_list
                if source_desc in names_list:
                    character['name'] = source_desc
                else:
                    # Fallback: try to match by source_image index
                    source_img = character.get('source_image', 0)
                    if source_img > 0 and source_img <= len(names_list):
                        character['name'] = names_list[source_img - 1]
        
        # Add file info summary
        combined_analysis['files_info'] = {
            'total_files_processed': len(processed_images),
            'total_file_size_bytes': sum(img['file_info']['file_size_bytes'] for img in processed_images),
            'file_formats': list(set(img['image_format'] for img in processed_images))
        }
        
        # Save characters if requested (to MongoDB)
        save_results = None
        if save_characters and 'characters_roster' in combined_analysis:
            # Extract actual character names from the roster (only successful ones)
            actual_names = [char.get('name', f'character_{i}') for i, char in enumerate(combined_analysis['characters_roster'], 1)]
            save_results = character_service_mongodb.save_multiple_characters_to_mongodb(
                combined_analysis['characters_roster'], actual_names
            )
        
        response = {"combined_character_analysis": combined_analysis}
        if save_results:
            response["save_results"] = save_results
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Multiple character image files analysis failed: {str(e)}"
        )


# ==================== CHARACTER MANAGEMENT (MONGODB-BASED) ====================

from app.services import character_service_mongodb

def get_all_saved_characters(skip: int = 0, limit: int = 100):
    """Get list of all saved characters from MongoDB"""
    try:
        result = character_service_mongodb.get_all_characters(skip, limit)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve characters: {str(e)}"
        )


def get_character_by_id(character_id: str):
    """Get a specific character by MongoDB ID"""
    try:
        result = character_service_mongodb.get_character_by_id(character_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', 'Character not found')
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve character: {str(e)}"
        )


def update_saved_character(character_id: str, updated_data: dict):
    """Update a saved character in MongoDB"""
    try:
        result = character_service_mongodb.update_character(character_id, updated_data)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', 'Character not found')
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update character: {str(e)}"
        )


def delete_saved_character(character_id: str):
    """Delete a saved character from MongoDB"""
    try:
        result = character_service_mongodb.delete_character(character_id)
        
        if not result.get('success'):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get('error', 'Character not found')
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete character: {str(e)}"
        )


def search_saved_characters(query: str = None, gender: str = None, age_range: str = None, skip: int = 0, limit: int = 100):
    """Search characters by name or filters in MongoDB"""
    try:
        result = character_service_mongodb.search_characters(query, gender, age_range, skip, limit)
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to search characters: {str(e)}"
        )
