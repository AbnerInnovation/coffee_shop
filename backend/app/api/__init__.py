"""
API package containing all API routes.
"""

from fastapi import APIRouter

# Create a router for all API endpoints
api_router = APIRouter()

# Import and include all routers here
from .routers import menu, auth, user, categories, tables, orders, cash_register, restaurants, restaurant_users, reports
from . import admin
from .subscription import router as subscription_router
from .sysadmin_payments import router as sysadmin_payments_router
from .v1.endpoints import menu_import, health

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(restaurants.router)  # Restaurant management
api_router.include_router(restaurant_users.router)  # Restaurant user management
api_router.include_router(categories.router)  # Now at /api/v1/categories/
api_router.include_router(menu.router, prefix="/menu")
api_router.include_router(menu_import.router, prefix="/menu", tags=["menu-import"])  # Menu import endpoints
api_router.include_router(user.router)
api_router.include_router(tables.router)
api_router.include_router(orders.router)
api_router.include_router(cash_register.router)  # New cash register router
api_router.include_router(subscription_router)  # Subscription management
api_router.include_router(sysadmin_payments_router)  # SysAdmin payment management
api_router.include_router(reports.router)  # Reports and analytics
api_router.include_router(admin.router)  # SysAdmin management
api_router.include_router(health.router)  # Health check endpoints
