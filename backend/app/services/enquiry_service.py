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
        background_tasks: Optional[BackgroundTasks] = None,
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
        new_enquiry, is_duplicate = enquiry_crud.create(
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
            return new_enquiry, True

        # ------------------------------------------------------------------
        # Step 4 – Trigger notifications asynchronously (save first → email second)
        # ------------------------------------------------------------------
        if background_tasks is not None:
            background_tasks.add_task(email_service, new_enquiry.id)

        return new_enquiry, False


enquiry_service = EnquiryService()
