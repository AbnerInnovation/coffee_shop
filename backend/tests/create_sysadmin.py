"""
Script to create a SYSADMIN user

Usage:
    SYSADMIN_EMAIL=admin@example.com SYSADMIN_PASSWORD=yourpassword python create_sysadmin.py
"""
import os
import sys
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.user import User, UserRole
from app.models.restaurant import Restaurant  # Import to resolve relationship
from app.core.security import get_password_hash

def create_sysadmin():
    """Create a SYSADMIN user"""
    # Get credentials from environment variables
    email = os.getenv("SYSADMIN_EMAIL")
    password = os.getenv("SYSADMIN_PASSWORD")
    
    if not email or not password:
        print("❌ Error: SYSADMIN_EMAIL and SYSADMIN_PASSWORD environment variables are required")
        print("\nUsage:")
        print("  SYSADMIN_EMAIL=admin@example.com SYSADMIN_PASSWORD=yourpassword python create_sysadmin.py")
        sys.exit(1)
    
    db: Session = SessionLocal()
    
    try:
        # Check if sysadmin already exists
        existing_sysadmin = db.query(User).filter(
            User.email == email
        ).first()
        
        if existing_sysadmin:
            print(f"❌ SYSADMIN user already exists with email: {email}")
            print(f"   User ID: {existing_sysadmin.id}")
            print(f"   Role: {existing_sysadmin.role}")
            return
        
        # Create new sysadmin user
        sysadmin_user = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name="System Administrator",
            role=UserRole.SYSADMIN,
            is_active=True,
            restaurant_id=None  # SYSADMIN is not tied to a specific restaurant
        )
        
        db.add(sysadmin_user)
        db.commit()
        
        # Get the ID before refresh to avoid enum mismatch issue
        user_id = sysadmin_user.id
        
        print("✅ SYSADMIN user created successfully!")
        print(f"   Email: {email}")
        print(f"   Role: SYSADMIN")
        print(f"   User ID: {user_id}")
        print("\n⚠️  IMPORTANT: Store credentials securely and change the password after first login!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating SYSADMIN user: {str(e)}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Creating SYSADMIN user...")
    create_sysadmin()
