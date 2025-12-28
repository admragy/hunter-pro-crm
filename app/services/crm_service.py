"""
CRM Service - Customer Relationship Management
Advanced CRM operations with AI-powered insights
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload

from app.models import Customer, Deal, Campaign, Message
from app.services.ai_service import AIService

logger = logging.getLogger(__name__)


class CRMService:
    """Advanced CRM Service with AI Integration"""
    
    def __init__(self, ai_service: AIService):
        self.ai_service = ai_service
    
    # ==================== CUSTOMER OPERATIONS ====================
    
    async def create_customer(
        self,
        db: AsyncSession,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        company: Optional[str] = None,
        **kwargs
    ) -> Customer:
        """Create a new customer"""
        try:
            customer = Customer(
                name=name,
                email=email,
                phone=phone,
                company=company,
                status=kwargs.get("status", "lead"),
                source=kwargs.get("source", "manual"),
                tags=kwargs.get("tags", []),
                metadata=kwargs.get("metadata", {})
            )
            
            db.add(customer)
            await db.commit()
            await db.refresh(customer)
            
            logger.info(f"✅ Customer created: {customer.name} (ID: {customer.id})")
            return customer
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error creating customer: {str(e)}")
            raise
    
    async def get_customer(
        self,
        db: AsyncSession,
        customer_id: int,
        include_messages: bool = False,
        include_deals: bool = False
    ) -> Optional[Customer]:
        """Get customer by ID with optional relationships"""
        try:
            query = select(Customer).where(Customer.id == customer_id)
            
            if include_messages:
                query = query.options(selectinload(Customer.messages))
            if include_deals:
                query = query.options(selectinload(Customer.deals))
            
            result = await db.execute(query)
            return result.scalar_one_or_none()
            
        except Exception as e:
            logger.error(f"❌ Error fetching customer: {str(e)}")
            return None
    
    async def search_customers(
        self,
        db: AsyncSession,
        query: Optional[str] = None,
        status: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Customer]:
        """Search customers with filters"""
        try:
            stmt = select(Customer)
            
            # Apply filters
            conditions = []
            if query:
                conditions.append(
                    or_(
                        Customer.name.ilike(f"%{query}%"),
                        Customer.email.ilike(f"%{query}%"),
                        Customer.phone.ilike(f"%{query}%"),
                        Customer.company.ilike(f"%{query}%")
                    )
                )
            
            if status:
                conditions.append(Customer.status == status)
            
            if tags:
                for tag in tags:
                    conditions.append(Customer.tags.contains([tag]))
            
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            stmt = stmt.limit(limit).offset(offset)
            
            result = await db.execute(stmt)
            return list(result.scalars().all())
            
        except Exception as e:
            logger.error(f"❌ Error searching customers: {str(e)}")
            return []
    
    async def update_customer(
        self,
        db: AsyncSession,
        customer_id: int,
        **updates
    ) -> Optional[Customer]:
        """Update customer information"""
        try:
            customer = await self.get_customer(db, customer_id)
            if not customer:
                return None
            
            for key, value in updates.items():
                if hasattr(customer, key):
                    setattr(customer, key, value)
            
            customer.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(customer)
            
            logger.info(f"✅ Customer updated: {customer.name} (ID: {customer.id})")
            return customer
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error updating customer: {str(e)}")
            raise
    
    async def delete_customer(
        self,
        db: AsyncSession,
        customer_id: int,
        soft_delete: bool = True
    ) -> bool:
        """Delete customer (soft or hard delete)"""
        try:
            customer = await self.get_customer(db, customer_id)
            if not customer:
                return False
            
            if soft_delete:
                customer.status = "deleted"
                customer.updated_at = datetime.utcnow()
                await db.commit()
            else:
                await db.delete(customer)
                await db.commit()
            
            logger.info(f"✅ Customer deleted: {customer_id}")
            return True
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error deleting customer: {str(e)}")
            return False
    
    # ==================== DEAL OPERATIONS ====================
    
    async def create_deal(
        self,
        db: AsyncSession,
        title: str,
        customer_id: int,
        value: float,
        **kwargs
    ) -> Deal:
        """Create a new deal"""
        try:
            deal = Deal(
                title=title,
                customer_id=customer_id,
                value=value,
                currency=kwargs.get("currency", "USD"),
                stage=kwargs.get("stage", "lead"),
                probability=kwargs.get("probability", 0.1),
                expected_close_date=kwargs.get("expected_close_date"),
                description=kwargs.get("description"),
                tags=kwargs.get("tags", []),
                metadata=kwargs.get("metadata", {})
            )
            
            db.add(deal)
            await db.commit()
            await db.refresh(deal)
            
            logger.info(f"✅ Deal created: {deal.title} (ID: {deal.id})")
            return deal
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error creating deal: {str(e)}")
            raise
    
    async def update_deal_stage(
        self,
        db: AsyncSession,
        deal_id: int,
        new_stage: str,
        probability: Optional[float] = None
    ) -> Optional[Deal]:
        """Update deal stage and probability"""
        try:
            deal = await db.get(Deal, deal_id)
            if not deal:
                return None
            
            deal.stage = new_stage
            if probability is not None:
                deal.probability = probability
            
            # Auto-update based on stage
            if new_stage == "won":
                deal.status = "won"
                deal.probability = 1.0
                deal.closed_at = datetime.utcnow()
            elif new_stage == "lost":
                deal.status = "lost"
                deal.probability = 0.0
                deal.closed_at = datetime.utcnow()
            
            deal.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(deal)
            
            logger.info(f"✅ Deal stage updated: {deal.title} -> {new_stage}")
            return deal
            
        except Exception as e:
            await db.rollback()
            logger.error(f"❌ Error updating deal stage: {str(e)}")
            raise
    
    async def get_pipeline_stats(self, db: AsyncSession) -> Dict[str, Any]:
        """Get pipeline statistics"""
        try:
            # Total deals by stage
            stage_stats = await db.execute(
                select(
                    Deal.stage,
                    func.count(Deal.id).label("count"),
                    func.sum(Deal.value).label("total_value"),
                    func.avg(Deal.probability).label("avg_probability")
                )
                .where(Deal.status == "active")
                .group_by(Deal.stage)
            )
            
            stages = {}
            for row in stage_stats:
                stages[row.stage] = {
                    "count": row.count,
                    "total_value": float(row.total_value or 0),
                    "avg_probability": float(row.avg_probability or 0)
                }
            
            # Win rate
            total_closed = await db.execute(
                select(func.count(Deal.id))
                .where(Deal.status.in_(["won", "lost"]))
            )
            total_won = await db.execute(
                select(func.count(Deal.id))
                .where(Deal.status == "won")
            )
            
            closed_count = total_closed.scalar() or 0
            won_count = total_won.scalar() or 0
            win_rate = (won_count / closed_count * 100) if closed_count > 0 else 0
            
            return {
                "stages": stages,
                "win_rate": round(win_rate, 2),
                "total_closed": closed_count,
                "total_won": won_count
            }
            
        except Exception as e:
            logger.error(f"❌ Error fetching pipeline stats: {str(e)}")
            return {}
    
    # ==================== AI-POWERED INSIGHTS ====================
    
    async def analyze_customer_sentiment(
        self,
        db: AsyncSession,
        customer_id: int,
        recent_days: int = 30
    ) -> Dict[str, Any]:
        """Analyze customer sentiment from recent messages"""
        try:
            # Get recent messages
            cutoff_date = datetime.utcnow() - timedelta(days=recent_days)
            result = await db.execute(
                select(Message)
                .where(
                    and_(
                        Message.customer_id == customer_id,
                        Message.created_at >= cutoff_date,
                        Message.direction == "incoming"
                    )
                )
                .order_by(Message.created_at.desc())
                .limit(50)
            )
            messages = list(result.scalars().all())
            
            if not messages:
                return {
                    "sentiment": "neutral",
                    "confidence": 0.0,
                    "message_count": 0,
                    "analysis": "No recent messages"
                }
            
            # Combine messages for analysis
            combined_text = "\n".join([msg.content for msg in messages if msg.content])
            
            # Analyze with AI
            sentiment = await self.ai_service.analyze_sentiment(combined_text[:2000])
            sentiment["message_count"] = len(messages)
            sentiment["period_days"] = recent_days
            
            return sentiment
            
        except Exception as e:
            logger.error(f"❌ Error analyzing customer sentiment: {str(e)}")
            return {
                "sentiment": "error",
                "confidence": 0.0,
                "message_count": 0,
                "error": str(e)
            }
    
    async def get_deal_insights(
        self,
        db: AsyncSession,
        deal_id: int
    ) -> Dict[str, Any]:
        """Get AI-powered insights for a deal"""
        try:
            deal = await db.get(Deal, deal_id)
            if not deal:
                return {"error": "Deal not found"}
            
            # Get customer and messages
            customer = await db.get(Customer, deal.customer_id)
            result = await db.execute(
                select(Message)
                .where(Message.customer_id == deal.customer_id)
                .order_by(Message.created_at.desc())
                .limit(20)
            )
            messages = list(result.scalars().all())
            
            # Prepare context for AI
            context = {
                "deal": {
                    "title": deal.title,
                    "value": deal.value,
                    "stage": deal.stage,
                    "probability": deal.probability
                },
                "customer": {
                    "name": customer.name if customer else "Unknown",
                    "status": customer.status if customer else "Unknown"
                },
                "recent_interactions": len(messages)
            }
            
            prompt = f"""Analyze this sales deal and provide insights:

Deal Information:
- Title: {deal.title}
- Value: ${deal.value:,.2f}
- Stage: {deal.stage}
- Probability: {deal.probability * 100}%
- Customer: {customer.name if customer else 'Unknown'}
- Recent Interactions: {len(messages)}

Provide:
1. Risk factors (1-3 bullet points)
2. Opportunities (1-3 bullet points)
3. Next best action
4. Estimated close likelihood

Format as JSON:
{{
    "risk_factors": ["risk1", "risk2"],
    "opportunities": ["opp1", "opp2"],
    "next_action": "action description",
    "close_likelihood": "high/medium/low"
}}"""
            
            response = await self.ai_service.generate(prompt, temperature=0.5)
            
            # Parse JSON response
            import json
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            if json_start != -1 and json_end > json_start:
                insights = json.loads(response[json_start:json_end])
                insights["context"] = context
                return insights
            else:
                return {
                    "error": "Could not parse AI response",
                    "raw_response": response
                }
            
        except Exception as e:
            logger.error(f"❌ Error generating deal insights: {str(e)}")
            return {"error": str(e)}
    
    async def suggest_next_actions(
        self,
        db: AsyncSession,
        customer_id: int
    ) -> List[Dict[str, Any]]:
        """Suggest next best actions for a customer"""
        try:
            customer = await self.get_customer(db, customer_id, include_messages=True)
            if not customer:
                return []
            
            # Get recent activity
            recent_messages = customer.messages[-10:] if customer.messages else []
            
            prompt = f"""Based on this customer information, suggest 3 specific next actions:

Customer: {customer.name}
Status: {customer.status}
Company: {customer.company or 'N/A'}
Recent messages: {len(recent_messages)}
Last contact: {customer.last_contact_date or 'Never'}

Provide 3 actionable suggestions as JSON:
[
    {{
        "action": "Action title",
        "description": "Why this action",
        "priority": "high/medium/low",
        "estimated_time": "X minutes"
    }}
]"""
            
            response = await self.ai_service.generate(prompt, temperature=0.7)
            
            # Parse JSON
            import json
            json_start = response.find("[")
            json_end = response.rfind("]") + 1
            if json_start != -1 and json_end > json_start:
                return json.loads(response[json_start:json_end])
            else:
                return []
            
        except Exception as e:
            logger.error(f"❌ Error suggesting next actions: {str(e)}")
            return []
    
    # ==================== ANALYTICS ====================
    
    async def get_customer_lifetime_value(
        self,
        db: AsyncSession,
        customer_id: int
    ) -> float:
        """Calculate customer lifetime value"""
        try:
            result = await db.execute(
                select(func.sum(Deal.value))
                .where(
                    and_(
                        Deal.customer_id == customer_id,
                        Deal.status == "won"
                    )
                )
            )
            return float(result.scalar() or 0)
            
        except Exception as e:
            logger.error(f"❌ Error calculating CLV: {str(e)}")
            return 0.0
    
    async def get_engagement_score(
        self,
        db: AsyncSession,
        customer_id: int,
        days: int = 30
    ) -> float:
        """Calculate customer engagement score (0-100)"""
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=days)
            
            # Count interactions
            result = await db.execute(
                select(func.count(Message.id))
                .where(
                    and_(
                        Message.customer_id == customer_id,
                        Message.created_at >= cutoff_date
                    )
                )
            )
            message_count = result.scalar() or 0
            
            # Score based on interactions
            # 0 messages = 0, 1-5 = 20-60, 5-10 = 60-80, 10+ = 80-100
            if message_count == 0:
                score = 0
            elif message_count <= 5:
                score = 20 + (message_count * 8)
            elif message_count <= 10:
                score = 60 + ((message_count - 5) * 4)
            else:
                score = min(100, 80 + ((message_count - 10) * 2))
            
            return float(score)
            
        except Exception as e:
            logger.error(f"❌ Error calculating engagement score: {str(e)}")
            return 0.0


async def get_crm_service(ai_service: AIService) -> CRMService:
    """Dependency injection for CRM service"""
    return CRMService(ai_service)
