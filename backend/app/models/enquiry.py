"""
Enquiry database model.

Stores every inbound lead from both the Service Enquiry Form (SCR-012)
and the Contact Us form (SCR-008).  The enquiry is always persisted first;
email delivery is attempted afterward so no lead is ever lost.
"""

import enum
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SAEnum
from sqlalchemy.sql import func
from app.models.base import Base


class EnquirySource(str, enum.Enum):
    """Which frontend form originated this enquiry."""
    service_enquiry = "service_enquiry"   # SCR-012
    contact_us = "contact_us"            # SCR-008


class EnquiryStatus(str, enum.Enum):
    """Lifecycle / CRM status that an admin can update."""
    new = "new"
    in_review = "in_review"
    contacted = "contacted"
    converted = "converted"
    closed = "closed"


class EmailStatus(str, enum.Enum):
    """Tracks whether the notification email was sent successfully."""
    pending = "pending"
    sent = "sent"
    failed = "failed"


# Canonical service slugs – must match the 4 seeded services in seed_content.py.
APPROVED_SERVICES = frozenset({
    "website-development",
    "application-development",
    "ai-agent-development",
    "offshore-development-team",
})


class Enquiry(Base):
    __tablename__ = "enquiries"

    id = Column(Integer, primary_key=True, index=True)

    # ---------- Contact fields ----------
    name = Column(String(150), nullable=False)
    email = Column(String(254), nullable=False, index=True)
    phone = Column(String(20), nullable=True)          # E.164 optional

    # ---------- Enquiry content ----------
    # NULL for contact-us form; required for service-enquiry form.
    service = Column(String(100), nullable=True, index=True)
    message = Column(Text, nullable=False)

    # ---------- Form metadata ----------
    source = Column(
        SAEnum(EnquirySource, name="enquiry_source_enum"),
        nullable=False,
        index=True,
    )

    # ---------- CRM status ----------
    status = Column(
        SAEnum(EnquiryStatus, name="enquiry_status_enum"),
        nullable=False,
        default=EnquiryStatus.new,
        index=True,
    )

    # ---------- Email delivery ----------
    email_status = Column(
        SAEnum(EmailStatus, name="email_status_enum"),
        nullable=False,
        default=EmailStatus.pending,
    )
    email_error = Column(Text, nullable=True)  # last error message if failed

    # ---------- Anti-spam / audit ----------
    ip_address = Column(String(45), nullable=True, index=True)   # IPv4 or IPv6
    idempotency_key = Column(String(64), nullable=True, unique=True, index=True)

    # ---------- Timestamps ----------
    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False, index=True
    )
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
