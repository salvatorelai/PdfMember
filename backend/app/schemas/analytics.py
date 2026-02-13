from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

class DownloadBase(BaseModel):
    user_id: int
    document_id: int
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

class DownloadCreate(DownloadBase):
    pass

class DownloadUpdate(DownloadBase):
    pass

class Download(DownloadBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

class DownloadStats(BaseModel):
    total_downloads: int
    daily_downloads: int
    top_documents: List[dict]

class ReadingStats(BaseModel):
    total_views: int
    daily_views: int
    avg_reading_time: float
