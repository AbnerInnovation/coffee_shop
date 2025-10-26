"""
Script to populate order_number for existing orders that don't have it.
Run this after the migration if there are orders with NULL order_number.
"""
from sqlalchemy import create_engine, text
from app.core.config import settings

def populate_order_numbers():
    """Populate order_number for orders that have NULL values."""
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        # Start transaction
        trans = conn.begin()
        
        try:
            # Update orders with NULL order_number
            result = conn.execute(text("""
                UPDATE orders o
                JOIN (
                    SELECT o1.id, 
                           (SELECT COUNT(*) 
                            FROM orders o2 
                            WHERE o2.restaurant_id = o1.restaurant_id 
                            AND o2.created_at <= o1.created_at) as row_num
                    FROM orders o1
                    WHERE o1.order_number IS NULL
                ) as temp ON o.id = temp.id
                SET o.order_number = temp.row_num
            """))
            
            rows_updated = result.rowcount
            print(f"✅ Updated {rows_updated} orders with order_number")
            
            # Commit transaction
            trans.commit()
            print("✅ Transaction committed successfully")
            
        except Exception as e:
            trans.rollback()
            print(f"❌ Error: {e}")
            print("Transaction rolled back")
            raise

if __name__ == "__main__":
    print("Starting order_number population...")
    populate_order_numbers()
    print("Done!")
