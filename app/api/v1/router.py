from fastapi import APIRouter
from app.api.v1.endpoints import services, content, seo, health, enquiries, contact
from app.api.v1.endpoints.admin import content as admin_content
from app.api.v1.endpoints.admin import enquiries as admin_enquiries
from app.api.v1.endpoints.admin import auth as admin_auth

api_router = APIRouter()

api_router.include_router(health.router, tags=["Health"])
api_router.include_router(services.router, prefix="/services", tags=["Services"])
api_router.include_router(content.router, prefix="/content", tags=["Content"])
api_router.include_router(seo.router, tags=["SEO"])

# Public form submissions
api_router.include_router(enquiries.router, prefix="/enquiries", tags=["Enquiries"])
api_router.include_router(contact.router, prefix="/contact", tags=["Contact"])

# Admin Authentication (Fixes the 404 errors)
api_router.include_router(admin_auth.router, prefix="/admin/auth", tags=["Admin Auth"])

# Admin Management
api_router.include_router(admin_content.router, prefix="/admin/content", tags=["Admin Content"])
api_router.include_router(admin_enquiries.router, prefix="/admin/enquiries", tags=["Admin Enquiries"])