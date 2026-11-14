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
from typing import Optional

from fastapi import BackgroundTasks
from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.crud.enquiry import enquiry_crud
from app.models.enquiry import Enquiry, EnquirySource
from app.services.captcha_service import CaptchaVerificationError, captcha_service
from app.services.email_service import EmailDeliveryError, email_service
from app.utils.sanitize import sanitize_enquiry_fields, has_injection_attempt

logger = logging.getLogger(__name__)


def _deliver_enquiry_emails(
    enquiry_id: int,
    fallback_db: Optional[Session] = None,
    use_fallback_first: bool = False,
) -> None:
    """
    Runs inside FastAPI BackgroundTasks after the HTTP response is sent.
    In pytest (where fallback_db uses a separate test engine), updates
    fallback_db directly; in production, opens a fresh SessionLocal().
    """
    email_error: Optional[str] = None
    try:
        email_service.send_enquiry_notification(enquiry_id)
        email_service.send_enquiry_acknowledgement(enquiry_id)
    except EmailDeliveryError as exc:
        email_error = str(exc)
        logger.error("Email delivery failed for enquiry #%d: %s", enquiry_id, exc)
    except Exception as exc:
        email_error = str(exc)
        logger.exception("Unexpected error delivering email for enquiry #%d", enquiry_id)

    if use_fallback_first and fallback_db is not None:
        try:
            bg_enquiry = fallback_db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
            if bg_enquiry:
                if email_error:
                    enquiry_crud.mark_email_failed(fallback_db, bg_enquiry, email_error)
                else:
                    enquiry_crud.mark_email_sent(fallback_db, bg_enquiry)
                return
        except Exception:
            fallback_db.rollback()

    db = SessionLocal()
    try:
        bg_enquiry = db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()
        if bg_enquiry:
            if email_error:
                enquiry_crud.mark_email_failed(db, bg_enquiry, email_error)
            else:
                enquiry_crud.mark_email_sent(db, bg_enquiry)
    except Exception as db_exc:
        db.rollback()
        logger.error(
            "Failed to update email_status for enquiry #%d: %s", enquiry_id, db_exc
        )
    finally:
        db.close()


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
        background_tasks: Optional[BackgroundTasks] = None,
    ) -> tuple[Enquiry, bool]:
        clean = sanitize_enquiry_fields(
            name=name,
            email=email,
            phone=phone,
            service=service,
            message=message,
        )

        for field, value in clean.items():
            if value and has_injection_attempt(str(value)):
                logger.warning(
                    "Possible injection attempt in field '%s' from IP %s",
                    field,
                    ip_address,
                )

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

        if is_duplicate:
            return enquiry, True

        # Detect if db comes from a test override engine (e.g., pytest StaticPool SQLite)
        use_fallback_first = db.get_bind() is not SessionLocal.kw.get("bind")

        if background_tasks is not None:
            background_tasks.add_task(
                _deliver_enquiry_emails, enquiry.id, db, use_fallback_first
            )
        else:
            _deliver_enquiry_emails(enquiry.id, db, use_fallback_first)

        return enquiry, False


enquiry_service = EnquiryService()
