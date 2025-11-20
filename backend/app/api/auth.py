"""Authentication endpoints using Supabase"""
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel, EmailStr
from typing import Optional
from ..services.auth_service import AuthService
from ..database import get_supabase

router = APIRouter(prefix="/api/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class AuthResponse(BaseModel):
    access_token: str
    user_id: str
    email: str

class GoogleAuthResponse(BaseModel):
    auth_url: str

@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest):
    """Register a new user with email and password"""
    try:
        result = await AuthService.register_with_email(request.email, request.password)
        if not result.get("user"):
            raise HTTPException(status_code=400, detail="Registration failed")
        
        user = result["user"]
        # Create access token
        access_token = AuthService.create_access_token(
            data={"sub": user.get("id"), "email": user.get("email")}
        )
        
        return AuthResponse(
            access_token=access_token,
            user_id=user.get("id"),
            email=user.get("email")
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest):
    """Login with email and password"""
    try:
        result = await AuthService.login_with_email(request.email, request.password)
        if not result.get("user"):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        user = result["user"]
        access_token = result.get("access_token") or AuthService.create_access_token(
            data={"sub": user.get("id"), "email": user.get("email")}
        )
        
        return AuthResponse(
            access_token=access_token,
            user_id=user.get("id"),
            email=user.get("email")
        )
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.get("/google/auth-url", response_model=GoogleAuthResponse)
async def get_google_auth_url():
    """Get Google OAuth authentication URL"""
    try:
        auth_url = await AuthService.get_google_auth_url()
        if not auth_url:
            raise HTTPException(status_code=500, detail="Failed to generate auth URL")
        return GoogleAuthResponse(auth_url=auth_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/verify", response_model=dict)
async def verify_token(token: str):
    """Verify a user session token"""
    try:
        user = await AuthService.verify_user_session(token)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user": user}
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))

@router.post("/logout")
async def logout():
    """Logout user (token invalidation handled by frontend)"""
    return {"message": "Logged out successfully"}