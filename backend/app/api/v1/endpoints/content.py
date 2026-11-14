from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud.content import content_crud
from app.schemas.content import FAQResponse, SocialLinkResponse
from app.services.content_service import content_service

router = APIRouter()

@router.get("/about", response_model=Dict[str, Any])
def get_about_us(db: Session = Depends(get_db)):
    return content_service.get_public_setting(db, "about_us")

@router.get("/why-choose-us", response_model=Dict[str, Any])
def get_why_choose_us(db: Session = Depends(get_db)):
    return content_service.get_public_setting(db, "why_choose_us")

@router.get("/capabilities", response_model=Dict[str, Any])
def get_capabilities(db: Session = Depends(get_db)):
    return content_service.get_public_setting(db, "capabilities")

@router.get("/faqs", response_model=List[FAQResponse])
def get_faqs(category: Optional[str] = None, db: Session = Depends(get_db)):
    return content_crud.get_published_faqs(db, category)

@router.get("/contact-info", response_model=Dict[str, Any])
def get_contact_info(db: Session = Depends(get_db)):
    return content_service.get_public_setting(db, "contact_info")

@router.get("/social-links", response_model=List[SocialLinkResponse])
def get_social_links(db: Session = Depends(get_db)):
    return content_crud.get_active_social_links(db)

@router.get("/privacy-policy", response_model=Dict[str, Any])
def get_privacy_policy(db: Session = Depends(get_db)):
    return content_service.get_public_setting(db, "privacy_policy")

@router.get("/terms", response_model=Dict[str, Any])
def get_terms(db: Session = Depends(get_db)):
    return content_service.get_public_setting(db, "terms_and_conditions")