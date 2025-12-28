"""
Customer API Routes
RESTful endpoints for customer management
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.services.crm_service import CRMService, get_crm_service
from app.services.ai_service import get_ai_service

router = APIRouter(prefix="/api/customers", tags=["customers"])


# ==================== SCHEMAS ====================

class CustomerCreate(BaseModel):
    name: str
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: str = "lead"
    source: str = "manual"
    tags: List[str] = []
    metadata: dict = {}


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    company: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[dict] = None


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: Optional[str]
    phone: Optional[str]
    company: Optional[str]
    status: str
    source: str
    tags: List[str]
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


# ==================== ENDPOINTS ====================

@router.post("/", response_model=CustomerResponse, status_code=201)
async def create_customer(
    customer: CustomerCreate,
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """
    Create a new customer
    
    - **name**: Customer name (required)
    - **email**: Email address
    - **phone**: Phone number
    - **company**: Company name
    - **status**: lead, prospect, customer, inactive
    - **source**: manual, website, referral, campaign
    - **tags**: List of tags
    """
    try:
        new_customer = await crm.create_customer(
            db=db,
            name=customer.name,
            email=customer.email,
            phone=customer.phone,
            company=customer.company,
            status=customer.status,
            source=customer.source,
            tags=customer.tags,
            metadata=customer.metadata
        )
        
        return CustomerResponse(
            id=new_customer.id,
            name=new_customer.name,
            email=new_customer.email,
            phone=new_customer.phone,
            company=new_customer.company,
            status=new_customer.status,
            source=new_customer.source,
            tags=new_customer.tags,
            created_at=new_customer.created_at.isoformat(),
            updated_at=new_customer.updated_at.isoformat()
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating customer: {str(e)}")


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    query: Optional[str] = Query(None, description="Search query"),
    status: Optional[str] = Query(None, description="Filter by status"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """
    List customers with optional filters
    
    - **query**: Search in name, email, phone, company
    - **status**: Filter by customer status
    - **tags**: Filter by tags
    - **limit**: Maximum results (1-100)
    - **offset**: Pagination offset
    """
    try:
        customers = await crm.search_customers(
            db=db,
            query=query,
            status=status,
            tags=tags,
            limit=limit,
            offset=offset
        )
        
        return [
            CustomerResponse(
                id=c.id,
                name=c.name,
                email=c.email,
                phone=c.phone,
                company=c.company,
                status=c.status,
                source=c.source,
                tags=c.tags,
                created_at=c.created_at.isoformat(),
                updated_at=c.updated_at.isoformat()
            )
            for c in customers
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing customers: {str(e)}")


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """Get customer by ID"""
    customer = await crm.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        company=customer.company,
        status=customer.status,
        source=customer.source,
        tags=customer.tags,
        created_at=customer.created_at.isoformat(),
        updated_at=customer.updated_at.isoformat()
    )


@router.patch("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    updates: CustomerUpdate,
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """Update customer information"""
    update_data = {k: v for k, v in updates.dict(exclude_unset=True).items()}
    
    customer = await crm.update_customer(db, customer_id, **update_data)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return CustomerResponse(
        id=customer.id,
        name=customer.name,
        email=customer.email,
        phone=customer.phone,
        company=customer.company,
        status=customer.status,
        source=customer.source,
        tags=customer.tags,
        created_at=customer.created_at.isoformat(),
        updated_at=customer.updated_at.isoformat()
    )


@router.delete("/{customer_id}", status_code=204)
async def delete_customer(
    customer_id: int,
    hard_delete: bool = Query(False, description="Permanent delete"),
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """Delete customer (soft delete by default)"""
    success = await crm.delete_customer(db, customer_id, soft_delete=not hard_delete)
    if not success:
        raise HTTPException(status_code=404, detail="Customer not found")


@router.get("/{customer_id}/sentiment")
async def get_customer_sentiment(
    customer_id: int,
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """
    Analyze customer sentiment from recent messages
    
    - **days**: Number of days to analyze (1-90)
    """
    sentiment = await crm.analyze_customer_sentiment(db, customer_id, days)
    return sentiment


@router.get("/{customer_id}/insights")
async def get_customer_insights(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """Get AI-powered customer insights and recommendations"""
    insights = {
        "customer_id": customer_id,
        "sentiment": await crm.analyze_customer_sentiment(db, customer_id, 30),
        "lifetime_value": await crm.get_customer_lifetime_value(db, customer_id),
        "engagement_score": await crm.get_engagement_score(db, customer_id, 30),
        "next_actions": await crm.suggest_next_actions(db, customer_id)
    }
    return insights


@router.get("/{customer_id}/lifetime-value")
async def get_lifetime_value(
    customer_id: int,
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """Calculate customer lifetime value"""
    clv = await crm.get_customer_lifetime_value(db, customer_id)
    return {
        "customer_id": customer_id,
        "lifetime_value": clv,
        "currency": "USD"
    }


@router.get("/{customer_id}/engagement")
async def get_engagement_score(
    customer_id: int,
    days: int = Query(30, ge=1, le=90),
    db: AsyncSession = Depends(get_db),
    crm: CRMService = Depends(get_crm_service)
):
    """
    Calculate customer engagement score (0-100)
    
    - **days**: Period to analyze (1-90)
    """
    score = await crm.get_engagement_score(db, customer_id, days)
    return {
        "customer_id": customer_id,
        "engagement_score": score,
        "period_days": days,
        "level": "high" if score >= 70 else "medium" if score >= 40 else "low"
    }
