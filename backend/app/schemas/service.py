from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ServiceBase(BaseModel):
    name: str
    slug: str
    short_description: str
    description: str
    icon: Optional[str] = None
    image_url: Optional[str] = None
    features: List[str] = []
    benefits: List[str] = []
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    og_image: Optional[str] = None
    canonical_url: Optional[str] = None
    is_active: bool = True
    display_order: int = 0

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    slug: Optional[str] = None
    short_description: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    image_url: Optional[str] = None
    features: Optional[List[str]] = None
    benefits: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    og_image: Optional[str] = None
    canonical_url: Optional[str] = None
    is_active: Optional[bool] = None
    display_order: Optional[int] = None

class ServiceResponse(ServiceBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class ServiceListResponse(BaseModel):
    id: int
    slug: str
    name: str
    short_description: str
    icon: Optional[str] = None
    display_order: int

    model_config = ConfigDict(from_attributes=True)