import os
import uuid
import shutil
import tempfile
from fastapi import HTTPException, status, UploadFile
from app.services import oauth_service

def upload_video(file: UploadFile, title: str, description: str, tags: list[str]):
    """Upload video to YouTube"""
    if not file:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No video file provided"
        )

    temp_dir = tempfile.gettempdir()
    temp_filename = f"temp_{uuid.uuid4()}.mp4"
    temp_path = os.path.join(temp_dir, temp_filename)

    try:
        # Save uploaded file to temp location
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Now pass the file path to the service
        response = oauth_service.upload_video_to_youtube(
            video_path=temp_path,
            title=title,
            description=description,
            tags=tags
        )

        return {
            "message": "Video uploaded successfully!",
            "video_id": response.get("id")
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Video upload failed: {str(e)}"
        )
    finally:
        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)
