"""
Database models for ContentPilot AI
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()


class SubscriptionTierEnum(str, enum.Enum):
    """Subscription tier enumeration"""
    STARTER = "starter"
    PRO = "pro"
    AGENCY = "agency"
    FREE = "free"


class ContentTypeEnum(str, enum.Enum):
    """Content type enumeration"""
    BLOG_POST = "blog_post"
    SOCIAL_MEDIA = "social_media"
    EMAIL_COPY = "email_copy"
    AD_COPY = "ad_copy"
    SEO_CONTENT = "seo_content"
    PRODUCT_DESCRIPTION = "product_description"


class SupportTicketStatusEnum(str, enum.Enum):
    """Support ticket status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"


class User(Base):
    """User model for authentication and account management"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    api_key = Column(String(255), unique=True, index=True, nullable=True)
    subscription_tier = Column(Enum(SubscriptionTierEnum), default=SubscriptionTierEnum.FREE, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    usage_limit = Column(Integer, default=0, nullable=False)  # 0 = unlimited
    stripe_customer_id = Column(String(255), nullable=True, index=True)
    stripe_subscription_id = Column(String(255), nullable=True, index=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    contents = relationship("Content", back_populates="user", cascade="all, delete-orphan")
    support_tickets = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, tier={self.subscription_tier})>"


class Content(Base):
    """Content generation history model"""
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content_type = Column(Enum(ContentTypeEnum), nullable=False, index=True)
    prompt = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    tokens_used = Column(Integer, default=0, nullable=False)
    model_used = Column(String(50), default="claude-3-haiku", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationship
    user = relationship("User", back_populates="contents")

    def __repr__(self):
        return f"<Content(id={self.id}, user_id={self.user_id}, type={self.content_type})>"


class SupportTicket(Base):
    """Support ticket model"""
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    subject = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(Enum(SupportTicketStatusEnum), default=SupportTicketStatusEnum.OPEN, nullable=False)
    ai_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship
    user = relationship("User", back_populates="support_tickets")

    def __repr__(self):
        return f"<SupportTicket(id={self.id}, user_id={self.user_id}, status={self.status})>"


class SubscriptionTier(Base):
    """Subscription tier configuration model"""
    __tablename__ = "subscription_tiers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, nullable=False)
    price = Column(Float, nullable=False)
    monthly_limit = Column(Integer, nullable=False)
    stripe_price_id = Column(String(255), nullable=True)
    features = Column(Text, nullable=True)  # JSON string of features
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<SubscriptionTier(name={self.name}, price={self.price})>"
