from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_admin_user  # Provided by Ashutosh
from app.crud.service import service_crud
from app.crud.content import content_crud
from app.schemas.service import ServiceCreate, ServiceUpdate, ServiceResponse
from app.schemas.content import (
    FAQCreate, FAQUpdate, FAQResponse,
    SocialLinkCreate, SocialLinkUpdate, SocialLinkResponse,
    SiteSettingUpdate
)
from app.services.content_service import content_service
from app.utils.slug import slugify

router = APIRouter()

# --- SERVICES ADMIN CRUD ---
@router.get("/services", response_model=List[ServiceResponse])
def admin_list_services(db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    return service_crud.get_all(db)

@router.post("/services", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
def admin_create_service(service_in: ServiceCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    if not service_in.slug:
        service_in.slug = slugify(service_in.name)
    existing = service_crud.get_by_slug(db, service_in.slug)
    if existing:
        raise HTTPException(status_code=400, detail=f"Service with slug '{service_in.slug}' already exists")
    service = service_crud.create(db, service_in)
    content_service.invalidate("service")
    return service

@router.put("/services/{service_id}", response_model=ServiceResponse)
def admin_update_service(service_id: int, service_in: ServiceUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    db_service = service_crud.get(db, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    updated = service_crud.update(db, db_service, service_in)
    content_service.invalidate("service")
    return updated

@router.delete("/services/{service_id}")
def admin_delete_service(service_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    db_service = service_crud.get(db, service_id)
    if not db_service:
        raise HTTPException(status_code=404, detail="Service not found")
    service_crud.delete(db, service_id)
    content_service.invalidate("service")
    return {"message": "Service successfully deleted"}

# --- FAQS ADMIN CRUD ---
@router.get("/faqs", response_model=List[FAQResponse])
def admin_list_faqs(db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    return content_crud.get_all_faqs(db)

@router.post("/faqs", response_model=FAQResponse, status_code=status.HTTP_201_CREATED)
def admin_create_faq(faq_in: FAQCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    faq = content_crud.create_faq(db, faq_in)
    return faq

@router.put("/faqs/{faq_id}", response_model=FAQResponse)
def admin_update_faq(faq_id: int, faq_in: FAQUpdate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    db_faq = db.query(content_crud.get_all_faqs(db)).filter_by(id=faq_id).first() if hasattr(content_crud, "get_faq") else None
    from app.models.content import FAQ
    db_faq = db.query(FAQ).filter(FAQ.id == faq_id).first()
    if not db_faq:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return content_crud.update_faq(db, db_faq, faq_in)

@router.delete("/faqs/{faq_id}")
def admin_delete_faq(faq_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    deleted = content_crud.delete_faq(db, faq_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="FAQ not found")
    return {"message": "FAQ deleted"}

# --- SOCIAL LINKS ADMIN CRUD ---
@router.get("/social-links", response_model=List[SocialLinkResponse])
def admin_list_social_links(db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    return content_crud.get_all_social_links(db)

@router.post("/social-links", response_model=SocialLinkResponse, status_code=status.HTTP_201_CREATED)
def admin_create_social_link(link_in: SocialLinkCreate, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    return content_crud.create_social_link(db, link_in)

@router.delete("/social-links/{link_id}")
def admin_delete_social_link(link_id: int, db: Session = Depends(get_db), current_user = Depends(get_current_admin_user)):
    deleted = content_crud.delete_social_link(db, link_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Social link not found")
    return {"message": "Social link deleted"}

# --- SITE CONTENT & SEO SECTIONS ---
@router.put("/sections/{section_key}")
def admin_update_site_section(
    section_key: str,
    payload: SiteSettingUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_admin_user)
):
    setting = content_crud.set_setting(db, key=section_key, value=payload.value)
    content_service.invalidate(f"setting:{section_key}")
    return {"message": f"Section '{section_key}' updated successfully", "data": setting.value}