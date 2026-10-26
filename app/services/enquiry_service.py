"""
Enquiry business-logic service.

Orchestrates:
  1. Input sanitisation
  2. CAPTCHA verification
  3. Database persistence (always first – no lead is lost)
  4. Email delivery (team notification + customer acknowledgement)
  5. Updating email_status on the DB row

The design principle is: **save first, email second**.
If email fails, the enquiry row is still present in the DB for recovery.
"""

import logging
import threading
from typing import Optional

from sqlalchemy.orm import Session

from app.crud.enquiry import enquiry_crud
from app.models.enquiry import Enquiry, EnquirySource
from app.services.captcha_service import CaptchaVerificationError, captcha_service
from app.services.email_service import EmailDeliveryError, email_service
from app.utils.sanitize import sanitize_enquiry_fields, has_injection_attempt

logger = logging.getLogger(__name__)


class EnquiryService:
    def process_submission(
        self,
        db: Session,
        *,
        name: str,
        email: str,
        phone: Optional[str],
        service: Optional[str],
        message: str,
        source: EnquirySource,
        ip_address: Optional[str],
        captcha_token: Optional[str] = None,
    ) -> tuple[Enquiry, bool]:
        """
        Full enquiry pipeline.

        Returns
        -------
        (enquiry, is_duplicate)
        """
        # ------------------------------------------------------------------
        # Step 1 – Sanitise inputs
        # ------------------------------------------------------------------
        clean = sanitize_enquiry_fields(
            name=name,
            email=email,
            phone=phone,
            service=service,
            message=message,
        )

        # Log injection attempts but don't block (Pydantic already rejected them)
        for field, value in clean.items():
            if value and has_injection_attempt(str(value)):
                logger.warning(
                    "Possible injection attempt in field '%s' from IP %s",
                    field,
                    ip_address,
                )

        # ------------------------------------------------------------------
        # Step 2 – CAPTCHA verification (skipped when CAPTCHA_ENABLED is false)
        # ------------------------------------------------------------------
        from app.core.config import settings

        if getattr(settings, "CAPTCHA_ENABLED", True):
            try:
                captcha_service.verify(captcha_token, ip=ip_address)
            except CaptchaVerificationError as exc:
                from fastapi import HTTPException, status
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail={
                        "success": False,
                        "error": {
                            "code": "CAPTCHA_FAILED",
                            "message": str(exc),
                            "details": [{"field": "captcha_token", "message": str(exc)}],
                        },
                    },
                ) from exc

        # ------------------------------------------------------------------
        # Step 3 – Persist to DB (idempotency guard inside)
        # ------------------------------------------------------------------
        enquiry, is_duplicate = enquiry_crud.create(
            db,
            name=clean["name"],
            email=clean["email"],
            phone=clean["phone"],
            service=clean["service"],
            message=clean["message"],
            source=source,
            ip_address=ip_address,
        )

        # On a duplicate we skip re-sending email
        if is_duplicate:
            return enquiry, True

        # ------------------------------------------------------------------
        # Step 4 – Send emails in a background thread (save first → email second)
        # The HTTP response is returned immediately; email delivery does not
        # block the caller and cannot cause a 500 even if SMTP is down.
        # ------------------------------------------------------------------
        enquiry_id = enquiry.id
        enquiry_cls = enquiry.__class__
        db_lock = threading.Lock()

        def _send_emails():
            email_error: Optional[str] = None
            try:
                email_service.send_enquiry_notification(enquiry_id)
                email_service.send_enquiry_acknowledgement(enquiry_id)
            except EmailDeliveryError as exc:
                email_error = str(exc)
                logger.error(
                    "Email delivery failed for enquiry #%d: %s", enquiry_id, exc
                )

            # ------------------------------------------------------------------
            # Step 5 – Update email_status on the DB row.
            # Re-uses the caller's session so it works in both production and
            # in-memory SQLite test environments (where SessionLocal() would
            # open a separate connection that cannot see the test tables).
            # ------------------------------------------------------------------
            try:
                with db_lock:
                    _bg_enquiry = db.query(enquiry_cls).filter(
                        enquiry_cls.id == enquiry_id
                    ).first()
                    if _bg_enquiry:
                        if email_error:
                            enquiry_crud.mark_email_failed(db, _bg_enquiry, email_error)
                        else:
                            enquiry_crud.mark_email_sent(db, _bg_enquiry)
            except Exception as db_exc:
                logger.error(
                    "Failed to update email_status for enquiry #%d: %s", enquiry_id, db_exc
                )

        t = threading.Thread(target=_send_emails, daemon=True)
        t.start()

        return enquiry, False


enquiry_service = EnquiryService()
