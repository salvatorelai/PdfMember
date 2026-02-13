from typing import List, Optional, Union, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from app.crud.base import CRUDBase
from app.models.document import Document, Category, Tag, DocumentStatus
from app.schemas.document import DocumentCreate, DocumentUpdate, CategoryCreate, CategoryUpdate, TagCreate

class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    async def get_multi_by_parent(self, db: AsyncSession, *, parent_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Category]:
        query = select(Category).filter(Category.parent_id == parent_id).offset(skip).limit(limit)
        result = await db.execute(query)
        return result.scalars().all()

class CRUDTag(CRUDBase[Tag, TagCreate, TagCreate]): # TagUpdate same as Create for now or ignore
    async def get_by_name(self, db: AsyncSession, *, name: str) -> Optional[Tag]:
        query = select(Tag).filter(Tag.name == name)
        result = await db.execute(query)
        return result.scalars().first()

class CRUDDocument(CRUDBase[Document, DocumentCreate, DocumentUpdate]):
    async def create_with_tags(self, db: AsyncSession, *, obj_in: DocumentCreate, created_by: int) -> Document:
        db_obj = Document(
            title=obj_in.title,
            description=obj_in.description,
            category_id=obj_in.category_id,
            file_path=obj_in.file_path,
            file_name=obj_in.file_name,
            file_size=obj_in.file_size,
            page_count=obj_in.page_count,
            cover_image=obj_in.cover_image,
            status=obj_in.status,
            created_by=created_by
        )
        
        if obj_in.tag_ids:
            query = select(Tag).filter(Tag.id.in_(obj_in.tag_ids))
            result = await db.execute(query)
            tags = result.scalars().all()
            db_obj.tags = tags
            
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        
        # Eager load relationships for response
        query = select(Document).options(selectinload(Document.category), selectinload(Document.tags)).filter(Document.id == db_obj.id)
        result = await db.execute(query)
        return result.scalars().first()

    async def get_multi_with_filters(
        self, 
        db: AsyncSession, 
        *, 
        skip: int = 0, 
        limit: int = 100,
        category_id: Optional[int] = None,
        status: Optional[DocumentStatus] = None
    ) -> List[Document]:
        query = select(Document).options(selectinload(Document.category), selectinload(Document.tags))
        
        if category_id:
            query = query.filter(Document.category_id == category_id)
        
        if status:
            query = query.filter(Document.status == status)
            
        query = query.order_by(Document.created_at.desc()).offset(skip).limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()

    async def get(self, db: AsyncSession, id: Any) -> Optional[Document]:
        # Override to eager load relationships
        query = select(Document).options(selectinload(Document.category), selectinload(Document.tags)).filter(Document.id == id)
        result = await db.execute(query)
        return result.scalars().first()

    async def remove(self, db: AsyncSession, *, id: int) -> Document:
        # Manually delete dependent records to avoid Foreign Key constraints
        from app.models.analytics import Download, ReadingHistory
        from app.models.token import DownloadToken
        from sqlalchemy import delete
        
        # DownloadToken
        await db.execute(delete(DownloadToken).where(DownloadToken.document_id == id))
        # Download
        await db.execute(delete(Download).where(Download.document_id == id))
        # ReadingHistory
        await db.execute(delete(ReadingHistory).where(ReadingHistory.document_id == id))
        
        return await super().remove(db, id=id)

document = CRUDDocument(Document)
category = CRUDCategory(Category)
tag = CRUDTag(Tag)
