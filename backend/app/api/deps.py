from typing import AsyncGenerator, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.core import security
from app.core.config import settings
from app.db.session import SessionLocal

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login/access-token"
)

reusable_oauth2_optional = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/login/access-token",
    auto_error=False
)

async def get_db() -> AsyncGenerator:
    async with SessionLocal() as session:
        yield session

async def get_current_user(
    db: AsyncSession = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> models.User:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )
    user = await crud.user.get(db, id=int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.status == models.UserStatus.BANNED:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

async def get_current_active_user(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.status != models.UserStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_superuser(
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.role not in [models.UserRole.ADMIN, models.UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_user_optional(
    db: AsyncSession = Depends(get_db), token: Optional[str] = Depends(reusable_oauth2_optional)
) -> Optional[models.User]:
    if not token:
        return None
    try:
        # We can reuse get_current_user logic but we need to pass token manually or mock dependency?
        # Easier to just decode here
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        token_data = schemas.TokenPayload(**payload)
    except (JWTError, ValidationError):
        return None
        
    user = await crud.user.get(db, id=int(token_data.sub))
    if not user or user.status == models.UserStatus.BANNED:
        return None
    return user
