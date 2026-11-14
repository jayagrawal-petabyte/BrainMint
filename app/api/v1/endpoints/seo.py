from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from app.api.deps import get_db
from app.crud.service import service_crud
from app.services.content_service import content_service
from app.core.config import settings

router = APIRouter()

@router.get("/sitemap.xml", response_class=Response)
def get_sitemap(db: Session = Depends(get_db)):
    base_url = getattr(settings, "SITE_URL", "https://brainmint.com").rstrip("/")
    services = service_crud.get_active_services(db)

    static_routes = ["", "/about", "/services", "/contact", "/privacy-policy", "/terms"]
    
    xml_entries = []
    for route in static_routes:
        xml_entries.append(f"""  <url>
    <loc>{base_url}{route}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.8</priority>
  </url>""")

    for s in services:
        xml_entries.append(f"""  <url>
    <loc>{base_url}/services/{s.slug}</loc>
    <changefreq>weekly</changefreq>
    <priority>0.9</priority>
  </url>""")

    sitemap_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{"".join(xml_entries)}
</urlset>"""

    return Response(content=sitemap_content, media_type="application/xml")

@router.get("/robots.txt", response_class=Response)
def get_robots():
    base_url = getattr(settings, "SITE_URL", "https://brainmint.com").rstrip("/")
    content = f"""User-agent: *
Allow: /
Disallow: /admin
Disallow: /api/

Sitemap: {base_url}/sitemap.xml
"""
    return Response(content=content, media_type="text/plain")

@router.get("/meta/{page_key}")
def get_page_seo(page_key: str, db: Session = Depends(get_db)):
    seo_data = content_service.get_public_setting(db, f"seo:{page_key}")
    return seo_data or {}