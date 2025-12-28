"""
Database Models Package
All SQLAlchemy models for the application
"""

from app.models.message import Message
from app.models.deal import Deal
from app.models.campaign import Campaign

__all__ = [
    "Message",
    "Deal",
    "Campaign"
]

# Base customer model (simple version for now)
from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class Customer(Base):
    """Customer Model"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, unique=True, nullable=True, index=True)
    phone = Column(String, nullable=True, index=True)
    company = Column(String, nullable=True)
    status = Column(String, default="lead", index=True)  # lead, prospect, customer, inactive
    source = Column(String, default="manual")  # manual, website, referral, campaign
    tags = Column(JSON, default=[])
    metadata = Column(JSON, default={})
    last_contact_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<Customer(id={self.id}, name='{self.name}', status='{self.status}')>"


__all__.append("Customer")
