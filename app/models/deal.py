"""
Hunter Pro CRM Ultimate Enterprise - Deal Model
Version: 7.0.0
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class DealStage(str, enum.Enum):
    """Deal pipeline stages"""
    LEAD = "lead"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"


class DealPriority(str, enum.Enum):
    """Deal priority levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Deal(Base):
    """Deal/Opportunity model"""
    
    __tablename__ = "deals"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    title = Column(String(200), nullable=False)
    description = Column(Text)
    
    # Value
    amount = Column(Float, default=0.0, nullable=False)
    currency = Column(String(3), default="SAR")  # ISO 4217
    
    # Stage & Priority
    stage = Column(Enum(DealStage), default=DealStage.LEAD, index=True)
    priority = Column(Enum(DealPriority), default=DealPriority.MEDIUM)
    
    # Probability & Forecasting
    probability = Column(Integer, default=0)  # 0-100%
    expected_revenue = Column(Float, default=0.0)  # amount * probability
    
    # Dates
    expected_close_date = Column(DateTime, nullable=True)
    actual_close_date = Column(DateTime, nullable=True)
    
    # Loss Reason (for lost deals)
    loss_reason = Column(Text, nullable=True)
    
    # Relationships
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # AI Insights
    ai_win_probability = Column(Float)  # AI-calculated win probability
    ai_recommendations = Column(Text)   # AI recommendations
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Soft Delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    # customer = relationship("Customer", back_populates="deals")
    # owner = relationship("User", back_populates="deals")
    # activities = relationship("Activity", back_populates="deal")
    
    def __repr__(self):
        return f"<Deal {self.title}>"
    
    @property
    def is_won(self) -> bool:
        """Check if deal is won"""
        return self.stage == DealStage.CLOSED_WON
    
    @property
    def is_lost(self) -> bool:
        """Check if deal is lost"""
        return self.stage == DealStage.CLOSED_LOST
    
    @property
    def is_closed(self) -> bool:
        """Check if deal is closed (won or lost)"""
        return self.is_won or self.is_lost
    
    @property
    def is_active(self) -> bool:
        """Check if deal is still active"""
        return not self.is_closed and self.deleted_at is None
    
    def calculate_expected_revenue(self):
        """Calculate expected revenue based on amount and probability"""
        self.expected_revenue = self.amount * (self.probability / 100.0)
    
    def to_dict(self) -> dict:
        """Convert deal to dictionary"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "amount": self.amount,
            "currency": self.currency,
            "stage": self.stage.value if self.stage else None,
            "priority": self.priority.value if self.priority else None,
            "probability": self.probability,
            "expected_revenue": self.expected_revenue,
            "customer_id": self.customer_id,
            "owner_id": self.owner_id,
            "expected_close_date": self.expected_close_date.isoformat() if self.expected_close_date else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "is_won": self.is_won,
            "is_lost": self.is_lost,
            "is_active": self.is_active,
        }