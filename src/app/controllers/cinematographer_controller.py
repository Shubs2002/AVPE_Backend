from fastapi import Request, HTTPException, status
from app.services.genai_service import generate_video_from_payload, generate_and_download_video, download_video
from app.services.story_to_video_service import extract_video_prompt_from_segment, extract_all_video_prompts, story_segment_to_video_request



def handle_generate_video(request_body: dict):
    """
    Validates and forwards structured payload to service.
    """
    try:
        # Check if user wants to download immediately
        download_immediately = request_body.pop("download", False)
        filename = request_body.pop("filename", None)
        
        if download_immediately:
            result = generate_and_download_video(request_body, download=True, filename=filename)
            return result
        else:
            videos = generate_video_from_payload(request_body)
            return {"videos": videos}
    except Exception as e:
        return {"error": str(e)}


def handle_download_video(request_body: dict):
    """
    Download a video from a given URL
    """
    try:
        video_url = request_body.get("video_url")
        filename = request_body.get("filename")
        download_dir = request_body.get("download_dir", "downloads")
        
        if not video_url:
            return {"success": False, "error": "video_url is required", "filepath": None}
        
        filepath = download_video(video_url, filename, download_dir)
        return {"success": True, "filepath": filepath, "error": None}
    except Exception as e:
        return {"success": False, "error": str(e), "filepath": None}

def handle_story_to_video(request_body: dict):
    """
    Convert a story segment to video generation
    """
    try:
        story_data = request_body.get("story_data")
        segment_number = request_body.get("segment_number")
        
        if not story_data:
            return {"error": "story_data is required"}
        
        if not segment_number:
            return {"error": "segment_number is required"}
        
        # Extract video options
        video_options = {
            "resolution": request_body.get("resolution", "720p"),
            "aspectRatio": request_body.get("aspectRatio", "9:16"),
            "download": request_body.get("download", False),
            "filename": request_body.get("filename")
        }
        
        # Convert story segment to video request
        video_request = story_segment_to_video_request(story_data, segment_number, **video_options)
        
        # Generate the video
        result = handle_generate_video(video_request)
        
        return {
            "segment_number": segment_number,
            "video_request": video_request,
            "result": result
        }
        
    except Exception as e:
        return {"error": str(e)}


def handle_extract_prompts(request_body: dict):
    """
    Extract clean video prompts from all story segments
    """
    try:
        story_data = request_body.get("story_data")
        
        if not story_data:
            return {"error": "story_data is required"}
        
        # Extract all prompts
        prompts = extract_all_video_prompts(story_data)
        
        return {
            "total_segments": len(prompts),
            "prompts": prompts
        }
        
    except Exception as e:
        return {"error": str(e)}
def handle_generate_full_story_videos(request_body: dict):
    """
    Generate videos for all segments in a story sequentially
    """
    try:
        story_data = request_body.get("story_data")
        generate_videos = request_body.get("generate_videos", True)
        
        if not story_data:
            return {"error": "story_data is required"}
        
        # Video options
        video_options = {
            "resolution": request_body.get("resolution", "720p"),
            "aspectRatio": request_body.get("aspectRatio", "9:16"),
            "download": request_body.get("download", False),
            "story_title": story_data.get("title", "story")
        }
        
        # Import the function
        from app.services.story_to_video_service import execute_story_video_generation
        
        # Execute the full pipeline
        results = execute_story_video_generation(story_data, video_options, generate_videos)
        
        return results
        
    except Exception as e:
        return {"error": str(e)}
def handle_retry_failed_segments(request_body: dict):
    """
    Retry generating videos for failed segments
    """
    try:
        previous_results = request_body.get("previous_results")
        
        if not previous_results:
            return {"error": "previous_results is required"}
        
        # Video options for retry
        video_options = {
            "resolution": request_body.get("resolution", "720p"),
            "aspectRatio": request_body.get("aspectRatio", "9:16"),
            "download": request_body.get("download", False)
        }
        
        # Import the function
        from app.services.story_to_video_service import retry_failed_segments, get_failed_segments_info
        
        # Check if there are failed segments
        failed_info = get_failed_segments_info(previous_results)
        
        if not failed_info["can_retry"]:
            return {
                "message": "No failed segments to retry",
                "failed_info": failed_info,
                "results": previous_results
            }
        
        # Retry failed segments
        updated_results = retry_failed_segments(previous_results, video_options)
        
        return {
            "message": f"Retry completed. {failed_info['total_failed']} segments were retried.",
            "failed_info": failed_info,
            "results": updated_results
        }
        
    except Exception as e:
        return {"error": str(e)}


def handle_get_failed_segments(request_body: dict):
    """
    Get information about failed segments
    """
    try:
        results = request_body.get("results")
        
        if not results:
            return {"error": "results is required"}
        
        from app.services.story_to_video_service import get_failed_segments_info
        
        failed_info = get_failed_segments_info(results)
        
        return failed_info
        
    except Exception as e:
        return {"error": str(e)}

def handle_generate_full_content_videos(request_body: dict):
    """
    Generate videos for all segments in any content type (story, meme, free_content) sequentially
    """
    try:
        content_data = request_body.get("content_data")
        content_type = request_body.get("content_type")  # Optional override
        generate_videos = request_body.get("generate_videos", True)
        auto_merge = request_body.get("auto_merge", False)
        cleanup_segments = request_body.get("cleanup_segments", True)
        
        if not content_data:
            return {"error": "content_data is required"}
        
        # Video options
        video_options = {
            "resolution": request_body.get("resolution", "720p"),
            "aspectRatio": request_body.get("aspectRatio", "9:16"),
            "download": request_body.get("download", False),
            "story_title": content_data.get("title", "content")
        }
        
        # Import the function
        from app.services.content_to_video_service import execute_content_video_generation
        
        # Execute the full pipeline
        results = execute_content_video_generation(content_data, content_type, video_options, generate_videos)
        
        # Auto-merge if requested and videos were generated
        if auto_merge and generate_videos and results.get("success_count", 0) > 0:
            print(f"\n🎬 Auto-merging enabled - attempting to merge {results['success_count']} segments...")
            
            try:
                from app.services.video_merger_service import merge_content_videos_complete
                
                merge_result = merge_content_videos_complete(
                    results, 
                    skip_missing=True,  # Skip missing for auto-merge
                    cleanup_segments=cleanup_segments
                )
                
                if merge_result["success"]:
                    results["merged_video"] = {
                        "success": True,
                        "merge_method": merge_result.get("merge_method", "client_side"),
                        "output_filename": merge_result.get("output_filename"),
                        "video_urls": merge_result.get("video_urls", []),
                        "total_segments": merge_result.get("total_segments", 0)
                    }
                    print(f"✅ Auto-merge prepared: {merge_result.get('merge_method', 'client_side')} approach")
                else:
                    results["merged_video"] = {
                        "success": False,
                        "error": merge_result.get("error", "Merge failed"),
                        "action_required": merge_result.get("action_required")
                    }
                    print(f"❌ Auto-merge failed: {merge_result.get('error')}")
                    
            except Exception as merge_error:
                results["merged_video"] = {
                    "success": False,
                    "error": f"Auto-merge error: {str(merge_error)}"
                }
                print(f"❌ Auto-merge error: {str(merge_error)}")
        
        # Add merge recommendation if not auto-merged
        elif generate_videos and results.get("success_count", 0) > 0 and not auto_merge:
            results["merge_recommendation"] = {
                "can_merge": results["success_count"] >= results["total_segments"] * 0.5,
                "success_rate": (results["success_count"] / results["total_segments"]) * 100,
                "message": f"You have {results['success_count']}/{results['total_segments']} segments ready. Use /api/merge-content-videos to create final video.",
                "next_step": "merge_videos"
            }
        
        return results
        
    except Exception as e:
        return {"error": str(e)}


def handle_content_segment_to_video(request_body: dict):
    """
    Convert any content segment (story, meme, free_content) to video generation
    """
    try:
        content_data = request_body.get("content_data")
        segment_number = request_body.get("segment_number")
        content_type = request_body.get("content_type")  # Optional override
        
        if not content_data:
            return {"error": "content_data is required"}
        
        if not segment_number:
            return {"error": "segment_number is required"}
        
        # Extract video options
        video_options = {
            "resolution": request_body.get("resolution", "720p"),
            "aspectRatio": request_body.get("aspectRatio", "9:16"),
            "download": request_body.get("download", False),
            "filename": request_body.get("filename")
        }
        
        # Import the function
        from app.services.content_to_video_service import content_segment_to_video_request, detect_content_type
        
        # Detect content type if not provided
        if not content_type:
            content_type = detect_content_type(content_data)
        
        # Convert content segment to video request
        video_request = content_segment_to_video_request(content_data, segment_number, content_type, **video_options)
        
        # Generate the video
        result = handle_generate_video(video_request)
        
        return {
            "content_type": content_type,
            "segment_number": segment_number,
            "video_request": video_request,
            "result": result
        }
        
    except Exception as e:
        return {"error": str(e)}


def handle_extract_content_prompts(request_body: dict):
    """
    Extract clean video prompts from all content segments (any type)
    """
    try:
        content_data = request_body.get("content_data")
        content_type = request_body.get("content_type")  # Optional override
        
        if not content_data:
            return {"error": "content_data is required"}
        
        # Import the function
        from app.services.content_to_video_service import extract_all_content_video_prompts, detect_content_type
        
        # Detect content type if not provided
        if not content_type:
            content_type = detect_content_type(content_data)
        
        # Extract all prompts
        prompts = extract_all_content_video_prompts(content_data, content_type)
        
        return {
            "content_type": content_type,
            "total_segments": len(prompts),
            "prompts": prompts
        }
        
    except Exception as e:
        return {"error": str(e)}
        
def handle_merge_content_videos(request_body: dict):
    """
    Merge all content video segments into a complete final video
    """
    try:
        results = request_body.get("results")
        skip_missing = request_body.get("skip_missing", False)
        cleanup_segments = request_body.get("cleanup_segments", True)
        output_filename = request_body.get("output_filename")
        server_side = request_body.get("server_side", True)  # Default to server-side merging
        
        if not results:
            return {"error": "results from video generation is required"}
        
        # Import the hybrid function
        from app.services.video_merger_service import merge_content_videos_complete
        
        # Execute the merge pipeline with server_side option
        merge_result = merge_content_videos_complete(
            results, 
            skip_missing, 
            cleanup_segments, 
            output_filename,
            server_side
        )
        
        return merge_result
        
    except Exception as e:
        return {"error": str(e)}


def handle_analyze_segments(request_body: dict):
    """
    Analyze segment status before merging
    """
    try:
        results = request_body.get("results")
        
        if not results:
            return {"error": "results from video generation is required"}
        
        # Import the function
        from app.services.video_merger_service import analyze_segments_status, create_merge_plan
        
        # Analyze segments
        analysis = analyze_segments_status(results)
        plan = create_merge_plan(analysis, skip_missing=False)
        
        return {
            "analysis": analysis,
            "plan": plan,
            "recommendations": {
                "can_merge": analysis["can_merge"],
                "completion_rate": analysis["completion_rate"],
                "missing_count": len(analysis["failed_segments"]) + len(analysis["missing_segments"]),
                "action_needed": "regenerate_missing" if plan["missing_actions"] else "ready_to_merge"
            }
        }
        
    except Exception as e:
        return {"error": str(e)}


def handle_check_ffmpeg(request_body: dict):
    """
    Check video merger service status (now cloud-native, no FFmpeg needed)
    """
    try:
        from app.services.video_merger_service import check_video_merger_status
        
        status = check_video_merger_status()
        
        return {
            "service_available": status["service_available"],
            "merge_method": status["merge_method"],
            "ffmpeg_required": status["ffmpeg_required"],
            "cloud_native": status["cloud_native"],
            "message": status["message"],
            "capabilities": status["capabilities"]
        }
        
    except Exception as e:
        return {"error": str(e)}