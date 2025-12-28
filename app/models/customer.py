"""
Hunter Pro CRM Ultimate Enterprise - Customer Model
Version: 7.0.0
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class CustomerStatus(str, enum.Enum):
    """Customer status enum"""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    CUSTOMER = "customer"
    LOST = "lost"
    INACTIVE = "inactive"


class CustomerSource(str, enum.Enum):
    """Customer source enum"""
    WEBSITE = "website"
    SOCIAL_MEDIA = "social_media"
    REFERRAL = "referral"
    ADVERTISING = "advertising"
    COLD_CALL = "cold_call"
    EMAIL = "email"
    WHATSAPP = "whatsapp"
    EVENT = "event"
    OTHER = "other"


class Customer(Base):
    """Customer/Lead model"""
    
    __tablename__ = "customers"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Basic Information
    name = Column(String(200), nullable=False, index=True)
    email = Column(String(255), index=True)
    phone = Column(String(20), index=True)
    company = Column(String(200))
    position = Column(String(100))
    website = Column(String(500))
    
    # Address
    address = Column(Text)
    city = Column(String(100))
    state = Column(String(100))
    country = Column(String(100), default="Saudi Arabia")
    postal_code = Column(String(20))
    
    # Status & Classification
    status = Column(Enum(CustomerStatus), default=CustomerStatus.NEW, index=True)
    source = Column(Enum(CustomerSource), default=CustomerSource.OTHER)
    tags = Column(Text)  # Comma-separated tags
    
    # Scoring & Value
    lead_score = Column(Integer, default=0)  # 0-100
    lifetime_value = Column(Float, default=0.0)
    potential_value = Column(Float, default=0.0)
    
    # Social Media
    linkedin_url = Column(String(500))
    twitter_url = Column(String(500))
    facebook_url = Column(String(500))
    instagram_url = Column(String(500))
    
    # Notes & Description
    description = Column(Text)
    notes = Column(Text)
    
    # AI Analysis
    ai_insights = Column(Text)  # AI-generated insights
    ai_summary = Column(Text)   # AI-generated summary
    sentiment_score = Column(Float)  # -1.0 to 1.0
    
    # Owner
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_contacted_at = Column(DateTime, nullable=True)
    last_activity_at = Column(DateTime, nullable=True)
    
    # Soft Delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    # owner = relationship("User", back_populates="customers")
    # deals = relationship("Deal", back_populates="customer")
    # messages = relationship("Message", back_populates="customer")
    # activities = relationship("Activity", back_populates="customer")
    
    def __repr__(self):
        return f"<Customer {self.name}>"
    
    @property
    def is_deleted(self) -> bool:
        """Check if customer is soft deleted"""
        return self.deleted_at is not None
    
    @property
    def tag_list(self) -> list:
        """Get tags as list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(",")]
        return []
    
    def add_tag(self, tag: str):
        """Add a tag to customer"""
        tags = self.tag_list
        if tag not in tags:
            tags.append(tag)
            self.tags = ", ".join(tags)
    
    def remove_tag(self, tag: str):
        """Remove a tag from customer"""
        tags = self.tag_list
        if tag in tags:
            tags.remove(tag)
            self.tags = ", ".join(tags)
    
    def to_dict(self) -> dict:
        """Convert customer to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "company": self.company,
            "position": self.position,
            "status": self.status.value if self.status else None,
            "source": self.source.value if self.source else None,
            "tags": self.tag_list,
            "lead_score": self.lead_score,
            "lifetime_value": self.lifetime_value,
            "potential_value": self.potential_value,
            "city": self.city,
            "country": self.country,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_contacted_at": self.last_contacted_at.isoformat() if self.last_contacted_at else None,
        }