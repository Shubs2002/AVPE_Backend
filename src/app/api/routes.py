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
    save_to_files: Optional[bool] = True
    output_directory: Optional[str] = "generated_movie_script"
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

class RetryFailedStorySetsRequest(BaseModel):
    previous_result: dict  # Result from previous generate_full_story_automatically call
    max_retries: Optional[int] = 3  # Maximum retry attempts per failed set

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
        payload.save_to_files,
        payload.output_directory,
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

@router.post("/retry-failed-story-sets")
async def retry_failed_story_sets_route(payload: RetryFailedStorySetsRequest) -> dict:
    """Retry failed sets from a previous story generation attempt with exponential backoff."""
    return screenwriter_controller.retry_failed_story_sets(payload.previous_result, payload.max_retries)


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
