from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.models.admin_user import AdminUser

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/admin/auth/login")

def get_current_active_admin(
    token: str = Depends(oauth2_scheme), 
    db: Session = Depends(get_db)
) -> AdminUser:
    """
    Validates the JWT access token and returns the current active admin user.
    Krishna will use this dependency to protect admin content CRUD routes.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[getattr(settings, "ALGORITHM", "HS256")]
        )
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(AdminUser).filter(AdminUser.email == email).first()
    if user is None:
        raise credentials_exception
        
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=400, detail="Inactive admin user")
        
    return user

# Alias to maintain compatibility if referenced anywhere else
get_current_admin_user = get_current_active_admin