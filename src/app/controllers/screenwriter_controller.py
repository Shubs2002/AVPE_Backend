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



def analyze_character_image_file(image: UploadFile, character_name: str, character_count: int = 1, save_character: bool = False):
    """Analyze an uploaded image file to generate detailed character roster."""
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
    
    # Validate character count
    if character_count <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character count must be greater than 0"
        )
    
    try:
        # Read and encode the image
        image_content = image.file.read()
        image_data = base64.b64encode(image_content).decode('utf-8')
        
        # Get image format from filename or content type
        image_format = "jpeg"  # default
        if image.filename:
            file_ext = image.filename.split('.')[-1].lower()
            if file_ext in ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'heic', 'heif']:
                image_format = 'jpeg' if file_ext in ['jpg', 'heic', 'heif'] else file_ext
        elif image.content_type:
            if 'jpeg' in image.content_type or 'jpg' in image.content_type:
                image_format = 'jpeg'
            elif 'png' in image.content_type:
                image_format = 'png'
            elif 'webp' in image.content_type:
                image_format = 'webp'
        
        # Analyze the image
        character_analysis = openai_service.analyze_character_from_image(
            image_data, image_format, character_count, character_name.strip()
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
        
        # Save character if requested
        save_result = None
        if save_character:
            save_result = openai_service.save_character_to_file(character_analysis, character_name.strip())
        
        response = {"character_analysis": character_analysis}
        if save_result:
            response["save_result"] = save_result
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Character image file analysis failed: {str(e)}"
        )

def analyze_multiple_character_images_files(images: list, character_names: str, character_count_per_image: int = 1, save_characters: bool = False):
    """Analyze multiple uploaded image files to generate a combined character roster."""
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
    
    if character_count_per_image <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Character count per image must be greater than 0"
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
            
            # Get image format from filename or content type
            image_format = "jpeg"  # default
            if image.filename:
                file_ext = image.filename.split('.')[-1].lower()
                if file_ext in ['jpg', 'jpeg', 'png', 'webp', 'gif', 'bmp', 'tiff', 'heic', 'heif']:
                    image_format = 'jpeg' if file_ext in ['jpg', 'heic', 'heif'] else file_ext
            elif image.content_type:
                if 'jpeg' in image.content_type or 'jpg' in image.content_type:
                    image_format = 'jpeg'
                elif 'png' in image.content_type:
                    image_format = 'png'
                elif 'webp' in image.content_type:
                    image_format = 'webp'
            
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
        
        # Analyze all images
        combined_analysis = openai_service.analyze_multiple_character_images(
            processed_images, character_count_per_image
        )
        
        # Update character names in the roster
        if 'characters_roster' in combined_analysis:
            for i, character in enumerate(combined_analysis['characters_roster']):
                if i < len(names_list):
                    character['name'] = names_list[i]
        
        # Add file info summary
        combined_analysis['files_info'] = {
            'total_files_processed': len(processed_images),
            'total_file_size_bytes': sum(img['file_info']['file_size_bytes'] for img in processed_images),
            'file_formats': list(set(img['image_format'] for img in processed_images))
        }
        
        # Save characters if requested
        save_results = None
        if save_characters and 'characters_roster' in combined_analysis:
            save_results = openai_service.save_multiple_characters_to_files(
                combined_analysis['characters_roster'], names_list
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