import time
import requests
import os
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from app.config.settings import settings
from app.connectors.genai_connector import get_genai_client


def generate_video_from_payload(payload: dict):
    """
    Calls Vertex AI Veo-3 model and generates a video using google-genai client.
    """

    client = get_genai_client()

    # Retry configuration for transient service errors (503 / UNAVAILABLE)
    max_retries = 3
    backoff_base = 5  # seconds, exponential backoff multiplier

    # Extract required + optional params
    prompt = payload.get("prompt")
    if not prompt:
        raise ValueError("Missing 'prompt' in request payload")

    duration = payload.get("durationSeconds", 8)
    resolution = payload.get("resolution", "720p")
    aspect_ratio = payload.get("aspectRatio", "9:16")
    # Note: generate_audio and sample_count are not supported in GenerateVideosConfig

    def _is_transient_service_error(exc_or_obj) -> bool:
        """Rudimentary check for transient service errors (503 / UNAVAILABLE)."""
        try:
            text = str(exc_or_obj)
            if "UNAVAILABLE" in text or "503" in text or "service is currently unavailable" in text.lower():
                return True
        except Exception:
            pass
        return False

    last_exception = None
    for attempt in range(max_retries):
        try:
            # Start async video generation
            operation = client.models.generate_videos(
                model=settings.VIDEO_GENERATION_MODEL,
                # model="veo-3.0-fast-generate-preview",
                prompt=prompt,
                config=types.GenerateVideosConfig(
                    duration_seconds=duration,
                    resolution=resolution,
                    aspect_ratio=aspect_ratio,
                )
            )

            # Poll until completion
            while not operation.done:
                print("Waiting for video generation to complete...")
                time.sleep(10)
                operation = client.operations.get(operation)

            # Check for errors in the operation
            if operation.error:
                # If the operation error looks transient, raise to trigger a retry
                if _is_transient_service_error(operation.error) and attempt < max_retries - 1:
                    wait = backoff_base * (2 ** attempt)
                    print(f"⚠️ Transient error detected (attempt {attempt+1}/{max_retries}), retrying after {wait}s: {operation.error}")
                    time.sleep(wait)
                    continue
                raise Exception(f"Video generation failed: {operation.error}")

            # If we reach here, operation completed successfully (no operation.error)
            last_exception = None
            break

        except Exception as e:
            last_exception = e
            # If it's a transient service error, retry (with backoff)
            if _is_transient_service_error(e) and attempt < max_retries - 1:
                wait = backoff_base * (2 ** attempt)
                print(f"⚠️ Transient error during generation (attempt {attempt+1}/{max_retries}), retrying after {wait}s: {e}")
                time.sleep(wait)
                continue
            # Non-retryable or exhausted retries -> re-raise after loop
            raise

    # If we exhausted retries and still have an exception, raise a clear error
    if last_exception is not None:
        raise Exception(f"Video generation failed after {max_retries} attempts: {last_exception}")

    # Collect results - handle the actual response structure with null checking
    results = []
    
    # Check if response exists
    if not operation.response:
        raise Exception("Video generation failed: No response received")
    
    # Try to extract generated videos
    if hasattr(operation.response, 'generated_videos') and operation.response.generated_videos:
        for generated in operation.response.generated_videos:
            if generated and hasattr(generated, 'video') and generated.video:
                # Extract URI from Video object - return just the URI string
                video_uri = generated.video.uri if hasattr(generated.video, 'uri') else str(generated.video)
                if video_uri:
                    results.append(video_uri)
    elif hasattr(operation.response, 'videos') and operation.response.videos:
        # Handle alternative response structure
        for video in operation.response.videos:
            if video:
                video_uri = video.uri if hasattr(video, 'uri') else str(video)
                if video_uri:
                    results.append(video_uri)
    else:
        # Log the actual response structure for debugging
        print(f"Unexpected response structure: {operation.response}")
        print(f"Response type: {type(operation.response)}")
        print(f"Response attributes: {dir(operation.response)}")
        
        # Try to get any video data from the response
        response_str = str(operation.response)
        if response_str and response_str != "None":
            results.append(response_str)
        else:
            raise Exception("Video generation failed: No video data in response")
    
    # Ensure we have at least one result
    if not results:
        raise Exception("Video generation failed: No video URLs generated")

    return results


def download_video(video_url: str, filename: str = None, download_dir: str = "downloads"):
    """
    Download video from Google's servers using multiple authentication methods
    
    Args:
        video_url: The video URL from Google GenAI
        filename: Optional custom filename (defaults to auto-generated)
        download_dir: Directory to save the video (defaults to 'downloads')
    
    Returns:
        str: Path to the downloaded file
    """
    # Create download directory if it doesn't exist
    os.makedirs(download_dir, exist_ok=True)
    
    # Generate filename if not provided
    if not filename:
        timestamp = int(time.time())
        filename = f"generated_video_{timestamp}.mp4"
    
    # Ensure filename has .mp4 extension
    if not filename.endswith('.mp4'):
        filename += '.mp4'
    
    filepath = os.path.join(download_dir, filename)
    
    # Try multiple authentication methods
    auth_methods = [
        {"Authorization": f"Bearer {settings.GOOGLE_STUDIO_API_KEY}"},
        {"X-Goog-Api-Key": settings.GOOGLE_STUDIO_API_KEY},
        {}  # No auth as fallback
    ]

    # Retry config for transient HTTP errors
    max_retries = 3
    backoff_base = 3  # seconds
    transient_statuses = {429, 502, 503}

    for i, headers in enumerate(auth_methods):
        auth_type = "Bearer token" if "Authorization" in headers else "API Key header" if "X-Goog-Api-Key" in headers else "No authentication"
        print(f"Attempt {i+1}: Downloading with {auth_type}...")
        print(f"URL: {video_url}")

        for attempt in range(max_retries):
            try:
                if attempt > 0:
                    wait = backoff_base * (2 ** (attempt - 1))
                    print(f"🔁 Transient issue, retry {attempt+1}/{max_retries} for auth '{auth_type}' after {wait}s...")
                    time.sleep(wait)

                # Make the GET request with streaming enabled
                response = requests.get(video_url, headers=headers, stream=True, timeout=60)

                if response.status_code == 200:
                    # Success! Download the file
                    total_size = int(response.headers.get('content-length', 0))
                    downloaded = 0

                    print("✅ Authentication successful, downloading...")
                    with open(filepath, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                                downloaded += len(chunk)
                                if total_size > 0:
                                    progress = (downloaded / total_size) * 100
                                    print(f"\rDownload progress: {progress:.1f}%", end="", flush=True)

                    print(f"\n✅ Video downloaded successfully: {filepath}")
                    file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
                    print(f"📊 File size: {file_size_mb:.2f} MB")
                    return filepath

                # If response is a transient error, retry up to max_retries
                if response.status_code in transient_statuses:
                    # If not last attempt, retry
                    text_snippet = response.text[:200]
                    print(f"⚠️ Transient HTTP {response.status_code} received: {text_snippet}")
                    if attempt < max_retries - 1:
                        continue
                    else:
                        # exhausted retries for this auth method, break to next auth
                        print(f"🔄 Exhausted retries for auth '{auth_type}' (status {response.status_code}). Trying next auth method...")
                        break

                # Non-transient non-200 response: don't retry for this auth method
                print(f"❌ Failed with status {response.status_code}: {response.text[:200]}")
                break

            except requests.exceptions.RequestException as e:
                # Treat network errors as transient and retry
                print(f"❌ Request exception: {str(e)}")
                if attempt < max_retries - 1:
                    print("🔄 Retrying request due to network error...")
                    continue
                else:
                    print("🔄 Exhausted retries for network errors on this auth method. Trying next auth method...")
                    break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                # Don't retry for unknown exceptions; try next auth method
                break

        # If we reach here and didn't return, try next authentication method
        if i < len(auth_methods) - 1:
            print("🔄 Trying next authentication method...")
            continue
    
    # If we get here, all methods failed
    error_msg = "All authentication methods failed. The video URL may have expired or the API key may be incorrect."
    print(f"\n❌ {error_msg}")
    raise Exception(error_msg)


def generate_and_download_video(payload: dict, download: bool = True, filename: str = None):
    """
    Generate video and optionally download it immediately
    
    Args:
        payload: Video generation parameters
        download: Whether to download the video after generation
        filename: Optional filename for downloaded video
    
    Returns:
        dict: Contains video URLs and local file paths if downloaded
    """
    # Generate the video
    video_urls = generate_video_from_payload(payload)
    
    result = {"videos": video_urls}
    
    if download:
        downloaded_files = []
        for i, url in enumerate(video_urls):
            # Create unique filename for each video
            if filename:
                file_name = f"{filename}_{i}.mp4" if len(video_urls) > 1 else f"{filename}.mp4"
            else:
                file_name = None
            
            try:
                filepath = download_video(url, file_name)
                downloaded_files.append(filepath)
            except Exception as e:
                print(f"Failed to download video {i}: {str(e)}")
                downloaded_files.append(None)
        
        result["downloaded_files"] = downloaded_files
    
    return result


def generate_thumbnail_image(content_data: dict, output_filename: str = None) -> dict:
    """
    Generate a thumbnail image using Google AI Studio API based on content data
    
    Args:
        content_data: Dictionary containing content information (title, characters, etc.)
        output_filename: Optional filename for the thumbnail (defaults to content title)
    
    Returns:
        dict: Contains success status, thumbnail path, and generation details
    """
    try:
        client = get_genai_client()
        
        # Build thumbnail prompt from content data
        prompt = _build_thumbnail_prompt(content_data)
        
        print(f"🎨 Generating thumbnail image...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Generate the thumbnail image
        response = client.models.generate_content(
            model="gemini-2.5-flash-image-preview",
            contents=[prompt],
        )
        
        # Process the response
        for part in response.candidates[0].content.parts:
            if part.text is not None:
                print(f"📋 AI Response: {part.text[:100]}...")
            elif part.inline_data is not None:
                # Save the generated image
                image = Image.open(BytesIO(part.inline_data.data))
                
                # Add text overlay with title
                image_with_text = _add_title_overlay(image, content_data)
                
                # Create output filename
                if not output_filename:
                    title = content_data.get("title", "thumbnail")
                    # Clean filename
                    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    output_filename = f"{safe_title}_thumbnail.png"
                
                # Ensure thumbnails directory exists
                os.makedirs("thumbnails", exist_ok=True)
                thumbnail_path = os.path.join("thumbnails", output_filename)
                
                # Save the final thumbnail
                image_with_text.save(thumbnail_path)
                
                print(f"✅ Thumbnail saved: {thumbnail_path}")
                
                return {
                    "success": True,
                    "thumbnail_path": thumbnail_path,
                    "filename": output_filename,
                    "prompt_used": prompt
                }
        
        return {
            "success": False,
            "error": "No image data received from AI model"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Thumbnail generation failed: {str(e)}"
        }


def _build_thumbnail_prompt(content_data: dict) -> str:
    """
    Build a detailed prompt for thumbnail generation based on content data
    
    Args:
        content_data: Dictionary containing content information
    
    Returns:
        str: Detailed prompt for thumbnail generation
    """
    title = content_data.get("title", "Video Title")
    characters_roster = content_data.get("characters_roster", [])
    content_type = content_data.get("content_type", "story")
    
    # Detect content type if not provided
    if not content_type:
        if 'meme_type' in content_data:
            content_type = "meme"
        elif 'value_proposition' in content_data:
            content_type = "free_content"
        else:
            content_type = "story"
    
    # Build character descriptions
    character_descriptions = []
    for char in characters_roster:
        char_name = char.get("name", "Character")
        char_desc = char.get("thumbnail_description", char.get("video_prompt_description", ""))
        if char_desc:
            character_descriptions.append(f"{char_name}: {char_desc}")
    
    # Build the prompt based on content type
    prompt_parts = [
        f"Create a vibrant, eye-catching realistic YouTube thumbnail image for a {content_type} video titled '{title}'.",
        "",
        "REQUIREMENTS:",
        "- High-quality, professional YouTube thumbnail style",
        "- Bright, saturated colors that grab attention",
        "- 16:9 aspect ratio (1280x1080 resolution)",
        "- Eye-catching composition that encourages clicks by people of middle age preferable teens",
        "- Leave space at the top for title text overlay",
        ""
    ]
    
    # Add characters if available
    if character_descriptions:
        prompt_parts.extend([
            "CHARACTERS TO INCLUDE:",
            *[f"- {desc}" for desc in character_descriptions],
            ""
        ])
    
    # Add content-specific styling
    if content_type == "story":
        prompt_parts.extend([
            "STYLE: Magical storybook illustration style",
            "- Fantasy/adventure theme with rich colors",
            "- Characters in dynamic, engaging poses",
            "- Magical elements like sparkles, glows, or fantasy backgrounds",
            "- Warm, inviting atmosphere that appeals to families"
        ])
    elif content_type == "meme":
        prompt_parts.extend([
            "STYLE: Comedic meme-style illustration",
            "- Bright, fun colors with high contrast",
            "- Exaggerated expressions and reactions",
            "- Dynamic, energetic composition",
            "- Elements that suggest humor and entertainment"
        ])
    elif content_type == "free_content":
        prompt_parts.extend([
            "STYLE: Professional educational content style",
            "- Clean, modern design with trustworthy appearance",
            "- Bright but professional color scheme",
            "- Elements that suggest learning and value",
            "- Approachable yet authoritative visual style"
        ])
    
    prompt_parts.extend([
        "",
        "COMPOSITION:",
        "- Characters prominently featured in foreground",
        "- Engaging background that supports the theme",
        "- Clear visual hierarchy with good contrast",
        "- Professional lighting that makes characters pop",
        "- Avoid placing important elements in corners (YouTube UI space)",
        "",
        "Create an image that would make viewers want to click and watch the video!"
    ])
    
    return "\n".join(prompt_parts)


def _add_title_overlay(image: Image.Image, content_data: dict) -> Image.Image:
    """
    Add title text overlay to the generated thumbnail image
    
    Args:
        image: PIL Image object
        content_data: Dictionary containing content information
    
    Returns:
        Image.Image: Image with title overlay added
    """
    try:
        # Create a copy of the image to work with
        img_with_text = image.copy()
        draw = ImageDraw.Draw(img_with_text)
        
        # Get title
        title = content_data.get("title", "Video Title")
        
        # Get image dimensions
        img_width, img_height = img_with_text.size
        
        # Try to load a font, fallback to default
        try:
            # Try different font sizes to fit the title
            font_size = min(img_width // 15, 60)  # Responsive font size
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            try:
                font = ImageFont.load_default()
            except:
                # If all else fails, use basic drawing without font
                font = None
        
        if font:
            # Calculate text size and position
            bbox = draw.textbbox((0, 0), title, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            # Position text in upper portion of image
            x = (img_width - text_width) // 2
            y = img_height // 8  # Top 1/8 of the image
            
            # Add text with outline for better readability
            outline_color = "black"
            text_color = "white"
            outline_width = 2
            
            # Draw text outline
            for adj_x in range(-outline_width, outline_width + 1):
                for adj_y in range(-outline_width, outline_width + 1):
                    draw.text((x + adj_x, y + adj_y), title, font=font, fill=outline_color)
            
            # Draw main text
            draw.text((x, y), title, font=font, fill=text_color)
        
        return img_with_text
        
    except Exception as e:
        print(f"⚠️ Warning: Failed to add title overlay: {str(e)}")
        return image  # Return original image if overlay fails


def generate_video_with_thumbnail(payload: dict, content_data: dict = None) -> dict:
    """
    Generate both video and thumbnail in one call
    
    Args:
        payload: Video generation parameters
        content_data: Content information for thumbnail generation
    
    Returns:
        dict: Contains video URLs and thumbnail information
    """
    try:
        # Generate the video first
        print("🎬 Generating video...")
        video_urls = generate_video_from_payload(payload)
        
        result = {
            "success": True,
            "video_urls": video_urls,
            "thumbnail": None
        }
        
        # Generate thumbnail if content_data is provided
        if content_data:
            print("🎨 Generating thumbnail...")
            
            # Use video title from payload if not in content_data
            if not content_data.get("title") and payload.get("story_title"):
                content_data["title"] = payload.get("story_title")
            
            thumbnail_result = generate_thumbnail_image(content_data)
            result["thumbnail"] = thumbnail_result
            
            if thumbnail_result.get("success"):
                print(f"✅ Video and thumbnail generated successfully!")
            else:
                print(f"⚠️ Video generated, but thumbnail failed: {thumbnail_result.get('error')}")
        else:
            print("ℹ️ No content data provided, skipping thumbnail generation")
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Video and thumbnail generation failed: {str(e)}"
        }