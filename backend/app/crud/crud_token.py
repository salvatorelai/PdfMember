from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.base import CRUDBase
from app.models.token import DownloadToken
from app.schemas.token import DownloadTokenCreate
from datetime import datetime

class CRUDDownloadToken(CRUDBase[DownloadToken, DownloadTokenCreate, DownloadTokenCreate]):
    async def create_token(
        self, db: AsyncSession, *, obj_in: DownloadTokenCreate, document_id: int, created_by: int, token_str: str, expires_at: datetime
    ) -> DownloadToken:
        db_obj = DownloadToken(
            token=token_str,
            document_id=document_id,
            password=obj_in.password,
            expires_at=expires_at,
            created_by=created_by,
            is_used=False
        )
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

download_token = CRUDDownloadToken(DownloadToken)

