from sqlalchemy import Column, Integer, String, Text, Boolean, JSON, DateTime
from sqlalchemy.sql import func
from app.models.base import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    name = Column(String(150), nullable=False)
    short_description = Column(String(300), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(255), nullable=True)
    image_url = Column(String(255), nullable=True)
    features = Column(JSON, default=list, nullable=False)  # List of string highlights
    benefits = Column(JSON, default=list, nullable=False)  # Key business benefits
    meta_title = Column(String(200), nullable=True)
    meta_description = Column(String(300), nullable=True)
    og_image = Column(String(255), nullable=True)
    canonical_url = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    display_order = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)