from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

class SystemSettingBase(BaseModel):
    key: str
    value: Optional[str] = None
    description: Optional[str] = None

class SystemSettingCreate(SystemSettingBase):
    pass

class SystemSettingUpdate(BaseModel):
    value: Optional[str] = None
    description: Optional[str] = None

class SystemSetting(SystemSettingBase):
    updated_at: datetime
    
    class Config:
        from_attributes = True

class BatchUploadResponse(BaseModel):
    total: int
    success: int
    failed: int
    results: List[dict]

