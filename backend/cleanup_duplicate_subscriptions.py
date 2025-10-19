"""
Script to clean up duplicate subscriptions for restaurants.
Keeps only the most recent active/trial subscription per restaurant.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.restaurant_subscription import RestaurantSubscription, SubscriptionStatus
from datetime import datetime

# Create database connection
engine = create_engine(settings.DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def cleanup_duplicate_subscriptions():
    """Clean up duplicate subscriptions, keeping only the most recent one per restaurant"""
    db = SessionLocal()
    try:
        # Get all restaurants with multiple active/trial subscriptions
        from sqlalchemy import func
        
        # Find restaurants with multiple subscriptions
        duplicates = db.query(
            RestaurantSubscription.restaurant_id,
            func.count(RestaurantSubscription.id).label('count')
        ).filter(
            RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
        ).group_by(
            RestaurantSubscription.restaurant_id
        ).having(
            func.count(RestaurantSubscription.id) > 1
        ).all()
        
        print(f"Found {len(duplicates)} restaurants with duplicate subscriptions")
        
        total_cancelled = 0
        
        for restaurant_id, count in duplicates:
            print(f"\nRestaurant ID {restaurant_id} has {count} subscriptions")
            
            # Get all subscriptions for this restaurant
            subscriptions = db.query(RestaurantSubscription).filter(
                RestaurantSubscription.restaurant_id == restaurant_id,
                RestaurantSubscription.status.in_([SubscriptionStatus.TRIAL, SubscriptionStatus.ACTIVE])
            ).order_by(RestaurantSubscription.created_at.desc()).all()
            
            # Keep the most recent one
            keep_subscription = subscriptions[0]
            print(f"  Keeping subscription ID {keep_subscription.id} (Plan: {keep_subscription.plan.display_name}, Created: {keep_subscription.created_at})")
            
            # Cancel the rest
            for sub in subscriptions[1:]:
                print(f"  Cancelling subscription ID {sub.id} (Plan: {sub.plan.display_name}, Created: {sub.created_at})")
                sub.status = SubscriptionStatus.CANCELLED
                sub.cancelled_at = datetime.utcnow()
                total_cancelled += 1
        
        # Commit changes
        db.commit()
        print(f"\n✅ Successfully cancelled {total_cancelled} duplicate subscriptions")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🧹 Starting cleanup of duplicate subscriptions...\n")
    cleanup_duplicate_subscriptions()
    print("\n✨ Cleanup complete!")
