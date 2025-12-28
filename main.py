"""
Hunter Pro CRM Ultimate Enterprise Edition v7.0.0
Main Application Entry Point

Advanced CRM System with:
- Multi-Provider AI Integration
- Real-time Analytics
- WhatsApp Integration
- Facebook Ads Management
- Enterprise Security
"""

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from app.core.config import settings
from app.core.database import engine, create_tables
from app.core.security import get_current_user
from app.api.routes import api_router
from app.services.websocket_service import manager, handle_chat_message, handle_typing_indicator
from fastapi import WebSocket, WebSocketDisconnect
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('logs/app.log')
    ]
)
logger = logging.getLogger(__name__)

# Create logs directory
Path("logs").mkdir(exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("🚀 Starting Hunter Pro CRM Ultimate Enterprise...")
    logger.info(f"📍 Environment: {settings.ENVIRONMENT}")
    logger.info(f"🔧 Debug Mode: {settings.DEBUG}")
    
    try:
        # Create database tables
        await create_tables()
        logger.info("✅ Database tables created/verified")
    except Exception as e:
        logger.error(f"❌ Database initialization error: {str(e)}")
    
    # Initialize AI services
    try:
        from app.services.ai_service import ai_service
        providers = ai_service.get_available_providers()
        logger.info(f"✅ AI Service initialized with {len(providers)} providers: {', '.join(providers)}")
    except Exception as e:
        logger.warning(f"⚠️ AI Service initialization warning: {str(e)}")
    
    logger.info("=" * 80)
    logger.info("🎉 Hunter Pro CRM is ready!")
    logger.info(f"📖 API Docs: http://{settings.HOST}:{settings.PORT}/docs")
    logger.info(f"🌐 Dashboard: http://{settings.HOST}:{settings.PORT}/")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down Hunter Pro CRM...")
    await engine.dispose()
    logger.info("✅ Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title="Hunter Pro CRM Ultimate Enterprise Edition",
    description="""
    🚀 **Advanced CRM System with AI Integration**
    
    ## Features
    
    * 🤖 **Multi-Provider AI**: OpenAI, Claude, Gemini, Groq, Ollama
    * 👥 **Customer Management**: Advanced CRM with AI insights
    * 💼 **Deal Pipeline**: Sales pipeline with intelligent scoring
    * 📱 **WhatsApp Integration**: 6 modes of operation
    * 📢 **Facebook Ads**: 10 Unicorn strategies
    * 📊 **Real-time Analytics**: Advanced reporting and insights
    * 🔒 **Enterprise Security**: JWT, 2FA, AES-256, RBAC
    * 🌍 **Multi-language**: Arabic RTL + 5 languages
    * 📱 **PWA Support**: Progressive Web App
    
    ## Quick Start
    
    1. **Authentication**: `/api/auth/login`
    2. **Create Customer**: `POST /api/customers`
    3. **Create Deal**: `POST /api/deals`
    4. **AI Generation**: `POST /api/ai/generate`
    
    ## Support
    
    * 📧 Email: support@hunterpro.com
    * 📚 Docs: https://docs.hunterpro.com
    * 💬 Discord: https://discord.gg/hunterpro
    """,
    version="7.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GZip Compression
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(api_router)


# ==================== WEBSOCKET ENDPOINTS ====================

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    """
    WebSocket endpoint for real-time chat and notifications
    """
    await manager.connect(websocket, user_id)
    
    try:
        while True:
            # Receive message
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            
            if message_type == "chat":
                await handle_chat_message(websocket, user_id, message_data)
            
            elif message_type == "typing":
                await handle_typing_indicator(user_id, message_data)
            
            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Unknown message type"
                })
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        manager.disconnect(websocket, user_id)


@app.get("/ws/status")
async def websocket_status():
    """
    Get WebSocket service status
    """
    return {
        "active_users": manager.get_active_users(),
        "status": "running"
    }


# ==================== ROOT ENDPOINTS ====================

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """
    Dashboard Homepage
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    try:
        # Test database connection
        from app.core.database import get_db
        async for db in get_db():
            await db.execute("SELECT 1")
            break
        
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check AI service
    try:
        from app.services.ai_service import ai_service
        ai_providers = ai_service.get_available_providers()
        ai_status = f"healthy ({len(ai_providers)} providers)"
    except Exception as e:
        ai_status = f"degraded: {str(e)}"
    
    return {
        "status": "running",
        "version": "7.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "api": "healthy",
            "database": db_status,
            "ai": ai_status
        }
    }


@app.get("/api")
async def api_info():
    """
    API Information
    """
    return {
        "name": "Hunter Pro CRM Ultimate Enterprise Edition API",
        "version": "7.0.0",
        "status": "running",
        "environment": settings.ENVIRONMENT,
        "endpoints": {
            "docs": "/docs",
            "redoc": "/redoc",
            "health": "/health",
            "customers": "/api/customers",
            "deals": "/api/deals",
            "ai": "/api/ai"
        },
        "features": [
            "Multi-Provider AI Integration",
            "Advanced CRM Operations",
            "Real-time Analytics",
            "WhatsApp Integration",
            "Facebook Ads Management",
            "Enterprise Security",
            "Multi-language Support"
        ]
    }


@app.get("/api/stats")
async def get_stats():
    """
    Dashboard statistics
    """
    try:
        from app.core.database import get_db
        from sqlalchemy import select, func
        from app.models import Customer, Deal
        
        async for db in get_db():
            # Total customers
            customer_result = await db.execute(select(func.count(Customer.id)))
            total_customers = customer_result.scalar() or 0
            
            # Active deals
            deal_result = await db.execute(
                select(func.count(Deal.id)).where(Deal.status == "active")
            )
            active_deals = deal_result.scalar() or 0
            
            # Total revenue
            revenue_result = await db.execute(
                select(func.sum(Deal.value)).where(Deal.status == "won")
            )
            total_revenue = revenue_result.scalar() or 0
            
            # Win rate
            total_closed = await db.execute(
                select(func.count(Deal.id)).where(Deal.status.in_(["won", "lost"]))
            )
            total_won = await db.execute(
                select(func.count(Deal.id)).where(Deal.status == "won")
            )
            
            closed_count = total_closed.scalar() or 0
            won_count = total_won.scalar() or 0
            win_rate = (won_count / closed_count * 100) if closed_count > 0 else 0
            
            return {
                "total_customers": total_customers,
                "active_deals": active_deals,
                "total_revenue": float(total_revenue),
                "win_rate": round(win_rate, 2)
            }
            
    except Exception as e:
        logger.error(f"Error fetching stats: {str(e)}")
        return {
            "total_customers": 0,
            "active_deals": 0,
            "total_revenue": 0.0,
            "win_rate": 0.0
        }


@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": f"The requested resource '{request.url.path}' was not found",
            "suggestion": "Check /docs for available endpoints"
        }
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Custom 500 handler"""
    logger.error(f"Internal server error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred. Please try again later.",
            "support": "support@hunterpro.com"
        }
    )


# ==================== MAIN ====================

if __name__ == "__main__":
    import uvicorn
    
    # Development server
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info",
        access_log=True
    )
