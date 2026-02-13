from typing import Any, Dict, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.core.security import get_password_hash, verify_password
from app.crud.base import CRUDBase
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate

class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    async def get_by_email(self, db: AsyncSession, *, email: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.email == email))
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, *, username: str) -> Optional[User]:
        result = await db.execute(select(User).filter(User.username == username))
        return result.scalars().first()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            hashed_password=get_password_hash(obj_in.password),
            username=obj_in.username,
            role=obj_in.role,
            is_active=obj_in.is_active,
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def authenticate(
        self, db: AsyncSession, *, username: str, password: str
    ) -> Optional[User]:
        user = await self.get_by_username(db, username=username)
        if not user:
            # Try email
            user = await self.get_by_email(db, email=username)
        
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    # Override create to handle password hashing
    # Wait, I already did that above. But wait, in the create method above I used hashed_password, but the model has password_hash.
    # Let me check the User model again.
    # User model has password_hash.
    # UserCreate has password.
    # Correcting the create method above.

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email,
            password_hash=get_password_hash(obj_in.password), # Corrected field name
            username=obj_in.username,
            role=obj_in.role,
            status=obj_in.status if hasattr(obj_in, 'status') else 'active', # UserStatus enum
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

user = CRUDUser(User)
