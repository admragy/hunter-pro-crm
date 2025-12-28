"""
Facebook Ads API Routes
Complete Facebook marketing integration
"""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

from app.services.facebook_ads_service import FacebookAdsService, get_facebook_ads_service

router = APIRouter(prefix="/api/facebook-ads", tags=["facebook_ads"])


# ==================== SCHEMAS ====================

class CreateCampaign(BaseModel):
    name: str
    objective: str
    status: str = "PAUSED"
    special_ad_categories: Optional[List[str]] = None


class CampaignInsights(BaseModel):
    campaign_id: str
    date_preset: str = "last_7d"


# ==================== ENDPOINTS ====================

@router.post("/campaigns")
async def create_campaign(
    data: CreateCampaign,
    facebook: FacebookAdsService = Depends(get_facebook_ads_service)
):
    """
    Create Facebook Ad Campaign
    """
    return await facebook.create_campaign(
        name=data.name,
        objective=data.objective,
        status=data.status,
        special_ad_categories=data.special_ad_categories
    )


@router.get("/campaigns/{campaign_id}/insights")
async def get_campaign_insights(
    campaign_id: str,
    date_preset: str = "last_7d",
    facebook: FacebookAdsService = Depends(get_facebook_ads_service)
):
    """
    Get campaign performance insights
    """
    return await facebook.get_campaign_insights(campaign_id, date_preset)


@router.get("/strategies")
async def list_strategies(
    facebook: FacebookAdsService = Depends(get_facebook_ads_service)
):
    """
    List all 10 Unicorn Strategies
    """
    return facebook.get_available_strategies()


@router.get("/account/insights")
async def get_account_insights(
    date_preset: str = "last_30d",
    facebook: FacebookAdsService = Depends(get_facebook_ads_service)
):
    """
    Get account-level insights
    """
    return await facebook.get_account_insights(date_preset)
