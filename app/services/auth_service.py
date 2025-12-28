"""
Authentication Service - Complete JWT, OAuth2, 2FA
Advanced authentication with multiple providers
"""

import os
import jwt
import pyotp
import qrcode
import io
import base64
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from passlib.context import CryptContext
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthService:
    """Complete Authentication Service"""
    
    def __init__(self):
        self.secret_key = os.getenv("JWT_SECRET", "your-super-secret-jwt-key")
        self.algorithm = os.getenv("JWT_ALGORITHM", "HS256")
        self.access_token_expire = int(os.getenv("JWT_EXPIRATION", "3600"))  # 1 hour
        self.refresh_token_expire = 60 * 60 * 24 * 7  # 7 days
    
    # ==================== PASSWORD HASHING ====================
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash"""
        return pwd_context.verify(plain_password, hashed_password)
    
    # ==================== JWT TOKENS ====================
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """Create JWT access token"""
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(seconds=self.access_token_expire)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create JWT refresh token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(seconds=self.refresh_token_expire)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh"
        })
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode JWT token"""
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
    
    def refresh_access_token(self, refresh_token: str) -> str:
        """Create new access token from refresh token"""
        payload = self.verify_token(refresh_token)
        
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        # Create new access token
        new_token_data = {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role")
        }
        
        return self.create_access_token(new_token_data)
    
    # ==================== 2FA (Two-Factor Authentication) ====================
    
    def generate_2fa_secret(self, user_email: str) -> Dict[str, Any]:
        """Generate 2FA secret and QR code"""
        # Generate secret
        secret = pyotp.random_base32()
        
        # Create TOTP
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=user_email,
            issuer_name="Hunter Pro CRM"
        )
        
        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "secret": secret,
            "qr_code": f"data:image/png;base64,{img_str}",
            "provisioning_uri": provisioning_uri
        }
    
    def verify_2fa_token(self, secret: str, token: str) -> bool:
        """Verify 2FA token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, count: int = 10) -> list:
        """Generate backup codes for 2FA"""
        import secrets
        return [secrets.token_hex(4).upper() for _ in range(count)]
    
    # ==================== OAUTH2 ====================
    
    async def oauth2_google_login(self, code: str) -> Dict[str, Any]:
        """Handle Google OAuth2 login"""
        import httpx
        
        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        redirect_uri = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:5000/auth/google/callback")
        
        # Exchange code for token
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            # Get user info
            user_response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            user_data = user_response.json()
            
            return {
                "email": user_data.get("email"),
                "name": user_data.get("name"),
                "picture": user_data.get("picture"),
                "provider": "google",
                "provider_id": user_data.get("id")
            }
    
    async def oauth2_azure_login(self, code: str) -> Dict[str, Any]:
        """Handle Azure AD OAuth2 login"""
        import httpx
        
        client_id = os.getenv("AZURE_CLIENT_ID")
        client_secret = os.getenv("AZURE_CLIENT_SECRET")
        tenant_id = os.getenv("AZURE_TENANT_ID")
        redirect_uri = os.getenv("AZURE_REDIRECT_URI", "http://localhost:5000/auth/azure/callback")
        
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token",
                data={
                    "code": code,
                    "client_id": client_id,
                    "client_secret": client_secret,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code"
                }
            )
            
            token_data = token_response.json()
            access_token = token_data.get("access_token")
            
            # Get user info
            user_response = await client.get(
                "https://graph.microsoft.com/v1.0/me",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            
            user_data = user_response.json()
            
            return {
                "email": user_data.get("mail") or user_data.get("userPrincipalName"),
                "name": user_data.get("displayName"),
                "provider": "azure",
                "provider_id": user_data.get("id")
            }
    
    # ==================== SESSION MANAGEMENT ====================
    
    def create_session(
        self,
        user_id: int,
        device_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create user session"""
        import uuid
        
        session_id = str(uuid.uuid4())
        
        return {
            "session_id": session_id,
            "user_id": user_id,
            "device_info": device_info or {},
            "created_at": datetime.utcnow(),
            "last_activity": datetime.utcnow(),
            "expires_at": datetime.utcnow() + timedelta(days=30)
        }
    
    # ==================== API KEY MANAGEMENT ====================
    
    def generate_api_key(self, user_id: int, name: str) -> Dict[str, Any]:
        """Generate API key for user"""
        import secrets
        
        api_key = f"hp_{secrets.token_urlsafe(32)}"
        
        return {
            "api_key": api_key,
            "user_id": user_id,
            "name": name,
            "created_at": datetime.utcnow(),
            "last_used": None,
            "expires_at": None  # Never expires by default
        }
    
    def verify_api_key(self, api_key: str) -> Optional[int]:
        """Verify API key and return user_id"""
        # This should query database
        # For now, return None
        # In production: query API keys table
        return None
    
    # ==================== SECURITY ====================
    
    def check_password_strength(self, password: str) -> Dict[str, Any]:
        """Check password strength"""
        import re
        
        score = 0
        feedback = []
        
        # Length check
        if len(password) >= 8:
            score += 1
        else:
            feedback.append("Password should be at least 8 characters")
        
        # Uppercase check
        if re.search(r'[A-Z]', password):
            score += 1
        else:
            feedback.append("Add uppercase letters")
        
        # Lowercase check
        if re.search(r'[a-z]', password):
            score += 1
        else:
            feedback.append("Add lowercase letters")
        
        # Number check
        if re.search(r'\d', password):
            score += 1
        else:
            feedback.append("Add numbers")
        
        # Special character check
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 1
        else:
            feedback.append("Add special characters")
        
        strength = "weak"
        if score >= 4:
            strength = "strong"
        elif score >= 3:
            strength = "medium"
        
        return {
            "strength": strength,
            "score": score,
            "max_score": 5,
            "feedback": feedback
        }
    
    def generate_reset_token(self, user_id: int) -> str:
        """Generate password reset token"""
        data = {
            "sub": str(user_id),
            "type": "reset",
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        
        return jwt.encode(data, self.secret_key, algorithm=self.algorithm)
    
    def verify_reset_token(self, token: str) -> int:
        """Verify password reset token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "reset":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid token type"
                )
            
            return int(payload.get("sub"))
            
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Reset token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid reset token"
            )


# Global auth service instance
auth_service = AuthService()


async def get_auth_service() -> AuthService:
    """Dependency injection for auth service"""
    return auth_service
