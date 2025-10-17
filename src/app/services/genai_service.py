import time
import requests
import os
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from app.config.settings import settings
from app.connectors.genai_connector import get_genai_client


def _prepare_image_input(image_input):
    """
    Prepare image input for Veo 3 video generation.
    
    Args:
        image_input: Can be:
            - PIL Image object
            - bytes (image data)
            - str (GCS URI starting with "gs://")
            - dict with 'gcs_uri' or 'data' keys
    
    Returns:
        types.Image: Prepared image object for Veo 3
    """
    # If it's already a types.Image, return as-is
    if isinstance(image_input, types.Image):
        return image_input
    
    # If it's a GCS URI string
    if isinstance(image_input, str) and image_input.startswith("gs://"):
        return types.Image(gcs_uri=image_input, mime_type="image/png")
    
    # If it's a dict with gcs_uri
    if isinstance(image_input, dict) and "gcs_uri" in image_input:
        return types.Image(
            gcs_uri=image_input["gcs_uri"],
            mime_type=image_input.get("mime_type", "image/png")
        )
    
    # If it's a PIL Image, convert to bytes
    if isinstance(image_input, Image.Image):
        buffer = BytesIO()
        image_input.save(buffer, format="PNG")
        image_bytes = buffer.getvalue()
        return types.Image(image_bytes=image_bytes, mime_type="image/png")
    
    # If it's bytes
    if isinstance(image_input, bytes):
        return types.Image(image_bytes=image_input, mime_type="image/png")
    
    # If it's a dict with data
    if isinstance(image_input, dict) and "data" in image_input:
        return types.Image(
            image_bytes=image_input["data"],
            mime_type=image_input.get("mime_type", "image/png")
        )
    
    raise ValueError(f"Unsupported image input type: {type(image_input)}")


def generate_video_from_payload(payload: dict):
    """
    Calls Vertex AI Veo-3 model and generates a video using google-genai client.
    
    Supports optional first and last frame images for better video continuity.
    
    Args:
        payload: Dictionary containing:
            - prompt (required): Text description of the video
            - durationSeconds (optional): Video duration (default: 8)
            - resolution (optional): Video resolution (default: "720p")
            - aspectRatio (optional): Aspect ratio (default: "9:16")
            - first_frame_image (optional): First frame image (PIL Image, bytes, or GCS URI)
            - last_frame_image (optional): Last frame image (PIL Image, bytes, or GCS URI)
            - first_frame_gcs_uri (optional): GCS URI for first frame (e.g., "gs://bucket/img.png")
            - last_frame_gcs_uri (optional): GCS URI for last frame
    
    Returns:
        list: List of generated video URLs
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
    
    # Extract optional frame images
    first_frame_image = payload.get("first_frame_image")  # PIL Image, bytes, or GCS URI
    last_frame_image = payload.get("last_frame_image")
    first_frame_gcs_uri = payload.get("first_frame_gcs_uri")  # Direct GCS URI
    last_frame_gcs_uri = payload.get("last_frame_gcs_uri")
    
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
            # Prepare config with optional last frame
            config_params = {
                "duration_seconds": duration,
                "resolution": resolution,
                "aspect_ratio": aspect_ratio,
            }
            
            # Add last frame if provided
            if last_frame_gcs_uri:
                config_params["last_frame"] = types.Image(
                    gcs_uri=last_frame_gcs_uri,
                    mime_type="image/png"
                )
            elif last_frame_image:
                config_params["last_frame"] = _prepare_image_input(last_frame_image)
            
            # Prepare generation parameters
            generation_params = {
                "model": settings.VIDEO_GENERATION_MODEL,
                "prompt": prompt,
                "config": types.GenerateVideosConfig(**config_params)
            }
            
            # Add first frame if provided (as 'image' parameter)
            if first_frame_gcs_uri:
                generation_params["image"] = types.Image(
                    gcs_uri=first_frame_gcs_uri,
                    mime_type="image/png"
                )
            elif first_frame_image:
                generation_params["image"] = _prepare_image_input(first_frame_image)
            
            # Start async video generation
            operation = client.models.generate_videos(**generation_params)

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


def extract_last_frame_from_video(video_path: str, output_path: str = None) -> str:
    """
    Extract the last frame from a video file.
    
    Args:
        video_path: Path to the video file
        output_path: Optional path to save the frame (defaults to auto-generated)
    
    Returns:
        str: Path to the extracted frame image
    """
    import cv2
    from PIL import Image
    
    print(f"🎞️ Extracting last frame from: {video_path}")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        raise Exception(f"Failed to open video: {video_path}")
    
    # Get total frame count
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        raise Exception(f"Video has no frames: {video_path}")
    
    # Set to last frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
    
    # Read the last frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise Exception(f"Failed to read last frame from video: {video_path}")
    
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(frame_rgb)
    
    # Generate output path if not provided
    if not output_path:
        timestamp = int(time.time())
        output_path = f"last_frame_{timestamp}.png"
    
    # Save the frame
    pil_image.save(output_path)
    print(f"✅ Last frame extracted: {output_path} ({pil_image.size})")
    
    return output_path


def generate_first_frame_with_imagen(character_keyframe_uri: str, frame_description: str, aspect_ratio: str = "9:16") -> 'Image.Image':
    """
    Generate the first frame using Imagen (nano banana model) by combining
    character keyframe with scene description.
    
    Args:
        character_keyframe_uri: URI of the character image (HTTP/HTTPS or GCS)
        frame_description: Description of the scene, pose, environment
        aspect_ratio: Aspect ratio for the generated frame
    
    Returns:
        PIL.Image: Generated first frame
    """
    from PIL import Image
    from io import BytesIO
    import requests
    
    print(f"🎨 Generating first frame with Imagen...")
    print(f"📝 Description: {frame_description[:100]}...")
    
    # Download character image if it's a URL
    if character_keyframe_uri.startswith("http://") or character_keyframe_uri.startswith("https://"):
        print(f"📥 Downloading character image from: {character_keyframe_uri[:50]}...")
        response = requests.get(character_keyframe_uri, timeout=30)
        response.raise_for_status()
        character_image = Image.open(BytesIO(response.content))
        print(f"✅ Character image loaded: {character_image.size}")
    else:
        raise ValueError(f"Unsupported character_keyframe_uri format: {character_keyframe_uri}")
    
    # Map aspect ratio to description
    aspect_ratio_descriptions = {
        "9:16": "vertical portrait orientation (9:16 aspect ratio)",
        "16:9": "horizontal landscape orientation (16:9 aspect ratio)",
        "1:1": "square format (1:1 aspect ratio)",
        "4:5": "vertical format (4:5 aspect ratio)"
    }
    
    aspect_ratio_desc = aspect_ratio_descriptions.get(aspect_ratio, f"{aspect_ratio} aspect ratio")
    
    # Build prompt for Imagen with aspect ratio
    prompt = f"Create a {aspect_ratio_desc} image. A scene with the character in this exact appearance: {frame_description}. Maintain character's exact look, colors, and features. The image must be in {aspect_ratio_desc}."
    
    print(f"🎨 Generating frame with Imagen ({aspect_ratio})...")
    print(f"📝 Full prompt: {prompt[:150]}...")
    
    # TODO: Implement actual Imagen (nano banana) API call with aspect ratio
    # For now, we'll resize the character image to match aspect ratio
    
    print(f"⚠️ Imagen generation not yet implemented - resizing character image to {aspect_ratio}")
    
    # Resize character image to match aspect ratio
    resized_image = _resize_to_aspect_ratio(character_image, aspect_ratio)
    
    return resized_image


def _resize_to_aspect_ratio(image: 'Image.Image', aspect_ratio: str) -> 'Image.Image':
    """
    Resize an image to match the specified aspect ratio.
    
    Args:
        image: PIL Image to resize
        aspect_ratio: Target aspect ratio (e.g., "9:16", "16:9", "1:1")
    
    Returns:
        PIL.Image: Resized image
    """
    from PIL import Image
    
    # Parse aspect ratio
    try:
        width_ratio, height_ratio = map(int, aspect_ratio.split(':'))
    except:
        print(f"⚠️ Invalid aspect ratio '{aspect_ratio}', using original image")
        return image
    
    # Calculate target dimensions
    original_width, original_height = image.size
    target_aspect = width_ratio / height_ratio
    current_aspect = original_width / original_height
    
    if abs(target_aspect - current_aspect) < 0.01:
        # Already correct aspect ratio
        return image
    
    # Determine new dimensions (maintain quality, crop if needed)
    if current_aspect > target_aspect:
        # Image is too wide, crop width
        new_height = original_height
        new_width = int(new_height * target_aspect)
    else:
        # Image is too tall, crop height
        new_width = original_width
        new_height = int(new_width / target_aspect)
    
    # Center crop
    left = (original_width - new_width) // 2
    top = (original_height - new_height) // 2
    right = left + new_width
    bottom = top + new_height
    
    cropped_image = image.crop((left, top, right, bottom))
    
    print(f"✅ Resized from {image.size} to {cropped_image.size} ({aspect_ratio})")
    
    return cropped_image


def generate_video_with_keyframes(
    prompt: str,
    first_frame=None,
    last_frame=None,
    duration: int = 8,
    resolution: str = "720p",
    aspect_ratio: str = "9:16"
):
    """
    Generate a video with optional first and last frame keyframes.
    
    This is a convenience function that makes it easy to generate videos
    with specific start and end frames for better continuity between segments.
    
    Args:
        prompt: Text description of the video
        first_frame: Optional first frame (PIL Image, bytes, GCS URI, HTTP/HTTPS URL, or dict)
        last_frame: Optional last frame (PIL Image, bytes, GCS URI, HTTP/HTTPS URL, or dict)
        duration: Video duration in seconds (default: 8)
        resolution: Video resolution (default: "720p")
        aspect_ratio: Aspect ratio (default: "9:16")
    
    Returns:
        list: List of generated video URLs
    
    Example:
        # Using PIL Images
        from PIL import Image
        first_img = Image.open("start.png")
        last_img = Image.open("end.png")
        urls = generate_video_with_keyframes(
            prompt="A cat walking across the room",
            first_frame=first_img,
            last_frame=last_img
        )
        
        # Using GCS URIs
        urls = generate_video_with_keyframes(
            prompt="A cat walking across the room",
            first_frame="gs://my-bucket/start.png",
            last_frame="gs://my-bucket/end.png"
        )
        
        # Using HTTP/HTTPS URLs (Cloudinary, etc.)
        urls = generate_video_with_keyframes(
            prompt="A cat walking across the room",
            first_frame="https://res.cloudinary.com/.../image.png"
        )
    """
    import requests
    from PIL import Image
    from io import BytesIO
    
    def process_image_input(image_input):
        """Process various image input types"""
        import os
        
        if image_input is None:
            return None
            
        # If it's a string, check what type
        if isinstance(image_input, str):
            # GCS URI - pass as is
            if image_input.startswith("gs://"):
                return {"type": "gcs_uri", "value": image_input}
            # HTTP/HTTPS URL - download and convert to PIL Image
            elif image_input.startswith("http://") or image_input.startswith("https://"):
                print(f"📥 Downloading image from URL: {image_input[:50]}...")
                response = requests.get(image_input, timeout=30)
                response.raise_for_status()
                img = Image.open(BytesIO(response.content))
                print(f"✅ Image downloaded: {img.size} {img.mode}")
                return {"type": "image", "value": img}
            # Local file path - load from disk
            elif os.path.exists(image_input):
                print(f"📂 Loading image from local file: {image_input}")
                img = Image.open(image_input)
                print(f"✅ Image loaded: {img.size} {img.mode}")
                return {"type": "image", "value": img}
            else:
                raise ValueError(f"Unsupported string format for image: {image_input}")
        else:
            # PIL Image, bytes, or dict - pass as is
            return {"type": "image", "value": image_input}
    
    payload = {
        "prompt": prompt,
        "durationSeconds": duration,
        "resolution": resolution,
        "aspectRatio": aspect_ratio
    }
    
    # Process first frame
    if first_frame:
        processed = process_image_input(first_frame)
        if processed:
            if processed["type"] == "gcs_uri":
                payload["first_frame_gcs_uri"] = processed["value"]
            else:
                payload["first_frame_image"] = processed["value"]
    
    # Process last frame
    if last_frame:
        processed = process_image_input(last_frame)
        if processed:
            if processed["type"] == "gcs_uri":
                payload["last_frame_gcs_uri"] = processed["value"]
            else:
                payload["last_frame_image"] = processed["value"]
    
    return generate_video_from_payload(payload)


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


def generate_thumbnail_image(content_data: dict, output_filename: str = None, content_type_override: str = None, aspect_ratio: str = "9:16") -> dict:
    """
    Generate a thumbnail image using Imagen (nano banana model) with title included in the image.
    
    Args:
        content_data: Dictionary containing content information (title, characters, etc.)
        output_filename: Optional filename for the thumbnail (defaults to content title)
        content_type_override: Optional content type override (e.g., "daily_character")
        aspect_ratio: Aspect ratio for the thumbnail (default: "9:16" for vertical videos)
    
    Returns:
        dict: Contains success status, thumbnail path, and generation details
    """
    try:
        from app.services.file_storage_manager import storage_manager, ContentType
        
        # Build thumbnail prompt from content data (includes title in the image and aspect ratio)
        prompt = _build_thumbnail_prompt(content_data, aspect_ratio)
        
        print(f"🎨 Generating thumbnail with Imagen (nano banana)...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # TODO: Implement actual Imagen (nano banana) API call
        # For now, using Gemini as placeholder
        client = get_genai_client()
        
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
                # Save the generated image (no text overlay - title is in the image)
                image = Image.open(BytesIO(part.inline_data.data))
                
                # Determine content type and title
                title = content_data.get("title", "thumbnail")
                content_type = content_type_override or content_data.get("content_type", "daily_character")
                
                # Map content type to ContentType constants
                content_type_map = {
                    "daily_character": ContentType.DAILY_CHARACTER,
                    "daily_character_life": ContentType.DAILY_CHARACTER,
                    "story": ContentType.STORY,
                    "movie": ContentType.MOVIE,
                    "meme": ContentType.MEME,
                    "free_content": ContentType.FREE_CONTENT,
                    "music_video": ContentType.MUSIC_VIDEO,
                    "whatsapp_story": ContentType.WHATSAPP_STORY,
                    "anime": ContentType.ANIME
                }
                
                content_type_constant = content_type_map.get(content_type, ContentType.DAILY_CHARACTER)
                
                # Get content directory from file storage manager
                content_dir = storage_manager.get_content_directory(content_type_constant, title)
                
                # Create output filename
                if not output_filename:
                    safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    output_filename = f"{safe_title}_thumbnail.png"
                
                # Save to content directory
                thumbnail_path = os.path.join(content_dir, output_filename)
                image.save(thumbnail_path)
                
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


def _build_thumbnail_prompt(content_data: dict, aspect_ratio: str = "9:16") -> str:
    """
    Build a detailed prompt for thumbnail generation based on content data
    
    Args:
        content_data: Dictionary containing content information
        aspect_ratio: Aspect ratio for the thumbnail (e.g., "9:16", "16:9", "1:1")
    
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
    
    # Map aspect ratio to description
    aspect_ratio_descriptions = {
        "9:16": "vertical (9:16 aspect ratio, portrait orientation for mobile/Instagram)",
        "16:9": "horizontal (16:9 aspect ratio, landscape orientation for YouTube)",
        "1:1": "square (1:1 aspect ratio for Instagram posts)",
        "4:5": "vertical (4:5 aspect ratio for Instagram feed)"
    }
    
    aspect_ratio_desc = aspect_ratio_descriptions.get(aspect_ratio, f"{aspect_ratio} aspect ratio")
    
    # Build character descriptions
    character_descriptions = []
    for char in characters_roster:
        char_name = char.get("name", "Character")
        char_desc = char.get("thumbnail_description", char.get("video_prompt_description", ""))
        if char_desc:
            character_descriptions.append(f"{char_name}: {char_desc}")
    
    # Build the prompt based on content type
    prompt_parts = [
        f"Create a vibrant, eye-catching realistic thumbnail image for a {content_type} video.",
        "",
        f"TITLE TO INCLUDE IN IMAGE: '{title}'",
        "- The title MUST be prominently displayed in the image",
        "- Use bold, eye-catching text that's easy to read",
        "- Place title at the top or center of the image",
        "- Use contrasting colors for text (white text with dark outline, or vice versa)",
        "- Make the title text large and clear",
        "",
        "REQUIREMENTS:",
        "- High-quality, professional thumbnail style",
        "- Bright, saturated colors that grab attention",
        f"- {aspect_ratio_desc}",
        "- Eye-catching composition that encourages clicks by people of middle age preferable teens",
        "- Title text integrated into the design (not added separately)",
        "- Optimized for the specified aspect ratio",
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