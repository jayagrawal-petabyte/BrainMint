"""
Admin endpoints for enquiry management.

All routes are protected by get_current_admin_user (JWT auth provided by Ashutosh).

Routes:
  GET    /admin/enquiries            – List with filters + pagination
  GET    /admin/enquiries/export     – CSV export
  GET    /admin/enquiries/{id}       – Detail view
  PATCH  /admin/enquiries/{id}/status – Update CRM status
"""

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from fastapi.responses import JSONResponse, Response
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_admin_user
from app.core.rate_limit import admin_enquiry_limiter, get_client_ip
from app.crud.enquiry import enquiry_crud
from app.models.enquiry import EmailStatus, EnquirySource, EnquiryStatus
from app.schemas.enquiry import EnquiryListResponse, EnquiryResponse, EnquiryStatusUpdate
from fastapi import Request, status

router = APIRouter()


@router.get(
    "",
    summary="List enquiries with filters and pagination",
    response_model=None,  # Returning envelope manually for consistency
)
def admin_list_enquiries(
    request: Request,
    source: Optional[EnquirySource] = Query(None, description="Filter by form source"),
    enquiry_status: Optional[EnquiryStatus] = Query(None, alias="status", description="Filter by CRM status"),
    email_status: Optional[EmailStatus] = Query(None, description="Filter by email delivery status"),
    search: Optional[str] = Query(None, max_length=100, description="Search name, email, or message"),
    date_from: Optional[datetime] = Query(None, description="ISO 8601 start date filter"),
    date_to: Optional[datetime] = Query(None, description="ISO 8601 end date filter"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    """
    Return paginated enquiry list with optional filters.
    Supports filtering by source, CRM status, email status, free-text search,
    and date range.
    """
    skip = (page - 1) * page_size
    items, total = enquiry_crud.list_admin(
        db,
        source=source,
        status=enquiry_status,
        email_status=email_status,
        search=search,
        date_from=date_from,
        date_to=date_to,
        skip=skip,
        limit=page_size,
    )

    return {
        "success": True,
        "data": {
            "items": [EnquiryListResponse.model_validate(e).model_dump() for e in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size,
        },
    }


@router.get(
    "/export",
    summary="Export enquiries to CSV",
    response_class=Response,
)
def admin_export_enquiries_csv(
    source: Optional[EnquirySource] = Query(None),
    enquiry_status: Optional[EnquiryStatus] = Query(None, alias="status"),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    """
    Stream all matching enquiries as a CSV file download.
    Apply the same filters as the list endpoint.
    Hard-capped at 10,000 rows to protect memory.
    """
    csv_content = enquiry_crud.export_csv(
        db,
        source=source,
        status=enquiry_status,
        date_from=date_from,
        date_to=date_to,
    )
    filename = f"enquiries_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get(
    "/{enquiry_id}",
    summary="Get enquiry detail",
    response_model=None,
)
def admin_get_enquiry(
    enquiry_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    """Return the full detail of a single enquiry including email_error."""
    enquiry = enquiry_crud.get_or_404(db, enquiry_id)
    return {
        "success": True,
        "data": EnquiryResponse.model_validate(enquiry).model_dump(),
    }


@router.patch(
    "/{enquiry_id}/status",
    summary="Update the CRM status of an enquiry",
    response_model=None,
)
def admin_update_enquiry_status(
    enquiry_id: int,
    payload: EnquiryStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_admin_user),
):
    """
    Update the CRM status of an enquiry.
    Valid transitions: new → in_review → contacted → converted | closed
    """
    enquiry = enquiry_crud.get_or_404(db, enquiry_id)
    updated = enquiry_crud.update_status(db, enquiry, payload.status)
    return {
        "success": True,
        "message": f"Enquiry #{enquiry_id} status updated to '{payload.status.value}'.",
        "data": EnquiryResponse.model_validate(updated).model_dump(),
    }
