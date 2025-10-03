from fastapi import HTTPException, status
from app.services import openai_service
import random

def build_story(idea: str, segments: int = 5):
    """Generate story segments from an idea using ChatGPT."""
    if not idea:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing story idea"
        )
    try:
        story = openai_service.generate_story_segments(idea, segments)
        return {"story": story}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Story generation failed: {str(e)}"
        )

def build_story_set(idea: str, total_segments: int, segments_per_set: int = 10, set_number: int = 1):
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
            idea, total_segments, segments_per_set, set_number
        )
        return {"story_set": story_set}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Story set generation failed: {str(e)}"
        )

def build_meme(idea: str = None, segments: int = 5):
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
        meme = openai_service.generate_meme_segments(idea, segments)
        return {"meme": meme}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Meme generation failed: {str(e)}"
        )

def build_free_content(idea: str = None, segments: int = 5):
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
        content = openai_service.generate_free_content(idea, segments)
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