"""
Quick script to check restaurants in database
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db.base import SessionLocal
from app.models import Restaurant

db = SessionLocal()

try:
    restaurants = db.query(Restaurant).all()
    
    print(f"\n{'='*60}")
    print(f"📊 RESTAURANTS IN DATABASE")
    print(f"{'='*60}\n")
    
    if not restaurants:
        print("❌ No restaurants found in database!")
        print("\n💡 You need to create a restaurant first.")
        print("   Options:")
        print("   1. Register through the frontend (/register)")
        print("   2. Create one manually in the database")
    else:
        print(f"✅ Found {len(restaurants)} restaurant(s):\n")
        for r in restaurants:
            print(f"  • ID: {r.id}")
            print(f"    Name: {r.name}")
            print(f"    Subdomain: {r.subdomain}")
            print(f"    Email: {r.email}")
            print(f"    Active: {r.is_active}")
            print(f"    Deleted: {'Yes' if r.deleted_at else 'No'}")
            print()
    
    print(f"{'='*60}\n")
    
finally:
    db.close()
