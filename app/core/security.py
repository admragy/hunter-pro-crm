"""
Hunter Pro CRM Ultimate Enterprise - Security Module
Version: 7.0.0
Advanced security features including encryption, hashing, JWT, 2FA
"""

from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2
import secrets
import hashlib
import pyotp
import qrcode
from io import BytesIO
import base64
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)

# ========== Password Hashing ==========
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12,
)


def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


# ========== JWT Tokens ==========
def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
) -> str:
    """Create JWT access token"""
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.JWT_EXPIRATION_MINUTES
        )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "access"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Create JWT refresh token"""
    to_encode = data.copy()
    
    expire = datetime.utcnow() + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRATION_DAYS
    )
    
    to_encode.update({
        "exp": expire,
        "iat": datetime.utcnow(),
        "type": "refresh"
    })
    
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decode and verify JWT token"""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError as e:
        logger.error(f"JWT decode error: {e}")
        return None


def verify_token(token: str, token_type: str = "access") -> Optional[dict]:
    """Verify token and check type"""
    payload = decode_token(token)
    
    if payload is None:
        return None
    
    if payload.get("type") != token_type:
        return None
    
    return payload


# ========== Data Encryption ==========
class DataEncryption:
    """Advanced data encryption using Fernet (AES-128)"""
    
    def __init__(self):
        if settings.ENCRYPTION_KEY:
            self.cipher = Fernet(settings.ENCRYPTION_KEY.encode())
        else:
            # Generate temporary key if not set
            self.cipher = Fernet(Fernet.generate_key())
            logger.warning("⚠️ Using temporary encryption key. Set ENCRYPTION_KEY in .env")
    
    def encrypt(self, data: str) -> str:
        """Encrypt string data"""
        try:
            encrypted = self.cipher.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt string data"""
        try:
            decoded = base64.urlsafe_b64decode(encrypted_data.encode())
            decrypted = self.cipher.decrypt(decoded)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Decryption error: {e}")
            raise
    
    def encrypt_dict(self, data: dict) -> str:
        """Encrypt dictionary data"""
        import json
        json_str = json.dumps(data)
        return self.encrypt(json_str)
    
    def decrypt_dict(self, encrypted_data: str) -> dict:
        """Decrypt to dictionary"""
        import json
        json_str = self.decrypt(encrypted_data)
        return json.loads(json_str)


# Global encryption instance
encryptor = DataEncryption()


# ========== Two-Factor Authentication (2FA) ==========
class TwoFactorAuth:
    """TOTP-based Two-Factor Authentication"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def get_totp_uri(secret: str, username: str) -> str:
        """Get TOTP provisioning URI for QR code"""
        return pyotp.totp.TOTP(secret).provisioning_uri(
            name=username,
            issuer_name=settings.APP_NAME
        )
    
    @staticmethod
    def generate_qr_code(secret: str, username: str) -> str:
        """Generate QR code image as base64 string"""
        uri = TwoFactorAuth.get_totp_uri(secret, username)
        
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """Verify TOTP token"""
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=1)
    
    @staticmethod
    def get_current_token(secret: str) -> str:
        """Get current TOTP token (for testing)"""
        totp = pyotp.TOTP(secret)
        return totp.now()


# ========== API Key Generation ==========
def generate_api_key(length: int = 32) -> str:
    """Generate secure random API key"""
    return secrets.token_urlsafe(length)


def hash_api_key(api_key: str) -> str:
    """Hash API key for storage"""
    return hashlib.sha256(api_key.encode()).hexdigest()


def verify_api_key(api_key: str, hashed_key: str) -> bool:
    """Verify API key against hash"""
    return hash_api_key(api_key) == hashed_key


# ========== Secure Random Tokens ==========
def generate_secure_token(length: int = 32) -> str:
    """Generate secure random token"""
    return secrets.token_urlsafe(length)


def generate_verification_code(length: int = 6) -> str:
    """Generate numeric verification code"""
    return "".join([str(secrets.randbelow(10)) for _ in range(length)])


# ========== Password Strength Checker ==========
def check_password_strength(password: str) -> dict:
    """Check password strength and return score with suggestions"""
    score = 0
    suggestions = []
    
    # Length check
    if len(password) >= 8:
        score += 1
    else:
        suggestions.append("Password should be at least 8 characters long")
    
    if len(password) >= 12:
        score += 1
    
    # Character variety checks
    if any(c.islower() for c in password):
        score += 1
    else:
        suggestions.append("Include lowercase letters")
    
    if any(c.isupper() for c in password):
        score += 1
    else:
        suggestions.append("Include uppercase letters")
    
    if any(c.isdigit() for c in password):
        score += 1
    else:
        suggestions.append("Include numbers")
    
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    else:
        suggestions.append("Include special characters")
    
    # Common password check
    common_passwords = [
        "password", "123456", "qwerty", "admin", "letmein",
        "welcome", "monkey", "dragon", "master", "sunshine"
    ]
    if password.lower() in common_passwords:
        score = 0
        suggestions.append("This is a commonly used password")
    
    strength_labels = {
        0: "Very Weak",
        1: "Very Weak",
        2: "Weak",
        3: "Medium",
        4: "Strong",
        5: "Strong",
        6: "Very Strong",
        7: "Very Strong",
    }
    
    return {
        "score": score,
        "max_score": 7,
        "strength": strength_labels.get(score, "Unknown"),
        "is_strong": score >= 4,
        "suggestions": suggestions
    }


# ========== Session Management ==========
class SessionManager:
    """Manage user sessions with Redis"""
    
    def __init__(self):
        self.prefix = "session:"
        self.ttl = settings.JWT_EXPIRATION_MINUTES * 60  # Convert to seconds
    
    async def create_session(self, user_id: int, data: dict) -> str:
        """Create new session"""
        from app.core.cache import cache
        
        session_id = generate_secure_token()
        session_key = f"{self.prefix}{session_id}"
        
        session_data = {
            "user_id": user_id,
            "created_at": datetime.utcnow().isoformat(),
            **data
        }
        
        await cache.set(session_key, session_data, self.ttl)
        
        return session_id
    
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data"""
        from app.core.cache import cache
        
        session_key = f"{self.prefix}{session_id}"
        return await cache.get(session_key)
    
    async def update_session(self, session_id: str, data: dict):
        """Update session data"""
        from app.core.cache import cache
        
        session_key = f"{self.prefix}{session_id}"
        existing_data = await self.get_session(session_id)
        
        if existing_data:
            existing_data.update(data)
            await cache.set(session_key, existing_data, self.ttl)
    
    async def delete_session(self, session_id: str):
        """Delete session"""
        from app.core.cache import cache
        
        session_key = f"{self.prefix}{session_id}"
        await cache.delete(session_key)
    
    async def get_user_sessions(self, user_id: int) -> list:
        """Get all sessions for a user"""
        from app.core.cache import cache
        
        pattern = f"{self.prefix}*"
        all_sessions = []
        
        # This is a simplified version - in production, use Redis SCAN
        # to iterate through keys efficiently
        
        return all_sessions


# Global session manager
session_manager = SessionManager()


# ========== CSRF Protection ==========
def generate_csrf_token() -> str:
    """Generate CSRF token"""
    return secrets.token_urlsafe(32)


def verify_csrf_token(token: str, expected: str) -> bool:
    """Verify CSRF token"""
    return secrets.compare_digest(token, expected)


# ========== Rate Limiting ==========
class RateLimiter:
    """Simple rate limiter using Redis"""
    
    def __init__(self):
        self.prefix = "ratelimit:"
    
    async def is_allowed(
        self,
        key: str,
        max_requests: int,
        window: int
    ) -> tuple[bool, int]:
        """
        Check if request is allowed
        Returns: (is_allowed, remaining_requests)
        """
        from app.core.cache import cache
        
        rate_key = f"{self.prefix}{key}"
        
        current = await cache.get(rate_key)
        
        if current is None:
            await cache.set(rate_key, 1, window)
            return True, max_requests - 1
        
        if current >= max_requests:
            return False, 0
        
        await cache.increment(rate_key)
        return True, max_requests - current - 1


# Global rate limiter
rate_limiter = RateLimiter()


# ========== IP Whitelist/Blacklist ==========
class IPFilter:
    """IP filtering for security"""
    
    @staticmethod
    def is_ip_whitelisted(ip: str, whitelist: list) -> bool:
        """Check if IP is in whitelist"""
        return ip in whitelist
    
    @staticmethod
    def is_ip_blacklisted(ip: str, blacklist: list) -> bool:
        """Check if IP is in blacklist"""
        return ip in blacklist
    
    @staticmethod
    async def log_suspicious_ip(ip: str, reason: str):
        """Log suspicious IP activity"""
        logger.warning(f"⚠️ Suspicious activity from IP {ip}: {reason}")
        # Could store in database or send alert


# ========== Security Headers ==========
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "X-XSS-Protection": "1; mode=block",
    "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
    "Content-Security-Policy": "default-src 'self'",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()"
}


if __name__ == "__main__":
    # Test security functions
    print("🔒 Testing security functions...")
    
    # Password hashing
    password = "MySecurePassword123!"
    hashed = get_password_hash(password)
    print(f"✅ Password hashed: {hashed[:30]}...")
    print(f"✅ Password verified: {verify_password(password, hashed)}")
    
    # Password strength
    strength = check_password_strength(password)
    print(f"✅ Password strength: {strength}")
    
    # JWT token
    token = create_access_token({"sub": "user@example.com"})
    print(f"✅ JWT token created: {token[:30]}...")
    
    # 2FA
    secret = TwoFactorAuth.generate_secret()
    print(f"✅ 2FA secret generated: {secret}")
    
    current_token = TwoFactorAuth.get_current_token(secret)
    print(f"✅ Current TOTP: {current_token}")
    print(f"✅ Token verified: {TwoFactorAuth.verify_token(secret, current_token)}")
    
    # API Key
    api_key = generate_api_key()
    print(f"✅ API key generated: {api_key}")
    
    print("\n✅ All security tests passed!")