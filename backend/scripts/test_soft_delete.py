"""
Test script to verify soft delete functionality.
"""
import sys
import os
from datetime import datetime

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.base import Base

def test_soft_delete():
    # Create test database tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Create a test user
        test_email = f"test_{int(datetime.utcnow().timestamp())}@example.com"
        user = User(
            email=test_email,
            hashed_password="test_password",
            full_name="Test User",
            role=UserRole.CUSTOMER
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"Created test user with ID: {user.id}")
        
        # Test soft delete
        print("\nTesting soft delete...")
        user.soft_delete()
        db.commit()
        
        # Verify user is marked as deleted
        deleted_user = db.query(User).filter(User.id == user.id).first()
        print(f"User deleted_at after soft delete: {deleted_user.deleted_at}")
        
        # Test that user is not returned by default query
        users = db.query(User).all()
        user_ids = [u.id for u in users]
        print(f"Users in default query: {user_ids}")
        print(f"Is test user in default query? {user.id in user_ids}")
        
        # Test with_deleted query
        all_users = db.query(User).execution_options(include_deleted=True).all()
        all_user_ids = [u.id for u in all_users]
        print(f"\nAll users (including deleted): {all_user_ids}")
        print(f"Is test user in all users query? {user.id in all_user_ids}")
        
        # Test restore
        print("\nTesting restore...")
        user.restore()
        db.commit()
        
        # Verify user is no longer marked as deleted
        restored_user = db.query(User).filter(User.id == user.id).first()
        print(f"User deleted_at after restore: {restored_user.deleted_at}")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        # Clean up
        db.close()
        print("\nTest completed.")

if __name__ == "__main__":
    test_soft_delete()
