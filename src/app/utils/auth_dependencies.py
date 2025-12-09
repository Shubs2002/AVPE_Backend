"""
Authentication Dependencies

FastAPI dependencies for protecting routes and extracting user information.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.services.auth_service import auth_service


# HTTP Bearer token scheme
security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Usage:
        @router.get("/protected")
        def protected_route(current_user: dict = Depends(get_current_user)):
            user_id = current_user["user_id"]
            ...
    """
    token = credentials.credentials
    
    # Verify token
    payload = auth_service.verify_token(token, token_type="access")
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Get user from database
    user = auth_service.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False))
) -> Optional[dict]:
    """
    Optional authentication - returns user if token provided, None otherwise.
    
    Usage:
        @router.get("/optional-auth")
        def optional_route(current_user: Optional[dict] = Depends(get_current_user_optional)):
            if current_user:
                # User is authenticated
                user_id = current_user["user_id"]
            else:
                # User is not authenticated
                ...
    """
    if not credentials:
        return None
    
    try:
        return get_current_user(credentials)
    except HTTPException:
        return None


def get_current_active_user(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dependency to get current active user (checks is_active flag).
    
    Usage:
        @router.get("/protected")
        def protected_route(current_user: dict = Depends(get_current_active_user)):
            ...
    """
    if not current_user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is disabled"
        )
    
    return current_user
