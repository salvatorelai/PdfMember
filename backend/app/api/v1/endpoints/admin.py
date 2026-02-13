from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, File, UploadFile, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app import crud, models, schemas
from app.api import deps
from datetime import datetime
from app.models.system import SystemSetting
from app.models.token import DownloadToken

router = APIRouter()

@router.get("/stats")
async def get_dashboard_stats(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Get admin dashboard statistics.
    """
    user_count = await crud.user.count(db)
    document_count = await crud.document.count(db)
    download_count = await crud.download.count(db)
    
    # Revenue is mocked for now as we don't have orders yet
    revenue = 0 
    
    return {
        "user_count": user_count,
        "document_count": document_count,
        "download_count": download_count,
        "revenue": revenue
    }

# --- User Management ---

@router.get("/users", response_model=List[schemas.User])
async def read_users(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = await crud.user.get_multi(db, skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}", response_model=schemas.User)
async def update_user(
    *,
    db: AsyncSession = Depends(deps.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = await crud.user.get(db, id=user_id)
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user = await crud.user.update(db, db_obj=user, obj_in=user_in)
    return user

# --- Document Management ---

@router.post("/upload/batch")
async def batch_upload_documents(
    files: List[UploadFile] = File(...),
    category_id: int = Form(...),
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Batch upload documents.
    """
    success_count = 0
    
    from app.services.oss import oss_service
    from app.models.document import DocumentStatus
    import os

    for file in files:
        try:
            content = await file.read()
            # Upload to OSS/Local
            file_path = oss_service.upload_file(content, file.filename, file.content_type)
            
            # Create Document
            doc_in = schemas.DocumentCreate(
                title=file.filename,
                category_id=category_id,
                file_path=file_path,
                file_name=file.filename,
                file_size=len(content),
                status=DocumentStatus.DRAFT
            )
            
            await crud.document.create_with_tags(db, obj_in=doc_in, created_by=current_user.id)
            success_count += 1
        except Exception as e:
            print(f"Failed to process file {file.filename}: {e}")
            # Continue with other files
            continue
            
    return {"success": success_count}


@router.post("/documents/{document_id}/analyze", response_model=schemas.DocumentResponse)
async def analyze_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Trigger AI analysis and screenshot generation for a document.
    """
    document = await crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # Get System Settings
    settings_list = await crud.system_setting.get_multi(db, limit=100)
    settings = {s.key: s.value for s in settings_list}
    
    # Configure AI
    ai_api_key = settings.get("ai_api_key")
    ai_base_url = settings.get("ai_base_url")
    ai_model = settings.get("ai_model", "gpt-3.5-turbo")
    
    from app.services.ai_service import ai_service
    if ai_api_key:
        ai_service.configure(api_key=ai_api_key, base_url=ai_base_url, model=ai_model)
        
    # Screenshot Config
    # screenshot_pages = int(settings.get("screenshot_pages", 3)) # Not used if indices are prioritized
    screenshot_indices_str = settings.get("screenshot_indices", "")
    screenshot_indices = [int(x.strip()) for x in screenshot_indices_str.split(",") if x.strip().isdigit()] if screenshot_indices_str else []
    
    # Enforce page 1 (index 0) is always captured
    final_indices = {0}
    if screenshot_indices:
        final_indices.update(screenshot_indices)
    
    # Sort indices
    sorted_indices = sorted(list(final_indices))
    
    from app.services.pdf_service import pdf_service
    import os
    import json
    
    # Post-processing
    # Resolve filesystem path for local processing
    file_path = document.file_path
    fs_path = None
    
    if file_path.startswith("/static/"):
        # Local storage
        fs_path = file_path.lstrip("/") # static/uploads/...
        if not os.path.exists(fs_path):
            # Try with current working directory
            fs_path = os.path.join(os.getcwd(), fs_path)
    else:
        # TODO: Handle OSS download if needed
        pass

    if fs_path and os.path.exists(fs_path):
        # 1. Screenshots
        screenshot_dir = "static/screenshots"
        screenshots = pdf_service.generate_screenshots(
            fs_path, 
            screenshot_dir, 
            page_indices=sorted_indices
        )
        
        doc_update_data = {}
        
        if screenshots:
            # Store all screenshots as JSON
            # Add /static/ prefix to all
            all_screenshots = ["/static/" + s for s in screenshots]
            screenshots_json = json.dumps(all_screenshots)
            
            cover_image = all_screenshots[0]
            doc_update_data["cover_image"] = cover_image
            doc_update_data["screenshots"] = screenshots_json
        
        # 2. AI Summary
        if ai_api_key:
            text = pdf_service.extract_text(fs_path)
            summary = ai_service.generate_summary(text)
            if summary:
                doc_update_data["description"] = summary
                doc_update_data["ai_summary"] = summary # Ensure both fields are updated if schema differs
        
        if doc_update_data:
            doc_update = schemas.DocumentUpdate(**doc_update_data)
            document = await crud.document.update(db, db_obj=document, obj_in=doc_update)
    
    return document

@router.get("/documents", response_model=List[schemas.DocumentResponse])
async def read_all_documents(
    db: AsyncSession = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all documents (for admin).
    """
    # Use get_multi_with_filters to ensure eager loading of relations
    documents = await crud.document.get_multi_with_filters(db, skip=skip, limit=limit)
    return documents

@router.put("/documents/{document_id}", response_model=schemas.DocumentResponse)
async def update_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    document_in: schemas.DocumentUpdate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update a document (status, etc).
    """
    document = await crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    document = await crud.document.update(db, db_obj=document, obj_in=document_in)
    
    # Re-fetch to ensure relations are loaded for response model
    document = await crud.document.get(db, id=document_id)
    return document

@router.delete("/documents/{document_id}", response_model=schemas.DocumentResponse)
async def delete_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Delete a document.
    """
    document = await crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    document = await crud.document.remove(db, id=document_id)
    return document

@router.post("/documents/{document_id}/secure-link", response_model=schemas.DownloadTokenResponse)
async def share_document(
    *,
    db: AsyncSession = Depends(deps.get_db),
    document_id: int,
    share_in: schemas.DownloadTokenCreate,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Generate a secure download link.
    """
    document = await crud.document.get(db, id=document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
        
    import secrets
    import string
    from datetime import timedelta
    
    token_str = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(minutes=share_in.expires_in_minutes)
    
    # Generate password if not provided
    if not share_in.password:
        # Generate a 6-character alphanumeric password
        alphabet = string.ascii_letters + string.digits
        share_in.password = ''.join(secrets.choice(alphabet) for i in range(6))

    token = await crud.download_token.create_token(
        db, 
        obj_in=share_in, 
        document_id=document_id,
        created_by=current_user.id,
        token_str=token_str,
        expires_at=expires_at
    )
    
    url = f"/download-verify/{token.token}"
    
    return {"token": token.token, "url": url, "password": token.password, "expires_at": token.expires_at}


# --- System Settings ---

@router.get("/settings", response_model=List[schemas.SystemSetting])
async def read_system_settings(
    db: AsyncSession = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Retrieve all system settings.
    """
    settings = await crud.system_setting.get_multi(db, limit=1000)
    return settings

@router.put("/settings", response_model=List[schemas.SystemSetting])
async def update_system_settings(
    *,
    db: AsyncSession = Depends(deps.get_db),
    settings_in: List[schemas.SystemSettingCreate],
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Update multiple system settings.
    """
    results = []
    for setting in settings_in:
        updated_setting = await crud.system_setting.create_or_update(db, obj_in=setting)
        results.append(updated_setting)
    return results
