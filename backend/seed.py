from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.base import SessionLocal
from app.models.user import User, UserRole
from app.models.menu import Category, MenuItem, MenuItemVariant
from app.models.table import Table
from app.models.order import Order, OrderStatus
from app.models.order_item import OrderItem
from datetime import datetime, timedelta, timezone
import bcrypt

# Password hashing function
def get_password_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_data() -> None:
    with SessionLocal() as session:
        with session.begin():
            # Check if data already exists
            result = session.execute(select(User).limit(1))
            if result.scalars().first():
                print("Database already seeded!")
                return

            print("Seeding database...")

            # Create admin user
            admin = User(
                email="admin@coffeeshop.com",
                hashed_password=get_password_hash("admin123"),
                full_name="Admin User",
                role=UserRole.ADMIN,
                is_active=True,
            )

            # Create staff user
            staff = User(
                email="staff@coffeeshop.com",
                hashed_password=get_password_hash("staff123"),
                full_name="Staff Member",
                role=UserRole.STAFF,
                is_active=True,
            )

            session.add_all([admin, staff])
            session.flush()

            # Create categories
            categories = [
                Category(name="COFFEE", description="Freshly brewed coffee drinks"),
                Category(name="TEA", description="A selection of fine teas"),
                Category(name="PASTRIES", description="Freshly baked goods"),
                Category(name="SANDWICHES", description="Fresh sandwiches and wraps"),
            ]

            session.add_all(categories)
            session.flush()

            # Create menu items
            menu_items = [
                # Coffee
                MenuItem(
                    name="Espresso",
                    description="A strong black coffee made by forcing steam through ground coffee beans.",
                    price=2.50,
                    category_id=next(c.id for c in categories if c.name == "COFFEE"),
                    is_available=True,
                ),
                MenuItem(
                    name="Cappuccino",
                    description="Espresso with steamed milk and a silky layer of foam.",
                    price=3.50,
                    category_id=next(c.id for c in categories if c.name == "COFFEE"),
                    is_available=True,
                ),
                # Tea
                MenuItem(
                    name="Green Tea",
                    description="Refreshing green tea with antioxidants.",
                    price=2.00,
                    category_id=next(c.id for c in categories if c.name == "TEA"),
                    is_available=True,
                ),
                # Pastries
                MenuItem(
                    name="Croissant",
                    description="Buttery, flaky pastry.",
                    price=2.50,
                    category_id=next(c.id for c in categories if c.name == "PASTRIES"),
                    is_available=True,
                ),
                # Sandwiches
                MenuItem(
                    name="Chicken Pesto Panini",
                    description="Grilled chicken with pesto, mozzarella, and tomatoes on ciabatta.",
                    price=7.50,
                    category_id=next(c.id for c in categories if c.name == "SANDWICHES"),
                    is_available=True,
                ),
            ]

            session.add_all(menu_items)
            session.flush()

            # Add variants to some menu items
            variants = [
                # Espresso variants
                MenuItemVariant(
                    menu_item_id=next(m.id for m in menu_items if m.name == "Espresso"),
                    name="Single",
                    price=2.50,
                    is_available=True,
                ),
                MenuItemVariant(
                    menu_item_id=next(m.id for m in menu_items if m.name == "Espresso"),
                    name="Double",
                    price=3.50,
                    is_available=True,
                ),
                # Cappuccino sizes
                MenuItemVariant(
                    menu_item_id=next(m.id for m in menu_items if m.name == "Cappuccino"),
                    name="Small (8oz)",
                    price=3.50,
                    is_available=True,
                ),
                MenuItemVariant(
                    menu_item_id=next(m.id for m in menu_items if m.name == "Cappuccino"),
                    name="Medium (12oz)",
                    price=4.50,
                    is_available=True,
                ),
                MenuItemVariant(
                    menu_item_id=next(m.id for m in menu_items if m.name == "Cappuccino"),
                    name="Large (16oz)",
                    price=5.50,
                    is_available=True,
                ),
            ]

            session.add_all(variants)
            session.flush()

            # Create tables
            tables = [
                Table(number=1, capacity=2, location="Window", is_occupied=False),
                Table(number=2, capacity=4, location="Window", is_occupied=False),
                Table(number=3, capacity=4, location="Middle", is_occupied=False),
                Table(number=4, capacity=6, location="Back", is_occupied=False),
                Table(number=5, capacity=2, location="Bar", is_occupied=False),
            ]

            session.add_all(tables)
            session.flush()

            # Create some sample orders
            orders = [
                Order(
                    table_id=tables[0].id,
                    status=OrderStatus.COMPLETED,
                    notes="Extra napkins please",
                    total_amount=8.50,
                    user_id=staff.id,
                    created_at=datetime.now(timezone.utc) - timedelta(days=1),
                ),
                Order(
                    table_id=tables[1].id,
                    status=OrderStatus.PREPARING,
                    total_amount=12.50,
                    user_id=staff.id,
                    created_at=datetime.now(timezone.utc),
                ),
            ]

            session.add_all(orders)
            session.flush()

            # Create order items
            order_items = [
                OrderItem(
                    order_id=orders[0].id,
                    menu_item_id=next(m.id for m in menu_items if m.name == "Cappuccino"),
                    variant_id=next(v.id for v in variants if v.name == "Medium (12oz)"),
                    quantity=2,
                    unit_price=4.50,
                    special_instructions="One with sugar, one without",
                ),
                OrderItem(
                    order_id=orders[0].id,
                    menu_item_id=next(m.id for m in menu_items if m.name == "Croissant"),
                    quantity=1,
                    unit_price=2.50,
                    special_instructions="Heated please",
                ),
                OrderItem(
                    order_id=orders[1].id,
                    menu_item_id=next(m.id for m in menu_items if m.name == "Chicken Pesto Panini"),
                    quantity=2,
                    unit_price=7.50,
                    special_instructions="One with no tomatoes",
                ),
            ]

            session.add_all(order_items)
            # session.commit() is handled by session.begin() context

            print("Database seeded successfully!")

if __name__ == "__main__":
    seed_data()
