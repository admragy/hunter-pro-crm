"""
Hunter Pro CRM Ultimate Enterprise - Campaign Model
Version: 7.0.0
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class CampaignType(str, enum.Enum):
    """Campaign types"""
    EMAIL = "email"
    SMS = "sms"
    WHATSAPP = "whatsapp"
    SOCIAL_MEDIA = "social_media"
    MIXED = "mixed"


class CampaignStatus(str, enum.Enum):
    """Campaign status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Campaign(Base):
    """Marketing Campaign model"""
    
    __tablename__ = "campaigns"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Type & Status
    type = Column(Enum(CampaignType), default=CampaignType.EMAIL, index=True)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT, index=True)
    
    # Content
    subject = Column(String(500))
    message_template = Column(Text)  # Template with variables like {{name}}
    
    # Media
    media_url = Column(String(1000))
    
    # Targeting
    target_segment = Column(String(100))  # all, new_leads, customers, etc.
    target_tags = Column(Text)  # Comma-separated tags
    target_count = Column(Integer, default=0)  # Number of recipients
    
    # Budget & Cost
    budget = Column(Float, default=0.0)
    cost_per_message = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Schedule
    scheduled_at = Column(DateTime, nullable=True)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Statistics
    sent_count = Column(Integer, default=0)
    delivered_count = Column(Integer, default=0)
    opened_count = Column(Integer, default=0)
    clicked_count = Column(Integer, default=0)
    replied_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # Conversion Tracking
    conversions = Column(Integer, default=0)
    conversion_value = Column(Float, default=0.0)
    
    # ROI Calculation
    roi = Column(Float, default=0.0)  # (conversion_value - total_cost) / total_cost * 100
    
    # A/B Testing
    is_ab_test = Column(Boolean, default=False)
    ab_variant = Column(String(10))  # A, B, C, etc.
    parent_campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # AI Optimization
    ai_optimized = Column(Boolean, default=False)
    ai_recommendations = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft Delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    # owner = relationship("User")
    # messages = relationship("Message", back_populates="campaign")
    # parent_campaign = relationship("Campaign", remote_side=[id])
    
    def __repr__(self):
        return f"<Campaign {self.name}>"
    
    @property
    def delivery_rate(self) -> float:
        """Calculate delivery rate percentage"""
        if self.sent_count == 0:
            return 0.0
        return (self.delivered_count / self.sent_count) * 100
    
    @property
    def open_rate(self) -> float:
        """Calculate open rate percentage"""
        if self.delivered_count == 0:
            return 0.0
        return (self.opened_count / self.delivered_count) * 100
    
    @property
    def click_rate(self) -> float:
        """Calculate click rate percentage"""
        if self.opened_count == 0:
            return 0.0
        return (self.clicked_count / self.opened_count) * 100
    
    @property
    def conversion_rate(self) -> float:
        """Calculate conversion rate percentage"""
        if self.sent_count == 0:
            return 0.0
        return (self.conversions / self.sent_count) * 100
    
    @property
    def is_active(self) -> bool:
        """Check if campaign is currently active"""
        return self.status in [CampaignStatus.RUNNING, CampaignStatus.SCHEDULED]
    
    def calculate_roi(self):
        """Calculate ROI percentage"""
        if self.total_cost == 0:
            self.roi = 0.0
        else:
            self.roi = ((self.conversion_value - self.total_cost) / self.total_cost) * 100
    
    def to_dict(self) -> dict:
        """Convert campaign to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type.value if self.type else None,
            "status": self.status.value if self.status else None,
            "target_count": self.target_count,
            "sent_count": self.sent_count,
            "delivered_count": self.delivered_count,
            "opened_count": self.opened_count,
            "conversions": self.conversions,
            "delivery_rate": round(self.delivery_rate, 2),
            "open_rate": round(self.open_rate, 2),
            "click_rate": round(self.click_rate, 2),
            "conversion_rate": round(self.conversion_rate, 2),
            "roi": round(self.roi, 2),
            "budget": self.budget,
            "total_cost": self.total_cost,
            "conversion_value": self.conversion_value,
            "scheduled_at": self.scheduled_at.isoformat() if self.scheduled_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_active": self.is_active,
        }