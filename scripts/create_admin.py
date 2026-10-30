import sys
import getpass
import argparse
from pathlib import Path

# Add backend directory to python path if running from root
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.models.admin_user import AdminUser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_initial_admin():
    parser = argparse.ArgumentParser(description="Create a secure admin user.")
    parser.add_argument("email", type=str, help="Admin email address")
    args = parser.parse_args()

    admin_email = args.email
    password = getpass.getpass("Enter admin password (min 10 characters): ")
    
    if len(password) < 10:
        print("Error: Password must be at least 10 characters long.")
        sys.exit(1)

    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.email == admin_email).first()
        if admin:
            print(f"Admin user {admin_email} already exists!")
            return

        hashed_password = pwd_context.hash(password)
        new_admin = AdminUser(
            email=admin_email,
            hashed_password=hashed_password,
            is_active=True
        )
        db.add(new_admin)
        db.commit()
        print(f"Successfully created admin user: {admin_email}")
        
    except Exception as e:
        db.rollback()
        print(f"Error creating admin: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    create_initial_admin()