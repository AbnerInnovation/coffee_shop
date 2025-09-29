"""
API package containing all API routes.
"""

from fastapi import APIRouter

# Create a router for all API endpoints
api_router = APIRouter()

# Import and include all routers here
from .routers import menu, auth, user, categories, tables, orders, cash_register

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(categories.router)  # Now at /api/v1/categories/
api_router.include_router(menu.router, prefix="/menu")
api_router.include_router(user.router)
api_router.include_router(tables.router)
api_router.include_router(orders.router)
api_router.include_router(cash_register.router)  # New cash register router
