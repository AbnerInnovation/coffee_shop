"""
Order Service - Compatibility Layer

This module provides backward compatibility by re-exporting functions from the new
modular order services. Existing code can continue to import from this module while
new code should import directly from app.services.orders.

DEPRECATED: This module is maintained for backward compatibility only.
New code should import directly from app.services.orders submodules.

Migration Guide:
    # Old way (still works)
    from app.services.order import get_orders, create_order_with_items
    
    # New way (recommended)
    from app.services.orders import get_orders, create_order_with_items
    from app.services.orders.payment_service import process_order_payment
    from app.services.orders.table_manager import handle_table_change
"""

# Re-export serializers
from .orders.serializers import (
    serialize_menu_item,
    serialize_variant,
    serialize_order_item,
    serialize_order_item_extra,
    serialize_order_person,
    serialize_order,
)

# Re-export order CRUD
from .orders.order_crud import (
    get_orders,
    get_order,
    create_order_with_items,
    update_order,
    delete_order,
)

# Re-export order items CRUD
from .orders.order_items_crud import (
    get_order_item,
    add_order_item,
    update_order_item,
    delete_order_item,
)

# Re-export table management
from .orders.table_manager import (
    mark_table_available_if_no_orders,
)

# Note: New functionality like payment_service, validators, and order_extras_crud
# should be imported directly from app.services.orders submodules

__all__ = [
    # Serializers
    "serialize_menu_item",
    "serialize_variant",
    "serialize_order_item",
    "serialize_order_item_extra",
    "serialize_order_person",
    "serialize_order",
    # Order CRUD
    "get_orders",
    "get_order",
    "create_order_with_items",
    "update_order",
    "delete_order",
    # Order Items CRUD
    "get_order_item",
    "add_order_item",
    "update_order_item",
    "delete_order_item",
    # Table Management
    "mark_table_available_if_no_orders",
]
