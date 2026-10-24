from sqlalchemy.orm import Session
from app.core.security import get_password_hash
from app.models.admin_user import AdminUser

def init_db(db: Session) -> None:
    admin = db.query(AdminUser).filter(AdminUser.email == "admin@brainmint.com").first()
    if not admin:
        default_admin = AdminUser(
            email="admin@brainmint.com",
            hashed_password=get_password_hash("Admin@12345"),
            is_active=True
        )
        db.add(default_admin)
        db.commit()
        print("Default admin user created successfully.")
    else:
        print("Admin user already exists.")