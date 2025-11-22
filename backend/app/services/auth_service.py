"""Authentication service using Supabase Auth"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from ..config import settings
from ..database import get_supabase

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class AuthService:
    """Service for handling authentication with Supabase"""
    
    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password"""
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[Dict[str, Any]]:
        """Verify and decode a JWT token"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError:
            return None
    
    @staticmethod
    async def register_with_email(email: str, password: str) -> Dict[str, Any]:
        """Register a new user with email and password using Supabase"""
        supabase = get_supabase()
        if not supabase:
            raise Exception("Supabase not configured")
        
        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
            })
            return {
                "user": response.user.model_dump() if response.user else None,
                "session": response.session.model_dump() if response.session else None,
            }
        except Exception as e:
            raise Exception(f"Registration failed: {str(e)}")
    
    @staticmethod
    async def login_with_email(email: str, password: str) -> Dict[str, Any]:
        """Login with email and password using Supabase"""
        supabase = get_supabase()
        if not supabase:
            raise Exception("Supabase not configured")
        
        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
            return {
                "user": response.user.model_dump() if response.user else None,
                "session": response.session.model_dump() if response.session else None,
                "access_token": response.session.access_token if response.session else None,
            }
        except Exception as e:
            raise Exception(f"Login failed: {str(e)}")
    
    @staticmethod
    async def get_google_auth_url() -> str:
        """Get Google OAuth URL for sign-in"""
        supabase = get_supabase()
        if not supabase:
            raise Exception("Supabase not configured")
        
        try:
            response = supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirectTo": "http://localhost:3000/auth/callback"
                }
            })
            return response.url if hasattr(response, 'url') else None
        except Exception as e:
            raise Exception(f"Google auth failed: {str(e)}")
    
    @staticmethod
    async def verify_user_session(token: str) -> Optional[Dict[str, Any]]:
        """Verify a user session token"""
        # First try to verify as our JWT token
        payload = AuthService.verify_token(token)
        if payload:
            # Return user data from JWT payload
            return {
                "id": payload.get("sub"),
                "email": payload.get("email")
            }
        
        # If that fails, try Supabase (for tokens from Supabase auth)
        supabase = get_supabase()
        if not supabase:
            return None
        
        try:
            response = supabase.auth.get_user(token)
            return response.user.model_dump() if response.user else None
        except Exception as e:
            return None
