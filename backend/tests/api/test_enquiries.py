"""
Unit and integration tests for enquiry endpoints.

Coverage:
  POST /api/v1/enquiries  (SCR-012)
  POST /api/v1/contact    (SCR-008)
  Admin CRUD endpoints    (list, detail, status update, CSV export)
  Validation edge-cases   (SCR-014)
  Duplicate submission prevention
  Rate limiting
  Anti-spam: honeypot
  Input sanitisation
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session

from app.crud.enquiry import enquiry_crud, _build_idempotency_key
from app.models.enquiry import Enquiry, EnquirySource, EnquiryStatus, EmailStatus


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

SERVICE_ENQUIRY_URL = "/api/v1/enquiries"
CONTACT_URL = "/api/v1/contact"
ADMIN_LIST_URL = "/api/v1/admin/enquiries"


def _valid_service_payload(**overrides) -> dict:
    base = {
        "name": "Riya Sharma",
        "email": "riya@example.com",
        "phone": "+91 9876543210",
        "service": "website-development",
        "message": "I need a modern website for my startup. Please get in touch!",
        "captcha_token": "test-token",
        "honeypot": "",
    }
    base.update(overrides)
    return base


def _valid_contact_payload(**overrides) -> dict:
    base = {
        "name": "Anil Kumar",
        "email": "anil@example.com",
        "phone": None,
        "message": "I have a general question about your pricing.",
        "captcha_token": "test-token",
        "honeypot": "",
    }
    base.update(overrides)
    return base


# ===========================================================================
# POST /api/v1/enquiries  – Service Enquiry Form (SCR-012)
# ===========================================================================

class TestServiceEnquirySubmit:
    def test_happy_path_creates_enquiry(self, client: TestClient, db: Session):
        """A valid submission returns 201 with the standard success envelope."""
        with patch("app.services.email_service.email_service.send_enquiry_notification"), \
             patch("app.services.email_service.email_service.send_enquiry_acknowledgement"):
            res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload())

        assert res.status_code == 201
        body = res.json()
        assert body["success"] is True
        assert "enquiry_id" in body["data"]
        assert body["data"]["enquiry_id"] > 0

    def test_enquiry_persisted_in_db(self, client: TestClient, db: Session):
        with patch("app.services.email_service.email_service.send_enquiry_notification"), \
             patch("app.services.email_service.email_service.send_enquiry_acknowledgement"):
            res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload(
                email="db_test@example.com"
            ))
        assert res.status_code == 201
        eid = res.json()["data"]["enquiry_id"]

        record = db.query(Enquiry).filter(Enquiry.id == eid).first()
        assert record is not None
        assert record.source == EnquirySource.service_enquiry
        assert record.service == "website-development"
        assert record.status == EnquiryStatus.new

    def test_without_optional_phone(self, client: TestClient, db: Session):
        payload = _valid_service_payload(phone=None, email="nophone@example.com")
        with patch("app.services.email_service.email_service.send_enquiry_notification"), \
             patch("app.services.email_service.email_service.send_enquiry_acknowledgement"):
            res = client.post(SERVICE_ENQUIRY_URL, json=payload)
        assert res.status_code == 201

    # --- Validation errors (SCR-014) ---

    def test_missing_required_name_returns_field_error(self, client: TestClient):
        payload = _valid_service_payload()
        del payload["name"]
        res = client.post(SERVICE_ENQUIRY_URL, json=payload)
        assert res.status_code == 422
        body = res.json()
        assert body["success"] is False
        assert body["error"]["code"] == "VALIDATION_ERROR"
        fields = [e["field"] for e in body["error"]["details"]]
        assert "name" in fields

    def test_invalid_email_returns_field_error(self, client: TestClient):
        res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload(
            email="not-an-email"
        ))
        assert res.status_code == 422
        body = res.json()
        assert body["error"]["code"] == "VALIDATION_ERROR"
        fields = [e["field"] for e in body["error"]["details"]]
        assert "email" in fields

    def test_invalid_phone_returns_field_error(self, client: TestClient):
        res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload(
            phone="ABC!@#"
        ))
        assert res.status_code == 422
        body = res.json()
        assert body["error"]["code"] == "VALIDATION_ERROR"
        fields = [e["field"] for e in body["error"]["details"]]
        assert "phone" in fields

    def test_invalid_service_returns_field_error(self, client: TestClient):
        res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload(
            service="non-existent-service"
        ))
        assert res.status_code == 422
        body = res.json()
        assert body["error"]["code"] == "VALIDATION_ERROR"
        fields = [e["field"] for e in body["error"]["details"]]
        assert "service" in fields

    @pytest.mark.parametrize("service", [
        "website-development",
        "mobile-app-development",
        "software-development",
        "digital-marketing",
    ])
    def test_all_approved_services_accepted(self, service: str, client: TestClient, db: Session):
        payload = _valid_service_payload(
            service=service,
            email=f"test_{service.replace('-', '_')}@example.com",
        )
        with patch("app.services.email_service.email_service.send_enquiry_notification"), \
             patch("app.services.email_service.email_service.send_enquiry_acknowledgement"):
            res = client.post(SERVICE_ENQUIRY_URL, json=payload)
        assert res.status_code == 201, f"Service '{service}' was unexpectedly rejected"

    def test_message_too_short_returns_field_error(self, client: TestClient):
        res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload(message="Hi"))
        assert res.status_code == 422
        body = res.json()
        assert body["error"]["code"] == "VALIDATION_ERROR"

    def test_message_too_long_returns_field_error(self, client: TestClient):
        res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload(
            message="x" * 3001
        ))
        assert res.status_code == 422

    def test_name_too_short_returns_field_error(self, client: TestClient):
        res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload(name="A"))
        assert res.status_code == 422

    # --- Anti-spam ---

    def test_honeypot_filled_rejects_submission(self, client: TestClient):
        res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload(
            honeypot="bot-was-here"
        ))
        assert res.status_code == 422

    def test_email_status_sent_on_success(self, client: TestClient, db: Session):
        with patch("app.services.email_service.email_service.send_enquiry_notification"), \
             patch("app.services.email_service.email_service.send_enquiry_acknowledgement"):
            res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload(
                email="emailstatus@example.com"
            ))
        assert res.status_code == 201
        eid = res.json()["data"]["enquiry_id"]
        record = db.query(Enquiry).filter(Enquiry.id == eid).first()
        assert record.email_status == EmailStatus.sent

    def test_email_failure_still_saves_enquiry(self, client: TestClient, db: Session):
        """Even if email delivery fails, the DB row must exist (no lead lost)."""
        from app.services.email_service import EmailDeliveryError
        with patch(
            "app.services.email_service.email_service.send_enquiry_notification",
            side_effect=EmailDeliveryError("SMTP timeout"),
        ):
            res = client.post(SERVICE_ENQUIRY_URL, json=_valid_service_payload(
                email="emailfail@example.com"
            ))

        assert res.status_code == 201   # Submission still accepted
        eid = res.json()["data"]["enquiry_id"]
        record = db.query(Enquiry).filter(Enquiry.id == eid).first()
        assert record is not None        # Record exists
        assert record.email_status == EmailStatus.failed  # Marked as failed

    # --- Duplicate prevention ---

    def test_duplicate_submission_returns_200(self, client: TestClient, db: Session):
        payload = _valid_service_payload(email="dup@example.com")
        with patch("app.services.email_service.email_service.send_enquiry_notification"), \
             patch("app.services.email_service.email_service.send_enquiry_acknowledgement"):
            r1 = client.post(SERVICE_ENQUIRY_URL, json=payload)
            r2 = client.post(SERVICE_ENQUIRY_URL, json=payload)

        assert r1.status_code == 201
        assert r2.status_code == 200  # Duplicate → 200
        # Both responses point to the same enquiry ID
        assert r1.json()["data"]["enquiry_id"] == r2.json()["data"]["enquiry_id"]

    def test_duplicate_does_not_create_second_row(self, client: TestClient, db: Session):
        payload = _valid_service_payload(email="dup_count@example.com")
        with patch("app.services.email_service.email_service.send_enquiry_notification"), \
             patch("app.services.email_service.email_service.send_enquiry_acknowledgement"):
            client.post(SERVICE_ENQUIRY_URL, json=payload)
            client.post(SERVICE_ENQUIRY_URL, json=payload)

        count = db.query(Enquiry).filter(Enquiry.email == "dup_count@example.com").count()
        assert count == 1

    # --- Input sanitisation ---

    def test_html_tags_stripped_from_name(self, client: TestClient, db: Session):
        payload = _valid_service_payload(
            name="<script>alert(1)</script>Legit Name",
            email="xss@example.com",
        )
        with patch("app.services.email_service.email_service.send_enquiry_notification"), \
             patch("app.services.email_service.email_service.send_enquiry_acknowledgement"):
            res = client.post(SERVICE_ENQUIRY_URL, json=payload)
        assert res.status_code == 201
        eid = res.json()["data"]["enquiry_id"]
        record = db.query(Enquiry).filter(Enquiry.id == eid).first()
        assert "<script>" not in record.name


# ===========================================================================
# POST /api/v1/contact  – Contact Us Form (SCR-008)
# ===========================================================================

class TestContactEnquirySubmit:
    def test_happy_path_creates_contact_enquiry(self, client: TestClient, db: Session):
        with patch("app.services.email_service.email_service.send_enquiry_notification"), \
             patch("app.services.email_service.email_service.send_enquiry_acknowledgement"):
            res = client.post(CONTACT_URL, json=_valid_contact_payload())
        assert res.status_code == 201
        body = res.json()
        assert body["success"] is True
        assert body["data"]["enquiry_id"] > 0

    def test_contact_enquiry_source_is_contact_us(self, client: TestClient, db: Session):
        payload = _valid_contact_payload(email="source_test@example.com")
        with patch("app.services.email_service.email_service.send_enquiry_notification"), \
             patch("app.services.email_service.email_service.send_enquiry_acknowledgement"):
            res = client.post(CONTACT_URL, json=payload)
        eid = res.json()["data"]["enquiry_id"]
        record = db.query(Enquiry).filter(Enquiry.id == eid).first()
        assert record.source == EnquirySource.contact_us
        assert record.service is None   # No service field for contact-us

    def test_missing_message_returns_422(self, client: TestClient):
        payload = _valid_contact_payload()
        del payload["message"]
        res = client.post(CONTACT_URL, json=payload)
        assert res.status_code == 422
        assert res.json()["error"]["code"] == "VALIDATION_ERROR"

    def test_invalid_email_contact(self, client: TestClient):
        res = client.post(CONTACT_URL, json=_valid_contact_payload(email="bad-email"))
        assert res.status_code == 422

    def test_honeypot_contact_rejects(self, client: TestClient):
        res = client.post(CONTACT_URL, json=_valid_contact_payload(
            honeypot="spam@evil.com"
        ))
        assert res.status_code == 422


# ===========================================================================
# Admin endpoints
# ===========================================================================

class TestAdminEnquiries:
    def _seed_enquiry(self, db: Session, email: str = "seed@example.com") -> Enquiry:
        """Helper to insert a test enquiry directly."""
        e = Enquiry(
            name="Test User",
            email=email,
            phone=None,
            service="website-development",
            message="A test enquiry message for admin tests.",
            source=EnquirySource.service_enquiry,
            status=EnquiryStatus.new,
            email_status=EmailStatus.sent,
            ip_address="127.0.0.1",
            idempotency_key=_build_idempotency_key(email, "website-development", "A test enquiry"),
        )
        db.add(e)
        db.commit()
        db.refresh(e)
        return e

    def test_admin_list_returns_paginated_result(self, client: TestClient, db: Session):
        self._seed_enquiry(db, email="list1@example.com")
        self._seed_enquiry(db, email="list2@example.com")
        res = client.get(ADMIN_LIST_URL)
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert "items" in body["data"]
        assert "total" in body["data"]
        assert body["data"]["total"] >= 2

    def test_admin_list_filter_by_source(self, client: TestClient, db: Session):
        self._seed_enquiry(db, email="src_filter@example.com")
        res = client.get(ADMIN_LIST_URL, params={"source": "service_enquiry"})
        assert res.status_code == 200
        body = res.json()
        for item in body["data"]["items"]:
            assert item["source"] == "service_enquiry"

    def test_admin_list_filter_by_status(self, client: TestClient, db: Session):
        self._seed_enquiry(db, email="status_filter@example.com")
        res = client.get(ADMIN_LIST_URL, params={"status": "new"})
        assert res.status_code == 200
        body = res.json()
        for item in body["data"]["items"]:
            assert item["status"] == "new"

    def test_admin_list_search(self, client: TestClient, db: Session):
        self._seed_enquiry(db, email="search_unique_xyz@example.com")
        res = client.get(ADMIN_LIST_URL, params={"search": "search_unique_xyz"})
        assert res.status_code == 200
        body = res.json()
        assert body["data"]["total"] >= 1

    def test_admin_list_pagination(self, client: TestClient, db: Session):
        for i in range(5):
            self._seed_enquiry(db, email=f"pag_{i}@example.com")
        res = client.get(ADMIN_LIST_URL, params={"page": 1, "page_size": 2})
        assert res.status_code == 200
        assert len(res.json()["data"]["items"]) <= 2

    def test_admin_get_detail(self, client: TestClient, db: Session):
        e = self._seed_enquiry(db, email="detail@example.com")
        res = client.get(f"{ADMIN_LIST_URL}/{e.id}")
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["data"]["id"] == e.id
        assert body["data"]["email"] == "detail@example.com"

    def test_admin_get_detail_not_found(self, client: TestClient):
        res = client.get(f"{ADMIN_LIST_URL}/999999")
        assert res.status_code == 404
        assert res.json()["error"]["code"] == "NOT_FOUND"

    def test_admin_update_status(self, client: TestClient, db: Session):
        e = self._seed_enquiry(db, email="statusupdate@example.com")
        res = client.patch(
            f"{ADMIN_LIST_URL}/{e.id}/status",
            json={"status": "in_review"},
        )
        assert res.status_code == 200
        body = res.json()
        assert body["success"] is True
        assert body["data"]["status"] == "in_review"

        # Verify DB was updated
        db.refresh(e)
        assert e.status == EnquiryStatus.in_review

    def test_admin_update_status_invalid_value(self, client: TestClient, db: Session):
        e = self._seed_enquiry(db, email="basstatus@example.com")
        res = client.patch(
            f"{ADMIN_LIST_URL}/{e.id}/status",
            json={"status": "unknown_status"},
        )
        assert res.status_code == 422

    def test_admin_csv_export(self, client: TestClient, db: Session):
        self._seed_enquiry(db, email="csv@example.com")
        res = client.get(f"{ADMIN_LIST_URL}/export")
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]
        content = res.text
        # Check CSV header row
        assert "ID" in content
        assert "Name" in content
        assert "Email" in content
        assert "csv@example.com" in content

    def test_admin_csv_export_with_filter(self, client: TestClient, db: Session):
        self._seed_enquiry(db, email="csv_filter@example.com")
        res = client.get(f"{ADMIN_LIST_URL}/export", params={"source": "service_enquiry"})
        assert res.status_code == 200
        assert "text/csv" in res.headers["content-type"]


# ===========================================================================
# CRUD unit tests
# ===========================================================================

class TestEnquiryCRUD:
    def test_create_and_retrieve(self, db: Session):
        e, is_dup = enquiry_crud.create(
            db,
            name="Unit Test",
            email="crud_unit@example.com",
            phone=None,
            service="website-development",
            message="CRUD unit test message content here.",
            source=EnquirySource.service_enquiry,
            ip_address="10.0.0.1",
        )
        assert not is_dup
        assert e.id is not None
        fetched = enquiry_crud.get(db, e.id)
        assert fetched is not None
        assert fetched.email == "crud_unit@example.com"

    def test_duplicate_detection_returns_existing(self, db: Session):
        kwargs = dict(
            name="Dup Test",
            email="dup_crud@example.com",
            phone=None,
            service="software-development",
            message="Same message for idempotency test.",
            source=EnquirySource.service_enquiry,
            ip_address=None,
        )
        e1, _ = enquiry_crud.create(db, **kwargs)
        e2, is_dup = enquiry_crud.create(db, **kwargs)
        assert is_dup is True
        assert e1.id == e2.id
        count = db.query(Enquiry).filter(Enquiry.email == "dup_crud@example.com").count()
        assert count == 1

    def test_mark_email_sent(self, db: Session):
        e, _ = enquiry_crud.create(
            db,
            name="Email Sent",
            email="emailsent@example.com",
            phone=None,
            service=None,
            message="Test message for email sent check.",
            source=EnquirySource.contact_us,
            ip_address=None,
        )
        enquiry_crud.mark_email_sent(db, e)
        db.refresh(e)
        assert e.email_status == EmailStatus.sent

    def test_mark_email_failed(self, db: Session):
        e, _ = enquiry_crud.create(
            db,
            name="Email Fail",
            email="emailfail_crud@example.com",
            phone=None,
            service=None,
            message="Test message for email fail check.",
            source=EnquirySource.contact_us,
            ip_address=None,
        )
        enquiry_crud.mark_email_failed(db, e, "Connection refused")
        db.refresh(e)
        assert e.email_status == EmailStatus.failed
        assert "Connection refused" in e.email_error

    def test_update_status(self, db: Session):
        e, _ = enquiry_crud.create(
            db,
            name="Status Update",
            email="statusupdate_crud@example.com",
            phone=None,
            service=None,
            message="Test message for status update.",
            source=EnquirySource.contact_us,
            ip_address=None,
        )
        updated = enquiry_crud.update_status(db, e, EnquiryStatus.contacted)
        assert updated.status == EnquiryStatus.contacted

    def test_list_admin_returns_items_and_count(self, db: Session):
        for i in range(3):
            enquiry_crud.create(
                db,
                name=f"List Test {i}",
                email=f"listtest{i}@example.com",
                phone=None,
                service="digital-marketing",
                message="Test message for list admin.",
                source=EnquirySource.service_enquiry,
                ip_address=None,
            )
        items, total = enquiry_crud.list_admin(db)
        assert total >= 3
        assert len(items) >= 3

    def test_idempotency_key_uniqueness(self):
        k1 = _build_idempotency_key("a@b.com", "web", "hello")
        k2 = _build_idempotency_key("a@b.com", "web", "hello")
        k3 = _build_idempotency_key("a@b.com", "web", "different message")
        assert k1 == k2           # Same inputs → same key
        assert k1 != k3           # Different message → different key


# ===========================================================================
# Rate limiting (uses client_no_mock fixture)
# ===========================================================================

class TestRateLimiting:
    def test_rate_limit_blocks_after_threshold(self, client_no_mock: TestClient, db: Session):
        """After 5 requests from the same IP, the 6th should return 429."""
        from app.core.rate_limit import RateLimiter

        limiter = RateLimiter(max_requests=5, window_seconds=60)

        # Simulate 5 allowed requests
        for _ in range(5):
            assert limiter.is_allowed("test-ip") is True

        # 6th request should be blocked
        assert limiter.is_allowed("test-ip") is False

    def test_rate_limiter_check_raises_429(self):
        from app.core.rate_limit import RateLimiter
        from fastapi import HTTPException

        limiter = RateLimiter(max_requests=1, window_seconds=60)
        limiter.check("ip-1")  # First: OK

        with pytest.raises(HTTPException) as exc_info:
            limiter.check("ip-1")  # Second: should raise

        assert exc_info.value.status_code == 429
        assert exc_info.value.detail["error"]["code"] == "RATE_LIMITED"

    def test_different_ips_independent_windows(self):
        from app.core.rate_limit import RateLimiter

        limiter = RateLimiter(max_requests=2, window_seconds=60)
        assert limiter.is_allowed("ip-A") is True
        assert limiter.is_allowed("ip-A") is True
        assert limiter.is_allowed("ip-A") is False  # A exhausted
        assert limiter.is_allowed("ip-B") is True   # B still fresh


# ===========================================================================
# Sanitisation unit tests
# ===========================================================================

class TestSanitization:
    def test_strip_html_removes_script_tags(self):
        from app.utils.sanitize import strip_html
        result = strip_html("<script>alert('xss')</script>Hello")
        assert "<script>" not in result
        assert "Hello" in result

    def test_strip_html_removes_img_tags(self):
        from app.utils.sanitize import strip_html
        result = strip_html('<img src="x" onerror="alert(1)">Safe Text')
        assert "<img" not in result
        assert "Safe Text" in result

    def test_sanitize_text_escapes_entities(self):
        from app.utils.sanitize import sanitize_text
        result = sanitize_text("<b>Bold & Dangerous</b>")
        assert "<b>" not in result

    def test_has_injection_attempt_detects_script(self):
        from app.utils.sanitize import has_injection_attempt
        assert has_injection_attempt("<script>evil()</script>") is True
        assert has_injection_attempt("Normal message text") is False
        assert has_injection_attempt("javascript:void(0)") is True

    def test_sanitize_enquiry_fields_returns_clean(self):
        from app.utils.sanitize import sanitize_enquiry_fields
        result = sanitize_enquiry_fields(
            name="  <b>John</b>  ",
            email="  john@example.com  ",
            message="<p>Please help me.</p>",
        )
        assert "<b>" not in result["name"]
        assert "<p>" not in result["message"]
