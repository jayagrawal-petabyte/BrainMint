from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.schemas.service import ServiceListResponse, ServiceResponse
from app.services.content_service import content_service

router = APIRouter()

@router.get("", response_model=List[ServiceListResponse])
def get_services(db: Session = Depends(get_db)):
    """Return list of active software consultancy services."""
    return content_service.get_public_services(db)

@router.get("/{slug}", response_model=ServiceResponse)
def get_service_by_slug(slug: str, db: Session = Depends(get_db)):
    """Return complete details for a specific service by slug."""
    service = content_service.get_public_service_by_slug(db, slug)
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{slug}' not found"
        )
    return service