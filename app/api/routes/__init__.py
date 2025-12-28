"""
Complete API Routes - All Services Integration
"""

from fastapi import APIRouter

# Import all route modules
from app.api.routes import (
    customers,
    deals,
    ai,
    auth
)

# Import new service routes
try:
    from app.api.routes import whatsapp
except:
    whatsapp = None

try:
    from app.api.routes import facebook_ads
except:
    facebook_ads = None

try:
    from app.api.routes import reports
except:
    reports = None

try:
    from app.api.routes import webhooks
except:
    webhooks = None

try:
    from app.api.routes import email
except:
    email = None

# Create main API router
api_router = APIRouter()

# Include all route modules
api_router.include_router(auth.router)          # Authentication
api_router.include_router(customers.router)     # Customer Management
api_router.include_router(deals.router)         # Deal Management
api_router.include_router(ai.router)            # AI Services

# Include new services if available
if whatsapp:
    api_router.include_router(whatsapp.router)      # WhatsApp Integration
if facebook_ads:
    api_router.include_router(facebook_ads.router)  # Facebook Ads
if reports:
    api_router.include_router(reports.router)       # Report Generation
if webhooks:
    api_router.include_router(webhooks.router)      # Webhook Management
if email:
    api_router.include_router(email.router)         # Email Services

__all__ = ["api_router"]
