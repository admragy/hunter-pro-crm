"""
Email Service - SMTP Integration & Templates
Complete email functionality with templates
"""

import os
import logging
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import aiosmtplib

logger = logging.getLogger(__name__)


class EmailService:
    """Complete Email Service"""
    
    def __init__(self):
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER")
        self.smtp_password = os.getenv("SMTP_PASSWORD")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "Hunter Pro CRM")
        
        logger.info("✅ Email Service initialized")
    
    async def send_email(
        self,
        to_email: str | List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        cc: Optional[List[str]] = None,
        bcc: Optional[List[str]] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Send email with optional HTML and attachments"""
        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email if isinstance(to_email, str) else ", ".join(to_email)
            message["Subject"] = subject
            
            if cc:
                message["Cc"] = ", ".join(cc)
            if bcc:
                message["Bcc"] = ", ".join(bcc)
            
            # Add body
            message.attach(MIMEText(body, "plain"))
            if html_body:
                message.attach(MIMEText(html_body, "html"))
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment["content"])
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment['filename']}"
                    )
                    message.attach(part)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )
            
            logger.info(f"✅ Email sent to {to_email}")
            return {
                "success": True,
                "to": to_email,
                "subject": subject
            }
            
        except Exception as e:
            logger.error(f"Email send error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def send_welcome_email(self, to_email: str, name: str) -> Dict[str, Any]:
        """Send welcome email"""
        subject = f"Welcome to Hunter Pro CRM, {name}!"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h1 style="color: #6366f1;">Welcome {name}!</h1>
            <p>Thank you for joining Hunter Pro CRM.</p>
            <p>Get started with our powerful features:</p>
            <ul>
                <li>AI-powered customer insights</li>
                <li>Advanced sales pipeline</li>
                <li>Real-time analytics</li>
            </ul>
            <a href="http://localhost:5000" style="background-color: #6366f1; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Get Started</a>
        </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            body=f"Welcome {name}!",
            html_body=html_body
        )


# Webhook Service
class WebhookService:
    """Webhook Management"""
    
    def __init__(self):
        self.webhooks: Dict[str, List[str]] = {}
        logger.info("✅ Webhook Service initialized")
    
    async def register_webhook(
        self,
        event_type: str,
        url: str,
        secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """Register webhook for event"""
        if event_type not in self.webhooks:
            self.webhooks[event_type] = []
        
        self.webhooks[event_type].append(url)
        
        return {
            "success": True,
            "event_type": event_type,
            "url": url
        }
    
    async def trigger_webhook(
        self,
        event_type: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Trigger webhook"""
        import httpx
        
        if event_type not in self.webhooks:
            return {"success": False, "error": "No webhooks registered"}
        
        results = []
        for url in self.webhooks[event_type]:
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.post(url, json=data, timeout=10.0)
                    results.append({
                        "url": url,
                        "status": response.status_code,
                        "success": response.status_code < 400
                    })
            except Exception as e:
                results.append({
                    "url": url,
                    "success": False,
                    "error": str(e)
                })
        
        return {
            "event_type": event_type,
            "triggered": len(results),
            "results": results
        }


# Global services
email_service = EmailService()
webhook_service = WebhookService()
