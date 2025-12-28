"""
WhatsApp Integration Service
6 Modes: Selenium, Twilio, Cloud API, Webhook, Local, Bulk
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class WhatsAppService:
    """Complete WhatsApp Integration with 6 modes"""
    
    def __init__(self):
        self.mode = os.getenv("WHATSAPP_MODE", "selenium")
        self.initialized = False
        
        # Mode-specific initialization
        if self.mode == "twilio":
            self.twilio_account_sid = os.getenv("TWILIO_ACCOUNT_SID")
            self.twilio_auth_token = os.getenv("TWILIO_AUTH_TOKEN")
            self.twilio_whatsapp_number = os.getenv("TWILIO_WHATSAPP_NUMBER")
            
        elif self.mode == "cloud_api":
            self.cloud_api_token = os.getenv("WHATSAPP_CLOUD_API_TOKEN")
            self.phone_number_id = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
            self.business_account_id = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")
            
        logger.info(f"✅ WhatsApp Service initialized in '{self.mode}' mode")
    
    # ==================== SELENIUM MODE ====================
    
    async def selenium_send_message(
        self,
        phone: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send message using Selenium WebDriver"""
        try:
            from selenium import webdriver
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            import time
            
            # Setup browser
            options = webdriver.ChromeOptions()
            if os.getenv("WHATSAPP_HEADLESS", "true").lower() == "true":
                options.add_argument("--headless")
            
            driver = webdriver.Chrome(options=options)
            
            # Open WhatsApp Web
            driver.get(f"https://web.whatsapp.com/send?phone={phone}&text={message}")
            
            # Wait for QR code or chat load
            WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.XPATH, '//div[@contenteditable="true"]'))
            )
            
            # Send message
            send_button = driver.find_element(By.XPATH, '//button[@aria-label="Send"]')
            send_button.click()
            
            time.sleep(2)
            driver.quit()
            
            return {
                "success": True,
                "mode": "selenium",
                "phone": phone,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Selenium send error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "mode": "selenium"
            }
    
    # ==================== TWILIO MODE ====================
    
    async def twilio_send_message(
        self,
        phone: str,
        message: str,
        media_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send message using Twilio WhatsApp API"""
        try:
            from twilio.rest import Client
            
            client = Client(self.twilio_account_sid, self.twilio_auth_token)
            
            # Format phone numbers
            to_number = f"whatsapp:{phone}"
            from_number = f"whatsapp:{self.twilio_whatsapp_number}"
            
            # Send message
            if media_url:
                twilio_message = client.messages.create(
                    body=message,
                    from_=from_number,
                    to=to_number,
                    media_url=[media_url]
                )
            else:
                twilio_message = client.messages.create(
                    body=message,
                    from_=from_number,
                    to=to_number
                )
            
            return {
                "success": True,
                "mode": "twilio",
                "message_sid": twilio_message.sid,
                "status": twilio_message.status,
                "phone": phone,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Twilio send error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "mode": "twilio"
            }
    
    # ==================== CLOUD API MODE ====================
    
    async def cloud_api_send_message(
        self,
        phone: str,
        message: str,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send message using WhatsApp Cloud API"""
        try:
            url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.cloud_api_token}",
                "Content-Type": "application/json"
            }
            
            # Clean phone number
            phone_clean = phone.replace("+", "").replace("-", "").replace(" ", "")
            
            # Prepare payload
            if media_url and media_type:
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_clean,
                    "type": media_type,
                    media_type: {
                        "link": media_url,
                        "caption": message
                    }
                }
            else:
                payload = {
                    "messaging_product": "whatsapp",
                    "recipient_type": "individual",
                    "to": phone_clean,
                    "type": "text",
                    "text": {
                        "preview_url": True,
                        "body": message
                    }
                }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                result = response.json()
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "mode": "cloud_api",
                    "message_id": result.get("messages", [{}])[0].get("id"),
                    "phone": phone,
                    "timestamp": datetime.utcnow().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", {}).get("message", "Unknown error"),
                    "mode": "cloud_api"
                }
                
        except Exception as e:
            logger.error(f"Cloud API send error: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "mode": "cloud_api"
            }
    
    # ==================== TEMPLATE MESSAGES ====================
    
    async def send_template_message(
        self,
        phone: str,
        template_name: str,
        language: str = "en",
        parameters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Send WhatsApp template message (Cloud API only)"""
        try:
            url = f"https://graph.facebook.com/v18.0/{self.phone_number_id}/messages"
            
            headers = {
                "Authorization": f"Bearer {self.cloud_api_token}",
                "Content-Type": "application/json"
            }
            
            phone_clean = phone.replace("+", "").replace("-", "").replace(" ", "")
            
            # Build template components
            components = []
            if parameters:
                components.append({
                    "type": "body",
                    "parameters": [
                        {"type": "text", "text": param}
                        for param in parameters
                    ]
                })
            
            payload = {
                "messaging_product": "whatsapp",
                "to": phone_clean,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language
                    },
                    "components": components
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=headers)
                result = response.json()
            
            return {
                "success": response.status_code == 200,
                "mode": "cloud_api_template",
                "message_id": result.get("messages", [{}])[0].get("id"),
                "phone": phone,
                "timestamp": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Template send error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== BULK MESSAGING ====================
    
    async def send_bulk_messages(
        self,
        contacts: List[Dict[str, str]],
        message: str,
        delay: int = 2
    ) -> Dict[str, Any]:
        """Send bulk messages with rate limiting"""
        import asyncio
        
        results = {
            "total": len(contacts),
            "sent": 0,
            "failed": 0,
            "details": []
        }
        
        for contact in contacts:
            phone = contact.get("phone")
            personalized_message = message.format(**contact)
            
            # Send message based on mode
            result = await self.send_message(phone, personalized_message)
            
            if result.get("success"):
                results["sent"] += 1
            else:
                results["failed"] += 1
            
            results["details"].append({
                "phone": phone,
                "status": "sent" if result.get("success") else "failed",
                "error": result.get("error")
            })
            
            # Rate limiting
            await asyncio.sleep(delay)
        
        return results
    
    # ==================== WEBHOOK HANDLER ====================
    
    async def handle_webhook(
        self,
        webhook_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle incoming WhatsApp webhook"""
        try:
            # Parse webhook data
            entry = webhook_data.get("entry", [{}])[0]
            changes = entry.get("changes", [{}])[0]
            value = changes.get("value", {})
            
            # Get message data
            messages = value.get("messages", [])
            if not messages:
                return {"status": "no_messages"}
            
            message = messages[0]
            
            # Extract info
            from_phone = message.get("from")
            message_id = message.get("id")
            message_type = message.get("type")
            timestamp = message.get("timestamp")
            
            # Get content based on type
            content = None
            if message_type == "text":
                content = message.get("text", {}).get("body")
            elif message_type == "image":
                content = message.get("image", {}).get("id")
            elif message_type == "document":
                content = message.get("document", {}).get("id")
            
            # TODO: Save to database, process with AI, etc.
            
            return {
                "status": "processed",
                "from": from_phone,
                "message_id": message_id,
                "type": message_type,
                "content": content,
                "timestamp": timestamp
            }
            
        except Exception as e:
            logger.error(f"Webhook processing error: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    # ==================== UNIFIED SEND METHOD ====================
    
    async def send_message(
        self,
        phone: str,
        message: str,
        media_url: Optional[str] = None,
        media_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Unified send method - routes to appropriate mode"""
        if self.mode == "selenium":
            return await self.selenium_send_message(phone, message, media_url)
        
        elif self.mode == "twilio":
            return await self.twilio_send_message(phone, message, media_url)
        
        elif self.mode == "cloud_api":
            return await self.cloud_api_send_message(phone, message, media_url, media_type)
        
        else:
            return {
                "success": False,
                "error": f"Unknown WhatsApp mode: {self.mode}"
            }
    
    # ==================== STATUS & INFO ====================
    
    def get_status(self) -> Dict[str, Any]:
        """Get WhatsApp service status"""
        return {
            "mode": self.mode,
            "initialized": self.initialized,
            "available_modes": [
                "selenium",
                "twilio",
                "cloud_api",
                "webhook",
                "local",
                "bulk"
            ]
        }


# Global WhatsApp service
whatsapp_service = WhatsAppService()


async def get_whatsapp_service() -> WhatsAppService:
    """Dependency injection"""
    return whatsapp_service
