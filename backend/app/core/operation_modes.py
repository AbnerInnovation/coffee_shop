"""
Operation Modes Configuration

Defines business operation modes and their feature configurations.
Each mode represents a different type of business (restaurant, POS, cafe, etc.)
and determines which features are enabled/disabled.

This follows the Strategy Pattern for mode-specific behavior.
"""

from enum import Enum as PyEnum
from typing import Dict, Any


class OperationMode(str, PyEnum):
    """
    Business operation modes.
    Determines the type of business and available features.
    """
    FULL_RESTAURANT = "full_restaurant"  # Complete restaurant with tables, kitchen, waiters
    POS_ONLY = "pos_only"                # Point of sale only (churros, ice cream, etc.)
    CAFE_MODE = "cafe_mode"              # Cafe with tables but no kitchen module
    FOOD_TRUCK = "food_truck"            # Mobile kitchen without tables
    QUICK_SERVICE = "quick_service"      # Quick service restaurant (order at counter)


class OrderType(str, PyEnum):
    """
    Order types supported by the system.
    """
    DINE_IN = "dine_in"              # Table service
    TAKEAWAY = "takeaway"            # Takeout
    DELIVERY = "delivery"            # Delivery
    POS_SALE = "pos_sale"            # Direct POS sale (no table)
    QUICK_SERVICE = "quick_service"  # Order at counter, deliver to table


# Configuration matrix for each operation mode
MODE_CONFIG: Dict[OperationMode, Dict[str, Any]] = {
    OperationMode.FULL_RESTAURANT: {
        # UI Features
        'show_tables': True,
        'show_kitchen': True,
        'show_waiters': True,
        'show_delivery': True,
        
        # Business Logic
        'requires_table_for_order': True,
        'allows_pos_sales': True,
        'allows_table_service': True,
        'allows_kitchen_orders': True,
        
        # Default Settings
        'default_order_type': OrderType.DINE_IN,
        
        # User Types Allowed
        'allowed_staff_types': ['waiter', 'cashier', 'kitchen'],
        
        # Validation Rules
        'min_tables': 1,
        'min_menu_items': 10,
        
        # Ticket Configuration
        'use_daily_tickets': False,
        'ticket_prefix': '',
    },
    
    OperationMode.POS_ONLY: {
        # UI Features
        'show_tables': False,           # No tables in UI
        'show_kitchen': False,          # No kitchen module
        'show_waiters': False,          # No waiter management
        'show_delivery': False,         # No delivery option
        
        # Business Logic
        'requires_table_for_order': False,  # Orders without table assignment
        'allows_pos_sales': True,
        'allows_table_service': False,
        'allows_kitchen_orders': False,
        
        # Default Settings
        'default_order_type': OrderType.POS_SALE,
        
        # User Types Allowed
        'allowed_staff_types': ['cashier'],  # Only cashiers
        
        # Validation Rules
        'min_tables': 0,
        'min_menu_items': 5,
        
        # Ticket Configuration
        'use_daily_tickets': True,      # Daily ticket numbers (YYYYMMDD-NNN)
        'ticket_prefix': '',
    },
    
    OperationMode.CAFE_MODE: {
        # UI Features
        'show_tables': True,
        'show_kitchen': False,          # No kitchen module (prepare at counter)
        'show_waiters': False,          # Order at counter
        'show_delivery': False,
        
        # Business Logic
        'requires_table_for_order': False,  # Order at counter
        'allows_pos_sales': True,
        'allows_table_service': True,       # Deliver to table
        'allows_kitchen_orders': False,
        
        # Default Settings
        'default_order_type': OrderType.QUICK_SERVICE,
        
        # User Types Allowed
        'allowed_staff_types': ['cashier'],
        
        # Validation Rules
        'min_tables': 5,
        'min_menu_items': 20,
        
        # Ticket Configuration
        'use_daily_tickets': True,
        'ticket_prefix': '',
    },
    
    OperationMode.FOOD_TRUCK: {
        # UI Features
        'show_tables': False,
        'show_kitchen': True,           # Mobile kitchen
        'show_waiters': False,
        'show_delivery': False,
        
        # Business Logic
        'requires_table_for_order': False,
        'allows_pos_sales': True,
        'allows_table_service': False,
        'allows_kitchen_orders': True,
        
        # Default Settings
        'default_order_type': OrderType.TAKEAWAY,
        
        # User Types Allowed
        'allowed_staff_types': ['cashier', 'kitchen'],
        
        # Validation Rules
        'min_tables': 0,
        'min_menu_items': 15,
        
        # Ticket Configuration
        'use_daily_tickets': True,
        'ticket_prefix': 'FT-',
    },
    
    OperationMode.QUICK_SERVICE: {
        # UI Features
        'show_tables': True,
        'show_kitchen': True,
        'show_waiters': False,          # Self-service
        'show_delivery': True,
        
        # Business Logic
        'requires_table_for_order': False,
        'allows_pos_sales': True,
        'allows_table_service': True,
        'allows_kitchen_orders': True,
        
        # Default Settings
        'default_order_type': OrderType.QUICK_SERVICE,
        
        # User Types Allowed
        'allowed_staff_types': ['cashier', 'kitchen'],
        
        # Validation Rules
        'min_tables': 10,
        'min_menu_items': 30,
        
        # Ticket Configuration
        'use_daily_tickets': False,
        'ticket_prefix': '',
    },
}


def get_mode_config(mode: OperationMode) -> Dict[str, Any]:
    """
    Get configuration for a specific operation mode.
    
    Args:
        mode: The operation mode
        
    Returns:
        Dictionary with mode configuration
    """
    return MODE_CONFIG.get(mode, MODE_CONFIG[OperationMode.FULL_RESTAURANT])


def is_feature_enabled(mode: OperationMode, feature: str) -> bool:
    """
    Check if a feature is enabled for a specific mode.
    
    Args:
        mode: The operation mode
        feature: Feature name to check
        
    Returns:
        True if feature is enabled, False otherwise
    """
    config = get_mode_config(mode)
    return config.get(feature, False)


def validate_order_for_mode(
    mode: OperationMode,
    order_data: dict
) -> tuple[bool, str]:
    """
    Validate that an order is compatible with the operation mode.
    
    Args:
        mode: The operation mode
        order_data: Order data to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    config = get_mode_config(mode)
    
    # Validate order type compatibility
    order_type = order_data.get('order_type')
    
    # Validate table requirement - only for Dine-in orders
    if config['requires_table_for_order'] and order_type == OrderType.DINE_IN and not order_data.get('table_id'):
        return False, "Este modo requiere asignar una mesa a la orden"
    if order_type == OrderType.DINE_IN and not config['allows_table_service']:
        return False, "Servicio a mesa no disponible en este modo"
    
    if order_type == OrderType.POS_SALE and not config['allows_pos_sales']:
        return False, "Ventas POS no disponibles en este modo"
    
    return True, ""


def get_default_order_type(mode: OperationMode) -> OrderType:
    """
    Get the default order type for a specific mode.
    
    Args:
        mode: The operation mode
        
    Returns:
        Default OrderType for the mode
    """
    config = get_mode_config(mode)
    return config.get('default_order_type', OrderType.DINE_IN)


def is_staff_type_allowed(mode: OperationMode, staff_type: str) -> bool:
    """
    Check if a staff type is allowed in a specific mode.
    
    Args:
        mode: The operation mode
        staff_type: Staff type to check (waiter, cashier, kitchen)
        
    Returns:
        True if staff type is allowed, False otherwise
    """
    config = get_mode_config(mode)
    allowed_types = config.get('allowed_staff_types', [])
    return staff_type in allowed_types
