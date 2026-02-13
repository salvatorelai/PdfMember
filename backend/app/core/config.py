from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache

class Settings(BaseSettings):
    APP_NAME: str = "PDF Platform"
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True
    
    # Database
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 3306
    DATABASE_USER: str = "root"
    DATABASE_PASSWORD: str = "root"
    DATABASE_NAME: str = "pdf_platform"
    
    # JWT
    SECRET_KEY: str = "development_secret_key"
    JWT_SECRET_KEY: str = "development_jwt_secret_key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    
    # OSS
    OSS_ACCESS_KEY_ID: Optional[str] = ""
    OSS_ACCESS_KEY_SECRET: Optional[str] = ""
    OSS_ENDPOINT: Optional[str] = ""
    OSS_BUCKET_NAME: Optional[str] = ""
    OSS_BUCKET_DOMAIN: Optional[str] = ""

    class Config:
        env_file = ".env"

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()
