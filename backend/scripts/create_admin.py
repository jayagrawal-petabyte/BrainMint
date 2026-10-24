import sys
from pathlib import Path

# Add backend directory to python path if running from root
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.admin_user import AdminUser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_initial_admin():
    db = SessionLocal()
    try:
        admin_email = "admin@brainmint.com"
        existing_admin = db.query(AdminUser).filter(AdminUser.email == admin_email).first()
        
        if existing_admin:
            print(f"Admin user {admin_email} already exists!")
            return

        hashed_password = pwd_context.hash("Admin@12345")
        new_admin = AdminUser(
            email=admin_email,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(new_admin)
        db.commit()
        print(f"Successfully created initial admin user: {admin_email} / Admin@12345")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_admin()