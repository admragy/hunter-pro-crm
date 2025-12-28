"""
Deal API Routes
RESTful endpoints for deal/pipeline management
"""

from typing import List, Optional
from datetime import datetime, date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.services.crm_service import CRMService, get_crm_service

router = APIRouter(prefix="/api/deals", tags=["deals"])


# ==================== SCHEMAS ====================

class DealCreate(BaseModel):
    title: str
    customer_id: int
    value: float
    currency: str = "USD"
    stage: str = "lead"
    probability: float = 0.1
    expected_close_date: Optional[date] = None
    description: Optional[str] = None
    tags: List[str] = []
    metadata: dict = {}


class DealUpdate(BaseModel):
    title: Optional[str] = None
    value: Optional[float] = None
    currency: Optional[str] = None
    stage: Optional[str] = None
    probability: Optional[float] = None
    expected_close_date: Optional[date] = None
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class DealResponse(BaseModel):
    id: int
    title: str
    customer_id: int
    value: float
    currency: str
    stage: str
    status: str
    probability: float
    expected_close_date: Optional[str]
    description: Optional[str]
    tags: List[str]
    created_at: str
    updated_at: str
    closed_at: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.post("/", response_model=DealResponse, status_code=201)
async def create_deal(
    deal: DealCreate,
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """
    Create a new deal
    
    - **title**: Deal title (required)
    - **customer_id**: Associated customer ID (required)
    - **value**: Deal value (required)
    - **currency**: Currency code (default: USD)
    - **stage**: lead, qualified, proposal, negotiation, closed
    - **probability**: Close probability 0.0-1.0
    - **expected_close_date**: Expected closing date
    """
    try:
        new_deal = await crm.create_deal(
            db=db,
            title=deal.title,
            customer_id=deal.customer_id,
            value=deal.value,
            currency=deal.currency,
            stage=deal.stage,
            probability=deal.probability,
            expected_close_date=deal.expected_close_date,
            description=deal.description,
            tags=deal.tags,
            metadata=deal.metadata
        )
        
        return DealResponse(
            id=new_deal.id,
            title=new_deal.title,
            customer_id=new_deal.customer_id,
            value=new_deal.value,
            currency=new_deal.currency,
            stage=new_deal.stage,
            status=new_deal.status,
            probability=new_deal.probability,
            expected_close_date=new_deal.expected_close_date.isoformat() if new_deal.expected_close_date else None,
            description=new_deal.description,
            tags=new_deal.tags,
            created_at=new_deal.created_at.isoformat(),
            updated_at=new_deal.updated_at.isoformat(),
            closed_at=new_deal.closed_at.isoformat() if new_deal.closed_at else None
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating deal: {str(e)}")


@router.patch("/{deal_id}/stage")
async def update_deal_stage(
    deal_id: int,
    stage: str = Query(..., description="New stage"),
    probability: Optional[float] = Query(None, ge=0, le=1),
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """
    Update deal stage
    
    **Stages:**
    - lead: Initial contact
    - qualified: Qualified prospect
    - proposal: Proposal sent
    - negotiation: In negotiation
    - won: Deal won
    - lost: Deal lost
    """
    deal = await crm.update_deal_stage(db, deal_id, stage, probability)
    if not deal:
        raise HTTPException(status_code=404, detail="Deal not found")
    
    return DealResponse(
        id=deal.id,
        title=deal.title,
        customer_id=deal.customer_id,
        value=deal.value,
        currency=deal.currency,
        stage=deal.stage,
        status=deal.status,
        probability=deal.probability,
        expected_close_date=deal.expected_close_date.isoformat() if deal.expected_close_date else None,
        description=deal.description,
        tags=deal.tags,
        created_at=deal.created_at.isoformat(),
        updated_at=deal.updated_at.isoformat(),
        closed_at=deal.closed_at.isoformat() if deal.closed_at else None
    )


@router.get("/pipeline/stats")
async def get_pipeline_stats(
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """
    Get pipeline statistics
    
    Returns:
    - Deals by stage
    - Total value by stage
    - Win rate
    - Average probability
    """
    stats = await crm.get_pipeline_stats(db)
    return stats


@router.get("/{deal_id}/insights")
async def get_deal_insights(
    deal_id: int,
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """
    Get AI-powered deal insights
    
    Returns:
    - Risk factors
    - Opportunities
    - Next best action
    - Close likelihood
    """
    insights = await crm.get_deal_insights(db, deal_id)
    return insights
