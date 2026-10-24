"""
Pydantic schemas for the enquiry feature.

Response shapes follow the site-wide convention:
  success  → { "success": true,  "data": {...},  "message": "..." }
  error    → { "success": false, "error": { "code": ..., "message": ..., "details": [...] } }
"""

import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator, model_validator

from app.models.enquiry import APPROVED_SERVICES, EmailStatus, EnquirySource, EnquiryStatus


# ---------------------------------------------------------------------------
# Shared validation helpers
# ---------------------------------------------------------------------------

# E.164-ish: optional leading +, 7-15 digits, optional spaces/dashes/dots
_PHONE_RE = re.compile(r"^\+?[\d\s\-.(]{7,20}$")


def _clean(s: str) -> str:
    """Strip surrounding whitespace."""
    return s.strip()


# ---------------------------------------------------------------------------
# Service Enquiry form (SCR-012) — POST /api/enquiries
# ---------------------------------------------------------------------------

class ServiceEnquiryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    service: str = Field(..., description="One of the 4 approved service slugs")
    message: str = Field(..., min_length=10, max_length=3000)

    # Anti-spam fields
    captcha_token: str = Field(..., description="hCaptcha / reCAPTCHA response token")
    honeypot: Optional[str] = Field(None, description="Must be empty – bot trap")

    @field_validator("name", "message", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return _clean(v) if isinstance(v, str) else v

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        v = _clean(v)
        if not _PHONE_RE.match(v):
            raise ValueError(
                "Phone number must be 7–20 characters and contain only digits, "
                "spaces, dashes, dots, parentheses, or a leading '+'."
            )
        return v

    @field_validator("service", mode="before")
    @classmethod
    def validate_service(cls, v: str) -> str:
        v = _clean(v).lower()
        if v not in APPROVED_SERVICES:
            raise ValueError(
                f"Service must be one of: {', '.join(sorted(APPROVED_SERVICES))}."
            )
        return v

    @model_validator(mode="after")
    def check_honeypot(self) -> "ServiceEnquiryCreate":
        if self.honeypot:
            # Silently reject – looks like a bot submission
            raise ValueError("Bot submission detected.")
        return self


# ---------------------------------------------------------------------------
# Contact Us form (SCR-008) — POST /api/contact
# ---------------------------------------------------------------------------

class ContactEnquiryCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=20)
    message: str = Field(..., min_length=10, max_length=3000)

    # Anti-spam
    captcha_token: str = Field(..., description="hCaptcha / reCAPTCHA response token")
    honeypot: Optional[str] = Field(None, description="Must be empty – bot trap")

    @field_validator("name", "message", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        return _clean(v) if isinstance(v, str) else v

    @field_validator("phone", mode="before")
    @classmethod
    def validate_phone(cls, v: Optional[str]) -> Optional[str]:
        if v is None or v == "":
            return None
        v = _clean(v)
        if not _PHONE_RE.match(v):
            raise ValueError(
                "Phone number must be 7–20 characters and contain only digits, "
                "spaces, dashes, dots, parentheses, or a leading '+'."
            )
        return v

    @model_validator(mode="after")
    def check_honeypot(self) -> "ContactEnquiryCreate":
        if self.honeypot:
            raise ValueError("Bot submission detected.")
        return self


# ---------------------------------------------------------------------------
# Admin update schema
# ---------------------------------------------------------------------------

class EnquiryStatusUpdate(BaseModel):
    status: EnquiryStatus


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

class EnquiryResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: Optional[str]
    service: Optional[str]
    message: str
    source: EnquirySource
    status: EnquiryStatus
    email_status: EmailStatus
    ip_address: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class EnquiryListResponse(BaseModel):
    id: int
    name: str
    email: str
    service: Optional[str]
    source: EnquirySource
    status: EnquiryStatus
    email_status: EmailStatus
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# ---------------------------------------------------------------------------
# Standard API envelope shapes (SCR-013 / SCR-014)
# ---------------------------------------------------------------------------

class FieldError(BaseModel):
    field: str
    message: str


class SuccessEnvelope(BaseModel):
    success: bool = True
    message: str
    data: Optional[dict] = None


class ErrorEnvelope(BaseModel):
    success: bool = False
    error: dict
