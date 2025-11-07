from fastapi import APIRouter, UploadFile, Form
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from typing import List, Optional

from app.controllers import (
    auth_controller,
    distributor_controller,
    screenwriter_controller,
    cinematographer_controller,
)
from app.utils.story_retry_helper import (
    get_retry_info_by_title,
    construct_retry_payload
)
from app.services.file_storage_manager import storage_manager, ContentType

router = APIRouter()


# ---------- AUTH ROUTES ----------
@router.get("/yt-auth", response_class=RedirectResponse)
def authorize() -> RedirectResponse:
    """Redirect user to YouTube OAuth2 authorization page."""
    auth_url = auth_controller.authorize_user()
    return RedirectResponse(auth_url)


@router.get("/yt-oauth2callback")
def oauth2callback(code: str) -> dict:
    """Handle OAuth2 callback from YouTube."""
    return auth_controller.handle_oauth_callback(code)


# ---------- YOUTUBE UPLOAD ----------
@router.post("/yt-upload")
def upload_video(
    file: UploadFile,
    title: str = Form(...),
    description: str = Form(""),
    tags: str = Form(""),
) -> dict:
    """Upload video to YouTube with metadata."""
    tag_list: List[str] = tags.split(",") if tags else []
    return distributor_controller.upload_video(file, title, description, tag_list)


# ---------- CONTENT GENERATION ----------
class GenerateStoryRequest(BaseModel):
    idea: str
    segments: Optional[int] = 7
    custom_character_roster: Optional[List[dict]] = None  # User-provided main character roster

class GenerateStorySetRequest(BaseModel):
    idea: str
    total_segments: int
    segments_per_set: Optional[int] = 10
    set_number: Optional[int] = 1
    custom_character_roster: Optional[List[dict]] = None  # User-provided main character roster

class GenerateFullmovieAutoRequest(BaseModel):
    idea: str
    total_segments: Optional[int] = None  # Optional - will auto-detect if not provided
    segments_per_set: Optional[int] = 10
    custom_character_roster: Optional[List[dict]] = None  # User-provided main character roster
    no_narration: Optional[bool] = False  # If true, no narration in any segment
    narration_only_first: Optional[bool] = False  # If true, narration only in first segment
    cliffhanger_interval: Optional[int] = 0  # Add cliffhangers every N segments (0 = no cliffhangers)
    content_rating: Optional[str] = "U"  # Content rating: "U" (Universal), "U/A" (Parental Guidance), "A" (Adult)

class GenerateMemeRequest(BaseModel):
    idea: Optional[str] = None  # Optional - will generate random meme if not provided
    segments: Optional[int] = 7
    custom_character_roster: Optional[List[dict]] = None  # User-provided main character roster

class GenerateFreeContentRequest(BaseModel):
    idea: Optional[str] = None  # Optional - will generate random content if not provided
    segments: Optional[int] = 7
    custom_character_roster: Optional[List[dict]] = None  # User-provided main character roster

class GenerateWhatsAppStoryRequest(BaseModel):
    idea: str  # Story idea for WhatsApp AI story
    segments: Optional[int] = 7  # Number of segments (default: 7 for WhatsApp stories)
    custom_character_roster: Optional[List[dict]] = None  # User-provided main character roster

class GenerateMusicVideoRequest(BaseModel):
    song_lyrics: str  # The complete song lyrics
    song_length: int  # Song length in seconds
    background_voice_needed: Optional[bool] = False  # Whether background narration/voice is needed
    additional_dialogues: Optional[List[dict]] = None  # Optional dialogues to add between verses [{"timestamp": 30, "character": "char_id", "line": "text"}]
    custom_character_roster: Optional[List[dict]] = None  # User-provided character roster for the music video
    music_genre: Optional[str] = None  # Optional music genre (pop, rock, hip-hop, etc.)
    visual_theme: Optional[str] = None  # Optional visual theme/concept for the video

class RetryFailedStorySetsRequest(BaseModel):
    previous_result: dict  # Result from previous generate_full_story_automatically call
    max_retries: Optional[int] = 3  # Maximum retry attempts per failed set

class RetryStoryByTitleRequest(BaseModel):
    title: str  # Story title (e.g., "Midnight Protocol")
    max_retries: Optional[int] = 3  # Maximum retry attempts per failed set
    content_type: Optional[str] = "movies"  # Content type (movies, stories, anime, etc.)

@router.post("/generate-prompt-based-story")
async def build_story_route(payload: GenerateStoryRequest) -> dict:
    """Generate a story outline from an idea."""
    return screenwriter_controller.build_story(payload.idea, payload.segments, payload.custom_character_roster)

@router.post("/generate-story-set")
async def build_story_set_route(payload: GenerateStorySetRequest) -> dict:
    """Generate a specific set of story segments (e.g., segments 1-10, 11-20, etc.) with complete metadata."""
    return screenwriter_controller.build_story_set(
        payload.idea, 
        payload.total_segments, 
        payload.segments_per_set, 
        payload.set_number,
        payload.custom_character_roster
    )

@router.post("/generate-movie-auto")
async def build_full_story_auto_route(payload: GenerateFullmovieAutoRequest) -> dict:
    """Generate a complete story automatically in sets and save to JSON files. Specify total_segments or let it auto-detect!"""
    return screenwriter_controller.build_full_story_auto(
        payload.idea,
        payload.total_segments,
        payload.segments_per_set,
        payload.custom_character_roster,
        payload.no_narration,
        payload.narration_only_first,
        payload.cliffhanger_interval,
        payload.content_rating
    )

@router.post("/generate-meme-segments")
async def build_meme_route(payload: GenerateMemeRequest) -> dict:
    """Generate meme segments from an idea."""
    return screenwriter_controller.build_meme(payload.idea, payload.segments, payload.custom_character_roster)

@router.post("/generate-free-content")
async def build_free_content_route(payload: GenerateFreeContentRequest) -> dict:
    """Generate viral free content segments from an idea."""
    return screenwriter_controller.build_free_content(payload.idea, payload.segments, payload.custom_character_roster)

@router.post("/generate-whatsapp-story")
async def build_whatsapp_story_route(payload: GenerateWhatsAppStoryRequest) -> dict:
    """Generate WhatsApp AI story with beautiful sceneries and moments animated by AI."""
    return screenwriter_controller.build_whatsapp_story(payload.idea, payload.segments, payload.custom_character_roster)

@router.post("/generate-music-video")
async def build_music_video_route(payload: GenerateMusicVideoRequest) -> dict:
    """Generate AI music video prompts from song lyrics for Veo3 video generation."""
    return screenwriter_controller.build_music_video(
        payload.song_lyrics,
        payload.song_length,
        payload.background_voice_needed,
        payload.additional_dialogues,
        payload.custom_character_roster,
        payload.music_genre,
        payload.visual_theme
    )

@router.post("/retry-failed-story-sets")
async def retry_failed_story_sets_route(payload: RetryFailedStorySetsRequest) -> dict:
    """Retry failed sets from a previous story generation attempt with exponential backoff."""
    return screenwriter_controller.retry_failed_story_sets(payload.previous_result, payload.max_retries)


@router.get("/story-status/{content_type}/{title}")
async def get_story_status_route(content_type: str, title: str) -> dict:
    """
    Check the status of a story generation - see which sets succeeded and which failed.
    
    Example:
        GET /api/story-status/movies/Midnight Protocol
    """
    return get_retry_info_by_title(title, content_type)


@router.post("/retry-story-by-title")
async def retry_story_by_title_route(payload: RetryStoryByTitleRequest) -> dict:
    """
    Retry failed sets for a story by providing just the title.
    Automatically finds the metadata and determines which sets failed.
    
    Example:
        POST /api/retry-story-by-title
        {
            "title": "Midnight Protocol",
            "content_type": "movies",
            "max_retries": 3
        }
    """
    # Get story info and failed sets
    retry_info = get_retry_info_by_title(payload.title, payload.content_type)
    
    if not retry_info["success"]:
        return {
            "success": False,
            "error": retry_info["error"],
            "title": payload.title
        }
    
    # Check if there are any failed sets
    if not retry_info["failed_sets"]:
        return {
            "success": True,
            "message": retry_info["message"],
            "title": payload.title,
            "total_sets": retry_info["total_sets"],
            "all_completed": True
        }
    
    # Construct retry payload
    retry_payload_data = construct_retry_payload(
        title=payload.title,
        content_type=payload.content_type,
        metadata=retry_info["metadata"],
        failed_sets=retry_info["failed_sets"],
        max_retries=payload.max_retries
    )
    
    # Call the existing retry function
    controller_result = screenwriter_controller.retry_failed_story_sets(
        retry_payload_data["previous_result"],
        retry_payload_data["max_retries"]
    )
    
    # Extract the actual result (controller wraps it in {"result": ...})
    actual_result = controller_result.get("result", controller_result)
    
    # Add context info to result
    return {
        "success": True,
        "story_result": actual_result,
        "original_failed_sets": retry_info["failed_sets"],
        "original_failed_count": retry_info["failed_count"]
    }


# ---------- TRENDING IDEAS GENERATION ----------
class GenerateTrendingIdeasRequest(BaseModel):
    content_type: Optional[str] = "all"  # "story", "meme", "free_content", or "all"
    count: Optional[int] = 5  # Number of ideas to generate



@router.post("/generate-trending-ideas")
async def generate_trending_ideas_route(payload: GenerateTrendingIdeasRequest) -> dict:
    """Generate 5 trending, creative, and unique content ideas."""
    return screenwriter_controller.generate_trending_ideas(payload.content_type, payload.count)



@router.post("/analyze-character-image-file")
async def analyze_character_image_file_route(
    image: UploadFile,
    character_name: str = Form(...),
    save_character: bool = Form(False)
) -> dict:
    """Analyze an uploaded image file to generate detailed character roster for video generation.
    
    NOTE: This endpoint analyzes SINGLE CHARACTER only (1 person per image).
    For multiple characters, use /analyze-multiple-character-images-files with separate images.
    """
    return screenwriter_controller.analyze_character_image_file(image, character_name, save_character)



@router.post("/analyze-multiple-character-images-files")
async def analyze_multiple_character_images_files_route(
    images: List[UploadFile],
    character_names: str = Form(...),  # Comma-separated names
    save_characters: bool = Form(False)
) -> dict:
    """Analyze multiple uploaded image files to generate a combined character roster.
    
    NOTE: Each image should contain ONLY 1 character.
    Provide one image per character you want to analyze.
    """
    return screenwriter_controller.analyze_multiple_character_images_files(images, character_names, save_characters)


@router.post("/create-character-from-image")
async def create_character_from_image_route(
    image: UploadFile,
    character_name: str = Form(...),
    remove_background: bool = Form(True),
    upload_to_cloudinary: bool = Form(True)
) -> dict:
    """
    🎭 Create a complete character from an uploaded image with AI analysis!
    
    This endpoint provides a complete character creation pipeline:
    
    **Pipeline Steps:**
    1. 🔍 **AI Analysis** - Gemini analyzes the image for ultra-detailed character description
    2. 🎨 **Background Removal** - Removes background for clean character image (optional)
    3. ☁️ **Cloudinary Upload** - Uploads processed image and gets public URL (optional)
    4. 💾 **MongoDB Storage** - Saves character data + image URL to database
    
    **What You Get:**
    - Complete character analysis (physical appearance, clothing, personality)
    - Clean character image with transparent background
    - Cloudinary-hosted image URL for use in video generation
    - MongoDB document with all character data
    
    **Perfect For:**
    - Creating custom characters for your stories
    - Building character libraries for video generation
    - Maintaining consistent character appearances across videos
    
    **Example Usage:**
    ```
    POST /api/create-character-from-image
    Form Data:
    - image: [your character image file]
    - character_name: "Hero Knight"
    - remove_background: true
    - upload_to_cloudinary: true
    ```
    
    **Response:**
    ```json
    {
        "success": true,
        "character_id": "507f1f77bcf86cd799439011",
        "character_name": "Hero Knight",
        "image_url": "https://res.cloudinary.com/.../hero_knight.png",
        "character_data": {
            "characters_roster": [{
                "name": "Hero Knight",
                "physical_appearance": {...},
                "clothing_style": {...},
                ...
            }]
        }
    }
    ```
    
    **Parameters:**
    - image: Image file (JPG, PNG, WEBP) - Max 10MB
    - character_name: Name for your character
    - remove_background: Remove image background (default: true)
    - upload_to_cloudinary: Upload to Cloudinary (default: true)
    
    **Note:** Make sure to configure Cloudinary credentials in .env file:
    - CLOUDINARY_CLOUD_NAME
    - CLOUDINARY_API_KEY
    - CLOUDINARY_API_SECRET
    """
    return screenwriter_controller.create_character_from_uploaded_image(
        image=image,
        character_name=character_name,
        remove_background=remove_background,
        upload_to_cloudinary=upload_to_cloudinary
    )


# ---------- COMPLETE VIDEO GENERATION ----------
class GenerateFullContentRequest(BaseModel):
    content_data: dict
    generate_videos: Optional[bool] = True
    resolution: Optional[str] = "720p"
    aspectRatio: Optional[str] = "9:16"
    download: Optional[bool] = False
    auto_merge: Optional[bool] = False  # Automatically merge segments into final video
    cleanup_segments: Optional[bool] = True  # Delete individual segments after merge
    # content_type is auto-detected from content_data structure

@router.post("/generate-full-content-videos")
async def generate_full_content_videos_route(payload: GenerateFullContentRequest) -> dict:
    """Generate complete videos for any content type (story, meme, free_content) with auto-merge. Content type is automatically detected from content_data structure."""
    return cinematographer_controller.handle_generate_full_content_videos(payload.dict())


# ---------- VIDEO GENERATION WITH KEYFRAMES ----------
class GenerateVideoWithKeyframesRequest(BaseModel):
    prompt: str
    first_frame_gcs_uri: Optional[str] = None  # Image URI: GCS (gs://...), HTTP/HTTPS URL, or Cloudinary URL
    last_frame_gcs_uri: Optional[str] = None   # Image URI: GCS (gs://...), HTTP/HTTPS URL, or Cloudinary URL
    duration: Optional[int] = 8
    resolution: Optional[str] = "720p"
    aspect_ratio: Optional[str] = "9:16"

@router.post("/generate-video-with-keyframes")
async def generate_video_with_keyframes_route(payload: GenerateVideoWithKeyframesRequest) -> dict:
    """
    Generate a video with optional first and last frame keyframes.
    
    This endpoint allows you to specify exact start and end frames for better
    video continuity between segments. Useful for:
    - Maintaining character consistency across segments
    - Creating smooth transitions between scenes
    - Ensuring visual continuity in multi-segment stories
    
    Example:
        POST /api/generate-video-with-keyframes
        {
            "prompt": "A cat walking across the room",
            "first_frame_gcs_uri": "gs://my-bucket/cat_start.png",
            "last_frame_gcs_uri": "gs://my-bucket/cat_end.png",
            "duration": 8,
            "aspect_ratio": "9:16"
        }
    """
    from app.services import genai_service
    
    try:
        video_urls = genai_service.generate_video_with_keyframes(
            prompt=payload.prompt,
            first_frame=payload.first_frame_gcs_uri,
            last_frame=payload.last_frame_gcs_uri,
            duration=payload.duration,
            resolution=payload.resolution,
            aspect_ratio=payload.aspect_ratio
        )
        
        return {
            "success": True,
            "video_urls": video_urls,
            "keyframes_used": {
                "first_frame": payload.first_frame_gcs_uri is not None,
                "last_frame": payload.last_frame_gcs_uri is not None
            }
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


# ---------- VIDEO MERGING ----------
class MergeContentVideosRequest(BaseModel):
    results: dict  # Results from video generation
    skip_missing: Optional[bool] = False
    cleanup_segments: Optional[bool] = True
    output_filename: Optional[str] = None
    server_side: Optional[bool] = True  # True = server merges and returns file, False = client-side instructions

class RetryFailedSegmentsRequest(BaseModel):
    previous_results: dict
    resolution: Optional[str] = "720p"
    aspectRatio: Optional[str] = "9:16"
    download: Optional[bool] = False

class DownloadVideoRequest(BaseModel):
    video_url: str  # The video URL to download
    filename: Optional[str] = None  # Optional custom filename
    download_dir: Optional[str] = "downloads"  # Directory to save the video

@router.post("/merge-content-videos")
async def merge_content_videos_route(payload: MergeContentVideosRequest) -> dict:
    """Merge all content video segments into a complete final video. Set server_side=true for actual file merging."""
    return cinematographer_controller.handle_merge_content_videos(payload.dict())

@router.post("/retry-failed-segments")
async def retry_failed_segments_route(payload: RetryFailedSegmentsRequest) -> dict:
    """Retry generating videos for failed segments."""
    return cinematographer_controller.handle_retry_failed_segments(payload.dict())

@router.get("/check-video-merger")
async def check_video_merger_route() -> dict:
    """Check video merger service status (cloud-native, no FFmpeg required)."""
    return cinematographer_controller.handle_check_ffmpeg({})

@router.get("/check-ffmpeg")
async def check_ffmpeg_route() -> dict:
    """Legacy endpoint - now returns cloud-native video merger status."""
    return cinematographer_controller.handle_check_ffmpeg({})

@router.post("/download-video")
async def download_video_route(payload: DownloadVideoRequest) -> dict:
    """Download a video from a URL using the same download logic as video generation."""
    return cinematographer_controller.handle_download_video(payload.dict())


# ---------- CHARACTER MANAGEMENT (MONGODB-BASED) ----------

@router.get("/characters")
async def get_all_characters_route(skip: int = 0, limit: int = 100) -> dict:
    """Get list of all saved characters from MongoDB with pagination"""
    return screenwriter_controller.get_all_saved_characters(skip, limit)


@router.get("/characters/{character_id}")
async def get_character_route(character_id: str) -> dict:
    """Get a specific character by MongoDB ID"""
    return screenwriter_controller.get_character_by_id(character_id)


class UpdateCharacterRequest(BaseModel):
    updated_data: dict  # Character data to update


@router.put("/characters/{character_id}")
async def update_character_route(character_id: str, payload: UpdateCharacterRequest) -> dict:
    """Update a saved character in MongoDB"""
    return screenwriter_controller.update_saved_character(character_id, payload.updated_data)


@router.delete("/characters/{character_id}")
async def delete_character_route(character_id: str) -> dict:
    """Delete a saved character from MongoDB"""
    return screenwriter_controller.delete_saved_character(character_id)


class SearchCharactersRequest(BaseModel):
    query: Optional[str] = None
    gender: Optional[str] = None
    age_range: Optional[str] = None
    skip: Optional[int] = 0
    limit: Optional[int] = 100


@router.post("/characters/search")
async def search_characters_route(payload: SearchCharactersRequest) -> dict:
    """Search characters by name or filters in MongoDB"""
    return screenwriter_controller.search_saved_characters(
        payload.query,
        payload.gender,
        payload.age_range,
        payload.skip,
        payload.limit
    )


@router.get("/characters/health/check")
async def check_mongodb_connection() -> dict:
    """Check MongoDB connection health"""
    from app.connectors.mongodb_connector import test_mongodb_connection
    return test_mongodb_connection()


# ---------- FILE STORAGE MANAGEMENT ----------
class MigrateContentRequest(BaseModel):
    old_directory: str  # Old directory path (e.g., "generated_movie_script")
    content_type: str  # Type of content (movies, stories, memes, etc.)

@router.get("/storage/content-types")
async def get_content_types_route() -> dict:
    """Get list of all supported content types."""
    return {
        "content_types": ContentType.all_types(),
        "descriptions": {
            ContentType.MOVIE: "Full-length movies with multiple sets",
            ContentType.STORY: "Story segments",
            ContentType.MEME: "Meme content",
            ContentType.FREE_CONTENT: "Free-form content",
            ContentType.MUSIC_VIDEO: "Music video segments",
            ContentType.WHATSAPP_STORY: "WhatsApp story format"
        }
    }

@router.get("/storage/list/{content_type}")
async def list_content_route(content_type: str) -> dict:
    """
    List all content items of a specific type.
    
    Example:
        GET /api/storage/list/movies
    """
    try:
        content_list = storage_manager.list_content(content_type)
        return {
            "success": True,
            "content_type": content_type,
            "count": len(content_list),
            "items": content_list
        }
    except ValueError as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/storage/info/{content_type}/{title}")
async def get_content_info_route(content_type: str, title: str) -> dict:
    """
    Get detailed information about a specific content item.
    
    Example:
        GET /api/storage/info/movies/Midnight Protocol
    """
    try:
        info = storage_manager.get_content_info(content_type, title)
        return {
            "success": True,
            **info
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.delete("/storage/delete/{content_type}/{title}")
async def delete_content_route(content_type: str, title: str) -> dict:
    """
    Delete all files for a content item.
    
    Example:
        DELETE /api/storage/delete/movies/Midnight Protocol
    """
    try:
        deleted = storage_manager.delete_content(content_type, title)
        if deleted:
            return {
                "success": True,
                "message": f"Deleted {content_type}/{title}"
            }
        else:
            return {
                "success": False,
                "error": "Content not found"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.post("/storage/migrate")
async def migrate_content_route(payload: MigrateContentRequest) -> dict:
    """
    Migrate content from old directory structure to new organized structure.
    
    Example:
        POST /api/storage/migrate
        {
            "old_directory": "generated_movie_script",
            "content_type": "movies"
        }
    """
    try:
        result = storage_manager.migrate_old_files(payload.old_directory, payload.content_type)
        return result
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

@router.get("/storage/stats")
async def get_storage_stats_route() -> dict:
    """Get statistics about all stored content."""
    stats = {}
    total_items = 0
    
    for content_type in ContentType.all_types():
        items = storage_manager.list_content(content_type)
        stats[content_type] = {
            "count": len(items),
            "items": items
        }
        total_items += len(items)
    
    return {
        "success": True,
        "total_items": total_items,
        "by_type": stats
    }



# ---------- ANIME GENERATION ----------
class GenerateAnimeAutoRequest(BaseModel):
    idea: str
    total_segments: Optional[int] = None  # Auto-detect if not provided
    segments_per_set: Optional[int] = 10
    custom_character_roster: Optional[List[dict]] = None
    anime_style: Optional[str] = "shonen"  # shonen, shojo, seinen, slice_of_life, mecha, isekai
    no_narration: Optional[bool] = False
    narration_only_first: Optional[bool] = False
    cliffhanger_interval: Optional[int] = 0
    content_rating: Optional[str] = "U/A"  # U, U/A, A

@router.post("/generate-anime-auto")
async def generate_anime_auto_route(payload: GenerateAnimeAutoRequest) -> dict:
    """
    Generate a complete Japanese anime story automatically in English.
    
    Creates anime-style content with:
    - Authentic Japanese anime aesthetics and art style
    - Large expressive anime eyes and distinctive character designs
    - Anime storytelling conventions and tropes
    - English dialogue and narration
    - Anime-specific visual effects and cinematography
    
    Anime Styles:
    - shonen: Action-packed with battles, friendship, and growth
    - shojo: Romantic with emotional depth and beautiful aesthetics
    - seinen: Mature themes with complex characters
    - slice_of_life: Everyday moments with warmth and humor
    - mecha: Giant robots and sci-fi battles
    - isekai: Fantasy world with magic and adventure
    
    Example:
        POST /api/generate-anime-auto
        {
            "idea": "A high school student discovers they have magical powers",
            "anime_style": "shonen",
            "total_segments": 30,
            "cliffhanger_interval": 10,
            "content_rating": "U/A"
        }
    """
    return screenwriter_controller.generate_anime_automatically(
        idea=payload.idea,
        total_segments=payload.total_segments,
        segments_per_set=payload.segments_per_set,
        custom_character_roster=payload.custom_character_roster,
        anime_style=payload.anime_style,
        no_narration=payload.no_narration,
        narration_only_first=payload.narration_only_first,
        cliffhanger_interval=payload.cliffhanger_interval,
        content_rating=payload.content_rating
    )



# ---------- DAILY CHARACTER LIFE CONTENT ----------
class GenerateDailyCharacterRequest(BaseModel):
    idea: str  # The daily life moment (e.g., "character sees reflection and gets scared")
    character_name: str  # Name of the character (e.g., "Floof")
    creature_language: Optional[str] = "Soft and High-Pitched"  # Voice description: Any description (e.g., "Soft and High-Pitched", "Deep and Grumbly", "Magical and mystical")
    num_segments: Optional[int] = 7  # Number of segments (max 10, default 7 for ~1 min)
    allow_dialogue: Optional[bool] = False  # Allow human dialogue/narration (default: False - creature sounds only)

@router.post("/generate-daily-character")
async def generate_daily_character_route(payload: GenerateDailyCharacterRequest) -> dict:
    """
    Generate daily character life content for Instagram using keyframe images.
    
    Perfect for Instagram pages showcasing a recurring character's daily life.
    Creates relatable, funny, engaging moments with NO dialogue/narration - only creature sounds.
    
    Features:
    - Simple: Just provide idea, character name, and voice type
    - Visual: Pure visual storytelling with creature sounds only
    - Quick: Maximum 10 segments (~1 minute video)
    - Keyframe-Ready: Designed for use with character images as keyframes
    - Viral: Optimized for Instagram engagement
    
    Character Voice Examples (you can use any description):
    - "Soft and High-Pitched" - Cute, gentle creature sounds
    - "Magical or Otherworldly" - Mystical, ethereal sounds
    - "Muffled and Low" - Deep, grumbly creature sounds
    - "Soft and High-Pitched and mystical" - Custom combination
    - "Deep and Grumbly with echoes" - Your own description
    - Any description that fits your character!
    
    Use Cases:
    - Funny reactions (seeing reflection, hearing noise)
    - Relatable struggles (waking up, cooking fails)
    - Character quirks (weird habits, behaviors)
    - Everyday adventures (shopping, commuting)
    - Emotional moments (happy, sad, confused)
    
    Example:
        POST /api/generate-daily-character
        {
            "idea": "Character sees his own reflection in a puddle and gets scared",
            "character_name": "Floof",
            "creature_language": "Soft and High-Pitched",
            "num_segments": 7
        }
    
    Response includes:
    - 7-10 segments (8 seconds each)
    - Pure visual storytelling (NO dialogue/narration)
    - Creature sound descriptions and timing
    - Scene descriptions for keyframe generation
    - Instagram optimization tips
    
    Note: Use the character's image as keyframe when generating videos with Veo3
    """
    return screenwriter_controller.generate_daily_character_content(
        idea=payload.idea,
        character_name=payload.character_name,
        creature_language=payload.creature_language,
        num_segments=payload.num_segments,
        allow_dialogue=payload.allow_dialogue
    )


class GenerateDailyCharacterVideosRequest(BaseModel):
    content_data: dict  # Output from /generate-daily-character
    character_keyframe_uri: str  # Image URI: GCS (gs://...), HTTP/HTTPS URL (https://...), or Cloudinary URL
    resolution: Optional[str] = "720p"
    aspect_ratio: Optional[str] = "9:16"
    download: Optional[bool] = False
    auto_merge: Optional[bool] = False  # Automatically merge segments into final video
    cleanup_segments: Optional[bool] = True  # Delete individual segments after merge

@router.post("/generate-daily-character-videos")
async def generate_daily_character_videos_route(payload: GenerateDailyCharacterVideosRequest) -> dict:
    """
    Generate videos for daily character content using keyframes.
    
    Takes the output from /generate-daily-character and generates videos for each segment
    using the character's image as the first keyframe for consistency.
    
    Features:
    - Automatic keyframe application for character consistency
    - Generates videos for all segments
    - Optional auto-merge into final video
    - Progress tracking for each segment
    
    Example:
        POST /api/generate-daily-character-videos
        {
            "content_data": {
                "title": "First Mirror Fumble",
                "character_name": "Floof",
                "segments": [...]
            },
            "character_keyframe_uri": "https://res.cloudinary.com/.../floof.png",
            "resolution": "720p",
            "aspect_ratio": "9:16",
            "auto_merge": true
        }
    
    Supported Image URIs:
    - GCS: "gs://your-bucket/characters/floof.png"
    - HTTP/HTTPS: "https://example.com/floof.png"
    - Cloudinary: "https://res.cloudinary.com/.../floof.png"
    
    Response includes:
    - Video URLs for each segment
    - Generation status and timing
    - Optional merged final video
    - Failed segments for retry
    """
    return cinematographer_controller.handle_generate_daily_character_videos(payload.dict())



class GenerateDailyCharacterVideosWithReferencesRequest(BaseModel):
    content_data: dict  # Output from /generate-daily-character
    character_keyframe_uri: str  # Character image URI for reference
    resolution: Optional[str] = "720p"
    aspect_ratio: Optional[str] = "9:16"
    download: Optional[bool] = False
    auto_merge: Optional[bool] = False
    cleanup_segments: Optional[bool] = True

@router.post("/generate-daily-character-videos-with-references")
async def generate_daily_character_videos_with_references_route(payload: GenerateDailyCharacterVideosWithReferencesRequest) -> dict:
    """
    Generate videos for daily character content using REFERENCE IMAGES for character consistency.
    
    NEW MODE: Uses both previous frame AND character keyframe as reference images (not as image parameter).
    This provides better character consistency across segments using Veo 3.1's reference image feature.
    
    Differences from /generate-daily-character-videos:
    - Previous frame → Used as REFERENCE IMAGE (not image parameter)
    - Character keyframe → Used as REFERENCE IMAGE
    - Both images guide character consistency without being the starting frame
    - Better for maintaining character appearance across segments
    
    Features:
    - Dual reference images (previous frame + character keyframe)
    - Enhanced character consistency with Veo 3.1
    - Automatic reference image management
    - Optional auto-merge into final video
    - Progress tracking for each segment
    
    Example:
        POST /api/generate-daily-character-videos-with-references
        {
            "content_data": {
                "title": "Floof's Splash Surprise",
                "character_name": "Floof",
                "segments": [...]
            },
            "character_keyframe_uri": "https://res.cloudinary.com/.../floof.png",
            "resolution": "720p",
            "aspect_ratio": "9:16",
            "auto_merge": true
        }
    
    Supported Image URIs:
    - GCS: "gs://your-bucket/characters/floof.png"
    - HTTP/HTTPS: "https://example.com/floof.png"
    - Cloudinary: "https://res.cloudinary.com/.../floof.png"
    
    Response includes:
    - Video URLs for each segment
    - Generation status and timing
    - Optional merged final video
    - Failed segments for retry
    """
    return cinematographer_controller.handle_generate_daily_character_videos_with_references(payload.dict())
