from fastapi import APIRouter, UploadFile, Form, File, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, Field, EmailStr
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
from app.utils.auth_dependencies import get_current_user, get_current_active_user
from app.services.auth_service import auth_service

router = APIRouter()


# ---------- USER AUTHENTICATION ROUTES ----------
class SendOTPRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")

class VerifyOTPRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP")

class RegisterRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address (must be verified)")
    password: str = Field(..., min_length=8, max_length=72, description="Password (8-72 characters)")
    full_name: str = Field(..., description="User's full name")
    otp: str = Field(..., min_length=6, max_length=6, description="6-digit OTP for verification")

class LoginRequest(BaseModel):
    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")

class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Refresh token")

@router.post("/auth/send-otp")
def send_otp(payload: SendOTPRequest) -> dict:
    """
    📧 Send OTP to email for verification
    
    **Public endpoint - no authentication required**
    
    **Step 1 of registration:** Send OTP to email address
    
    Sends a 6-digit OTP to the provided email address.
    OTP expires in 10 minutes.
    
    **Example:**
    ```json
    {
      "email": "user@example.com"
    }
    ```
    
    **Returns:**
    ```json
    {
      "success": true,
      "message": "OTP sent to user@example.com",
      "expires_in_minutes": 10
    }
    ```
    """
    from app.services.email_service import email_service
    return email_service.send_otp_email(payload.email)

@router.post("/auth/verify-otp")
def verify_otp(payload: VerifyOTPRequest) -> dict:
    """
    ✅ Verify OTP
    
    **Public endpoint - no authentication required**
    
    **Step 2 of registration:** Verify the OTP sent to email
    
    Verifies the 6-digit OTP. Once verified, you can proceed with registration.
    
    **Example:**
    ```json
    {
      "email": "user@example.com",
      "otp": "123456"
    }
    ```
    
    **Returns:**
    ```json
    {
      "success": true,
      "message": "Email verified successfully"
    }
    ```
    """
    from app.services.email_service import email_service
    return email_service.verify_otp(payload.email, payload.otp)

@router.post("/auth/register")
def register(payload: RegisterRequest) -> dict:
    """
    🔐 Register a new user account
    
    **Public endpoint - no authentication required**
    
    **Step 3 of registration:** Create account after email verification
    
    Creates a new user account with:
    - Verified email address (OTP must be verified first)
    - Securely hashed password (bcrypt)
    - User profile information
    - Automatic user_id generation (user_xxx format)
    
    **Registration Flow:**
    1. POST /auth/send-otp - Send OTP to email
    2. POST /auth/verify-otp - Verify OTP
    3. POST /auth/register - Register with verified email + OTP
    
    **Example:**
    ```json
    {
      "email": "user@example.com",
      "password": "SecurePass123!",
      "full_name": "John Doe",
      "otp": "123456"
    }
    ```
    """
    from app.services.email_service import email_service
    
    # Verify OTP before registration (mark as used)
    otp_result = email_service.verify_otp(payload.email, payload.otp, mark_as_used=True)
    if not otp_result.get("success"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=otp_result.get("error", "Invalid or expired OTP")
        )
    
    # Register user
    user = auth_service.register_user(
        email=payload.email,
        password=payload.password,
        full_name=payload.full_name
    )
    
    # Clean up: Delete OTP after successful registration
    email_service.delete_otp(payload.email)
    
    return {
        "success": True,
        "message": "User registered successfully",
        "user": user
    }

@router.post("/auth/login")
def login(payload: LoginRequest) -> dict:
    """
    🔑 Login and get access tokens
    
    **Public endpoint - no authentication required**
    
    Authenticates user and returns:
    - Access token (30 min expiry) - use for API requests
    - Refresh token (7 days expiry) - use to get new access token
    - User profile data
    
    **Usage:**
    1. Login to get tokens
    2. Use access_token in Authorization header: `Bearer <token>`
    3. When access_token expires, use refresh_token to get new one
    
    **Returns:**
    ```json
    {
      "access_token": "eyJ...",
      "refresh_token": "eyJ...",
      "token_type": "bearer",
      "user": {
        "user_id": "user_xxx",
        "email": "user@example.com",
        "full_name": "John Doe"
      }
    }
    ```
    """
    return auth_service.login(
        email=payload.email,
        password=payload.password
    )

@router.post("/auth/refresh")
def refresh_token(payload: RefreshTokenRequest) -> dict:
    """
    🔄 Refresh access token
    
    **Public endpoint - no authentication required**
    
    Use refresh token to get a new access token when the old one expires.
    
    **Usage:**
    - When you get 401 Unauthorized, use refresh token to get new access token
    - Refresh tokens are long-lived (7 days)
    - Access tokens are short-lived (30 minutes)
    
    **Returns:**
    ```json
    {
      "access_token": "eyJ...",
      "token_type": "bearer"
    }
    ```
    """
    return auth_service.refresh_access_token(payload.refresh_token)

@router.get("/auth/me")
def get_current_user_info(current_user: dict = Depends(get_current_active_user)) -> dict:
    """
    👤 Get current user information
    
    **Protected endpoint - requires authentication**
    
    Returns the profile of the currently authenticated user.
    
    **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Returns:**
    ```json
    {
      "user_id": "user_xxx",
      "email": "user@example.com",
      "full_name": "John Doe",
      "is_active": true
    }
    ```
    """
    return current_user


# ---------- YOUTUBE AUTH ROUTES ----------
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
    idea: str = Field(..., description="Story idea or concept", example="A hero's journey through a magical land")
    segments: Optional[int] = Field(7, description="Number of segments to generate", ge=1, example=7)
    custom_character_roster: Optional[List[dict]] = Field(None, description="Detailed character roster with full descriptions, personalities, and roles. Use this for complex stories with detailed characters.")
    character_names: Optional[str] = Field(None, description="Quick character specification: comma-separated character names (e.g., 'Floof, Buddy'). Alternative to custom_character_roster for simple character setup.", example="Floof, Buddy")
    creature_languages: Optional[str] = Field(None, description="Comma-separated creature voice types matching character_names order. Options: 'Soft and High-Pitched', 'Deep and Grumbly', 'Magical or Otherworldly'", example="Soft and High-Pitched, Deep and Grumbly")

class GenerateStorySetRequest(BaseModel):
    idea: str = Field(..., description="Story idea or concept", example="A hero's journey through a magical land")
    total_segments: int = Field(..., description="Total number of segments in the complete story", ge=1, example=50)
    segments_per_set: Optional[int] = Field(10, description="Number of segments to generate per set", ge=1, le=20, example=10)
    set_number: Optional[int] = Field(1, description="Which set to generate (e.g., set 1 = segments 1-10, set 2 = segments 11-20)", ge=1, example=1)
    custom_character_roster: Optional[List[dict]] = Field(None, description="Detailed character roster with full descriptions, personalities, and roles")
    character_names: Optional[str] = Field(None, description="Quick character specification: comma-separated names", example="Floof, Buddy")
    creature_languages: Optional[str] = Field(None, description="Comma-separated creature voice types", example="Soft and High-Pitched, Deep and Grumbly")

class GenerateFullmovieAutoRequest(BaseModel):
    idea: str = Field(..., description="Movie idea or concept", example="A hero's journey through a magical land")
    total_segments: Optional[int] = Field(None, description="Total number of segments (auto-detected if not provided)", ge=1, example=50)
    segments_per_set: Optional[int] = Field(10, description="Number of segments to generate per set", ge=1, le=20, example=10)
    custom_character_roster: Optional[List[dict]] = Field(None, description="Detailed character roster with full descriptions, personalities, and roles")
    no_narration: Optional[bool] = Field(False, description="If true, no narration in any segment")
    narration_only_first: Optional[bool] = Field(False, description="If true, narration only in first segment")
    cliffhanger_interval: Optional[int] = Field(0, description="Add cliffhangers every N segments (0 = no cliffhangers)", ge=0, example=10)
    content_rating: Optional[str] = Field("U", description="Content rating: 'U' (Universal), 'U/A' (Parental Guidance), 'A' (Adult)", example="U")
    character_names: Optional[str] = Field(None, description="Quick character specification: comma-separated names", example="Floof, Buddy")
    creature_languages: Optional[str] = Field(None, description="Comma-separated creature voice types", example="Soft and High-Pitched, Deep and Grumbly")

class GenerateMemeRequest(BaseModel):
    idea: Optional[str] = Field(None, description="Meme idea (optional - will generate random meme if not provided)", example="Character reacts to Monday morning")
    segments: Optional[int] = Field(7, description="Number of segments to generate", ge=1, le=10, example=7)
    custom_character_roster: Optional[List[dict]] = Field(None, description="Detailed character roster")
    character_names: Optional[str] = Field(None, description="Quick character specification: comma-separated names", example="Floof")
    creature_languages: Optional[str] = Field(None, description="Comma-separated creature voice types", example="Soft and High-Pitched")

class GenerateFreeContentRequest(BaseModel):
    idea: Optional[str] = Field(None, description="Content idea (optional - will generate random content if not provided)", example="Character discovers something amazing")
    segments: Optional[int] = Field(7, description="Number of segments to generate", ge=1, le=10, example=7)
    custom_character_roster: Optional[List[dict]] = Field(None, description="Detailed character roster")
    character_names: Optional[str] = Field(None, description="Quick character specification: comma-separated names", example="Floof")
    creature_languages: Optional[str] = Field(None, description="Comma-separated creature voice types", example="Soft and High-Pitched")

class GenerateWhatsAppStoryRequest(BaseModel):
    idea: str = Field(..., description="Story idea for WhatsApp AI story with beautiful sceneries", example="A peaceful journey through nature")
    segments: Optional[int] = Field(7, description="Number of segments (default: 7 for WhatsApp stories)", ge=1, le=10, example=7)
    custom_character_roster: Optional[List[dict]] = Field(None, description="Detailed character roster")
    character_names: Optional[str] = Field(None, description="Quick character specification: comma-separated names", example="Floof")
    creature_languages: Optional[str] = Field(None, description="Comma-separated creature voice types", example="Soft and High-Pitched")

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


# ---------- SHORT FILM GENERATION ----------

class GenerateShortFilmRequest(BaseModel):
    idea: str = Field(..., description="Film concept/story", example="A lonely robot discovers the meaning of friendship")
    character_ids: Optional[List[str]] = Field(None, description="List of character IDs to use (optional)", example=["char_floof_xxx", "char_poof_yyy"])
    num_segments: Optional[int] = Field(None, description="Number of segments (optional - Gemini decides if not provided)", ge=10, le=200, example=50)
    allow_dialogue: Optional[bool] = Field(True, description="Allow dialogue in the film (default: True)")
    film_style: Optional[str] = Field("cinematic drama", description="Style of film", example="cinematic drama")

@router.post("/generate-short-film")
async def generate_short_film_route(
    payload: GenerateShortFilmRequest,
    current_user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """
    🎬 Generate professional short film content using Gemini 3 Pro with thinking mode.
    
    Create cinematic short films with:
    - 🎭 Strong narrative arc (beginning, middle, end)
    - 🎨 Professional cinematography and visual storytelling
    - 💬 Natural dialogue (optional)
    - 🎯 Emotional depth and character development
    - 📽️ Three-act structure
    - 🎬 Cinematic camera work
    
    **Film Styles:**
    - "cinematic drama" - Emotional, character-driven stories
    - "thriller" - Suspenseful, tension-filled narratives
    - "romance" - Love stories with emotional depth
    - "sci-fi" - Futuristic, imaginative concepts
    - "horror" - Scary, atmospheric stories
    - "comedy" - Funny, lighthearted films
    - "mystery" - Intriguing, puzzle-like narratives
    
    **Segment Count:**
    - Short films: 20-40 segments (2.5-5 minutes)
    - Medium films: 40-70 segments (5-9 minutes)
    - Longer films: 70-100 segments (9-13 minutes)
    - Or let Gemini decide the optimal length
    
    **With Characters:**
    - Provide character_ids to use your saved characters
    - Characters maintain visual consistency
    - Supports multi-character films
    
    **Without Characters:**
    - Gemini creates characters as needed for the story
    
    **Example:**
    ```json
    {
      "idea": "A lonely robot discovers the meaning of friendship",
      "character_ids": ["char_robot_xxx"],
      "num_segments": 50,
      "allow_dialogue": true,
      "film_style": "sci-fi"
    }
    ```
    
    **Returns:**
    - Complete short film script with segments
    - Cinematic camera descriptions
    - Three-act structure
    - Emotional arc
    - Visual storytelling
    """
    return screenwriter_controller.generate_short_film(
        idea=payload.idea,
        character_ids=payload.character_ids,
        num_segments=payload.num_segments,
        allow_dialogue=payload.allow_dialogue,
        film_style=payload.film_style
    )


# ---------- CHARACTER MANAGEMENT (NEW FLOW) ----------

# Pydantic Models for Character Management
class AnalyzeCharacterRequest(BaseModel):
    character_name: str = Field(..., description="Name of the character to analyze", example="Floof")


# Removed CreateCharacterRequest - now using Form data with file upload


class UpdateCharacterRequest(BaseModel):
    character_name: Optional[str] = Field(None, description="Updated character name")
    voice_type: Optional[str] = Field(None, description="Updated voice type")
    keywords: Optional[List[str]] = Field(None, description="Updated keywords")
    metadata: Optional[dict] = Field(None, description="Updated metadata")


class SearchCharactersRequest(BaseModel):
    query: Optional[str] = Field(None, description="Text search query for character name", example="Floof")
    voice_type: Optional[str] = Field(None, description="Filter by voice type", example="Soft and High-Pitched")
    keywords: Optional[List[str]] = Field(None, description="Filter by keywords", example=["cute"])
    skip: Optional[int] = Field(0, description="Number of records to skip", ge=0)
    limit: Optional[int] = Field(100, description="Maximum number of records to return", ge=1, le=1000)


@router.post("/characters/analyze")
async def analyze_character_route(
    image: UploadFile = File(..., description="Character image file"),
    character_name: str = Form(..., description="Name of the character"),
    can_speak: bool = Form(..., description="Can the character speak human language? true = can speak words, false = only creature sounds"),
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    """
    🔍 Analyze character image and get AI suggestions
    
    **Protected endpoint - requires authentication**
    
    **Step 1 of 2-step character creation process**
    
    Upload a character image and get AI-powered suggestions for:
    - **Subject (DETAILED visual description of how the character looks - AI-DETECTED from image)**
    - Gender detection
    - Voice description (creative, detailed - format based on can_speak)
    - Comprehensive keywords (AI-analyzed)
    
    **IMPORTANT: can_speak parameter determines voice description format:**
    - can_speak = true → Voice description includes accent (British, American, etc.)
    - can_speak = false → Voice description describes creature sounds only
    
    **Subject is AI-detected:** Gemini analyzes the image and generates a DETAILED description of how the character looks, including type, features, colors, and style (10-30 words). This helps with consistent character representation in video generation. No need to provide it as input!
    
    The user can then review and edit these suggestions before creating the character.
    
    **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Input:**
    ```
    image: [file]
    character_name: "Floof"
    can_speak: false
    ```
    
    **Returns (NO character_id - generated in create step):**
    ```json
    {
      "character_name": "Floof",
      "subject": "A fluffy pink creature with big round eyes, small body, soft fur, and adorable innocent expression",
      "gender": "creature",
      "voice_description": "Soft high-pitched and playful creature sounds",
      "keywords": "cute, fluffy, small, friendly, ...",
      "can_speak": false
    }
    ```
    """
    from app.controllers.character_controller import character_controller
    return await character_controller.analyze_character_image(image, character_name, can_speak)


@router.post("/characters/create")
async def create_character_route(
    image: UploadFile = File(..., description="Character image file"),
    character_name: str = Form(..., description="Name of the character"),
    subject: str = Form(..., description="Detailed visual description of how the character looks (from analyze step)", example="A fluffy pink creature with big round eyes, small body, soft fur, and adorable innocent expression"),
    gender: str = Form(..., description="Gender: male/female/non-binary/creature/undefined"),
    voice_description: str = Form(..., description="Voice description (format depends on can_speak: with accent if true, creature sounds if false)"),
    keywords: str = Form(..., description="Comma-separated keywords string (max 500 chars)"),
    is_private: bool = Form(True, description="Private (true) = only you can see, Public (false) = everyone can see"),
    can_speak: bool = Form(False, description="Can speak human language (true) or only creature sounds (false, default)"),
    current_user: dict = Depends(get_current_active_user)
) -> dict:
    """
    💾 Create a new character with encrypted storage
    
    **Protected endpoint - requires authentication**
    
    **Step 2 of 2-step character creation process**
    
    After analyzing the character (Step 1), create the character with:
    - **Character ID auto-generated** (format: char_charactername_uuid)
    - User-reviewed/edited data from analyze step
    - Image upload to Cloudinary
    - Encrypted storage in MongoDB
    - **user_id automatically extracted from auth token**
    
    **Headers:**
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Input Format (from analyze output, NO character_id needed):**
    ```
    character_name: "Floof"
    subject: "A fluffy pink creature with big round eyes, small body, soft fur, and adorable innocent expression"
    gender: "creature"
    voice_description: "Soft high-pitched and playful creature sounds"
    keywords: "cute, fluffy, small, friendly, ..."
    can_speak: false
    is_private: true
    ```
    
    **What happens:**
    1. character_id auto-generated (char_charactername_uuid)
    2. user_id extracted from JWT token (automatic)
    3. Image uploaded to Cloudinary (with thumbnail generation)
    4. Sensitive data encrypted (character_id, cloudinary_public_id)
    5. Character saved to MongoDB with user_id
    6. Returns character data with public URLs and generated character_id
    
    **Security:**
    - character_id: Encrypted with Fernet
    - cloudinary_public_id: Encrypted with Fernet
    - user_id: Automatically from authenticated user
    - Only decrypted for authorized requests
    """
    from app.controllers.character_controller import character_controller
    
    # Extract user_id from authenticated user
    user_id = current_user["user_id"]
    
    return await character_controller.create_character(
        image=image,
        character_name=character_name,
        subject=subject,
        gender=gender,
        voice_description=voice_description,
        keywords=keywords,
        is_private=is_private,
        can_speak=can_speak,
        user_id=user_id
    )


@router.get("/characters")
async def get_all_characters_route(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[str] = None,
    current_user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """
    📋 Get all characters with pagination and privacy filtering
    
    **Public endpoint - authentication optional**
    
    Returns characters based on privacy settings:
    - **Authenticated users**: See their own characters (private + public) + all public characters from others
    - **Unauthenticated users**: See only public characters
    
    **Privacy Logic:**
    - Private characters (is_private=true): Only visible to creator
    - Public characters (is_private=false): Visible to everyone
    
    **Pagination:**
    - skip: Number of records to skip (default: 0)
    - limit: Maximum records to return (default: 100, max: 1000)
    
    **Filtering:**
    - user_id: Optional filter by specific user (shows only that user's characters)
    
    **Headers (optional):**
    ```
    Authorization: Bearer <access_token>
    ```
    
    **Example Responses:**
    
    Authenticated user sees:
    - Their own private characters
    - Their own public characters
    - All public characters from other users
    
    Unauthenticated user sees:
    - Only public characters from all users
    """
    from app.controllers.character_controller import character_controller
    
    # Extract current_user_id if authenticated
    current_user_id = current_user.get("user_id") if current_user else None
    
    return character_controller.get_all_characters(
        skip=skip,
        limit=limit,
        user_id=user_id,
        current_user_id=current_user_id
    )


@router.get("/characters/{character_id}")
async def get_character_route(character_id: str) -> dict:
    """
    🔍 Get a specific character by ID
    
    Returns complete character data including:
    - Decrypted character_id and cloudinary_public_id
    - Full metadata
    - Image URLs
    - Keywords and voice type
    
    **Note:** character_id is the decrypted UUID, not the MongoDB _id
    """
    from app.controllers.character_controller import character_controller
    return character_controller.get_character_by_id(character_id)


@router.put("/characters/{character_id}")
async def update_character_route(
    character_id: str,
    payload: UpdateCharacterRequest
) -> dict:
    """
    ✏️ Update a character
    
    Update character information:
    - character_name
    - voice_type
    - keywords
    - metadata
    
    **Note:** Image updates not yet implemented (coming soon)
    """
    from app.controllers.character_controller import character_controller
    return await character_controller.update_character(
        character_id=character_id,
        updated_data=payload.dict(exclude_none=True)
    )


@router.delete("/characters/{character_id}")
async def delete_character_route(character_id: str) -> dict:
    """
    🗑️ Delete a character
    
    Deletes character from:
    1. Cloudinary (removes image)
    2. MongoDB (removes document)
    
    **Note:** This action cannot be undone
    """
    from app.controllers.character_controller import character_controller
    return await character_controller.delete_character(character_id)


@router.post("/characters/search")
async def search_characters_route(payload: SearchCharactersRequest) -> dict:
    """
    🔎 Search characters
    
    Search characters by:
    - Text query (searches character_name)
    - Voice type filter
    - Keywords filter
    
    **Returns:** Paginated list of matching characters
    """
    from app.controllers.character_controller import character_controller
    return character_controller.search_characters(
        query=payload.query,
        voice_type=payload.voice_type,
        keywords=payload.keywords,
        skip=payload.skip,
        limit=payload.limit
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
    idea: str = Field(
        ..., 
        description="The daily life moment or situation for the character(s) to experience", 
        example="Character sees his reflection in a puddle and gets scared"
    )
    character_id: Optional[str] = Field(
        None,
        description="Character ID from database (e.g., char_xxx). Required for single character. System automatically fetches: character_name, voice_description, gender, keywords, cloudinary_url, can_speak. Checks privacy permissions.",
        example="char_a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    )
    character_ids: Optional[List[str]] = Field(
        None,
        description="Array of character IDs for multi-character stories. Required for multiple characters. System fetches all details automatically for each character including speech capabilities.",
        example=["char_xxx", "char_yyy"]
    )
    num_segments: Optional[int] = Field(
        None, 
        description="Number of video segments to generate. Each segment is ~8 seconds. If not provided, Gemini will automatically determine the optimal number based on the story. Can generate unlimited segments.", 
        ge=1, 
        example=7
    )

@router.post("/generate-daily-character")
async def generate_daily_character_route(
    payload: GenerateDailyCharacterRequest,
    current_user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """
    Generate daily character life content for Instagram.
    
    **NEW: Character ID Support - Simplified Input!**
    
    Now you can just provide a character_id and the system automatically fetches:
    - Character name
    - Voice description (creature_language)
    - Gender
    - Keywords
    - Cloudinary URL (for video generation)
    
    **Two Ways to Use:**
    
    **Option 1: Character ID (Recommended - Simple!)**
    ```json
    {
      "idea": "Character sees reflection and gets scared",
      "character_id": "char_xxx",
      "num_segments": 7
    }
    ```
    
    **Option 2: Multiple Character IDs**
    ```json
    {
      "idea": "Two characters have an adventure",
      "character_ids": ["char_xxx", "char_yyy"],
      "num_segments": 7
    }
    ```
    
    **Option 3: Manual Input (Legacy)**
    ```json
    {
      "idea": "Character sees reflection and gets scared",
      "character_name": "Floof",
      "creature_language": "Soft and High-Pitched",
      "num_segments": 7
    }
    ```
    
    **Privacy Rules:**
    - Public characters: Anyone can use
    - Private characters: Only owner can use
    - Unauthenticated users: Can only use public characters
    
    **Headers (optional for public characters):**
    ```
    Authorization: Bearer <access_token>
    ```
    
    Response includes:
    - Story segments with character details
    - Character metadata (for video generation)
    - Creature sound descriptions
    - Scene descriptions
    """
    from app.services.character_service import character_service
    
    # Get user_id if authenticated
    user_id = current_user.get("user_id") if current_user else None
    
    # character_id or character_ids is required
    if not payload.character_id and not payload.character_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="character_id (single character) or character_ids (multiple characters) is required. Please create a character first using /api/characters/create"
        )
    
    try:
        # Determine which character IDs to use
        if payload.character_ids:
            character_ids = payload.character_ids
        elif payload.character_id:
            character_ids = [payload.character_id]
        else:
            character_ids = []
        
        # Fetch and validate each character
        characters = []
        character_names = []
        creature_languages = []
        
        for char_id in character_ids:
            try:
                # Get character from database
                character = character_service.get_character_by_id(char_id)
            except ValueError as e:
                # Character not found
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Character '{char_id}' not found in database. Please create the character first using /api/characters/create or verify the character_id is correct. If the character exists but still cannot be fetched, please contact support."
                )
            
            # Check privacy permissions
            if character.get("is_private"):
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Character '{char_id}' is private. Authentication required."
                    )
                if character.get("user_id") != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Character '{char_id}' is private and belongs to another user."
                    )
            
            # Character is accessible - extract details
            characters.append(character)
            character_names.append(character["character_name"])
            creature_languages.append(character["voice_description"])
            
            print(f"✅ Using character: {character['character_name']} ({char_id})")
        
        # Build character_name and creature_language strings
        character_name = ", ".join(character_names)
        creature_language = ", ".join(creature_languages)
        
        # Determine if ANY character can speak (if any can, allow dialogue)
        allow_dialogue = any(char.get("can_speak", False) for char in characters)
        
        print(f"🗣️  Speech capability: {'Enabled' if allow_dialogue else 'Disabled (creature sounds only)'}")
        
        # Generate content with character details
        content = screenwriter_controller.generate_daily_character_content(
            idea=payload.idea,
            character_name=character_name,
            creature_language=creature_language,
            num_segments=payload.num_segments,
            allow_dialogue=allow_dialogue,  # Automatically determined from character
            num_characters=len(characters)  # Pass the actual number of characters
        )
        
        # Add character metadata to response for video generation
        result["character_metadata"] = {
            "character_ids": character_ids,
            "characters": [
                {
                    "character_id": char["character_id"],
                    "character_name": char["character_name"],
                    "cloudinary_url": char["cloudinary_url"],
                    "gender": char["gender"],
                    "voice_description": char["voice_description"],
                    "can_speak": char.get("can_speak", False)
                }
                for char in characters
            ]
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}. If this persists, please contact support."
        )


@router.post("/v2/generate-daily-character")
async def generate_daily_character_v2_route(
    payload: GenerateDailyCharacterRequest,
    current_user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """
    Generate daily character life content using Gemini 3 Pro with thinking mode (V2).
    
    🚀 ENHANCED VERSION with Gemini 3 Pro's extended thinking capabilities!
    
    Improvements over v1:
    - 🧠 Gemini 3 Pro with high thinking budget for better reasoning
    - 🎨 More creative and engaging content
    - 📈 Better story flow and character consistency
    - ♾️ Supports unlimited segments (auto-splits into sets)
    - ⚡ Faster response with optimized processing
    
    Perfect for Instagram pages showcasing a recurring character's daily life.
    Creates relatable, funny, engaging moments with NO dialogue/narration - only creature sounds.
    
    Features:
    - Simple: Just provide idea, character name, and voice type
    - Visual: Pure visual storytelling with creature sounds only
    - Unlimited: Any number of segments (auto-splits into sets of 10)
    - Keyframe-Ready: Designed for use with character images as keyframes
    - Viral: Optimized for Instagram engagement
    
    Character Voice Examples:
    - "Soft and High-Pitched" - Cute, gentle creature sounds
    - "Magical or Otherworldly" - Mystical, ethereal sounds
    - "Muffled and Low" - Deep, grumbly creature sounds
    - Any custom description that fits your character!
    
    Use Cases:
    - Funny reactions (seeing reflection, hearing noise)
    - Relatable struggles (waking up, cooking fails)
    - Character quirks (weird habits, behaviors)
    - Everyday adventures (shopping, commuting)
    - Emotional moments (happy, sad, confused)
    
    Example:
        POST /api/v2/generate-daily-character
        {
            "idea": "Character discovers a mysterious glowing object in the park",
            "character_name": "Floof",
            "creature_language": "Soft and High-Pitched with mystical undertones",
            "num_segments": 15
        }
    
    Response includes:
    - Unlimited segments (8 seconds each)
    - Pure visual storytelling (NO dialogue/narration by default)
    - Creature sound descriptions and timing
    - Scene descriptions for keyframe generation
    - Instagram optimization tips
    - Enhanced creativity from Gemini 3 Pro thinking
    
    Note: Use the character's image as keyframe when generating videos with Veo3
    
    **NEW: Now supports character_id for simplified input!**
    ```json
    {
      "idea": "Character discovers a mysterious glowing object",
      "character_id": "char_xxx",
      "num_segments": 15
    }
    ```
    """
    from app.services.character_service import character_service
    
    # Get user_id if authenticated
    user_id = current_user.get("user_id") if current_user else None
    
    # character_id or character_ids is required
    if not payload.character_id and not payload.character_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="character_id (single character) or character_ids (multiple characters) is required. Please create a character first using /api/characters/create"
        )
    
    try:
        # Determine which character IDs to use
        if payload.character_ids:
            character_ids = payload.character_ids
        elif payload.character_id:
            character_ids = [payload.character_id]
        else:
            character_ids = []
        
        # Fetch and validate each character
        characters = []
        character_names = []
        creature_languages = []
        
        for char_id in character_ids:
            try:
                # Get character from database
                character = character_service.get_character_by_id(char_id)
            except ValueError as e:
                # Character not found
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Character '{char_id}' not found in database. Please create the character first using /api/characters/create or verify the character_id is correct. If the character exists but still cannot be fetched, please contact support."
                )
            
            # Check privacy permissions
            if character.get("is_private"):
                if not user_id:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail=f"Character '{char_id}' is private. Authentication required."
                    )
                if character.get("user_id") != user_id:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Character '{char_id}' is private and belongs to another user."
                    )
            
            # Character is accessible - extract details
            characters.append(character)
            character_names.append(character["character_name"])
            creature_languages.append(character["voice_description"])
            
            print(f"✅ Using character: {character['character_name']} ({char_id})")
        
        # Build character_name, creature_language, and subject strings
        character_name = ", ".join(character_names)
        creature_language = ", ".join(creature_languages)
        # Extract subjects for veo_prompt (e.g., "fluffy pink creature, small robot")
        character_subjects = [char.get("subject", "creature") for char in characters]
        character_subject = ", ".join(character_subjects)
        
        # Determine if ANY character can speak (if any can, allow dialogue)
        allow_dialogue = any(char.get("can_speak", False) for char in characters)
        
        print(f"🗣️  Speech capability: {'Enabled' if allow_dialogue else 'Disabled (creature sounds only)'}")
        print(f"📝 Character subject(s): {character_subject}")
        
        # Generate content with character details
        # Note: This returns {"content": {...}}
        content_response = screenwriter_controller.generate_daily_character_content_v2(
            idea=payload.idea,
            character_name=character_name,
            creature_language=creature_language,
            character_subject=character_subject,  # NEW: Pass subject for veo_prompt
            num_segments=payload.num_segments,
            allow_dialogue=allow_dialogue,  # Automatically determined from character
            num_characters=len(characters)  # Pass the actual number of characters
        )
        
        # Build result with content_data containing both content and character_metadata
        # content_response already has {"content": {...}}, so we merge it with character_metadata
        result = {
            "content_data": {
                **content_response,  # This adds "content": {...}
                "character_metadata": {
                    "character_ids": character_ids,
                    "characters": [
                        {
                            "character_id": char["character_id"],
                            "character_name": char["character_name"],
                            "cloudinary_url": char["cloudinary_url"],
                            "gender": char["gender"],
                            "voice_description": char["voice_description"],
                            "can_speak": char.get("can_speak", False)
                        }
                        for char in characters
                    ]
                }
            }
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate content: {str(e)}. If this persists, please contact support."
        )


class GenerateDailyCharacterVideosRequest(BaseModel):
    content_data: dict = Field(
        ..., 
        description="Content from /generate-daily-character-v2. If it contains character_metadata, character images are extracted automatically. No other character fields needed!"
    )
    character_id: Optional[str] = Field(
        None,
        description="[OPTIONAL] Only needed if content_data lacks character_metadata. Character ID from database.",
        example="char_a1b2c3d4-e5f6-7890-abcd-ef1234567890"
    )
    character_ids: Optional[List[str]] = Field(
        None,
        description="[OPTIONAL] Only needed if content_data lacks character_metadata. Array of character IDs for multi-character content.",
        example=["char_xxx", "char_yyy"]
    )
    character_keyframe_uri: Optional[str] = Field(
        None, 
        description="[DEPRECATED - NOT NEEDED] System extracts from character_metadata automatically.", 
        example="gs://your-bucket/characters/floof.png"
    )
    character_keyframe_uris: Optional[List[str]] = Field(
        None, 
        description="[DEPRECATED - NOT NEEDED] System extracts from character_metadata automatically.", 
        example=["gs://bucket/floof.png", "gs://bucket/buddy.png"]
    )
    resolution: Optional[str] = Field(
        "720p", 
        description="Video resolution. Options: '480p' (854x480), '720p' (1280x720, recommended), '1080p' (1920x1080), '4K' (3840x2160)", 
        example="720p"
    )
    aspect_ratio: Optional[str] = Field(
        "9:16", 
        description="Video aspect ratio. Options: '9:16' (vertical/portrait for Instagram/TikTok), '16:9' (horizontal/landscape for YouTube), '1:1' (square for Instagram feed)", 
        example="9:16"
    )
    download: Optional[bool] = Field(
        False, 
        description="Download generated videos to local storage after generation. Useful for backup or local processing."
    )
    auto_merge: Optional[bool] = Field(
        False, 
        description="Automatically merge all segment videos into a single final video after generation. Requires all segments to generate successfully."
    )
    cleanup_segments: Optional[bool] = Field(
        True, 
        description="Delete individual segment video files after successful merge (only applies if auto_merge=true). Saves storage space."
    )
    image_model: Optional[str] = Field(
        "gemini-2.5-flash-image",
        description="Image generation model for creating first and last frames. Options: 'gemini-2.5-flash-image' (stable, recommended, good quality) or 'gemini-3-pro-image-preview' (experimental, latest, may have better quality but less stable)",
        example="gemini-2.5-flash-image"
    )

@router.post("/generate-daily-character-videos")
async def generate_daily_character_videos_route(
    payload: GenerateDailyCharacterVideosRequest,
    current_user: Optional[dict] = Depends(get_current_user)
) -> dict:
    """
    Generate videos for daily character content using character IDs or direct URIs.
    
    **NEW: Character ID Support with Privacy Checking**
    
    Now you can use character IDs instead of direct URIs. The system will:
    1. Fetch character from database
    2. Check privacy permissions (private characters only accessible by owner)
    3. Decrypt Cloudinary URL automatically
    4. Use the URL for video generation
    
    **Privacy Rules:**
    - Public characters (is_private=false): Anyone can use
    - Private characters (is_private=true): Only the owner can use
    - Unauthenticated users: Can only use public characters
    
    **Two Ways to Specify Characters:**
    
    **Option 1: Character ID (Recommended)**
    ```json
    {
      "content_data": {...},
      "character_id": "char_xxx",  // Single character
      "resolution": "720p"
    }
    ```
    
    **Option 2: Multiple Character IDs**
    ```json
    {
      "content_data": {...},
      "character_ids": ["char_xxx", "char_yyy"],  // Multiple characters
      "resolution": "720p"
    }
    ```
    
    **Option 3: Direct URI (Legacy)**
    ```json
    {
      "content_data": {...},
      "character_keyframe_uri": "https://res.cloudinary.com/.../floof.png",
      "resolution": "720p"
    }
    ```
    
    **Example with Character ID:**
    ```json
    {
      "content_data": {
        "title": "First Mirror Fumble",
        "character_name": "Floof",
        "segments": [...]
      },
      "character_id": "char_a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "resolution": "720p",
      "aspect_ratio": "9:16",
      "auto_merge": true
    }
    ```
    
    **Headers (optional for public characters):**
    ```
    Authorization: Bearer <access_token>
    ```
    
    Response includes:
    - Video URLs for each segment
    - Generation status and timing
    - Optional merged final video
    - Failed segments for retry
    """
    from app.services.character_service import character_service
    
    # Get user_id if authenticated
    user_id = current_user.get("user_id") if current_user else None
    
    # Unwrap content_data if it's wrapped in "content" key
    content_data = payload.content_data
    print(f"🔍 Initial content_data keys: {list(content_data.keys())[:10]}")
    
    # Check if character_metadata exists at the top level before unwrapping
    character_metadata_at_top = content_data.get("character_metadata") if "character_metadata" in content_data else None
    
    if "content" in content_data and isinstance(content_data["content"], dict):
        print("📦 Unwrapping content_data from nested 'content' key")
        content_data = content_data["content"]
        print(f"🔍 After unwrap, content_data keys: {list(content_data.keys())[:10]}")
        
        # If character_metadata was at top level, add it back after unwrapping
        if character_metadata_at_top:
            content_data["character_metadata"] = character_metadata_at_top
            print("✅ Preserved character_metadata from top level")
    
    # Check if content_data has character_metadata (from new flow)
    print(f"🔍 Has character_metadata: {'character_metadata' in content_data}")
    
    if "character_metadata" in content_data and content_data["character_metadata"]:
        # New flow: character IDs already resolved in script generation
        character_metadata = content_data["character_metadata"]
        character_ids = character_metadata.get("character_ids", [])
        characters = character_metadata.get("characters", [])
        
        print(f"🎭 Found {len(characters)} character(s) in metadata")
        
        # Build character name to URL mapping
        character_map = {}
        for char in characters:
            char_name = char["character_name"]
            char_url = char["cloudinary_url"]
            character_map[char_name] = char_url
            print(f"   📸 {char_name}: {char_url[:60]}...")
        
        # Process each segment and assign character images based on characters_present
        segments = content_data.get("segments", [])
        for segment in segments:
            characters_present = segment.get("characters_present", [])
            
            if characters_present:
                # Get URLs for characters present in this segment
                segment_character_urls = []
                for char_name in characters_present:
                    if char_name in character_map:
                        segment_character_urls.append(character_map[char_name])
                    else:
                        print(f"⚠️  Warning: Character '{char_name}' in segment {segment.get('segment', '?')} not found in metadata")
                
                # Store character URLs in segment for video generation
                if len(segment_character_urls) == 1:
                    segment["character_keyframe_uri"] = segment_character_urls[0]
                    print(f"   ✅ Segment {segment.get('segment', '?')}: Using {characters_present[0]}")
                elif len(segment_character_urls) > 1:
                    segment["character_keyframe_uris"] = segment_character_urls  # FIX: Use full array, not just first element
                    print(f"   ✅ Segment {segment.get('segment', '?')}: Using {len(segment_character_urls)} characters: {', '.join(characters_present)}")
        
        # Extract all unique character URLs for top-level parameter
        all_character_urls = list(character_map.values())
        
        # Update payload with processed content_data and character URIs
        payload_dict = payload.dict()
        payload_dict["content_data"] = content_data
        
        # Add top-level character_keyframe_uri(s) for controller
        if len(all_character_urls) == 1:
            payload_dict["character_keyframe_uri"] = all_character_urls[0]
            print(f"🔑 Added character_keyframe_uri: {all_character_urls[0][:60]}...")
        else:
            payload_dict["character_keyframe_uri"] = all_character_urls[0]  # Primary character
            payload_dict["character_keyframe_uris"] = all_character_urls
            print(f"🔑 Added character_keyframe_uri (primary): {all_character_urls[0][:60]}...")
            print(f"🔑 Added character_keyframe_uris: {len(all_character_urls)} URLs")
        
        print(f"🎬 Ready to generate videos for {len(segments)} segment(s)")
        print(f"🔍 Payload keys being sent: {list(payload_dict.keys())}")
        return cinematographer_controller.handle_generate_daily_character_videos(payload_dict)
    
    # Resolve character IDs to URIs if provided directly
    elif payload.character_id or payload.character_ids:
        try:
            # Determine which character IDs to use
            if payload.character_ids:
                character_ids = payload.character_ids
            elif payload.character_id:
                character_ids = [payload.character_id]
            else:
                character_ids = []
            
            # Fetch and validate each character
            character_uris = []
            for char_id in character_ids:
                # Get character from database
                character = character_service.get_character_by_id(char_id)
                
                # Check privacy permissions
                if character.get("is_private"):
                    # Private character - only owner can use
                    if not user_id:
                        raise HTTPException(
                            status_code=status.HTTP_401_UNAUTHORIZED,
                            detail=f"Character '{char_id}' is private. Authentication required."
                        )
                    if character.get("user_id") != user_id:
                        raise HTTPException(
                            status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"Character '{char_id}' is private and belongs to another user."
                        )
                
                # Character is accessible - use the decrypted Cloudinary URL
                character_uris.append(character["cloudinary_url"])
                print(f"✅ Character '{char_id}' authorized for user: {user_id or 'public'}")
            
            # Update payload with resolved URIs
            payload_dict = payload.dict()
            if len(character_uris) == 1:
                payload_dict["character_keyframe_uri"] = character_uris[0]
            else:
                payload_dict["character_keyframe_uris"] = character_uris
            
            return cinematographer_controller.handle_generate_daily_character_videos(payload_dict)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to resolve character: {str(e)}"
            )
    else:
        # Legacy mode - direct URIs provided
        return cinematographer_controller.handle_generate_daily_character_videos(payload.dict())


@router.post("/generate-daily-character-videos-with-refs")
async def generate_daily_character_videos_with_refs_route(
    content_data: str = Form(...),  # JSON string of content data
    character_keyframe_uri: str = Form(...),
    resolution: str = Form("720p"),
    aspect_ratio: str = Form("9:16"),
    download: bool = Form(False),
    auto_merge: bool = Form(False),
    cleanup_segments: bool = Form(True),
    reference_images: List[UploadFile] = []  # Multiple reference images
) -> dict:
    """
    Generate videos with additional reference images for better frame generation.
    
    This endpoint accepts multiple reference images (JPG, PNG, WEBP) that will be used
    by Imagen to generate more accurate and consistent frames.
    
    Form Data:
    - content_data: JSON string of content from /generate-daily-character
    - character_keyframe_uri: Main character image URL
    - reference_images: Multiple image files (optional)
    - resolution: Video resolution (default: "720p")
    - aspect_ratio: Video aspect ratio (default: "9:16")
    - download: Download videos locally (default: false)
    - auto_merge: Auto-merge segments (default: false)
    - cleanup_segments: Cleanup after merge (default: true)
    
    Example (using curl):
        curl -X POST "http://localhost:8000/api/generate-daily-character-videos-with-refs" \\
          -F "content_data=@content.json" \\
          -F "character_keyframe_uri=https://cloudinary.com/.../char.png" \\
          -F "reference_images=@ref1.jpg" \\
          -F "reference_images=@ref2.png" \\
          -F "reference_images=@ref3.webp" \\
          -F "aspect_ratio=16:9"
    """
    import json
    
    # Parse content_data JSON
    try:
        content_data_dict = json.loads(content_data)
    except json.JSONDecodeError:
        return {"error": "Invalid JSON in content_data"}
    
    # Read reference images into memory
    reference_images_data = []
    if reference_images:
        print(f"📥 Received {len(reference_images)} reference images")
        for idx, img_file in enumerate(reference_images):
            try:
                img_data = await img_file.read()
                reference_images_data.append(img_data)
                print(f"✅ Reference image {idx+1}: {img_file.filename} ({len(img_data)} bytes)")
            except Exception as e:
                print(f"⚠️ Failed to read reference image {idx+1}: {str(e)}")
    
    # Build payload
    payload = {
        "content_data": content_data_dict,
        "character_keyframe_uri": character_keyframe_uri,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "download": download,
        "auto_merge": auto_merge,
        "cleanup_segments": cleanup_segments,
        "reference_images": reference_images_data  # Add reference images
    }
    
    return cinematographer_controller.handle_generate_daily_character_videos(payload)


class GenerateDailyCharacterVideosWithReferencesRequest(BaseModel):
    content_data: dict = Field(
        ..., 
        description="Complete output from /generate-daily-character or /generate-daily-character-v2 endpoint containing all segments and character information"
    )
    character_keyframe_uri: str = Field(
        ..., 
        description="Character image URI used as reference image for character consistency. Supports: GCS (gs://bucket/image.png), HTTP/HTTPS URLs, Cloudinary URLs", 
        example="gs://your-bucket/characters/floof.png"
    )
    resolution: Optional[str] = Field(
        "720p", 
        description="Video resolution. Options: '480p' (854x480), '720p' (1280x720, recommended), '1080p' (1920x1080), '4K' (3840x2160)", 
        example="720p"
    )
    aspect_ratio: Optional[str] = Field(
        "9:16", 
        description="Video aspect ratio. Options: '9:16' (vertical/portrait for Instagram/TikTok), '16:9' (horizontal/landscape for YouTube), '1:1' (square for Instagram feed)", 
        example="9:16"
    )
    download: Optional[bool] = Field(
        False, 
        description="Download generated videos to local storage after generation"
    )
    auto_merge: Optional[bool] = Field(
        False, 
        description="Automatically merge all segment videos into a single final video after generation"
    )
    cleanup_segments: Optional[bool] = Field(
        True, 
        description="Delete individual segment video files after successful merge (only applies if auto_merge=true)"
    )
    image_model: Optional[str] = Field(
        "gemini-2.5-flash-image",
        description="Image generation model for creating frames. Options: 'gemini-2.5-flash-image' (stable, recommended) or 'gemini-3-pro-image-preview' (experimental, latest)",
        example="gemini-2.5-flash-image"
    )

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


# ---------- IMAGE EDITING & GENERATION ROUTES ----------

class GenerateSingleImageRequest(BaseModel):
    prompt: str = Field(..., description="Text description of the image to generate")
    aspect_ratio: Optional[str] = Field("16:9", description="Image aspect ratio (1:1, 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9)")
    resolution: Optional[str] = Field("2K", description="Image resolution (1K, 2K, 4K)")
    use_google_search: Optional[bool] = Field(False, description="Enable Google Search for current information")
    model: Optional[str] = Field("gemini-2.5-flash-image", description="Gemini model to use")


class GenerateBulkImagesRequest(BaseModel):
    prompts: List[str] = Field(..., description="List of text prompts for image generation", min_items=1)
    aspect_ratio: Optional[str] = Field("16:9", description="Image aspect ratio")
    resolution: Optional[str] = Field("2K", description="Image resolution")
    use_google_search: Optional[bool] = Field(False, description="Enable Google Search")
    output_dir: Optional[str] = Field("generated_images", description="Directory to save images")
    delay_between_requests: Optional[float] = Field(2.0, description="Delay in seconds between requests (for rate limiting)")
    model: Optional[str] = Field("gemini-2.5-flash-image", description="Gemini model to use")


class EditSingleImageRequest(BaseModel):
    image_path: str = Field(..., description="Path to the image to edit")
    edit_prompt: str = Field(..., description="Text description of the edit to make")
    aspect_ratio: Optional[str] = Field("16:9", description="Output aspect ratio")
    resolution: Optional[str] = Field("2K", description="Output resolution")
    model: Optional[str] = Field("gemini-2.5-flash-image", description="Gemini model to use")


class EditBulkImagesRequest(BaseModel):
    image_paths: List[str] = Field(..., description="List of paths to images to edit", min_items=1)
    edit_prompts: List[str] = Field(..., description="List of edit prompts (one per image, or single prompt for all)", min_items=1)
    aspect_ratio: Optional[str] = Field("16:9", description="Output aspect ratio")
    resolution: Optional[str] = Field("2K", description="Output resolution")
    output_dir: Optional[str] = Field("edited_images", description="Directory to save edited images")
    delay_between_requests: Optional[float] = Field(2.0, description="Delay in seconds between requests")
    model: Optional[str] = Field("gemini-2.5-flash-image", description="Gemini model to use")


@router.post("/images/generate")
async def generate_single_image_route(payload: GenerateSingleImageRequest) -> dict:
    """
    🎨 Generate a single image from a text prompt using Gemini.
    
    **Features:**
    - Text-to-image generation
    - Optional Google Search integration for current information
    - Multiple aspect ratios and resolutions
    - Returns both image path and optional text response
    
    **Example:**
    ```json
    {
      "prompt": "A cute fluffy pink creature with big curious eyes in a sunny park",
      "aspect_ratio": "16:9",
      "resolution": "2K",
      "use_google_search": false
    }
    ```
    
    **Response:**
    ```json
    {
      "success": true,
      "image_path": "generated_images/image_20260220_143022.png",
      "text_response": "Generated a cute creature...",
      "prompt": "A cute fluffy pink creature..."
    }
    ```
    """
    from app.services.image_edit_service import get_image_edit_service
    
    try:
        service = get_image_edit_service(model=payload.model)
        
        image, image_path, text_response = service.generate_single_image(
            prompt=payload.prompt,
            aspect_ratio=payload.aspect_ratio,
            resolution=payload.resolution,
            use_google_search=payload.use_google_search
        )
        
        return {
            "success": True,
            "image_path": image_path,
            "text_response": text_response,
            "prompt": payload.prompt,
            "aspect_ratio": payload.aspect_ratio,
            "resolution": payload.resolution
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "prompt": payload.prompt
        }


@router.post("/images/generate-bulk")
async def generate_bulk_images_route(payload: GenerateBulkImagesRequest) -> dict:
    """
    🎨 Generate multiple images iteratively (free tier friendly).
    
    **Features:**
    - Batch image generation with rate limiting
    - Automatic delay between requests
    - Individual success/failure tracking
    - Progress logging
    
    **Free Tier Optimization:**
    - Processes images one at a time
    - Configurable delay between requests (default: 2s)
    - Continues on individual failures
    
    **Example:**
    ```json
    {
      "prompts": [
        "A sunny beach with palm trees",
        "A snowy mountain peak at sunset",
        "A bustling city street at night"
      ],
      "aspect_ratio": "16:9",
      "resolution": "2K",
      "delay_between_requests": 2.0
    }
    ```
    
    **Response:**
    ```json
    {
      "success": true,
      "total_images": 3,
      "success_count": 3,
      "failed_count": 0,
      "results": [
        {
          "index": 1,
          "prompt": "A sunny beach...",
          "status": "completed",
          "image_path": "generated_images/image_1_20260220_143022.png",
          "text_response": "..."
        }
      ]
    }
    ```
    """
    from app.services.image_edit_service import get_image_edit_service
    
    try:
        service = get_image_edit_service(model=payload.model)
        
        results = service.generate_bulk_images(
            prompts=payload.prompts,
            aspect_ratio=payload.aspect_ratio,
            resolution=payload.resolution,
            use_google_search=payload.use_google_search,
            output_dir=payload.output_dir,
            delay_between_requests=payload.delay_between_requests
        )
        
        success_count = sum(1 for r in results if r["status"] == "completed")
        failed_count = sum(1 for r in results if r["status"] == "failed")
        
        return {
            "success": True,
            "total_images": len(payload.prompts),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results,
            "output_dir": payload.output_dir
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_images": len(payload.prompts)
        }


@router.post("/images/edit")
async def edit_single_image_route(payload: EditSingleImageRequest) -> dict:
    """
    ✏️ Edit an existing image using a text prompt.
    
    **Features:**
    - Text-based image editing
    - Maintains image context
    - Multiple edit operations possible
    - Returns edited image path
    
    **Example:**
    ```json
    {
      "image_path": "generated_images/image_20260220_143022.png",
      "edit_prompt": "Change the sky to sunset colors with orange and pink",
      "aspect_ratio": "16:9",
      "resolution": "2K"
    }
    ```
    
    **Response:**
    ```json
    {
      "success": true,
      "input_image": "generated_images/image_20260220_143022.png",
      "output_path": "edited_images/edited_20260220_143045.png",
      "text_response": "Changed sky to sunset colors...",
      "edit_prompt": "Change the sky to sunset colors..."
    }
    ```
    """
    from app.services.image_edit_service import get_image_edit_service
    import os
    
    # Validate image exists
    if not os.path.exists(payload.image_path):
        return {
            "success": False,
            "error": f"Image not found: {payload.image_path}",
            "input_image": payload.image_path
        }
    
    try:
        service = get_image_edit_service(model=payload.model)
        
        edited_image, output_path, text_response = service.edit_image_with_prompt(
            image_path=payload.image_path,
            edit_prompt=payload.edit_prompt,
            aspect_ratio=payload.aspect_ratio,
            resolution=payload.resolution
        )
        
        return {
            "success": True,
            "input_image": payload.image_path,
            "output_path": output_path,
            "text_response": text_response,
            "edit_prompt": payload.edit_prompt,
            "aspect_ratio": payload.aspect_ratio,
            "resolution": payload.resolution
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "input_image": payload.image_path,
            "edit_prompt": payload.edit_prompt
        }


@router.post("/images/edit-bulk")
async def edit_bulk_images_route(payload: EditBulkImagesRequest) -> dict:
    """
    ✏️ Edit multiple images iteratively (free tier friendly).
    
    **Features:**
    - Batch image editing with rate limiting
    - Single prompt for all images OR individual prompts
    - Automatic delay between requests
    - Individual success/failure tracking
    
    **Free Tier Optimization:**
    - Processes images one at a time
    - Configurable delay between requests (default: 2s)
    - Continues on individual failures
    
    **Example (single prompt for all):**
    ```json
    {
      "image_paths": [
        "generated_images/image_1.png",
        "generated_images/image_2.png",
        "generated_images/image_3.png"
      ],
      "edit_prompts": ["Add a rainbow in the sky"],
      "aspect_ratio": "16:9",
      "resolution": "2K",
      "delay_between_requests": 2.0
    }
    ```
    
    **Example (individual prompts):**
    ```json
    {
      "image_paths": [
        "generated_images/image_1.png",
        "generated_images/image_2.png"
      ],
      "edit_prompts": [
        "Make it daytime",
        "Make it nighttime"
      ],
      "delay_between_requests": 2.0
    }
    ```
    
    **Response:**
    ```json
    {
      "success": true,
      "total_images": 3,
      "success_count": 3,
      "failed_count": 0,
      "results": [
        {
          "index": 1,
          "input_image": "generated_images/image_1.png",
          "edit_prompt": "Add a rainbow...",
          "status": "completed",
          "output_path": "edited_images/edited_1_20260220_143022.png",
          "text_response": "..."
        }
      ]
    }
    ```
    """
    from app.services.image_edit_service import get_image_edit_service
    import os
    
    # Validate all images exist
    missing_images = [path for path in payload.image_paths if not os.path.exists(path)]
    if missing_images:
        return {
            "success": False,
            "error": f"Images not found: {', '.join(missing_images)}",
            "total_images": len(payload.image_paths)
        }
    
    # Validate prompt count
    if len(payload.edit_prompts) != 1 and len(payload.edit_prompts) != len(payload.image_paths):
        return {
            "success": False,
            "error": f"Number of prompts ({len(payload.edit_prompts)}) must be 1 or match number of images ({len(payload.image_paths)})",
            "total_images": len(payload.image_paths)
        }
    
    try:
        service = get_image_edit_service(model=payload.model)
        
        results = service.edit_bulk_images(
            image_paths=payload.image_paths,
            edit_prompts=payload.edit_prompts,
            aspect_ratio=payload.aspect_ratio,
            resolution=payload.resolution,
            output_dir=payload.output_dir,
            delay_between_requests=payload.delay_between_requests
        )
        
        success_count = sum(1 for r in results if r["status"] == "completed")
        failed_count = sum(1 for r in results if r["status"] == "failed")
        
        return {
            "success": True,
            "total_images": len(payload.image_paths),
            "success_count": success_count,
            "failed_count": failed_count,
            "results": results,
            "output_dir": payload.output_dir
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "total_images": len(payload.image_paths)
        }
