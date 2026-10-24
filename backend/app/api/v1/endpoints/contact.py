"""
POST /api/v1/contact  – Contact Us Form (SCR-008)

Identical anti-spam stack to /api/v1/enquiries:
  1. Rate limiting     – 5 requests per IP per 60 s
  2. Honeypot field    – validated inside the Pydantic schema
  3. CAPTCHA           – hCaptcha / reCAPTCHA via captcha_service
  4. Server-side validation – Pydantic with field-level errors (SCR-014)
  5. Input sanitisation – HTML/XSS stripping before DB write

The contact form does not require a service selection and uses
EnquirySource.contact_us so admin can filter by origin.
"""

from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.core.rate_limit import enquiry_limiter, get_client_ip
from app.models.enquiry import EnquirySource
from app.schemas.enquiry import ContactEnquiryCreate
from app.services.enquiry_service import enquiry_service

router = APIRouter()


def _format_validation_errors(exc: ValidationError) -> JSONResponse:
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
    summary="Submit a contact-us enquiry (SCR-008)",
    response_description="Message received successfully",
    status_code=status.HTTP_201_CREATED,
)
async def submit_contact_enquiry(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    **POST /api/v1/contact**

    Accepts the Contact Us form payload.  No service selection required.
    Returns a consistent success envelope (SCR-013) on success, or a
    field-level error envelope (SCR-014) on validation failure.
    """
    client_ip = get_client_ip(request)
    enquiry_limiter.check(client_ip)

    try:
        raw = await request.json()
        payload = ContactEnquiryCreate(**raw)
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

    enquiry, is_duplicate = enquiry_service.process_submission(
        db,
        name=payload.name,
        email=str(payload.email),
        phone=payload.phone,
        service=None,            # Contact Us has no service field
        message=payload.message,
        source=EnquirySource.contact_us,
        ip_address=client_ip,
        captcha_token=payload.captcha_token,
    )

    http_status = status.HTTP_200_OK if is_duplicate else status.HTTP_201_CREATED
    return JSONResponse(
        status_code=http_status,
        content={
            "success": True,
            "message": (
                "We've already got your message and will be in touch shortly."
                if is_duplicate
                else "Thanks for reaching out! We'll get back to you within 24 hours."
            ),
            "data": {
                "enquiry_id": enquiry.id,
                "email_status": enquiry.email_status.value,
            },
        },
    )
