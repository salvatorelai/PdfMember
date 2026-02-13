from typing import Optional
from datetime import datetime
from pydantic import BaseModel
from app.models.membership import MembershipType

# Membership Schemas
class MembershipBase(BaseModel):
    type: MembershipType
    download_quota: int
    download_used: int
    expires_at: Optional[datetime] = None

class MembershipCreate(MembershipBase):
    user_id: int

class MembershipUpdate(BaseModel):
    type: Optional[MembershipType] = None
    download_quota: Optional[int] = None
    download_used: Optional[int] = None
    expires_at: Optional[datetime] = None

class Membership(MembershipBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# RedeemCode Schemas
class RedeemCodeBase(BaseModel):
    code: str
    type: MembershipType
    uses_total: int = 1
    expires_at: Optional[datetime] = None
    is_active: bool = True

class RedeemCodeCreate(RedeemCodeBase):
    pass

class RedeemCodeUpdate(BaseModel):
    uses_remaining: Optional[int] = None
    is_active: Optional[bool] = None

class RedeemCode(RedeemCodeBase):
    id: int
    uses_remaining: int
    created_by: int
    created_at: datetime
    used_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class RedeemRequest(BaseModel):
    code: str
