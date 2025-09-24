from app.config.settings import settings

import os
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

CLIENT_SECRETS_FILE = os.path.join("src", "app", "config", settings.AVPE_FILE_NAME)
SCOPES = [settings.SCOPES]
REDIRECT_URI = settings.REDIRECT_URI

user_credentials = None  # temp storage for demo


def get_auth_url():
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    return auth_url


def exchange_code_for_credentials(code: str):
    global user_credentials
    flow = Flow.from_client_secrets_file(
        CLIENT_SECRETS_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )
    flow.fetch_token(code=code)
    user_credentials = flow.credentials
    return user_credentials


def upload_video_to_youtube(video_path: str, title: str, description: str, tags: list[str]):
    """
    Upload a video to YouTube using a file path instead of UploadFile.
    """
    global user_credentials
    if not user_credentials:
        raise Exception("User not authenticated. Please authenticate first.")

    youtube = build("youtube", "v3", credentials=user_credentials)

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "title": title,
                "description": description,
                "tags": tags or []
            },
            "status": {"privacyStatus": "public"}
        },
        media_body=MediaFileUpload(video_path, chunksize=-1, resumable=True)
    )

    response = request.execute()
    return response
