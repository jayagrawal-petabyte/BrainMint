from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.core.config import settings
from app.core.database import get_db
from app.models.admin_user import AdminUser
from pydantic import BaseModel, EmailStr

limiter = Limiter(key_func=get_remote_address)
router = APIRouter(prefix="/auth", tags=["Authentication"])

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

@router.post("/login")
@limiter.limit("5/minute")
def admin_login(
    request: Request, 
    form_data: LoginRequest, 
    db: Session = Depends(get_db)
):
    """
    Admin login with IP rate-limiting, database brute-force account lockout, 
    and JWT access/refresh token generation.
    """
    user = db.query(AdminUser).filter(AdminUser.email == form_data.email).first()

    if user:
        # Check if account is locked out due to multiple failed attempts
        if user.locked_until and user.locked_until > datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Account temporarily locked due to multiple failed login attempts. Try again later."
            )

    if not user or not verify_password(form_data.password, user.hashed_password):
        if user:
            user.failed_login_attempts = (user.failed_login_attempts or 0) + 1
            # Lock out for 15 minutes after 5 failed attempts
            if user.failed_login_attempts >= 5:
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Check if user account is active
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=400, detail="Inactive admin user")

    # Reset failed attempts and lockout timer on successful login
    if user.failed_login_attempts or user.locked_until:
        user.failed_login_attempts = 0
        user.locked_until = None
        db.commit()

    # Generate access and refresh tokens
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "type": "access"}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email, "type": "refresh"}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }