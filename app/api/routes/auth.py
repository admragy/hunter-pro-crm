"""
Authentication API Routes
Complete authentication endpoints: JWT, OAuth2, 2FA
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.auth_service import AuthService, get_auth_service

router = APIRouter(prefix="/api/auth", tags=["authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


# ==================== SCHEMAS ====================

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    name: str
    company: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int


class Enable2FAResponse(BaseModel):
    secret: str
    qr_code: str
    backup_codes: list


class Verify2FA(BaseModel):
    token: str


class PasswordReset(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str


class RefreshToken(BaseModel):
    refresh_token: str


# ==================== ENDPOINTS ====================

@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
    auth: AuthService = Depends(get_auth_service)
):
    """
    Register a new user
    
    - **email**: Valid email address
    - **password**: Strong password (min 8 chars, uppercase, lowercase, number, special char)
    - **name**: User's full name
    - **company**: Company name (optional)
    """
    # Check password strength
    strength = auth.check_password_strength(user_data.password)
    if strength["strength"] == "weak":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Password is too weak",
                "feedback": strength["feedback"]
            }
        )
    
    # Check if user exists
    # TODO: Query database
    # For now, proceed with registration
    
    # Hash password
    hashed_password = auth.hash_password(user_data.password)
    
    # Create user (mock)
    user_id = 1  # TODO: Insert into database
    
    # Create tokens
    token_data = {
        "sub": str(user_id),
        "email": user_data.email,
        "role": "user"
    }
    
    access_token = auth.create_access_token(token_data)
    refresh_token = auth.create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=auth.access_token_expire
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    auth: AuthService = Depends(get_auth_service)
):
    """
    Login with email and password
    
    Returns access token and refresh token
    """
    # TODO: Query user from database
    # For now, mock user
    user_email = form_data.username
    user_password = form_data.password
    
    # Mock: Check credentials
    # In production: Query database and verify
    if user_email != "admin@hunterpro.com":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Mock user data
    user_id = 1
    user_role = "admin"
    
    # Create tokens
    token_data = {
        "sub": str(user_id),
        "email": user_email,
        "role": user_role
    }
    
    access_token = auth.create_access_token(token_data)
    refresh_token = auth.create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=auth.access_token_expire
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_data: RefreshToken,
    auth: AuthService = Depends(get_auth_service)
):
    """
    Refresh access token using refresh token
    """
    new_access_token = auth.refresh_access_token(refresh_data.refresh_token)
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=refresh_data.refresh_token,
        expires_in=auth.access_token_expire
    )


@router.get("/me")
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    auth: AuthService = Depends(get_auth_service)
):
    """
    Get current authenticated user
    """
    payload = auth.verify_token(token)
    
    # TODO: Query user from database
    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "role": payload.get("role")
    }


# ==================== 2FA ENDPOINTS ====================

@router.post("/2fa/enable", response_model=Enable2FAResponse)
async def enable_2fa(
    token: str = Depends(oauth2_scheme),
    auth: AuthService = Depends(get_auth_service)
):
    """
    Enable two-factor authentication
    
    Returns:
    - Secret key for authenticator app
    - QR code for easy setup
    - Backup codes for account recovery
    """
    payload = auth.verify_token(token)
    user_email = payload.get("email")
    
    # Generate 2FA secret
    twofa_data = auth.generate_2fa_secret(user_email)
    
    # Generate backup codes
    backup_codes = auth.generate_backup_codes()
    
    # TODO: Save secret and backup codes to database
    
    return Enable2FAResponse(
        secret=twofa_data["secret"],
        qr_code=twofa_data["qr_code"],
        backup_codes=backup_codes
    )


@router.post("/2fa/verify")
async def verify_2fa(
    verify_data: Verify2FA,
    token: str = Depends(oauth2_scheme),
    auth: AuthService = Depends(get_auth_service)
):
    """
    Verify 2FA token
    """
    payload = auth.verify_token(token)
    
    # TODO: Get user's 2FA secret from database
    secret = "mock_secret"  # Replace with actual secret
    
    is_valid = auth.verify_2fa_token(secret, verify_data.token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA token"
        )
    
    return {"message": "2FA verified successfully"}


@router.post("/2fa/disable")
async def disable_2fa(
    token: str = Depends(oauth2_scheme),
    auth: AuthService = Depends(get_auth_service)
):
    """
    Disable two-factor authentication
    """
    payload = auth.verify_token(token)
    
    # TODO: Remove 2FA secret from database
    
    return {"message": "2FA disabled successfully"}


# ==================== PASSWORD RESET ====================

@router.post("/password/reset")
async def request_password_reset(
    reset_data: PasswordReset,
    auth: AuthService = Depends(get_auth_service)
):
    """
    Request password reset
    
    Sends reset link to user's email
    """
    # TODO: Query user from database
    user_id = 1  # Mock
    
    # Generate reset token
    reset_token = auth.generate_reset_token(user_id)
    
    # TODO: Send email with reset link
    reset_link = f"http://localhost:5000/reset-password?token={reset_token}"
    
    return {
        "message": "Password reset link sent to your email",
        "reset_link": reset_link  # For development only
    }


@router.post("/password/reset/confirm")
async def confirm_password_reset(
    reset_data: PasswordResetConfirm,
    auth: AuthService = Depends(get_auth_service)
):
    """
    Confirm password reset with token
    """
    # Verify reset token
    user_id = auth.verify_reset_token(reset_data.token)
    
    # Check password strength
    strength = auth.check_password_strength(reset_data.new_password)
    if strength["strength"] == "weak":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Password is too weak",
                "feedback": strength["feedback"]
            }
        )
    
    # Hash new password
    new_hashed_password = auth.hash_password(reset_data.new_password)
    
    # TODO: Update password in database
    
    return {"message": "Password reset successful"}


# ==================== OAUTH2 ENDPOINTS ====================

@router.get("/google/authorize")
async def google_authorize():
    """
    Redirect to Google OAuth2 authorization
    """
    import os
    
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/api/auth/google/callback")
    
    auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid email profile&"
        f"access_type=offline"
    )
    
    return {"auth_url": auth_url}


@router.get("/google/callback")
async def google_callback(
    code: str,
    db: AsyncSession = Depends(get_db),
    auth: AuthService = Depends(get_auth_service)
):
    """
    Handle Google OAuth2 callback
    """
    # Get user data from Google
    user_data = await auth.oauth2_google_login(code)
    
    # TODO: Find or create user in database
    user_id = 1  # Mock
    
    # Create tokens
    token_data = {
        "sub": str(user_id),
        "email": user_data["email"],
        "role": "user"
    }
    
    access_token = auth.create_access_token(token_data)
    refresh_token = auth.create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=auth.access_token_expire
    )


@router.get("/azure/authorize")
async def azure_authorize():
    """
    Redirect to Azure AD OAuth2 authorization
    """
    import os
    
    client_id = os.getenv("AZURE_CLIENT_ID")
    tenant_id = os.getenv("AZURE_TENANT_ID")
    redirect_uri = os.getenv("AZURE_REDIRECT_URI", "http://localhost:5000/api/auth/azure/callback")
    
    auth_url = (
        f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize?"
        f"client_id={client_id}&"
        f"redirect_uri={redirect_uri}&"
        f"response_type=code&"
        f"scope=openid email profile"
    )
    
    return {"auth_url": auth_url}


@router.get("/azure/callback")
async def azure_callback(
    code: str,
    db: AsyncSession = Depends(get_db),
    auth: AuthService = Depends(get_auth_service)
):
    """
    Handle Azure AD OAuth2 callback
    """
    # Get user data from Azure
    user_data = await auth.oauth2_azure_login(code)
    
    # TODO: Find or create user in database
    user_id = 1  # Mock
    
    # Create tokens
    token_data = {
        "sub": str(user_id),
        "email": user_data["email"],
        "role": "user"
    }
    
    access_token = auth.create_access_token(token_data)
    refresh_token = auth.create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=auth.access_token_expire
    )


# ==================== API KEYS ====================

@router.post("/api-keys")
async def create_api_key(
    name: str,
    token: str = Depends(oauth2_scheme),
    auth: AuthService = Depends(get_auth_service)
):
    """
    Create API key for programmatic access
    """
    payload = auth.verify_token(token)
    user_id = int(payload.get("sub"))
    
    api_key_data = auth.generate_api_key(user_id, name)
    
    # TODO: Save to database
    
    return api_key_data


@router.get("/api-keys")
async def list_api_keys(
    token: str = Depends(oauth2_scheme),
    auth: AuthService = Depends(get_auth_service)
):
    """
    List user's API keys
    """
    payload = auth.verify_token(token)
    
    # TODO: Query from database
    
    return {"api_keys": []}


# ==================== UTILITY ====================

@router.post("/check-password-strength")
async def check_password_strength(
    password: str,
    auth: AuthService = Depends(get_auth_service)
):
    """
    Check password strength
    
    Returns strength score and feedback
    """
    return auth.check_password_strength(password)
