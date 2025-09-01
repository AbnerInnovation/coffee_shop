"""
API package containing all API routes.
"""

from fastapi import APIRouter

# Create a router for all API endpoints
api_router = APIRouter()

# Import and include all routers here
from .routers import menu, auth, user

# Include all routers
api_router.include_router(auth.router)
api_router.include_router(menu.router, prefix="/menu")
api_router.include_router(user.router)
