"""
Services Package
Business logic and integrations
"""

from app.services.ai_service import AIService, ai_service, get_ai_service
from app.services.crm_service import CRMService, get_crm_service

__all__ = [
    "AIService",
    "ai_service",
    "get_ai_service",
    "CRMService",
    "get_crm_service"
]
