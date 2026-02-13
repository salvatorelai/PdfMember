from sqlalchemy import Column, String, Text, DateTime
from datetime import datetime
from app.db.base_class import Base

class SystemSetting(Base):
    __tablename__ = "system_settings"
    
    key = Column(String(100), primary_key=True, index=True)
    value = Column(Text, nullable=True)
    description = Column(String(255), nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
