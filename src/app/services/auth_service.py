"""
Authentication Service

Handles user authentication, JWT token generation, and password hashing.
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict
from jose import JWTError, jwt
import bcrypt
from fastapi import HTTPException, status

from app.config.settings import settings
from app.connectors.mongodb_connector import get_collection


class AuthService:
    """Service for authentication operations"""
    
    def __init__(self):
        self.collection_name = "users"
        self.secret_key = settings.JWT_SECRET_KEY
        self.algorithm = settings.JWT_ALGORITHM
        self.access_token_expire_minutes = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt (with manual 72-byte truncation)"""
        # Manually truncate password to 72 bytes BEFORE passing to bcrypt
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Generate salt and hash
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        # Manually truncate password to 72 bytes BEFORE passing to bcrypt
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        # Verify password
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    
    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: dict) -> str:
        """Create a JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, token_type: str = "access") -> Dict:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Check token type
            if payload.get("type") != token_type:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail=f"Invalid token type. Expected {token_type}"
                )
            
            return payload
        
        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    
    def register_user(self, email: str, password: str, full_name: str) -> Dict:
        """Register a new user"""
        collection = get_collection(self.collection_name)
        
        # Check if user already exists
        existing_user = collection.find_one({"email": email.lower()})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Generate user_id with user_ prefix
        user_id = f"user_{uuid.uuid4()}"
        
        # Hash password
        hashed_password = self.hash_password(password)
        
        # Create user document
        user_doc = {
            "user_id": user_id,
            "email": email.lower(),
            "full_name": full_name,
            "hashed_password": hashed_password,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        # Save to MongoDB
        collection.insert_one(user_doc)
        
        print(f"✅ User registered: {email} (ID: {user_id})")
        
        # Return user data (without password)
        return {
            "user_id": user_id,
            "email": email.lower(),
            "full_name": full_name,
            "is_active": True,
            "created_at": user_doc["created_at"].isoformat()
        }
    
    def authenticate_user(self, email: str, password: str) -> Dict:
        """Authenticate a user and return user data"""
        collection = get_collection(self.collection_name)
        
        # Find user by email
        user = collection.find_one({"email": email.lower()})
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not self.verify_password(password, user["hashed_password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is disabled"
            )
        
        # Return user data (without password)
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_active": user["is_active"]
        }
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by user_id"""
        collection = get_collection(self.collection_name)
        user = collection.find_one({"user_id": user_id})
        
        if not user:
            return None
        
        # Return user data (without password)
        return {
            "user_id": user["user_id"],
            "email": user["email"],
            "full_name": user["full_name"],
            "is_active": user["is_active"]
        }
    
    def login(self, email: str, password: str) -> Dict:
        """Login user and return tokens"""
        # Authenticate user
        user = self.authenticate_user(email, password)
        
        # Create tokens
        access_token = self.create_access_token(data={"sub": user["user_id"]})
        refresh_token = self.create_refresh_token(data={"sub": user["user_id"]})
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user
        }
    
    def refresh_access_token(self, refresh_token: str) -> Dict:
        """Refresh access token using refresh token"""
        # Verify refresh token
        payload = self.verify_token(refresh_token, token_type="refresh")
        user_id = payload.get("sub")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Get user
        user = self.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Create new access token
        access_token = self.create_access_token(data={"sub": user_id})
        
        return {
            "access_token": access_token,
            "token_type": "bearer"
        }


# Global instance
auth_service = AuthService()
