from typing import Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from app import crud, models, schemas
from app.api import deps
from app.services.oss import oss_service
from app.models.document import DocumentStatus
from app.models.analytics import Download
from app.models.membership import MembershipType
from datetime import datetime

router = APIRouter()

# --- Categories ---
@router.get("/categories", response_model=List[schemas.CategoryResponse])
async def read_categories(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    parent_id: Optional[int] = None,
    all_categories: bool = False
) -> Any:
    """
    Retrieve categories.
    """
    if all_categories:
        categories = await crud.category.get_multi(db, skip=skip, limit=limit)
    else:
        categories = await crud.category.get_multi_by_parent(
            db, parent_id=parent_id, skip=skip, limit=limit
        )
    return categories

@router.post("/categories", response_model=schemas.CategoryResponse)
async def create_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_in: schemas.CategoryCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Create new category.
    """
    category = await crud.category.create(db, obj_in=category_in)
    return category

@router.put("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def update_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int,
    category_in: schemas.CategoryUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a category.
    """
    category = await crud.category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = await crud.category.update(db, db_obj=category, obj_in=category_in)
    return category

@router.delete("/categories/{category_id}", response_model=schemas.CategoryResponse)
async def delete_category(
    *,
    db: AsyncSession = Depends(deps.get_db),
    category_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a category.
    """
    category = await crud.category.get(db, id=category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    category = await crud.category.remove(db, id=category_id)
    return category

# --- Documents ---
@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Upload a document file to OSS/Local storage.
    Returns the file path and metadata.
    """
    content = await file.read()
    file_path = oss_service.upload_file(content, file.filename, file.content_type)
    
    return {
        "file_path": file_path,
        "file_name": file.filename,
        "file_size": len(content),
        "content_type": file.content_type
    }

@router.post("/", response_model=schemas.DocumentResponse)
async def create_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_in: schemas.DocumentCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Create new document.
    """
    document = await crud.document.create_with_tags(
        db, obj_in=document_in, created_by=current_user.id
    )
    return document

@router.get("/{id}/download", response_model=schemas.DocumentDownloadUrl)
async def download_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Download a document.
    """
    # 1. Get Document
    document = await crud.document.get(db, id=id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # 2. Get/Create Membership
    membership = await crud.membership.get_by_user(db, user_id=current_user.id)
    if not membership:
        membership = await crud.membership.create_free_membership(db, user_id=current_user.id)
        
    # 3. Check Quota
    # Lifetime members ignore quota (or have huge quota)
    if membership.type != MembershipType.LIFETIME:
        # Check expiry
        if membership.expires_at and membership.expires_at < datetime.utcnow():
            raise HTTPException(status_code=403, detail="Membership expired")
            
        # Check quota
        if membership.download_used >= membership.download_quota:
             raise HTTPException(status_code=403, detail="Download quota exceeded")

    # 4. Update Stats
    membership.download_used += 1
    document.download_count += 1
    
    # 5. Record Analytics
    download_record = Download(
        user_id=current_user.id,
        document_id=document.id,
        ip_address=None,
        user_agent=None
    )
    db.add(download_record)
    
    await db.commit()
    
    return {"url": document.file_path}

@router.get("/", response_model=List[schemas.DocumentResponse])
async def read_documents(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    category_id: Optional[int] = None,
    status: Optional[DocumentStatus] = DocumentStatus.PUBLISHED, # Default to published for public
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional) # Optional auth
) -> Any:
    """
    Retrieve documents.
    """
    # If admin/author, might want to see drafts. For now simplified.
    documents = await crud.document.get_multi_with_filters(
        db, skip=skip, limit=limit, category_id=category_id, status=status
    )
    return documents

@router.get("/{id}", response_model=schemas.DocumentResponse)
async def read_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    id: int,
    current_user: Optional[models.User] = Depends(deps.get_current_user_optional)
) -> Any:
    """
    Get document by ID.
    """
    document = await crud.document.get(db, id=id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions if not published
    if document.status != DocumentStatus.PUBLISHED:
        if not current_user:
             raise HTTPException(status_code=404, detail="Document not found")
        # Allow owner or admin
        if document.created_by != current_user.id and not current_user.role in [models.UserRole.ADMIN, models.UserRole.SUPER_ADMIN]:
             raise HTTPException(status_code=404, detail="Document not found")
             
    return document

# --- Secure Download ---

@router.get("/download-token/{token}")
async def check_download_token(
    token: str,
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Check if a download token is valid and return document info (but not file).
    """
    from sqlalchemy.future import select
    from app.models.token import DownloadToken
    
    result = await db.execute(select(DownloadToken).filter(DownloadToken.token == token))
    db_token = result.scalars().first()
    
    if not db_token:
        raise HTTPException(status_code=404, detail="Invalid token")
        
    if db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")
        
    if db_token.is_used: # If we want one-time use. Requirement didn't say, but secure usually implies limits. Let's not enforce one-time for now unless asked.
        pass
        
    # Return doc info
    doc = await crud.document.get(db, id=db_token.document_id)
    return {
        "valid": True,
        "document_title": doc.title,
        "expires_at": db_token.expires_at,
        "requires_password": bool(db_token.password)
    }

@router.post("/download-token/{token}")
async def use_download_token(
    token: str,
    password_in: dict = Body(...), # Expect {"password": "..."}
    db: AsyncSession = Depends(deps.get_db),
) -> Any:
    """
    Validate password and return file URL (or stream file).
    """
    from sqlalchemy.future import select
    from app.models.token import DownloadToken
    
    result = await db.execute(select(DownloadToken).filter(DownloadToken.token == token))
    db_token = result.scalars().first()
    
    if not db_token:
        raise HTTPException(status_code=404, detail="Invalid token")
        
    if db_token.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Token expired")
        
    input_password = password_in.get("password")
    if db_token.password and input_password != db_token.password:
        raise HTTPException(status_code=403, detail="Incorrect password")
        
    # Return file path/url
    doc = await crud.document.get(db, id=db_token.document_id)
    
    # Mark as used if needed
    # db_token.is_used = True
    # await db.commit()
    
    return {"url": doc.file_path}

