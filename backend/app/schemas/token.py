from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: Optional[str] = None

class DownloadTokenCreate(BaseModel):
    password: Optional[str] = None
    expires_in_minutes: int = 60
    max_downloads: int = 1

class DownloadTokenResponse(BaseModel):
    token: str
    url: str
    password: Optional[str] = None
    expires_at: datetime


