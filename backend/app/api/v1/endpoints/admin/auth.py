from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext

from app.core.config import settings
from app.core.database import get_db
from app.core.security import verify_password, create_access_token, create_refresh_token
from app.models.admin_user import AdminUser
from app.api.deps import get_current_active_admin

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class LoginRequest(BaseModel):
    email: str
    password: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

class ForgotPasswordRequest(BaseModel):
    email: EmailStr

class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


@router.post("/login")
def admin_login(form_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate admin user and return access & refresh tokens.
    """
    user = db.query(AdminUser).filter(AdminUser.email == form_data.email).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=400, detail="Inactive admin user")
    
    access_token = create_access_token(data={"sub": user.email, "type": "access"})
    refresh_token = create_refresh_token(data={"sub": user.email, "type": "refresh"})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh")
def refresh_access_token(payload_data: RefreshTokenRequest):
    """
    Issues a new access token using a valid refresh token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token",
    )
    try:
        payload = jwt.decode(
            payload_data.refresh_token, 
            settings.SECRET_KEY, 
            algorithms=[getattr(settings, "ALGORITHM", "HS256")]
        )
        if payload.get("type") != "refresh":
            raise credentials_exception
            
        email: str = payload.get("sub")
        if not email:
            raise credentials_exception
            
        access_token_expires = timedelta(minutes=getattr(settings, "ACCESS_TOKEN_EXPIRE_MINUTES", 30))
        expire = datetime.utcnow() + access_token_expires
        
        new_access_token = jwt.encode(
            {"sub": email, "exp": expire, "type": "access"}, 
            settings.SECRET_KEY, 
            algorithm=getattr(settings, "ALGORITHM", "HS256")
        )
        return {"access_token": new_access_token, "token_type": "bearer"}
        
    except JWTError:
        raise credentials_exception


@router.post("/logout")
def logout_admin(admin: AdminUser = Depends(get_current_active_admin)):
    """
    Logs out the current authenticated admin.
    """
    return {"message": "Successfully logged out. Please clear your tokens on the client side."}


@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """
    Generates a password reset token.
    """
    admin = db.query(AdminUser).filter(AdminUser.email == data.email).first()
    if not admin:
        return {"message": "If the email exists, a password reset link has been sent."}
    
    expire = datetime.utcnow() + timedelta(minutes=15)
    reset_token = jwt.encode(
        {"sub": admin.email, "exp": expire, "type": "reset"}, 
        settings.SECRET_KEY, 
        algorithm=getattr(settings, "ALGORITHM", "HS256")
    )
    
    # Note: You can trigger your email service here to dispatch reset_token to admin.email
    return {"message": "Password reset link sent to email.", "debug_reset_token": reset_token}


@router.post("/reset-password")
def reset_password(data: ResetPasswordRequest, db: Session = Depends(get_db)):
    """
    Resets the admin password using the provided reset token.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Invalid or expired password reset token",
    )
    try:
        payload = jwt.decode(
            data.token, 
            settings.SECRET_KEY, 
            algorithms=[getattr(settings, "ALGORITHM", "HS256")]
        )
        if payload.get("type") != "reset":
            raise credentials_exception
            
        email: str = payload.get("sub")
        admin = db.query(AdminUser).filter(AdminUser.email == email).first()
        if not admin:
            raise credentials_exception
            
        admin.hashed_password = pwd_context.hash(data.new_password)
        db.commit()
        
        return {"message": "Password has been successfully reset."}
        
    except JWTError:
        raise credentials_exception