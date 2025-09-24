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

class GenerateMemeRequest(BaseModel):
    idea: Optional[str] = None  # Optional - will generate random meme if not provided
    segments: Optional[int] = 7

class GenerateFreeContentRequest(BaseModel):
    idea: Optional[str] = None  # Optional - will generate random content if not provided
    segments: Optional[int] = 7

@router.post("/generate-prompt-based-story")
async def build_story_route(payload: GenerateStoryRequest) -> dict:
    """Generate a story outline from an idea."""
    return screenwriter_controller.build_story(payload.idea, payload.segments)

@router.post("/generate-meme-segments")
async def build_meme_route(payload: GenerateMemeRequest) -> dict:
    """Generate meme segments from an idea."""
    return screenwriter_controller.build_meme(payload.idea, payload.segments)

@router.post("/generate-free-content")
async def build_free_content_route(payload: GenerateFreeContentRequest) -> dict:
    """Generate viral free content segments from an idea."""
    return screenwriter_controller.build_free_content(payload.idea, payload.segments)


# ---------- TRENDING IDEAS GENERATION ----------
class GenerateTrendingIdeasRequest(BaseModel):
    content_type: Optional[str] = "all"  # "story", "meme", "free_content", or "all"
    count: Optional[int] = 5  # Number of ideas to generate

@router.post("/generate-trending-ideas")
async def generate_trending_ideas_route(payload: GenerateTrendingIdeasRequest) -> dict:
    """Generate 5 trending, creative, and unique content ideas."""
    return screenwriter_controller.generate_trending_ideas(payload.content_type, payload.count)


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