"""
WhatsApp API Routes
Complete WhatsApp integration endpoints
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.services.whatsapp_service import WhatsAppService, get_whatsapp_service

router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])


# ==================== SCHEMAS ====================

class SendMessage(BaseModel):
    phone: str
    message: str
    media_url: Optional[str] = None
    media_type: Optional[str] = None


class SendTemplate(BaseModel):
    phone: str
    template_name: str
    language: str = "en"
    parameters: Optional[List[str]] = None


class BulkMessage(BaseModel):
    contacts: List[Dict[str, str]]
    message: str
    delay: int = 2


# ==================== ENDPOINTS ====================

@router.post("/send")
async def send_whatsapp_message(
    data: SendMessage,
    whatsapp: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Send WhatsApp message
    
    Supports all 6 modes: Selenium, Twilio, Cloud API, Webhook, Local, Bulk
    """
    result = await whatsapp.send_message(
        phone=data.phone,
        message=data.message,
        media_url=data.media_url,
        media_type=data.media_type
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    return result


@router.post("/send-template")
async def send_template_message(
    data: SendTemplate,
    whatsapp: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Send WhatsApp template message (Cloud API only)
    """
    result = await whatsapp.send_template_message(
        phone=data.phone,
        template_name=data.template_name,
        language=data.language,
        parameters=data.parameters
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error"))
    
    return result


@router.post("/send-bulk")
async def send_bulk_messages(
    data: BulkMessage,
    whatsapp: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Send bulk WhatsApp messages
    
    Includes rate limiting and personalization
    """
    result = await whatsapp.send_bulk_messages(
        contacts=data.contacts,
        message=data.message,
        delay=data.delay
    )
    
    return result


@router.post("/webhook")
async def whatsapp_webhook(
    webhook_data: Dict[str, Any],
    whatsapp: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Handle incoming WhatsApp webhook
    """
    result = await whatsapp.handle_webhook(webhook_data)
    return result


@router.get("/status")
async def whatsapp_status(
    whatsapp: WhatsAppService = Depends(get_whatsapp_service)
):
    """
    Get WhatsApp service status
    """
    return whatsapp.get_status()
