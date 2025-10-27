"""
Hybrid video merger service
Supports both server-side merging (using Python libraries) and client-side merging.
Server-side merging creates actual merged files and cleans up segments.
"""
import os
import json
import requests
import subprocess
import tempfile
import shutil
from typing import List, Dict, Optional
from app.config.settings import settings


class VideoMerger:
    def __init__(self):
        self.environment = os.getenv("ENV", "dev")
    
    def merge_videos(self, video_urls: List[str], output_filename: str = "merged_video", 
                    server_side: bool = True) -> Dict:
        """
        Merge videos using server-side or client-side approach
        
        Args:
            video_urls: List of video URLs to merge
            output_filename: Desired output filename
            server_side: If True, merge on server and return file. If False, return client instructions.
            
        Returns:
            Dict with merge results
        """
        if server_side:
            return self._merge_videos_server_side(video_urls, output_filename)
        else:
            return self._prepare_client_side_merge(video_urls, output_filename)
    
    def _merge_videos_server_side(self, video_urls: List[str], output_filename: str) -> Dict:
        """
        Server-side video merging that creates actual merged file
        """
        try:
            print(f"🎬 Starting server-side video merge for {len(video_urls)} segments...")
            
            # Create output directory
            output_dir = "merged_videos"
            os.makedirs(output_dir, exist_ok=True)
            
            # Download all video segments first
            downloaded_files = []
            temp_dir = tempfile.mkdtemp()
            
            try:
                for i, url in enumerate(video_urls):
                    print(f"📥 Downloading segment {i+1}/{len(video_urls)}...")
                    
                    # Download video segment
                    response = requests.get(url, stream=True, timeout=60)
                    if response.status_code == 200:
                        temp_file = os.path.join(temp_dir, f"segment_{i+1}.mp4")
                        with open(temp_file, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)
                        downloaded_files.append(temp_file)
                        print(f"✅ Downloaded segment {i+1}: {os.path.getsize(temp_file) / 1024 / 1024:.1f} MB")
                    else:
                        print(f"❌ Failed to download segment {i+1}: HTTP {response.status_code}")
                        return {
                            "success": False,
                            "error": f"Failed to download segment {i+1}: HTTP {response.status_code}"
                        }
                
                if not downloaded_files:
                    return {
                        "success": False,
                        "error": "No video segments could be downloaded"
                    }
                
                # Try FFmpeg first, then fallback to Python-based merging
                merge_result = self._try_ffmpeg_merge(downloaded_files, output_filename, output_dir)
                
                if not merge_result["success"]:
                    print("⚠️ FFmpeg merge failed, trying Python-based merge...")
                    merge_result = self._python_based_merge(downloaded_files, output_filename, output_dir)
                
                return merge_result
                
            finally:
                # Cleanup temporary files
                try:
                    shutil.rmtree(temp_dir)
                    print(f"🧹 Cleaned up temporary files")
                except:
                    pass
                    
        except Exception as e:
            return {
                "success": False,
                "error": f"Server-side merge failed: {str(e)}"
            }
    
    def _try_ffmpeg_merge(self, downloaded_files: List[str], output_filename: str, output_dir: str) -> Dict:
        """
        Try to merge using FFmpeg if available
        """
        try:
            # Check if FFmpeg is available
            result = subprocess.run(['ffmpeg', '-version'], 
                                  capture_output=True, text=True, timeout=5)
            if result.returncode != 0:
                return {"success": False, "error": "FFmpeg not available"}
            
            print("🔧 Using FFmpeg for video merging...")
            
            # Create file list for FFmpeg
            filelist_path = os.path.join(output_dir, "temp_filelist.txt")
            with open(filelist_path, 'w') as f:
                for file_path in downloaded_files:
                    # FFmpeg requires forward slashes
                    normalized_path = file_path.replace('\\', '/')
                    f.write(f"file '{normalized_path}'\n")
            
            # Output file path
            output_path = os.path.join(output_dir, f"{output_filename}.mp4")
            
            # FFmpeg command
            cmd = [
                'ffmpeg', '-f', 'concat', '-safe', '0',
                '-i', filelist_path, '-c', 'copy', '-y', output_path
            ]
            
            # Run FFmpeg
            process = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Cleanup filelist
            try:
                os.remove(filelist_path)
            except:
                pass
            
            if process.returncode == 0 and os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                return {
                    "success": True,
                    "method": "ffmpeg",
                    "output_file": output_path,
                    "file_size": file_size,
                    "segments_merged": len(downloaded_files)
                }
            else:
                return {
                    "success": False,
                    "error": f"FFmpeg failed: {process.stderr}"
                }
                
        except (subprocess.TimeoutExpired, FileNotFoundError, subprocess.SubprocessError):
            return {"success": False, "error": "FFmpeg not available or failed"}
    
    def _python_based_merge(self, downloaded_files: List[str], output_filename: str, output_dir: str) -> Dict:
        """
        Python-based video merging using moviepy (fallback)
        """
        try:
            # Try to import moviepy
            try:
                from moviepy import VideoFileClip, concatenate_videoclips
            except ImportError:
                return {
                    "success": False,
                    "error": "MoviePy not available. Install with: pip install moviepy",
                    "suggestion": "Use client-side merging or install FFmpeg"
                }
            
            print("🐍 Using Python MoviePy for video merging...")
            
            # Load video clips
            clips = []
            for file_path in downloaded_files:
                clip = VideoFileClip(file_path)
                clips.append(clip)
            
            # Concatenate clips
            final_clip = concatenate_videoclips(clips)
            
            # Output file path
            output_path = os.path.join(output_dir, f"{output_filename}.mp4")
            
            # Write final video
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            
            # Close clips to free memory
            for clip in clips:
                clip.close()
            final_clip.close()
            
            if os.path.exists(output_path):
                file_size = os.path.getsize(output_path)
                return {
                    "success": True,
                    "method": "moviepy",
                    "output_file": output_path,
                    "file_size": file_size,
                    "segments_merged": len(downloaded_files)
                }
            else:
                return {
                    "success": False,
                    "error": "MoviePy merge failed - output file not created"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Python-based merge failed: {str(e)}"
            }
    

    
    def _prepare_client_side_merge(self, video_urls: List[str], output_filename: str) -> Dict:
        """
        Prepare data for client-side video merging using Web APIs
        """
        return {
            "success": True,
            "merge_method": "client_side",
            "video_urls": video_urls,
            "output_filename": output_filename,
            "instructions": {
                "method": "Use Web APIs (MediaRecorder, Canvas, or WebCodecs)",
                "steps": [
                    "Download video segments on client",
                    "Use HTML5 Canvas or WebCodecs API to merge",
                    "Generate final merged video blob",
                    "Allow user to download or upload to cloud storage"
                ]
            },
            "web_merge_config": {
                "format": "mp4",
                "codec": "h264",
                "quality": "high"
            }
        }
    



def merge_videos(video_urls: List[str], output_filename: str = "merged_video", 
                server_side: bool = True) -> Dict:
    """
    Merge videos using server-side or client-side approach
    
    Args:
        video_urls: List of video URLs to merge
        output_filename: Desired output filename
        server_side: If True, merge on server. If False, return client instructions.
        
    Returns:
        Dict with merge results
    """
    merger = VideoMerger()
    return merger.merge_videos(video_urls, output_filename, server_side)


def merge_content_videos_complete(results: dict, skip_missing: bool = False, 
                                cleanup_segments: bool = True, 
                                output_filename: str = None,
                                server_side: bool = True) -> dict:
    """
    Complete pipeline to merge all content videos
    
    Args:
        results: Results from video generation
        skip_missing: Whether to skip missing segments
        cleanup_segments: Whether to delete individual segments after merge
        output_filename: Custom output filename
        server_side: If True, merge on server and create file. If False, return client instructions.
    
    Returns:
        dict: Complete merge results
    """
    merge_type = "Server-Side" if server_side else "Client-Side"
    print(f"🎬 Starting {merge_type} Video Merge Pipeline...")
    print("=" * 60)
    
    # Extract video URLs from results
    video_urls = results.get("video_urls", [])
    
    if not video_urls:
        return {
            "success": False,
            "error": "No video URLs found in results"
        }
    
    # Create output filename
    if not output_filename:
        content_title = results.get("content_title", results.get("story_title", "merged_content"))
        safe_title = "".join(c for c in content_title if c.isalnum() or c in (' ', '-', '_')).strip()
        safe_title = safe_title.replace(' ', '_')
        output_filename = f"{safe_title}_complete"
    
    # Use appropriate merger
    merge_result = merge_videos(video_urls, output_filename, server_side)
    
    # Generate thumbnail
    thumbnail_result = None
    try:
        from app.services.genai_service import generate_thumbnail_image
        
        # Get aspect ratio from results (default to 9:16 for vertical videos)
        aspect_ratio = results.get("aspect_ratio", results.get("aspectRatio", "9:16"))
        
        content_data = {
            "title": results.get("content_title", results.get("story_title", "Video")),
            "characters_roster": results.get("characters_roster", []),
            "content_type": results.get("content_type", "story")
        }
        
        # Try to get first frame path for reference (if available)
        reference_image_path = None
        if results.get("segments_results"):
            first_segment = results["segments_results"][0]
            # Check for generated first frame or last frame
            reference_image_path = first_segment.get("first_frame_generated") or first_segment.get("last_frame_generated")
            
            if reference_image_path:
                print(f"🖼️ Using first frame as thumbnail reference: {reference_image_path}")
            else:
                print(f"⚠️ No first frame found in segment results")
        else:
            print(f"⚠️ No segments_results found for thumbnail reference")
        
        thumbnail_result = generate_thumbnail_image(
            content_data, 
            f"{output_filename}_thumbnail.png",
            aspect_ratio=aspect_ratio,
            reference_image_path=reference_image_path  # Pass first frame for consistency
        )
        
        if thumbnail_result.get("success"):
            print(f"✅ Thumbnail generated: {thumbnail_result['thumbnail_path']}")
        else:
            print(f"⚠️ Thumbnail generation failed: {thumbnail_result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"⚠️ Thumbnail generation failed: {str(e)}")
        thumbnail_result = {"success": False, "error": str(e)}
    
    # Final result
    final_result = {
        "success": merge_result.get("success", False),
        "merge_method": merge_result.get("method", "client_side" if not server_side else "server_side"),
        "server_side": server_side,
        "merge_result": merge_result,
        "thumbnail_result": thumbnail_result,
        "total_segments": len(video_urls),
        "completion_rate": 100.0
    }
    
    # Add appropriate result fields based on merge type
    if server_side and merge_result.get("success"):
        final_result.update({
            "output_file": merge_result.get("output_file"),
            "file_size": merge_result.get("file_size"),
            "segments_merged": merge_result.get("segments_merged")
        })
        
        # Cleanup downloaded segment files if requested
        if cleanup_segments:
            cleanup_result = cleanup_downloaded_segments(results.get("downloaded_files", []))
            final_result["cleanup_result"] = cleanup_result
    else:
        final_result.update({
            "video_urls": video_urls,
            "output_filename": output_filename,
            "instructions": merge_result.get("instructions", {})
        })
    
    print(f"\n🎉 {merge_type} Video Merge Pipeline Complete!")
    print("=" * 60)
    
    if server_side and merge_result.get("success"):
        print(f"✅ Merged video created: {merge_result.get('output_file')}")
        print(f"📊 File size: {merge_result.get('file_size', 0) / 1024 / 1024:.1f} MB")
        print(f"🔗 Segments merged: {merge_result.get('segments_merged', 0)}")
    else:
        print(f"✅ Video URLs ready for merging: {len(video_urls)}")
        print(f"📝 Output filename: {output_filename}")
    
    if thumbnail_result and thumbnail_result.get("success"):
        print(f"🎨 Thumbnail: {thumbnail_result['thumbnail_path']}")
    
    # Cleanup frames AFTER thumbnail generation (if all successful)
    if results.get("success_count") == results.get("total_segments") and results.get("error_count", 0) == 0:
        try:
            import shutil
            from app.services.file_storage_manager import storage_manager, ContentType
            import os
            
            content_title = results.get("content_title", results.get("story_title"))
            content_type = results.get("content_type", "daily_character")
            
            if content_title:
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
                content_dir = storage_manager.get_content_directory(content_type_constant, content_title, create=False)
                frames_dir = os.path.join(content_dir, "frames")
                
                if os.path.exists(frames_dir):
                    print(f"\n🧹 Cleaning up temporary frames...")
                    shutil.rmtree(frames_dir)
                    print(f"✅ Frames directory deleted: {frames_dir}")
                    final_result["frames_cleaned"] = True
                else:
                    final_result["frames_cleaned"] = False
        except Exception as cleanup_error:
            print(f"⚠️ Frame cleanup failed: {str(cleanup_error)}")
            final_result["frames_cleaned"] = False
    else:
        final_result["frames_cleaned"] = False
    
    return final_result


def cleanup_downloaded_segments(downloaded_files: List[str]) -> Dict:
    """
    Clean up downloaded segment files
    
    Args:
        downloaded_files: List of file paths to delete
        
    Returns:
        Dict with cleanup results
    """
    if not downloaded_files:
        return {"deleted_count": 0, "message": "No files to cleanup"}
    
    deleted_count = 0
    errors = []
    
    for file_path in downloaded_files:
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                deleted_count += 1
                print(f"🗑️ Deleted: {os.path.basename(file_path)}")
        except Exception as e:
            errors.append(f"Failed to delete {file_path}: {str(e)}")
    
    return {
        "deleted_count": deleted_count,
        "total_files": len(downloaded_files),
        "errors": errors,
        "success": len(errors) == 0
    }


def check_video_merger_status() -> Dict:
    """
    Check the status of video merger service
    
    Returns:
        Dict with service status and capabilities
    """
    return {
        "service_available": True,
        "merge_method": "client_side",
        "ffmpeg_required": False,
        "cloud_native": True,
        "environment": os.getenv("ENV", "dev"),
        "capabilities": [
            "Client-side video merging instructions",
            "Thumbnail generation",
            "Cloud deployment ready",
            "No server-side processing overhead"
        ],
        "message": "Video merger service ready - uses client-side merging for optimal performance"
    }


def get_deployment_info() -> Dict:
    """
    Get deployment information for video processing
    """
    env = os.getenv("ENV", "dev")
    
    return {
        "environment": env,
        "approach": "client_side_merging",
        "cloud_native": True,
        "ffmpeg_required": False,
        "reasons": [
            "No server-side video processing overhead",
            "Scales better with user load", 
            "Reduces server costs and complexity",
            "Works on all cloud platforms (Render, Vercel, etc.)",
            "No binary dependencies"
        ],
        "implementation": {
            "backend": "Provide video URLs and merge instructions",
            "frontend": "Use Web APIs (Canvas, MediaRecorder, WebCodecs) to merge videos",
            "storage": "Upload final video to cloud storage or download locally"
        },
        "benefits": [
            "Zero server processing time",
            "Unlimited concurrent users",
            "No timeout issues",
            "Lower hosting costs",
            "Better user experience"
        ]
    }