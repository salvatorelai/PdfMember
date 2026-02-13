from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey, DECIMAL
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.base_class import Base

class MembershipType(str, enum.Enum):
    FREE = "free"
    NORMAL = "normal"
    LIFETIME = "lifetime"

class Membership(Base):
    __tablename__ = "memberships"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    type = Column(Enum(MembershipType), default=MembershipType.FREE, index=True)
    expires_at = Column(DateTime, nullable=True, index=True)
    download_quota = Column(Integer, default=0)
    download_used = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="membership")

class RedeemCode(Base):
    __tablename__ = "redeem_codes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False)
    type = Column(Enum(MembershipType), nullable=False)
    uses_total = Column(Integer, default=1)
    uses_remaining = Column(Integer, default=1)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    used_at = Column(DateTime, nullable=True)
    
    # Relationships
    redemptions = relationship("Redemption", back_populates="redeem_code")

class Redemption(Base):
    __tablename__ = "redemptions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    redeem_code_id = Column(Integer, ForeignKey("redeem_codes.id"), nullable=False)
    membership_type = Column(Enum(MembershipType), nullable=False)
    old_expires_at = Column(DateTime, nullable=True)
    new_expires_at = Column(DateTime, nullable=True)
    old_quota = Column(Integer, nullable=True)
    new_quota = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="redemptions")
    redeem_code = relationship("RedeemCode", back_populates="redemptions")

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    product_type = Column(String(50), nullable=False) # normal_member, lifetime_member
    amount = Column(DECIMAL(10, 2), nullable=False)
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING, index=True)
    pay_method = Column(String(50), nullable=True)
    transaction_id = Column(String(100), nullable=True)
    paid_at = Column(DateTime, nullable=True)
    expired_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="orders")
