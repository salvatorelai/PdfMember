from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.crud.base import CRUDBase
from app.models.membership import Membership, RedeemCode, MembershipType, Redemption
from app.schemas.membership import MembershipCreate, MembershipUpdate, RedeemCodeCreate, RedeemCodeUpdate

class CRUDMembership(CRUDBase[Membership, MembershipCreate, MembershipUpdate]):
    async def get_by_user(self, db: AsyncSession, *, user_id: int) -> Optional[Membership]:
        result = await db.execute(select(Membership).filter(Membership.user_id == user_id))
        return result.scalars().first()

    async def create_free_membership(self, db: AsyncSession, *, user_id: int) -> Membership:
        db_obj = Membership(
            user_id=user_id,
            type=MembershipType.FREE,
            download_quota=5,  # Free users get 5 downloads
            download_used=0
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

class CRUDRedeemCode(CRUDBase[RedeemCode, RedeemCodeCreate, RedeemCodeUpdate]):
    async def get_by_code(self, db: AsyncSession, *, code: str) -> Optional[RedeemCode]:
        result = await db.execute(select(RedeemCode).filter(RedeemCode.code == code))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: RedeemCodeCreate, created_by: int) -> RedeemCode:
        db_obj = RedeemCode(
            code=obj_in.code,
            type=obj_in.type,
            uses_total=obj_in.uses_total,
            uses_remaining=obj_in.uses_total, # Initialize remaining = total
            expires_at=obj_in.expires_at,
            is_active=obj_in.is_active,
            created_by=created_by
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

membership = CRUDMembership(Membership)
redeem_code = CRUDRedeemCode(RedeemCode)
