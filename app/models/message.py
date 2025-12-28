"""
Hunter Pro CRM Ultimate Enterprise - Message Model
Version: 7.0.0
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MessageChannel(str, enum.Enum):
    """Message channel types"""
    WHATSAPP = "whatsapp"
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    IN_APP = "in_app"
    OTHER = "other"


class MessageDirection(str, enum.Enum):
    """Message direction"""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class MessageStatus(str, enum.Enum):
    """Message delivery status"""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    READ = "read"
    FAILED = "failed"


class Message(Base):
    """Message/Communication model"""
    
    __tablename__ = "messages"
    
    # Primary Key
    id = Column(Integer, primary_key=True, index=True)
    
    # Message Content
    subject = Column(String(500))
    body = Column(Text, nullable=False)
    
    # Channel & Direction
    channel = Column(Enum(MessageChannel), default=MessageChannel.WHATSAPP, index=True)
    direction = Column(Enum(MessageDirection), default=MessageDirection.OUTBOUND)
    status = Column(Enum(MessageStatus), default=MessageStatus.PENDING, index=True)
    
    # Contact Information
    from_number = Column(String(50))
    to_number = Column(String(50))
    from_email = Column(String(255))
    to_email = Column(String(255))
    
    # Media Attachments
    media_url = Column(String(1000))
    media_type = Column(String(100))  # image, video, document, audio
    media_size = Column(Integer)  # in bytes
    
    # Customer Relationship
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=True, index=True)
    
    # Campaign Relationship
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # Tracking
    opened_at = Column(DateTime, nullable=True)
    clicked_at = Column(DateTime, nullable=True)
    replied_at = Column(DateTime, nullable=True)
    
    # External IDs (from providers)
    external_id = Column(String(200), unique=True, nullable=True)  # Provider message ID
    thread_id = Column(String(200), nullable=True)  # Conversation thread
    
    # Error Information
    error_code = Column(String(50))
    error_message = Column(Text)
    
    # AI Analysis
    ai_sentiment = Column(String(20))  # positive, negative, neutral
    ai_intent = Column(String(100))  # inquiry, complaint, purchase, etc.
    ai_summary = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    sent_at = Column(DateTime, nullable=True)
    delivered_at = Column(DateTime, nullable=True)
    
    # Soft Delete
    deleted_at = Column(DateTime, nullable=True)
    
    # Relationships
    # customer = relationship("Customer", back_populates="messages")
    # campaign = relationship("Campaign", back_populates="messages")
    
    def __repr__(self):
        return f"<Message {self.id} - {self.channel.value}>"
    
    @property
    def is_delivered(self) -> bool:
        """Check if message was delivered"""
        return self.status in [MessageStatus.DELIVERED, MessageStatus.READ]
    
    @property
    def is_read(self) -> bool:
        """Check if message was read"""
        return self.status == MessageStatus.READ
    
    @property
    def is_failed(self) -> bool:
        """Check if message failed"""
        return self.status == MessageStatus.FAILED
    
    @property
    def has_media(self) -> bool:
        """Check if message has media attachment"""
        return self.media_url is not None
    
    def to_dict(self) -> dict:
        """Convert message to dictionary"""
        return {
            "id": self.id,
            "subject": self.subject,
            "body": self.body,
            "channel": self.channel.value if self.channel else None,
            "direction": self.direction.value if self.direction else None,
            "status": self.status.value if self.status else None,
            "to_number": self.to_number,
            "to_email": self.to_email,
            "customer_id": self.customer_id,
            "has_media": self.has_media,
            "media_url": self.media_url,
            "media_type": self.media_type,
            "ai_sentiment": self.ai_sentiment,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "delivered_at": self.delivered_at.isoformat() if self.delivered_at else None,
            "is_delivered": self.is_delivered,
            "is_read": self.is_read,
        }