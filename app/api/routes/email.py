"""
Email & Webhook API Routes
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any

from app.services.email_service import email_service, webhook_service

# Email Router
email_router = APIRouter(prefix="/api/email", tags=["email"])

# Webhook Router
webhook_router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


# ==================== EMAIL SCHEMAS ====================

class SendEmail(BaseModel):
    to_email: EmailStr | List[EmailStr]
    subject: str
    body: str
    html_body: Optional[str] = None
    cc: Optional[List[EmailStr]] = None
    bcc: Optional[List[EmailStr]] = None


class WelcomeEmail(BaseModel):
    to_email: EmailStr
    name: str


# ==================== WEBHOOK SCHEMAS ====================

class RegisterWebhook(BaseModel):
    event_type: str
    url: str
    secret: Optional[str] = None


class TriggerWebhook(BaseModel):
    event_type: str
    data: Dict[str, Any]


# ==================== EMAIL ENDPOINTS ====================

@email_router.post("/send")
async def send_email(data: SendEmail):
    """
    Send email
    """
    return await email_service.send_email(
        to_email=data.to_email,
        subject=data.subject,
        body=data.body,
        html_body=data.html_body,
        cc=data.cc,
        bcc=data.bcc
    )


@email_router.post("/welcome")
async def send_welcome_email(data: WelcomeEmail):
    """
    Send welcome email to new user
    """
    return await email_service.send_welcome_email(
        to_email=data.to_email,
        name=data.name
    )


# ==================== WEBHOOK ENDPOINTS ====================

@webhook_router.post("/register")
async def register_webhook(data: RegisterWebhook):
    """
    Register webhook for event
    """
    return await webhook_service.register_webhook(
        event_type=data.event_type,
        url=data.url,
        secret=data.secret
    )


@webhook_router.post("/trigger")
async def trigger_webhook(data: TriggerWebhook):
    """
    Trigger webhook manually (for testing)
    """
    return await webhook_service.trigger_webhook(
        event_type=data.event_type,
        data=data.data
    )


@webhook_router.get("/list")
async def list_webhooks():
    """
    List all registered webhooks
    """
    return {
        "webhooks": webhook_service.webhooks
    }


# Export routers
router = email_router
webhooks_router = webhook_router

__all__ = ["router", "webhooks_router"]
