from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from app import crud, models, schemas
from app.api import deps
from app.models.membership import MembershipType, Redemption

router = APIRouter()

@router.get("/me", response_model=schemas.Membership)
async def read_my_membership(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get current user's membership details.
    """
    membership = await crud.membership.get_by_user(db, user_id=current_user.id)
    if not membership:
        # Create free membership if not exists
        membership = await crud.membership.create_free_membership(db, user_id=current_user.id)
    return membership

@router.post("/redeem", response_model=schemas.Membership)
async def redeem_code(
    *,
    db: AsyncSession = Depends(deps.get_db),
    code_in: schemas.RedeemRequest,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Redeem a membership code.
    """
    # 1. Validate code
    code = await crud.redeem_code.get_by_code(db, code=code_in.code)
    if not code:
        raise HTTPException(status_code=404, detail="Invalid redeem code")
    
    if not code.is_active:
        raise HTTPException(status_code=400, detail="Code is inactive")
        
    if code.expires_at and code.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Code has expired")
        
    if code.uses_remaining <= 0:
        raise HTTPException(status_code=400, detail="Code has been fully used")

    # 2. Get/Create User Membership
    user_membership = await crud.membership.get_by_user(db, user_id=current_user.id)
    if not user_membership:
        user_membership = await crud.membership.create_free_membership(db, user_id=current_user.id)

    # 3. Apply Benefits
    # Calculate new expiration
    now = datetime.utcnow()
    current_expiry = user_membership.expires_at or now
    if current_expiry < now:
        current_expiry = now
        
    # Define benefits based on type
    duration_days = 30 # Default 30 days
    quota_increase = 0
    
    if code.type == MembershipType.LIFETIME:
        new_expiry = None # Lifetime
        new_quota = 999999
        new_type = MembershipType.LIFETIME
    else:
        new_expiry = current_expiry + timedelta(days=duration_days)
        new_quota = 100 # Normal monthly quota
        new_type = MembershipType.NORMAL

    # Record redemption
    redemption = Redemption(
        user_id=current_user.id,
        redeem_code_id=code.id,
        membership_type=code.type,
        old_expires_at=user_membership.expires_at,
        new_expires_at=new_expiry,
        old_quota=user_membership.download_quota,
        new_quota=new_quota
    )
    db.add(redemption)

    # Update membership
    user_membership.type = new_type
    user_membership.expires_at = new_expiry
    user_membership.download_quota = new_quota
    
    # Update code usage
    code.uses_remaining -= 1
    if code.uses_remaining <= 0:
        code.is_active = False
    
    await db.commit()
    await db.refresh(user_membership)
    
    return user_membership

@router.post("/codes", response_model=schemas.RedeemCode)
async def create_redeem_code(
    *,
    db: AsyncSession = Depends(deps.get_db),
    code_in: schemas.RedeemCodeCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create a new redeem code (Admin only).
    """
    code = await crud.redeem_code.get_by_code(db, code=code_in.code)
    if code:
        raise HTTPException(status_code=400, detail="Code already exists")
        
    code = await crud.redeem_code.create(db, obj_in=code_in, created_by=current_user.id)
    return code
