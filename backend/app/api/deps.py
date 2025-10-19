"""
API dependencies for authentication and authorization.
Re-exports commonly used dependencies for convenience.
"""
from app.services.user import get_current_active_user as get_current_user
from app.core.dependencies import get_current_restaurant

__all__ = ['get_current_user', 'get_current_restaurant']
