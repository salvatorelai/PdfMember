from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, field_validator
from app.models.document import DocumentStatus

# --- Category Schemas ---
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[int] = None
    icon: Optional[str] = None
    sort_order: Optional[int] = 0
    is_active: Optional[bool] = True

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(CategoryBase):
    pass

class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class DocumentDownloadUrl(BaseModel):
    url: str

# --- Tag Schemas ---
class TagBase(BaseModel):
    name: str

class TagCreate(TagBase):
    pass

class TagResponse(TagBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Document Schemas ---
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[DocumentStatus] = DocumentStatus.DRAFT

class DocumentCreate(DocumentBase):
    file_path: str
    file_name: str
    file_size: int
    page_count: Optional[int] = None
    cover_image: Optional[str] = None
    tag_ids: Optional[List[int]] = []

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    ai_summary: Optional[str] = None
    category_id: Optional[int] = None
    status: Optional[DocumentStatus] = None
    cover_image: Optional[str] = None
    tag_ids: Optional[List[int]] = None
    screenshots: Optional[str] = None # JSON string

class DocumentResponse(DocumentBase):
    id: int
    file_path: str
    file_name: str
    file_size: int
    page_count: Optional[int]
    view_count: int
    download_count: int
    created_by: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime]
    cover_image: Optional[str]
    screenshots: Optional[List[str]] = []
    category: Optional[CategoryResponse]
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True

    @property
    def screenshots_list(self):
        # This might not work directly with Pydantic v2 from_attributes
        pass
        
    @classmethod
    def model_validate(cls, obj, *args, **kwargs):
        # Handle JSON string parsing for screenshots
        # Pydantic v2 uses model_validate? Or field_validator?
        # Let's use validator for compatibility or field_validator for v2
        return super().model_validate(obj, *args, **kwargs)
    
    @field_validator('screenshots', mode='before')
    def parse_screenshots(cls, v):
        if v is None:
            return []
        if isinstance(v, str):
            try:
                import json
                return json.loads(v)
            except:
                return []
        return v
