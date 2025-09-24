from fastapi import HTTPException, status
from app.services import oauth_service

def authorize_user():
    """Get Google OAuth URL"""
    try:
        return oauth_service.get_auth_url()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate auth URL: {str(e)}"
        )

def handle_oauth_callback(code: str):
    """Exchange code for credentials"""
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing authorization code"
        )
    try:
        oauth_service.exchange_code_for_credentials(code)
        return {"message": "Authentication successful! You can now upload videos."}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"OAuth callback failed: {str(e)}"
        )
