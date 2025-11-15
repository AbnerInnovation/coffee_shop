"""
Orders Service Package

This package provides modular services for order management, following SOLID principles.

Modules:
- order_crud: Basic CRUD operations for orders
- order_items_crud: CRUD operations for order items
- order_extras_crud: CRUD operations for order item extras
- payment_service: Payment processing and cash register integration
- table_manager: Table occupancy management
- validators: Reusable validation functions
- serializers: Data serialization helpers

Usage:
    # Direct imports (recommended for new code)
    from app.services.orders.payment_service import process_order_payment
    from app.services.orders.table_manager import handle_table_change
    
    # Or import from package
    from app.services.orders import process_order_payment, handle_table_change
"""

# Serializers
from .serializers import (
    serialize_menu_item,
    serialize_variant,
    serialize_order_item,
    serialize_order_item_extra,
    serialize_order_person,
    serialize_order,
)

# Order CRUD
from .order_crud import (
    get_orders,
    get_order,
    create_order_with_items,
    update_order,
    delete_order,
)

# Order Items CRUD
from .order_items_crud import (
    get_order_item,
    add_order_item,
    update_order_item,
    update_order_item_status,
    delete_order_item,
)

# Helper to avoid circular import - will be populated after imports
_update_order_item_status = None

# Order Extras CRUD
from .order_extras_crud import (
    add_extra_to_item,
    get_item_extras,
    update_item_extra,
    delete_item_extra,
)

# Payment Service
from .payment_service import (
    process_order_payment,
    validate_payment_method,
    can_cancel_order,
)

# Table Manager
from .table_manager import (
    mark_table_occupied,
    mark_table_available_if_no_orders,
    handle_table_change,
)

# Validators
from .validators import (
    validate_menu_item_exists,
    validate_table_exists,
    validate_order_exists,
    validate_order_item_exists,
    validate_can_modify_order,
)

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
    "update_order_item_status",
    "delete_order_item",
    # Order Extras CRUD
    "add_extra_to_item",
    "get_item_extras",
    "update_item_extra",
    "delete_item_extra",
    # Payment Service
    "process_order_payment",
    "validate_payment_method",
    "can_cancel_order",
    # Table Manager
    "mark_table_occupied",
    "mark_table_available_if_no_orders",
    "handle_table_change",
    # Validators
    "validate_menu_item_exists",
    "validate_table_exists",
    "validate_order_exists",
    "validate_order_item_exists",
    "validate_can_modify_order",
]
