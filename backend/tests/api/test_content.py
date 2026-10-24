"""
Tests for content and services endpoints.

Refactored to use the shared conftest fixtures (in-memory SQLite + session
override) so they run fully self-contained without a real database or seed data.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.service import Service
from app.models.content import SiteSetting, FAQ, SocialLink


# ---------------------------------------------------------------------------
# Seed helpers
# ---------------------------------------------------------------------------

def _seed_services(db: Session) -> list[Service]:
    """Insert the 4 canonical BrainMint services."""
    slugs = [
        ("Website Development", "website-development"),
        ("Mobile App Development", "mobile-app-development"),
        ("Software Development", "software-development"),
        ("Digital Marketing", "digital-marketing"),
    ]
    services = []
    for name, slug in slugs:
        s = Service(
            name=name,
            slug=slug,
            short_description=f"Short desc for {name}",
            description=f"Full description for {name}.",
            features=["Feature A", "Feature B"],
            benefits=["Benefit A"],
            is_active=True,
            display_order=len(services),
        )
        db.add(s)
        services.append(s)
    db.commit()
    for s in services:
        db.refresh(s)
    return services


def _seed_site_settings(db: Session):
    """Insert the site-content settings accessed by content endpoints."""
    keys = [
        "about_us",
        "why_choose_us",
        "capabilities",
        "contact_info",
        "privacy_policy",
        "terms_and_conditions",
    ]
    for key in keys:
        db.add(SiteSetting(key=key, value={"content": f"Placeholder for {key}"}))
    db.commit()


# ===========================================================================
# Services endpoints
# ===========================================================================

class TestServicesEndpoints:
    def test_get_services_list_returns_all_active(self, client: TestClient, db: Session):
        _seed_services(db)
        response = client.get("/api/v1/services")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 4

    def test_get_service_by_slug_success(self, client: TestClient, db: Session):
        _seed_services(db)
        response = client.get("/api/v1/services/website-development")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "website-development"
        assert "features" in data
        assert "benefits" in data

    def test_get_service_by_slug_not_found(self, client: TestClient):
        response = client.get("/api/v1/services/non-existent-service-slug")
        assert response.status_code == 404
        data = response.json()
        assert data["success"] is False
        assert data["error"]["code"] == "NOT_FOUND"


# ===========================================================================
# Content endpoints
# ===========================================================================

class TestContentEndpoints:
    def test_get_content_endpoints_return_200(self, client: TestClient, db: Session):
        _seed_site_settings(db)
        endpoints = [
            "/api/v1/content/about",
            "/api/v1/content/why-choose-us",
            "/api/v1/content/capabilities",
            "/api/v1/content/faqs",
            "/api/v1/content/contact-info",
            "/api/v1/content/social-links",
            "/api/v1/content/privacy-policy",
            "/api/v1/content/terms",
        ]
        for ep in endpoints:
            res = client.get(ep)
            assert res.status_code == 200, f"Failed at endpoint: {ep}"

    def test_get_faqs_returns_list(self, client: TestClient, db: Session):
        db.add(FAQ(question="Q1?", answer="A1", category="general", is_published=True))
        db.commit()
        res = client.get("/api/v1/content/faqs")
        assert res.status_code == 200
        assert isinstance(res.json(), list)

    def test_get_social_links_returns_list(self, client: TestClient, db: Session):
        db.add(SocialLink(platform="LinkedIn", url="https://linkedin.com/company/brainmint", is_active=True))
        db.commit()
        res = client.get("/api/v1/content/social-links")
        assert res.status_code == 200
        assert isinstance(res.json(), list)


# ===========================================================================
# SEO endpoints
# ===========================================================================

class TestSEOEndpoints:
    def test_get_sitemap_returns_xml(self, client: TestClient, db: Session):
        _seed_services(db)
        response = client.get("/api/v1/sitemap.xml")
        assert response.status_code == 200
        assert "application/xml" in response.headers["content-type"]
        assert "<urlset" in response.text
        assert "website-development" in response.text

    def test_get_robots_txt(self, client: TestClient):
        response = client.get("/api/v1/robots.txt")
        assert response.status_code == 200
        assert "User-agent:" in response.text


# ===========================================================================
# Admin content endpoints
# ===========================================================================

class TestAdminContentEndpoints:
    def test_admin_create_and_delete_faq(self, client: TestClient, db: Session):
        faq_payload = {
            "question": "What technologies do you use?",
            "answer": "We use modern stacks tailored to high-scale production.",
            "category": "technical",
            "display_order": 1,
            "is_published": True,
        }
        create_res = client.post("/api/v1/admin/content/faqs", json=faq_payload)
        assert create_res.status_code == 201, create_res.text
        created_faq = create_res.json()
        faq_id = created_faq["id"]

        delete_res = client.delete(f"/api/v1/admin/content/faqs/{faq_id}")
        assert delete_res.status_code == 200

    def test_admin_list_services(self, client: TestClient, db: Session):
        _seed_services(db)
        res = client.get("/api/v1/admin/content/services")
        assert res.status_code == 200
        assert len(res.json()) >= 4

    def test_admin_update_site_section(self, client: TestClient, db: Session):
        payload = {"value": {"content": "Updated about us text."}}
        res = client.put("/api/v1/admin/content/sections/about_us", json=payload)
        assert res.status_code == 200
        body = res.json()
        assert "updated successfully" in body["message"].lower()