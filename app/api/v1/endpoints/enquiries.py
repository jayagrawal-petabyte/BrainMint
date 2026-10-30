"""
POST /api/v1/enquiries  – Service Enquiry Form (SCR-012)

Anti-spam stack (applied in order):
  1. Rate limiting     – 5 requests per IP per 60 s
  2. Honeypot field    – validated inside the Pydantic schema
  3. CAPTCHA           – hCaptcha / reCAPTCHA via captcha_service
  4. Server-side validation – Pydantic with field-level errors (SCR-014)
  5. Input sanitisation – HTML/XSS stripping before DB write
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.rate_limit import enquiry_limiter, get_client_ip
from app.models.enquiry import EnquirySource
from app.schemas.enquiry import ServiceEnquiryCreate, EnquiryResponse
from app.services.enquiry_service import enquiry_service

router = APIRouter()


def _format_validation_errors(exc: ValidationError) -> JSONResponse:
    """
    Convert Pydantic v2 ValidationError into the SCR-014 field-level error envelope.
    """
    details = []
    for err in exc.errors(include_url=False):
        field = ".".join(str(loc) for loc in err["loc"]) if err["loc"] else "body"
        details.append({"field": field, "message": err["msg"]})

    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "One or more fields failed validation.",
                "details": details,
            },
        },
    )


@router.post(
    "",
    summary="Submit a service enquiry (SCR-012)",
    response_description="Enquiry received successfully",
    status_code=status.HTTP_201_CREATED,
)
async def submit_service_enquiry(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    **POST /api/v1/enquiries**

    Accepts the Service Enquiry Form payload.  Returns a consistent
    success envelope (SCR-013) on success, or a field-level error
    envelope (SCR-014) on validation failure.

    Anti-spam: rate-limited per IP, honeypot field checked inside schema,
    CAPTCHA token verified server-side.
    """
    # --- Rate limit check ---
    client_ip = get_client_ip(request)
    enquiry_limiter.check(client_ip)

    # --- Parse & validate body ---
    try:
        raw = await request.json()
        payload = ServiceEnquiryCreate(**raw)
    except ValidationError as exc:
        return _format_validation_errors(exc)
    except Exception:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "Request body must be valid JSON.",
                    "details": None,
                },
            },
        )

    # --- Business logic (sanitise → captcha → DB → email) ---
    enquiry, is_duplicate = enquiry_service.process_submission(
        db,
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone,
        service=payload.service,
        message=payload.message,
        source=EnquirySource.service_enquiry,
        ip_address=client_ip,
        captcha_token=payload.captcha_token,
    )

    http_status = status.HTTP_200_OK if is_duplicate else status.HTTP_201_CREATED
    return JSONResponse(
        status_code=http_status,
        content={
            "success": True,
            "message": (
                "Your enquiry has already been received. We'll be in touch shortly."
                if is_duplicate
                else "Thank you! We've received your enquiry and will get back to you within 24 hours."
            ),
            "data": {
                "enquiry_id": enquiry.id,
                "email_status": enquiry.email_status.value,
            },
        },
    )
