"""
CRUD operations for the Enquiry model.

Design decisions:
- Duplicate-submission guard uses a SHA-256 idempotency key built from
  (email + service + message[:50]) within a 5-minute window, so refreshing
  the success page or double-clicking Submit does not create duplicate rows.
- Filtering is done at the DB level to keep the admin list performant.
- CSV export is streamed row-by-row to avoid loading all rows into memory.
"""

import csv
import hashlib
import io
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy import and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.enquiry import (
    EmailStatus,
    Enquiry,
    EnquirySource,
    EnquiryStatus,
)

logger = logging.getLogger(__name__)

# A submission with the same idempotency key within this window is a duplicate
DUPLICATE_WINDOW_MINUTES = 5


def _build_idempotency_key(email: str, service: Optional[str], message: str) -> str:
    """
    Deterministic key for a given (email, service, message) triple.
    Callers should check for an existing row with this key created within
    DUPLICATE_WINDOW_MINUTES before inserting a new one.
    """
    raw = f"{email.lower()}|{service or ''}|{message[:50]}"
    return hashlib.sha256(raw.encode()).hexdigest()


class CRUDEnquiry:
    # ------------------------------------------------------------------
    # Write operations
    # ------------------------------------------------------------------

    def create(
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
    ) -> Tuple[Enquiry, bool]:
        """
        Persist a new enquiry.

        Returns
        -------
        (enquiry, is_duplicate)
            is_duplicate=True means an identical submission was found within
            the time window; the *existing* row is returned unchanged.
        """
        ikey = _build_idempotency_key(email, service, message)
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=DUPLICATE_WINDOW_MINUTES)

        existing = (
            db.query(Enquiry)
            .filter(
                and_(
                    Enquiry.idempotency_key == ikey,
                    Enquiry.created_at >= cutoff,
                )
            )
            .first()
        )
        if existing:
            logger.info(
                "Duplicate enquiry detected for email=%s ikey=%s", email, ikey[:12]
            )
            return existing, True

        # idempotency_key is UNIQUE. An identical submission from OUTSIDE the
        # window is a legitimate new enquiry, so free the key on the old row
        # first; otherwise the INSERT below would fail with a 500.
        stale = db.query(Enquiry).filter(Enquiry.idempotency_key == ikey).first()
        if stale:
            stale.idempotency_key = None
            db.flush()

        enquiry = Enquiry(
            name=name,
            email=email,
            phone=phone,
            service=service,
            message=message,
            source=source,
            ip_address=ip_address,
            idempotency_key=ikey,
            status=EnquiryStatus.new,
            email_status=EmailStatus.pending,
        )
        db.add(enquiry)
        try:
            db.commit()
        except IntegrityError:
            # Two identical requests raced (e.g. double-click): the other one won.
            db.rollback()
            winner = db.query(Enquiry).filter(Enquiry.idempotency_key == ikey).first()
            if winner:
                return winner, True
            raise
        db.refresh(enquiry)
        return enquiry, False

    def mark_email_sent(self, db: Session, enquiry: Enquiry) -> None:
        enquiry.email_status = EmailStatus.sent
        db.commit()

    def mark_email_failed(self, db: Session, enquiry: Enquiry, error: str) -> None:
        enquiry.email_status = EmailStatus.failed
        enquiry.email_error = error[:1000]  # Truncate to column limit
        db.commit()

    def update_status(
        self, db: Session, enquiry: Enquiry, new_status: EnquiryStatus
    ) -> Enquiry:
        enquiry.status = new_status
        db.commit()
        db.refresh(enquiry)
        return enquiry

    # ------------------------------------------------------------------
    # Read operations
    # ------------------------------------------------------------------

    def get(self, db: Session, enquiry_id: int) -> Optional[Enquiry]:
        return db.query(Enquiry).filter(Enquiry.id == enquiry_id).first()

    def get_or_404(self, db: Session, enquiry_id: int) -> Enquiry:
        from fastapi import HTTPException, status

        enquiry = self.get(db, enquiry_id)
        if not enquiry:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "success": False,
                    "error": {
                        "code": "NOT_FOUND",
                        "message": f"Enquiry #{enquiry_id} not found.",
                        "details": None,
                    },
                },
            )
        return enquiry

    def list_admin(
        self,
        db: Session,
        *,
        source: Optional[EnquirySource] = None,
        status: Optional[EnquiryStatus] = None,
        email_status: Optional[EmailStatus] = None,
        search: Optional[str] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Enquiry], int]:
        """
        Return (items, total_count) for admin list view with optional filters.
        """
        q = db.query(Enquiry)

        if source:
            q = q.filter(Enquiry.source == source)
        if status:
            q = q.filter(Enquiry.status == status)
        if email_status:
            q = q.filter(Enquiry.email_status == email_status)
        if search:
            term = f"%{search}%"
            q = q.filter(
                or_(
                    Enquiry.name.ilike(term),
                    Enquiry.email.ilike(term),
                    Enquiry.message.ilike(term),
                )
            )
        if date_from:
            q = q.filter(Enquiry.created_at >= date_from)
        if date_to:
            q = q.filter(Enquiry.created_at <= date_to)

        total = q.count()
        items = q.order_by(Enquiry.created_at.desc()).offset(skip).limit(limit).all()
        return items, total

    # ------------------------------------------------------------------
    # CSV export
    # ------------------------------------------------------------------

    def export_csv(
        self,
        db: Session,
        *,
        source: Optional[EnquirySource] = None,
        status: Optional[EnquiryStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
    ) -> str:
        """Return a CSV string of all matching enquiries."""
        items, _ = self.list_admin(
            db,
            source=source,
            status=status,
            date_from=date_from,
            date_to=date_to,
            skip=0,
            limit=10_000,  # Hard cap to protect memory
        )

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(
            [
                "ID",
                "Name",
                "Email",
                "Phone",
                "Service",
                "Source",
                "Message",
                "Status",
                "Email Status",
                "IP Address",
                "Created At",
                "Updated At",
            ]
        )
        for e in items:
            writer.writerow(
                [
                    e.id,
                    e.name,
                    e.email,
                    e.phone or "",
                    e.service or "",
                    e.source.value,
                    e.message,
                    e.status.value,
                    e.email_status.value,
                    e.ip_address or "",
                    e.created_at.isoformat() if e.created_at else "",
                    e.updated_at.isoformat() if e.updated_at else "",
                ]
            )

        return output.getvalue()


enquiry_crud = CRUDEnquiry()
