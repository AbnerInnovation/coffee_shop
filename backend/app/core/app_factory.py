"""
FastAPI application factory.

Creates and configures the FastAPI application instance with all
middleware, exception handlers, and routes.
"""
from fastapi import FastAPI
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from .config import settings
from .logging_config import setup_logging
from .rate_limit import limiter
from ..middleware.cors import configure_cors
from ..middleware.security import SecurityHeadersMiddleware
from ..middleware.restaurant import RestaurantMiddleware
from .openapi import configure_openapi
from .exception_handlers import register_exception_handlers
from .lifespan import lifespan
from ..api import api_router


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured application instance
    """
    # Setup logging
    setup_logging(
        log_level=getattr(settings, 'LOG_LEVEL', 'INFO'),
        log_file_max_bytes=getattr(settings, 'LOG_FILE_MAX_BYTES', 10 * 1024 * 1024),
        log_file_backup_count=getattr(settings, 'LOG_FILE_BACKUP_COUNT', 5)
    )
    
    # Import models to ensure they are registered with SQLAlchemy
    from ..models.restaurant import Restaurant
    from ..models.user import User
    from ..models.menu import MenuItem, MenuItemVariant, Category
    from ..models.order import Order, OrderItem
    from ..models.table import Table
    
    # Create FastAPI app
    app = FastAPI(
        title="Coffee Shop API",
        description="API for managing a coffee shop's menu and orders",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Configure OpenAPI schema
    configure_openapi(app)
    
    # Configure rate limiting
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Configure CORS middleware
    configure_cors(app)
    
    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Add tenant context middleware (subdomain -> restaurant)
    app.add_middleware(RestaurantMiddleware)
    
    # Register exception handlers
    register_exception_handlers(app)
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    # Root endpoint
    @app.get("/")
    @limiter.limit("100/minute")
    async def root(request):
        return {"message": "Welcome to Coffee Shop API"}
    
    return app
