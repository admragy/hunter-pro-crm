"""
Webhooks API Routes - Separate file
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.services.email_service import webhook_service

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])


class RegisterWebhook(BaseModel):
    event_type: str
    url: str
    secret: Optional[str] = None


class TriggerWebhook(BaseModel):
    event_type: str
    data: Dict[str, Any]


@router.post("/register")
async def register_webhook(data: RegisterWebhook):
    """Register webhook for event"""
    return await webhook_service.register_webhook(
        event_type=data.event_type,
        url=data.url,
        secret=data.secret
    )


@router.post("/trigger")
async def trigger_webhook(data: TriggerWebhook):
    """Trigger webhook"""
    return await webhook_service.trigger_webhook(
        event_type=data.event_type,
        data=data.data
    )


@router.get("/list")
async def list_webhooks():
    """List all webhooks"""
    return {"webhooks": webhook_service.webhooks}
