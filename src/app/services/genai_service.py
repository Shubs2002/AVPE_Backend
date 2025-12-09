import time
import requests
import os
import json
import base64
from google.genai import types
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
from app.config.settings import settings
from app.connectors.genai_connector import get_genai_client


def analyze_image_with_gemini(image_data: str, prompt: str) -> dict:
    """
    Analyze an image using Gemini 3 Pro with high-resolution analysis
    
    Args:
        image_data: Base64 encoded image data
        prompt: Analysis prompt
        
    Returns:
        dict: Analysis results
    """
    try:
        print(f"🤖 Analyzing image with Gemini 3 Pro...")
        
        # Get Gemini client
        client = get_genai_client()
        
        # Decode base64 image
        if image_data.startswith('data:image'):
            # Remove data URL prefix
            image_data = image_data.split(',')[1]
        
        image_bytes = base64.b64decode(image_data)
        
        # Create PIL Image to get format
        pil_image = Image.open(BytesIO(image_bytes))
        image_format = (pil_image.format or 'PNG').lower()
        
        # Convert to bytes for Gemini
        img_byte_arr = BytesIO()
        pil_image.save(img_byte_arr, format=pil_image.format or 'PNG')
        img_bytes = img_byte_arr.getvalue()
        
        # Generate analysis with Gemini 3 Pro using proper format
        response = client.models.generate_content(
            model="gemini-3-pro-preview",
            contents=[
                types.Content(
                    parts=[
                        types.Part(text=prompt),
                        types.Part(
                            inline_data=types.Blob(
                                mime_type=f"image/{image_format}",
                                data=img_bytes
                            )
                        )
                    ]
                )
            ]
        )
        
        # Extract response text
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
        analysis_data = json.loads(response_text)
        
        print(f"✅ Image analysis complete!")
        
        return analysis_data
        
    except Exception as e:
        print(f"❌ Gemini analysis error: {str(e)}")
        raise ValueError(f"Failed to analyze image with Gemini: {str(e)}")


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
    Calls Vertex AI Veo-3.1 model and generates a video using google-genai client.
    
    Supports reference images for better character consistency (Veo 3.1 feature).
    Now using google-genai SDK v1.45.0+ with VideoGenerationReferenceImage support!
    
    Args:
        payload: Dictionary containing:
            - prompt (required): Text description of the video
            - durationSeconds (optional): Video duration (default: 8)
            - resolution (optional): Video resolution (default: "720p")
            - aspectRatio (optional): Aspect ratio (default: "9:16")
            - first_frame_image (optional): First frame image (PIL Image, bytes, or GCS URI) - used as main image
            - last_frame_image (optional): Last frame image (PIL Image, bytes, or GCS URI)
            - reference_images (optional): List of reference images for character consistency
            - reference_image_urls (optional): List of URLs to download and use as references
    
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
    
    # Extract reference images (Veo 3.1 feature)
    reference_images = payload.get("reference_images", [])  # List of PIL Images
    reference_image_urls = payload.get("reference_image_urls", [])  # List of URLs to download
    
    # NEW: Option to use frames as reference images instead of image parameter
    use_frames_as_references = payload.get("use_frames_as_references", False)
    
    # Note: generate_audio and sample_count are not supported in GenerateVideosConfig

    def _is_transient_service_error(exc_or_obj) -> bool:
        """Check for transient service errors (503 / UNAVAILABLE / OVERLOADED)."""
        try:
            text = str(exc_or_obj).lower()
            # Check for various transient error indicators
            transient_indicators = [
                "unavailable",
                "503",
                "service is currently unavailable",
                "overloaded",  # Code 14
                "'code': 14",  # Explicit code 14 check
                "currently overloaded",
                "please try again later"
            ]
            return any(indicator in text for indicator in transient_indicators)
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
            
            # Add last_frame to config if provided (Veo 3.1 interpolation)
            if last_frame_gcs_uri:
                config_params["last_frame"] = types.Image(
                    gcs_uri=last_frame_gcs_uri,
                    mime_type="image/png"
                )
                print(f"🎬 Last frame added to config (GCS): {last_frame_gcs_uri}")
            elif last_frame_image:
                config_params["last_frame"] = _prepare_image_input(last_frame_image)
                print(f"🎬 Last frame added to config for interpolation")
            
            # Prepare reference images for Veo 3.1 (character consistency)
            reference_image_objects = []
            
            # Download and prepare reference images from URLs
            if reference_image_urls:
                print(f"📥 Downloading {len(reference_image_urls)} reference images...")
                for idx, url in enumerate(reference_image_urls):
                    try:
                        if url.startswith("http://") or url.startswith("https://"):
                            response = requests.get(url, timeout=30)
                            response.raise_for_status()
                            ref_image = Image.open(BytesIO(response.content))
                            
                            # Create reference image object
                            ref_obj = types.VideoGenerationReferenceImage(
                                image=_prepare_image_input(ref_image),
                                reference_type="asset"  # For character/object consistency
                            )
                            reference_image_objects.append(ref_obj)
                            print(f"✅ Reference image {idx+1} loaded: {url[:50]}...")
                    except Exception as e:
                        print(f"⚠️ Failed to load reference image {idx+1}: {str(e)}")
            
            # Add provided reference images
            if reference_images:
                for idx, ref_img in enumerate(reference_images):
                    try:
                        ref_obj = types.VideoGenerationReferenceImage(
                            image=_prepare_image_input(ref_img),
                            reference_type="asset"
                        )
                        reference_image_objects.append(ref_obj)
                        print(f"✅ Reference image {idx+1} added")
                    except Exception as e:
                        print(f"⚠️ Failed to add reference image {idx+1}: {str(e)}")
            
            # NEW: Add first/last frames as reference images if flag is set
            if use_frames_as_references:
                print(f"🎨 Using frames as reference images (character consistency mode)")
                
                # Add first frame as reference
                if first_frame_gcs_uri:
                    try:
                        ref_obj = types.VideoGenerationReferenceImage(
                            image=types.Image(gcs_uri=first_frame_gcs_uri, mime_type="image/png"),
                            reference_type="asset"
                        )
                        reference_image_objects.append(ref_obj)
                        print(f"✅ First frame added as reference image (GCS)")
                    except Exception as e:
                        print(f"⚠️ Failed to add first frame as reference: {str(e)}")
                elif first_frame_image:
                    try:
                        ref_obj = types.VideoGenerationReferenceImage(
                            image=_prepare_image_input(first_frame_image),
                            reference_type="asset"
                        )
                        reference_image_objects.append(ref_obj)
                        print(f"✅ First frame added as reference image")
                    except Exception as e:
                        print(f"⚠️ Failed to add first frame as reference: {str(e)}")
                
                # Add last frame as reference
                if last_frame_gcs_uri:
                    try:
                        ref_obj = types.VideoGenerationReferenceImage(
                            image=types.Image(gcs_uri=last_frame_gcs_uri, mime_type="image/png"),
                            reference_type="asset"
                        )
                        reference_image_objects.append(ref_obj)
                        print(f"✅ Last frame added as reference image (GCS)")
                    except Exception as e:
                        print(f"⚠️ Failed to add last frame as reference: {str(e)}")
                elif last_frame_image:
                    try:
                        ref_obj = types.VideoGenerationReferenceImage(
                            image=_prepare_image_input(last_frame_image),
                            reference_type="asset"
                        )
                        reference_image_objects.append(ref_obj)
                        print(f"✅ Last frame added as reference image")
                    except Exception as e:
                        print(f"⚠️ Failed to add last frame as reference: {str(e)}")
            
            # Determine if we have a starting frame (image parameter)
            # When use_frames_as_references is True, don't use frames as image parameter
            has_starting_frame = False
            if not use_frames_as_references:
                has_starting_frame = (last_frame_gcs_uri or last_frame_image or 
                                     first_frame_gcs_uri or first_frame_image)
            
            # IMPORTANT: Google Gemini API doesn't support using both 'image' and 'reference_images' together
            # Choose one approach based on what's available
            if has_starting_frame and reference_image_objects:
                print(f"⚠️ Cannot use both image parameter and reference images - prioritizing image parameter")
                reference_image_objects = []  # Clear reference images
            
            # Add reference images to config if available (and no starting frame)
            if reference_image_objects:
                config_params["reference_images"] = reference_image_objects
                print(f"🎨 Using {len(reference_image_objects)} reference images for character consistency")
            
            # Prepare generation parameters
            generation_params = {
                "model": settings.VIDEO_GENERATION_MODEL,
                "prompt": prompt,
                "config": types.GenerateVideosConfig(**config_params)
            }
            
            # IMPORTANT: Only add 'image' parameter if NOT using frames as references
            # When use_frames_as_references=True, frames are already added to reference_images
            if not use_frames_as_references:
                # CORRECT BEHAVIOR: Use FIRST frame as 'image' parameter
                # Last frame is already in config for interpolation
                if first_frame_gcs_uri:
                    generation_params["image"] = types.Image(
                        gcs_uri=first_frame_gcs_uri,
                        mime_type="image/png"
                    )
                    print(f"🖼️ Using first frame as IMAGE parameter (GCS): {first_frame_gcs_uri}")
                elif first_frame_image:
                    generation_params["image"] = _prepare_image_input(first_frame_image)
                    print(f"🖼️ Using first frame as IMAGE parameter")
                else:
                    print(f"⚠️ No first frame provided - video will start without keyframe")
            else:
                print(f"ℹ️ Frames are being used as reference images only (no image parameter)")
            
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
        "9:16": "Portrait (9:16 aspect ratio)",
        "3:4": "Portrait full screen (3:4 aspect ratio)",
        "16:9": "Widescreen (16:9 aspect ratio)",
        "1:1": "square (1:1 aspect ratio)",
        "4:3": "fullscreen (4:3 aspect ratio)"
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
    aspect_ratio: str = "9:16",
    reference_image_urls: list = None,
    use_frames_as_references: bool = False
):
    """
    Generate a video with optional first and last frame keyframes and reference images (Veo 3.1).
    
    This is a convenience function that makes it easy to generate videos
    with specific start and end frames for better continuity between segments.
    
    Args:
        prompt: Text description of the video
        first_frame: Optional first frame (PIL Image, bytes, GCS URI, HTTP/HTTPS URL, or dict) - main starting image
        last_frame: Optional last frame (PIL Image, bytes, GCS URI, HTTP/HTTPS URL, or dict)
        duration: Video duration in seconds (default: 8)
        resolution: Video resolution (default: "720p")
        aspect_ratio: Aspect ratio (default: "9:16")
        reference_image_urls: Optional list of image URLs to use as references for character consistency (Veo 3.1)
        use_frames_as_references: If True, treats first/last frames as reference images instead of image parameter (default: False)
    
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
    
    # Add reference image URLs for Veo 3.1 character consistency
    if reference_image_urls:
        payload["reference_image_urls"] = reference_image_urls
        print(f"� Adding {len(reference_image_urls)} reference images for character consistency")
    
    # Add the new flag to use frames as references
    if use_frames_as_references:
        payload["use_frames_as_references"] = True
        print(f"🎨 Frames will be used as reference images (character consistency mode)")
    
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


def generate_thumbnail_image(
    content_data: dict, 
    output_filename: str = None, 
    content_type_override: str = None, 
    aspect_ratio: str = "9:16",
    reference_image_path: str = None,
    image_model: str = "gemini-2.5-flash-image"
) -> dict:
    """
    Generate a thumbnail image using Imagen (nano banana model) with title included in the image.
    
    Args:
        content_data: Dictionary containing content information (title, characters, etc.)
        output_filename: Optional filename for the thumbnail (defaults to content title)
        content_type_override: Optional content type override (e.g., "daily_character")
        aspect_ratio: Aspect ratio for the thumbnail (default: "9:16" for vertical videos)
        reference_image_path: Optional path to reference image (e.g., first frame) for visual consistency
    
    Returns:
        dict: Contains success status, thumbnail path, and generation details
    """
    try:
        from app.services.file_storage_manager import storage_manager, ContentType
        
        # Build thumbnail prompt from content data (includes title in the image and aspect ratio)
        prompt = _build_thumbnail_prompt(content_data, aspect_ratio)
        
        print(f"🎨 Generating thumbnail with {image_model}...")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        client = get_genai_client()
        
        contents = [prompt]
        
        # Add reference image if provided (e.g., first frame for visual consistency)
        if reference_image_path:
            try:
                import os
                if os.path.exists(reference_image_path):
                    print(f"🖼️ Loading reference image: {reference_image_path}")
                    ref_image = Image.open(reference_image_path)
                    contents.append(ref_image)
                    print(f"✅ Reference image loaded for visual consistency")
                else:
                    print(f"⚠️ Reference image not found: {reference_image_path}")
            except Exception as e:
                print(f"⚠️ Could not load reference image: {str(e)}")
        
        # Get character images if available for reference
        characters_roster = content_data.get("characters_roster", [])
        
        # Add character images as reference if available
        if characters_roster:
            for char in characters_roster:
                char_image_url = char.get("image_url")
                if char_image_url:
                    try:
                        import requests
                        print(f"📥 Loading character image: {char.get('name', 'Character')}")
                        response_img = requests.get(char_image_url, timeout=10)
                        char_image = Image.open(BytesIO(response_img.content))
                        contents.append(char_image)
                        print(f"✅ Character image loaded for reference")
                    except Exception as e:
                        print(f"⚠️ Could not load character image: {str(e)}")
        
        # Generate the thumbnail image with specified model using proper ImageConfig
        response = client.models.generate_content(
            model=image_model,
            contents=contents,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio=aspect_ratio
                )
            )
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
    
    # Build character descriptions
    character_descriptions = []
    for char in characters_roster:
        char_name = char.get("name", "Character")
        char_desc = char.get("thumbnail_description", char.get("video_prompt_description", ""))
        if char_desc:
            character_descriptions.append(f"{char_name}: {char_desc}")
    
    # Build the prompt based on content type (aspect ratio handled by ImageConfig)
    prompt_parts = [
        f"Create a STUNNING, PROFESSIONAL, REALISTIC thumbnail image for a {content_type} video.",
        "",
        "⚠️ CRITICAL CHARACTER CONSISTENCY RULE:",
        "If character reference images are provided, use them EXACTLY as shown. DO NOT change, modify, or reinterpret the characters:",
        "- Keep the EXACT same species/type (if it's a fluffy creature, keep it fluffy; if it's a robot, keep it a robot)",
        "- Keep the EXACT same colors, patterns, and markings",
        "- Keep the EXACT same body shape, size, and proportions",
        "- Keep the EXACT same facial features and expressions style",
        "- Keep the EXACT same clothing, accessories, or distinctive features",
        "- DO NOT make the character more realistic, cartoonish, or change its art style",
        "- DO NOT add or remove any features from the character",
        "- Character appearance must be IDENTICAL to the reference image",
        "",
        f"🎯 TITLE TO DISPLAY: '{title}'",
        "- Display the title prominently with BOLD, LARGE text",
        "- Use eye-catching typography (thick, bold fonts)",
        "- Add text effects: drop shadow, outline, or glow for readability",
        "- Place title strategically (top third or center)",
        "- Use HIGH CONTRAST colors (white text with black outline is most readable)",
        "- Make text HUGE - it should be readable even at small sizes",
        "",
        "🎨 VISUAL STYLE:",
        "- HYPER-REALISTIC, high-quality 3D rendering or photorealistic style",
        "- VIBRANT, SATURATED colors that POP on screen",
        "- Professional lighting with dramatic highlights and shadows",
        "- Cinematic composition with depth and dimension",
        "- Sharp focus on main subjects, slight blur on background",
        "",
        "📐 COMPOSITION RULES:",
        "- Rule of thirds for character placement",
        "- Leave space at edges for platform UI (YouTube, Instagram)",
        "- Create visual hierarchy: characters → title → background",
        "- Use leading lines to draw eye to important elements",
        "",
        "🎭 THUMBNAIL PSYCHOLOGY:",
        "- Create CURIOSITY - make viewers want to know more",
        "- Show EMOTION - expressive faces and reactions",
        "- Use CONTRAST - bright vs dark, big vs small",
        "- Add MOVEMENT - dynamic poses, action elements",
        "- Include FOCAL POINT - one clear main subject",
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
    elif content_type == "daily_character" or content_type == "daily_character_life":
        prompt_parts.extend([
            "STYLE: Cute, relatable character moment style",
            "- Bright, cheerful colors that appeal to all ages",
            "- Character with expressive, endearing features",
            "- Fun, lighthearted atmosphere",
            "- Instagram-optimized visual appeal"
        ])
    
    prompt_parts.extend([
        "",
        "✨ FINAL TOUCHES:",
        "- Characters prominently featured in foreground",
        "- Engaging background that supports the theme",
        "- Clear visual hierarchy with excellent contrast",
        "- Professional lighting that makes subjects POP",
        "- Avoid placing important elements in corners (platform UI space)",
        "- Add subtle visual effects (glow, sparkles, light rays) for extra appeal",
        "",
        "⚠️ REMINDER: If character reference images were provided, the characters in the thumbnail MUST look IDENTICAL to those references. NO modifications to character appearance allowed!",
        "",
        "🎯 GOAL: Create a thumbnail so attractive that viewers CAN'T resist clicking!"
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