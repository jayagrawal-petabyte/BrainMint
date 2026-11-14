from typing import Any, List, Optional, Dict
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class FAQBase(BaseModel):
    question: str
    answer: str
    category: str = "general"
    display_order: int = 0
    is_published: bool = True

class FAQCreate(FAQBase):
    pass

class FAQUpdate(BaseModel):
    question: Optional[str] = None
    answer: Optional[str] = None
    category: Optional[str] = None
    display_order: Optional[int] = None
    is_published: Optional[bool] = None

class FAQResponse(FAQBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SocialLinkBase(BaseModel):
    platform: str
    url: str
    icon: Optional[str] = None
    display_order: int = 0
    is_active: bool = True

class SocialLinkCreate(SocialLinkBase):
    pass

class SocialLinkUpdate(BaseModel):
    platform: Optional[str] = None
    url: Optional[str] = None
    icon: Optional[str] = None
    display_order: Optional[int] = None
    is_active: Optional[bool] = None

class SocialLinkResponse(SocialLinkBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

class SiteSettingUpdate(BaseModel):
    value: Dict[str, Any]

class SiteSettingResponse(BaseModel):
    key: str
    value: Dict[str, Any]
    description: Optional[str] = None
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SEOMeta(BaseModel):
    title: str
    description: str
    keywords: Optional[str] = None
    og_title: Optional[str] = None
    og_description: Optional[str] = None
    og_image: Optional[str] = None
    canonical_url: Optional[str] = None