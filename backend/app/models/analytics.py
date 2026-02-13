from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, BigInteger, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.base_class import Base

class Download(Base):
    __tablename__ = "downloads"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="downloads")
    document = relationship("Document", back_populates="downloads")

class ReadingHistory(Base):
    __tablename__ = "reading_history"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    last_page = Column(Integer, default=1)
    total_time = Column(Integer, default=0) # seconds
    is_completed = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'document_id', name='uk_user_doc'),
    )
    
    # Relationships
    user = relationship("User", back_populates="reading_history")
    document = relationship("Document", back_populates="reading_history")
