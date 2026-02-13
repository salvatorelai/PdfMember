from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class DownloadToken(Base):
    __tablename__ = "download_tokens"
    
    token = Column(String(64), primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    password = Column(String(255), nullable=True) # Plain text or hashed? User said "url and password". Usually shared password.
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_by = Column(Integer, nullable=False) # User ID who created the link
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    document = relationship("Document")
