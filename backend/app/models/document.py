from sqlalchemy import Column, Integer, String, DateTime, Enum, Boolean, ForeignKey, Text, BigInteger, Table
from sqlalchemy.orm import relationship, backref
from datetime import datetime
import enum

from app.db.base_class import Base

# Association table for Document <-> Tag
document_tags = Table(
    "document_tags",
    Base.metadata,
    Column("document_id", Integer, ForeignKey("documents.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True),
)

class DocumentStatus(str, enum.Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"

class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    slug = Column(String(50), unique=True, nullable=False)
    description = Column(String(255), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    icon = Column(String(100), nullable=True)
    sort_order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="category")
    children = relationship("Category", backref=backref("parent", remote_side=[id]))

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(30), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", secondary=document_tags, back_populates="tags")

class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False, index=True)
    description = Column(Text, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    cover_image = Column(String(500), nullable=True)
    file_path = Column(String(500), nullable=False) # OSS path
    file_name = Column(String(255), nullable=False)
    file_size = Column(BigInteger, nullable=False)
    page_count = Column(Integer, nullable=True)
    
    # New fields for AI and Screenshots
    ai_summary = Column(Text, nullable=True)
    screenshots = Column(Text, nullable=True) # JSON string of list of paths
    
    view_count = Column(Integer, default=0)
    download_count = Column(Integer, default=0)
    status = Column(Enum(DocumentStatus), default=DocumentStatus.DRAFT, index=True)
    is_delete = Column(Boolean, default=False)
    created_by = Column(Integer, nullable=False) # Simplified, could link to User if needed
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    published_at = Column(DateTime, nullable=True)
    
    # Relationships
    category = relationship("Category", back_populates="documents")
    tags = relationship("Tag", secondary=document_tags, back_populates="documents")
    downloads = relationship("Download", back_populates="document")
    reading_history = relationship("ReadingHistory", back_populates="document")
