"""
Video frame extraction service for extracting frames from generated videos.
"""
import cv2
from PIL import Image
import os


def extract_last_frame_from_video(video_path: str, output_path: str = None) -> str:
    """
    Extract the last frame from a video file.
    
    Args:
        video_path: Path to the video file
        output_path: Optional path to save the frame (defaults to auto-generated)
    
    Returns:
        str: Path to the extracted frame image
    """
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
        import time
        timestamp = int(time.time())
        output_path = f"last_frame_{timestamp}.png"
    
    # Save the frame
    pil_image.save(output_path)
    print(f"✅ Last frame extracted: {output_path} ({pil_image.size})")
    
    return output_path


def extract_first_frame_from_video(video_path: str, output_path: str = None) -> str:
    """
    Extract the first frame from a video file.
    
    Args:
        video_path: Path to the video file
        output_path: Optional path to save the frame (defaults to auto-generated)
    
    Returns:
        str: Path to the extracted frame image
    """
    print(f"🎞️ Extracting first frame from: {video_path}")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Failed to open video: {video_path}")
    
    # Read the first frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise Exception(f"Failed to read first frame from video: {video_path}")
    
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(frame_rgb)
    
    # Generate output path if not provided
    if not output_path:
        import time
        timestamp = int(time.time())
        output_path = f"first_frame_{timestamp}.png"
    
    # Save the frame
    pil_image.save(output_path)
    print(f"✅ First frame extracted: {output_path} ({pil_image.size})")
    
    return output_path


def extract_frame_at_time(video_path: str, time_seconds: float, output_path: str = None) -> str:
    """
    Extract a frame at a specific time from a video file.
    
    Args:
        video_path: Path to the video file
        time_seconds: Time in seconds to extract the frame
        output_path: Optional path to save the frame (defaults to auto-generated)
    
    Returns:
        str: Path to the extracted frame image
    """
    print(f"🎞️ Extracting frame at {time_seconds}s from: {video_path}")
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise Exception(f"Failed to open video: {video_path}")
    
    # Get FPS
    fps = cap.get(cv2.CAP_PROP_FPS)
    if fps == 0:
        raise Exception(f"Could not determine FPS for video: {video_path}")
    
    # Calculate frame number
    frame_number = int(time_seconds * fps)
    
    # Set to desired frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
    
    # Read the frame
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        raise Exception(f"Failed to read frame at {time_seconds}s from video: {video_path}")
    
    # Convert BGR to RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    # Convert to PIL Image
    pil_image = Image.fromarray(frame_rgb)
    
    # Generate output path if not provided
    if not output_path:
        import time
        timestamp = int(time.time())
        output_path = f"frame_{time_seconds}s_{timestamp}.png"
    
    # Save the frame
    pil_image.save(output_path)
    print(f"✅ Frame at {time_seconds}s extracted: {output_path} ({pil_image.size})")
    
    return output_path
