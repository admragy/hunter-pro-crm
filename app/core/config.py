"""
Hunter Pro CRM Ultimate Enterprise - Configuration Management
Version: 7.0.0
"""

import os
from typing import List, Optional
from pydantic_settings import BaseSettings
from pydantic import Field, validator
from functools import lru_cache


class Settings(BaseSettings):
    """Application Settings with validation and type hints"""
    
    # ========== Application ==========
    APP_NAME: str = "Hunter Pro CRM Ultimate Enterprise"
    APP_VERSION: str = "7.0.0"
    APP_DESCRIPTION: str = "AI-Powered CRM with Multi-Channel Integration"
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    DEBUG: bool = True
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 5000
    WORKERS: int = 4
    RELOAD: bool = True
    
    # ========== Security ==========
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 10080  # 7 days
    REFRESH_TOKEN_EXPIRATION_DAYS: int = 30
    
    ENCRYPTION_KEY: Optional[str] = None
    AES_KEY: Optional[str] = None
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # ========== Database ==========
    DATABASE_URL: str = "sqlite+aiosqlite:///./hunter_pro.db"
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_ECHO: bool = False
    
    # ========== Redis ==========
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_PASSWORD: Optional[str] = None
    REDIS_DB: int = 0
    REDIS_MAX_CONNECTIONS: int = 50
    CACHE_TTL: int = 3600
    CACHE_ENABLED: bool = True
    
    # ========== AI Configuration ==========
    DEFAULT_AI_PROVIDER: str = "auto"
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2000
    AI_TIMEOUT: int = 30
    
    # OpenAI
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_ORG_ID: Optional[str] = None
    
    # Anthropic Claude
    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20240620"
    
    # Google Gemini
    GOOGLE_API_KEY: Optional[str] = None
    GOOGLE_PROJECT_ID: Optional[str] = None
    GEMINI_FLASH_MODEL: str = "gemini-1.5-flash"
    GEMINI_PRO_MODEL: str = "gemini-1.5-pro"
    
    # Groq
    GROQ_API_KEY: Optional[str] = None
    GROQ_MODEL: str = "llama-3.1-70b-versatile"
    
    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3:8b"
    OLLAMA_TIMEOUT: int = 120
    
    # Vector Database
    VECTOR_DB_TYPE: str = "qdrant"
    PINECONE_API_KEY: Optional[str] = None
    PINECONE_ENVIRONMENT: Optional[str] = None
    PINECONE_INDEX_NAME: str = "hunter-pro-vectors"
    
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: Optional[str] = None
    QDRANT_COLLECTION_NAME: str = "hunter_pro_embeddings"
    
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384
    
    # ========== WhatsApp ==========
    WHATSAPP_MODE: str = "selenium"
    WHATSAPP_ENABLED: bool = True
    WHATSAPP_HEADLESS: bool = False
    WHATSAPP_PHONE_NUMBER: Optional[str] = None
    WHATSAPP_SESSION_PATH: str = "./whatsapp_sessions"
    WHATSAPP_DELAY_MIN: int = 1
    WHATSAPP_DELAY_MAX: int = 3
    WHATSAPP_MAX_RETRIES: int = 3
    
    # Twilio
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_WHATSAPP_NUMBER: Optional[str] = None
    
    # Cloud API
    WHATSAPP_CLOUD_API_TOKEN: Optional[str] = None
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = None
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = None
    WEBHOOK_VERIFY_TOKEN: Optional[str] = None
    WEBHOOK_SECRET: Optional[str] = None
    
    BULK_MESSAGE_BATCH_SIZE: int = 50
    BULK_MESSAGE_DELAY: int = 2
    BULK_MESSAGE_MAX_PER_DAY: int = 1000
    
    # ========== Facebook & Social Media ==========
    FACEBOOK_APP_ID: Optional[str] = None
    FACEBOOK_APP_SECRET: Optional[str] = None
    FACEBOOK_ACCESS_TOKEN: Optional[str] = None
    FACEBOOK_AD_ACCOUNT_ID: Optional[str] = None
    FACEBOOK_PAGE_ID: Optional[str] = None
    FACEBOOK_PIXEL_ID: Optional[str] = None
    FACEBOOK_API_VERSION: str = "v19.0"
    
    INSTAGRAM_BUSINESS_ACCOUNT_ID: Optional[str] = None
    INSTAGRAM_ACCESS_TOKEN: Optional[str] = None
    
    # Google Ads
    GOOGLE_ADS_CLIENT_ID: Optional[str] = None
    GOOGLE_ADS_CLIENT_SECRET: Optional[str] = None
    GOOGLE_ADS_DEVELOPER_TOKEN: Optional[str] = None
    GOOGLE_ADS_REFRESH_TOKEN: Optional[str] = None
    GOOGLE_ADS_CUSTOMER_ID: Optional[str] = None
    
    # TikTok
    TIKTOK_APP_ID: Optional[str] = None
    TIKTOK_SECRET: Optional[str] = None
    TIKTOK_ACCESS_TOKEN: Optional[str] = None
    TIKTOK_ADVERTISER_ID: Optional[str] = None
    
    # LinkedIn
    LINKEDIN_CLIENT_ID: Optional[str] = None
    LINKEDIN_CLIENT_SECRET: Optional[str] = None
    LINKEDIN_ACCESS_TOKEN: Optional[str] = None
    LINKEDIN_ACCOUNT_ID: Optional[str] = None
    
    # ========== Email ==========
    SMTP_ENABLED: bool = True
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USE_TLS: bool = True
    SMTP_USERNAME: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_FROM_EMAIL: Optional[str] = None
    SMTP_FROM_NAME: str = "Hunter Pro CRM"
    
    SENDGRID_API_KEY: Optional[str] = None
    MAILGUN_API_KEY: Optional[str] = None
    MAILGUN_DOMAIN: Optional[str] = None
    
    # ========== SMS ==========
    VONAGE_API_KEY: Optional[str] = None
    VONAGE_API_SECRET: Optional[str] = None
    VONAGE_FROM_NUMBER: Optional[str] = None
    
    MESSAGEBIRD_API_KEY: Optional[str] = None
    
    # ========== Payments ==========
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None
    STRIPE_SECRET_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    
    PAYPAL_CLIENT_ID: Optional[str] = None
    PAYPAL_CLIENT_SECRET: Optional[str] = None
    PAYPAL_MODE: str = "sandbox"
    
    # ========== CRM Integrations ==========
    SALESFORCE_USERNAME: Optional[str] = None
    SALESFORCE_PASSWORD: Optional[str] = None
    SALESFORCE_SECURITY_TOKEN: Optional[str] = None
    SALESFORCE_DOMAIN: str = "login"
    
    HUBSPOT_API_KEY: Optional[str] = None
    HUBSPOT_ACCESS_TOKEN: Optional[str] = None
    
    PIPEDRIVE_API_TOKEN: Optional[str] = None
    PIPEDRIVE_COMPANY_DOMAIN: Optional[str] = None
    
    # ========== E-commerce ==========
    SHOPIFY_API_KEY: Optional[str] = None
    SHOPIFY_API_SECRET: Optional[str] = None
    SHOPIFY_ACCESS_TOKEN: Optional[str] = None
    SHOPIFY_STORE_NAME: Optional[str] = None
    
    WOOCOMMERCE_URL: Optional[str] = None
    WOOCOMMERCE_CONSUMER_KEY: Optional[str] = None
    WOOCOMMERCE_CONSUMER_SECRET: Optional[str] = None
    
    # ========== Cloud Storage ==========
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_S3_BUCKET: Optional[str] = None
    
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    GOOGLE_CLOUD_BUCKET: Optional[str] = None
    GOOGLE_APPLICATION_CREDENTIALS: Optional[str] = None
    
    AZURE_STORAGE_CONNECTION_STRING: Optional[str] = None
    AZURE_STORAGE_CONTAINER: Optional[str] = None
    
    # ========== Analytics ==========
    GOOGLE_ANALYTICS_ID: Optional[str] = None
    GOOGLE_TAG_MANAGER_ID: Optional[str] = None
    MIXPANEL_TOKEN: Optional[str] = None
    SEGMENT_WRITE_KEY: Optional[str] = None
    
    SENTRY_DSN: Optional[str] = None
    SENTRY_ENVIRONMENT: str = "development"
    SENTRY_TRACES_SAMPLE_RATE: float = 1.0
    
    # ========== Background Jobs ==========
    CELERY_BROKER_URL: str = "redis://localhost:6379/1"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/2"
    
    # ========== WebSocket ==========
    WEBSOCKET_ENABLED: bool = True
    WEBSOCKET_PATH: str = "/ws"
    WEBSOCKET_PING_INTERVAL: int = 30
    
    # ========== File Upload ==========
    MAX_UPLOAD_SIZE: int = 10485760  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "gif", "pdf", "doc", "docx", "xls", "xlsx", "csv", "txt", "zip"]
    UPLOAD_DIRECTORY: str = "./uploads"
    
    # ========== PWA ==========
    PWA_ENABLED: bool = True
    PWA_NAME: str = "Hunter Pro CRM"
    PWA_SHORT_NAME: str = "HunterPro"
    PWA_THEME_COLOR: str = "#4F46E5"
    PWA_BACKGROUND_COLOR: str = "#ffffff"
    
    # ========== Localization ==========
    DEFAULT_LANGUAGE: str = "ar"
    SUPPORTED_LANGUAGES: List[str] = ["ar", "en", "fr", "de", "es"]
    TIMEZONE: str = "Asia/Riyadh"
    
    # ========== Feature Flags ==========
    FEATURE_AI_CHAT: bool = True
    FEATURE_WHATSAPP: bool = True
    FEATURE_FACEBOOK_ADS: bool = True
    FEATURE_EMAIL_CAMPAIGNS: bool = True
    FEATURE_SMS_CAMPAIGNS: bool = True
    FEATURE_ANALYTICS: bool = True
    FEATURE_API: bool = True
    FEATURE_WEBHOOKS: bool = True
    FEATURE_MULTI_TENANT: bool = False
    
    # ========== Compliance ==========
    GDPR_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 365
    ENABLE_AUDIT_LOG: bool = True
    
    # ========== Development ==========
    ENABLE_SWAGGER: bool = True
    ENABLE_REDOC: bool = True
    ENABLE_GRAPHIQL: bool = True
    DEBUG_TOOLBAR: bool = True
    
    # ========== Admin ==========
    ADMIN_EMAIL: str = "admin@hunterpro.com"
    ADMIN_PASSWORD: str = "ChangeThisPassword123!"
    ADMIN_FIRST_NAME: str = "Admin"
    ADMIN_LAST_NAME: str = "User"
    
    # ========== Custom ==========
    COMPANY_NAME: str = "Your Company Name"
    COMPANY_LOGO_URL: str = "/static/images/logo.png"
    SUPPORT_EMAIL: str = "support@hunterpro.com"
    SUPPORT_PHONE: str = "+1-234-567-8900"
    
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v
    
    @validator("SUPPORTED_LANGUAGES", pre=True)
    def parse_supported_languages(cls, v):
        if isinstance(v, str):
            return [lang.strip() for lang in v.split(",")]
        return v
    
    @validator("ALLOWED_EXTENSIONS", pre=True)
    def parse_allowed_extensions(cls, v):
        if isinstance(v, str):
            return [ext.strip() for ext in v.split(",")]
        return v
    
    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"
    
    @property
    def is_staging(self) -> bool:
        return self.ENVIRONMENT == "staging"
    
    @property
    def database_url_sync(self) -> str:
        """Convert async database URL to sync version"""
        return self.DATABASE_URL.replace("+aiosqlite", "").replace("+asyncpg", "")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Global settings instance
settings = get_settings()


# Helper functions
def is_feature_enabled(feature_name: str) -> bool:
    """Check if a feature flag is enabled"""
    feature_attr = f"FEATURE_{feature_name.upper()}"
    return getattr(settings, feature_attr, False)


def get_ai_provider_config(provider: str) -> dict:
    """Get configuration for specific AI provider"""
    configs = {
        "openai": {
            "api_key": settings.OPENAI_API_KEY,
            "model": settings.OPENAI_MODEL,
            "org_id": settings.OPENAI_ORG_ID,
        },
        "anthropic": {
            "api_key": settings.ANTHROPIC_API_KEY,
            "model": settings.ANTHROPIC_MODEL,
        },
        "gemini_flash": {
            "api_key": settings.GOOGLE_API_KEY,
            "model": settings.GEMINI_FLASH_MODEL,
        },
        "gemini_pro": {
            "api_key": settings.GOOGLE_API_KEY,
            "model": settings.GEMINI_PRO_MODEL,
        },
        "groq": {
            "api_key": settings.GROQ_API_KEY,
            "model": settings.GROQ_MODEL,
        },
        "ollama": {
            "base_url": settings.OLLAMA_BASE_URL,
            "model": settings.OLLAMA_MODEL,
            "timeout": settings.OLLAMA_TIMEOUT,
        },
    }
    return configs.get(provider, {})


def get_whatsapp_config() -> dict:
    """Get WhatsApp configuration based on mode"""
    base_config = {
        "mode": settings.WHATSAPP_MODE,
        "enabled": settings.WHATSAPP_ENABLED,
        "phone_number": settings.WHATSAPP_PHONE_NUMBER,
    }
    
    if settings.WHATSAPP_MODE == "selenium":
        base_config.update({
            "headless": settings.WHATSAPP_HEADLESS,
            "session_path": settings.WHATSAPP_SESSION_PATH,
            "delay_min": settings.WHATSAPP_DELAY_MIN,
            "delay_max": settings.WHATSAPP_DELAY_MAX,
        })
    elif settings.WHATSAPP_MODE == "twilio":
        base_config.update({
            "account_sid": settings.TWILIO_ACCOUNT_SID,
            "auth_token": settings.TWILIO_AUTH_TOKEN,
            "whatsapp_number": settings.TWILIO_WHATSAPP_NUMBER,
        })
    elif settings.WHATSAPP_MODE == "cloud_api":
        base_config.update({
            "api_token": settings.WHATSAPP_CLOUD_API_TOKEN,
            "phone_number_id": settings.WHATSAPP_PHONE_NUMBER_ID,
            "business_account_id": settings.WHATSAPP_BUSINESS_ACCOUNT_ID,
        })
    
    return base_config


if __name__ == "__main__":
    # Test configuration
    print(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION}")
    print(f"📦 Environment: {settings.ENVIRONMENT}")
    print(f"🔧 Debug Mode: {settings.DEBUG}")
    print(f"🗄️ Database: {settings.DATABASE_URL}")
    print(f"🤖 Default AI Provider: {settings.DEFAULT_AI_PROVIDER}")
    print(f"📱 WhatsApp Mode: {settings.WHATSAPP_MODE}")
    print(f"✅ Configuration loaded successfully!")