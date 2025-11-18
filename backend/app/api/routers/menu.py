"""
Menu Router - Main Entry Point

This module aggregates all menu-related routers for better organization.
The original menu.py has been refactored into separate modules:
- menu_items.py: CRUD operations for menu items
- menu_variants.py: CRUD operations for menu item variants
- menu_special_notes.py: Special notes tracking and statistics

This approach follows SOLID principles and improves maintainability.
"""

from fastapi import APIRouter

# Import sub-routers
from app.api.routers import menu_items, menu_variants, menu_special_notes

# Create main menu router
router = APIRouter(
    prefix="",
    tags=["menu"],
)

# Include menu items router (handles /menu/ endpoints)
router.include_router(menu_items.router)

# Include variants router under menu items (handles /menu/{item_id}/variants)
menu_items.router.include_router(menu_variants.router)

# Include special notes router (handles /menu/special-notes)
router.include_router(menu_special_notes.router)
