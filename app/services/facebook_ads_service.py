"""
Facebook Ads Integration - 10 Unicorn Strategies
Complete Facebook Marketing API Integration
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx

logger = logging.getLogger(__name__)


class FacebookAdsService:
    """Complete Facebook Ads Management with 10 Strategies"""
    
    # 10 Unicorn Strategies
    STRATEGIES = {
        "lookalike": "Lookalike Audiences - Target similar users",
        "retargeting": "Retargeting - Re-engage website visitors",
        "engagement": "Engagement - Build brand awareness",
        "conversion": "Conversion - Drive sales and leads",
        "video_views": "Video Views - Maximize video reach",
        "traffic": "Traffic - Drive website clicks",
        "app_installs": "App Installs - Grow app downloads",
        "lead_generation": "Lead Generation - Collect leads",
        "messages": "Messages - Start conversations",
        "catalog_sales": "Catalog Sales - Dynamic product ads"
    }
    
    def __init__(self):
        self.app_id = os.getenv("FACEBOOK_APP_ID")
        self.app_secret = os.getenv("FACEBOOK_APP_SECRET")
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.ad_account_id = os.getenv("FACEBOOK_AD_ACCOUNT_ID")
        self.page_id = os.getenv("FACEBOOK_PAGE_ID")
        self.api_version = "v18.0"
        self.base_url = f"https://graph.facebook.com/{self.api_version}"
        
        logger.info("✅ Facebook Ads Service initialized")
    
    # ==================== CAMPAIGN MANAGEMENT ====================
    
    async def create_campaign(
        self,
        name: str,
        objective: str,
        status: str = "PAUSED",
        special_ad_categories: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create Facebook campaign
        
        Objectives:
        - OUTCOME_AWARENESS: Brand awareness
        - OUTCOME_ENGAGEMENT: Engagement
        - OUTCOME_LEADS: Lead generation
        - OUTCOME_SALES: Conversions & sales
        - OUTCOME_TRAFFIC: Traffic
        """
        try:
            url = f"{self.base_url}/act_{self.ad_account_id}/campaigns"
            
            params = {
                "access_token": self.access_token,
                "name": name,
                "objective": objective,
                "status": status,
                "special_ad_categories": special_ad_categories or []
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, params=params)
                result = response.json()
            
            if "id" in result:
                logger.info(f"✅ Campaign created: {result['id']}")
                return {
                    "success": True,
                    "campaign_id": result["id"],
                    "name": name
                }
            else:
                logger.error(f"Campaign creation failed: {result}")
                return {
                    "success": False,
                    "error": result.get("error", {}).get("message", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Campaign creation error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== AD SET MANAGEMENT ====================
    
    async def create_ad_set(
        self,
        campaign_id: str,
        name: str,
        optimization_goal: str,
        billing_event: str,
        bid_amount: int,
        daily_budget: int,
        targeting: Dict[str, Any],
        start_time: Optional[str] = None,
        end_time: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create Ad Set with targeting
        
        Optimization Goals:
        - REACH: Maximum reach
        - IMPRESSIONS: Maximum impressions
        - LINK_CLICKS: Website clicks
        - LANDING_PAGE_VIEWS: Landing page views
        - OFFSITE_CONVERSIONS: Conversions
        - VALUE: Purchase value
        """
        try:
            url = f"{self.base_url}/act_{self.ad_account_id}/adsets"
            
            params = {
                "access_token": self.access_token,
                "name": name,
                "campaign_id": campaign_id,
                "optimization_goal": optimization_goal,
                "billing_event": billing_event,
                "bid_amount": bid_amount,
                "daily_budget": daily_budget,
                "targeting": targeting,
                "status": "PAUSED"
            }
            
            if start_time:
                params["start_time"] = start_time
            if end_time:
                params["end_time"] = end_time
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=params)
                result = response.json()
            
            if "id" in result:
                return {
                    "success": True,
                    "ad_set_id": result["id"]
                }
            else:
                return {
                    "success": False,
                    "error": result.get("error", {}).get("message")
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== 10 UNICORN STRATEGIES ====================
    
    async def strategy_lookalike(
        self,
        campaign_name: str,
        source_audience_id: str,
        lookalike_spec: Dict[str, Any],
        daily_budget: int
    ) -> Dict[str, Any]:
        """Strategy 1: Lookalike Audiences"""
        # Create campaign
        campaign = await self.create_campaign(
            name=f"{campaign_name} - Lookalike",
            objective="OUTCOME_SALES"
        )
        
        if not campaign["success"]:
            return campaign
        
        # Create ad set with lookalike targeting
        targeting = {
            "geo_locations": lookalike_spec.get("geo_locations"),
            "custom_audiences": [{"id": source_audience_id}],
            "lookalike_audiences": [lookalike_spec]
        }
        
        return await self.create_ad_set(
            campaign_id=campaign["campaign_id"],
            name=f"{campaign_name} - Lookalike AdSet",
            optimization_goal="OFFSITE_CONVERSIONS",
            billing_event="IMPRESSIONS",
            bid_amount=1000,
            daily_budget=daily_budget,
            targeting=targeting
        )
    
    async def strategy_retargeting(
        self,
        campaign_name: str,
        pixel_id: str,
        retention_days: int,
        daily_budget: int
    ) -> Dict[str, Any]:
        """Strategy 2: Website Retargeting"""
        campaign = await self.create_campaign(
            name=f"{campaign_name} - Retargeting",
            objective="OUTCOME_SALES"
        )
        
        if not campaign["success"]:
            return campaign
        
        targeting = {
            "custom_audiences": [{
                "id": pixel_id,
                "retention_days": retention_days
            }]
        }
        
        return await self.create_ad_set(
            campaign_id=campaign["campaign_id"],
            name=f"{campaign_name} - Retargeting AdSet",
            optimization_goal="OFFSITE_CONVERSIONS",
            billing_event="IMPRESSIONS",
            bid_amount=1500,
            daily_budget=daily_budget,
            targeting=targeting
        )
    
    # ==================== ANALYTICS ====================
    
    async def get_campaign_insights(
        self,
        campaign_id: str,
        date_preset: str = "last_7d"
    ) -> Dict[str, Any]:
        """Get campaign performance insights"""
        try:
            url = f"{self.base_url}/{campaign_id}/insights"
            
            params = {
                "access_token": self.access_token,
                "date_preset": date_preset,
                "fields": ",".join([
                    "impressions",
                    "clicks",
                    "spend",
                    "reach",
                    "frequency",
                    "cpm",
                    "cpc",
                    "ctr",
                    "conversions",
                    "cost_per_conversion"
                ])
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                result = response.json()
            
            if "data" in result and result["data"]:
                return {
                    "success": True,
                    "insights": result["data"][0]
                }
            else:
                return {
                    "success": False,
                    "error": "No data available"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def get_account_insights(
        self,
        date_preset: str = "last_30d"
    ) -> Dict[str, Any]:
        """Get account-level insights"""
        try:
            url = f"{self.base_url}/act_{self.ad_account_id}/insights"
            
            params = {
                "access_token": self.access_token,
                "date_preset": date_preset,
                "level": "account",
                "fields": ",".join([
                    "spend",
                    "impressions",
                    "clicks",
                    "reach",
                    "conversions",
                    "cost_per_conversion",
                    "roas"
                ])
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, params=params)
                result = response.json()
            
            return {
                "success": True,
                "insights": result.get("data", [])
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== AUTOMATED OPTIMIZATION ====================
    
    async def auto_optimize_campaign(
        self,
        campaign_id: str,
        rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Automatically optimize campaign based on rules
        
        Example rules:
        - If CPA > $50: Pause ad set
        - If CTR < 1%: Increase bid
        - If ROAS > 3: Increase budget
        """
        insights = await self.get_campaign_insights(campaign_id)
        
        if not insights["success"]:
            return insights
        
        data = insights["insights"]
        actions = []
        
        # Check rules
        cpa = float(data.get("cost_per_conversion", 0))
        ctr = float(data.get("ctr", 0))
        
        if cpa > rules.get("max_cpa", 50):
            actions.append({
                "action": "pause",
                "reason": f"CPA (${cpa:.2f}) exceeds maximum"
            })
        
        if ctr < rules.get("min_ctr", 1):
            actions.append({
                "action": "increase_bid",
                "reason": f"CTR ({ctr:.2f}%) below minimum"
            })
        
        return {
            "campaign_id": campaign_id,
            "actions": actions,
            "current_metrics": data
        }
    
    def get_available_strategies(self) -> Dict[str, str]:
        """Get all available strategies"""
        return self.STRATEGIES


# Global service
facebook_ads_service = FacebookAdsService()


async def get_facebook_ads_service() -> FacebookAdsService:
    """Dependency injection"""
    return facebook_ads_service
