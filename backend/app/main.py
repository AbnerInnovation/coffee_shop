from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
import logging

from .core.config import settings
from .db.base import Base, engine, get_db
from .core.security import oauth2_scheme
from .middleware.restaurant import RestaurantMiddleware
from .middleware.security import SecurityHeadersMiddleware
from .core.rate_limit import limiter
from .core.exceptions import (
    AppException,
    ResourceNotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    DatabaseError,
    ExternalServiceError
)
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Import models to ensure they are registered with SQLAlchemy
from .models.restaurant import Restaurant
from .models.user import User
from .models.menu import MenuItem, MenuItemVariant, Category
from .models.order import Order, OrderItem
from .models.table import Table

# Import API router
from app.api import api_router

# Create FastAPI app
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    
    openapi_schema = get_openapi(
        title="Coffee Shop API",
        version="0.1.0",
        description="""
        API for managing a coffee shop's menu and orders.
        
        ## Authentication
        
        1. First, get an access token by making a POST request to `/auth/token` with your username and password
        2. Click the 'Authorize' button and enter: `Bearer YOUR_ACCESS_TOKEN`
        
        ## Available Scopes
        - `read:items`: Read menu items
        - `write:items`: Create/update/delete menu items
        - `read:orders`: View orders
        - `write:orders`: Create/update orders
        - `admin`: Full administrative access
        """,
        routes=app.routes,
    )
    
    # Define OAuth2 scopes
    scopes = {
        "read:items": "Read menu items",
        "write:items": "Create/update/delete menu items",
        "read:orders": "View orders",
        "write:orders": "Create/update orders",
        "admin": "Full administrative access"
    }
    
    # Add security schemes with scopes
    openapi_schema["components"]["securitySchemes"] = {
        "OAuth2PasswordBearer": {
            "type": "oauth2",
            "flows": {
                "password": {
                    "tokenUrl": "/api/v1/auth/token",
                    "scopes": scopes
                }
            },
            "description": "Use /auth/token to get the JWT token. Format: Bearer {token}",
        }
    }
    
    # Add global security
    openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

# Background tasks
import asyncio
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    Handles background tasks like flushing special note statistics.
    """
    # Startup
    logger.info("Starting background tasks...")
    
    # Create background task for flushing special note stats
    async def flush_special_notes_task():
        """Background task that flushes special note statistics every 5 minutes."""
        from .services.special_notes import SpecialNotesService
        
        while True:
            try:
                await asyncio.sleep(300)  # 5 minutes
                
                # Get a database session
                db = next(get_db())
                try:
                    updated_count = SpecialNotesService.flush_updates(db)
                    if updated_count > 0:
                        logger.info(f"Flushed {updated_count} special note updates to database")
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"Error in special notes flush task: {str(e)}", exc_info=True)
    
    # Start the background task
    task = asyncio.create_task(flush_special_notes_task())
    
    yield
    
    # Shutdown
    logger.info("Shutting down background tasks...")
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass

app = FastAPI(
    title="Coffee Shop API",
    description="API for managing a coffee shop's menu and orders",
    version="0.1.0",
    lifespan=lifespan
)

# Set the custom OpenAPI schema
app.openapi = custom_openapi

# Configure rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://*.shopacoffee.local:3000",
        "https://www.shopacoffee.com",
        "https://*.shopacoffee.com",
    ],  # explicit safe origins
    allow_origin_regex=r"^https?://([a-z0-9-]+\.)?localhost(:\d+)?$|^https?://([a-z0-9-]+\.)?shopacoffee\.com$|^https?://([a-z0-9-]+\.)?shopacoffee\.local(:\d+)?$",
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,  # Cache preflight response for 10 minutes
)

# Security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Tenant context middleware (subdomain -> restaurant)
app.add_middleware(RestaurantMiddleware)

# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """
    Handle custom application exceptions.
    
    Provides consistent error responses for all custom exceptions
    with proper logging and error context.
    """
    # Determine log level based on status code
    if exc.status_code >= 500:
        logger.error(
            f"{exc.__class__.__name__}: {exc.message}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
                "details": exc.details,
                "exception_type": exc.__class__.__name__
            },
            exc_info=True
        )
    elif exc.status_code >= 400:
        logger.warning(
            f"{exc.__class__.__name__}: {exc.message}",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": exc.status_code,
                "details": exc.details
            }
        )
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "message": exc.message,
                "type": exc.__class__.__name__,
                "status_code": exc.status_code,
                **exc.details
            }
        }
    )

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    """
    Handle database integrity constraint violations.
    
    Common causes: unique constraint violations, foreign key violations, etc.
    """
    logger.warning(
        f"Database integrity error: {str(exc.orig)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": "IntegrityError"
        }
    )
    
    # Try to provide a more user-friendly message
    error_msg = str(exc.orig)
    if "unique constraint" in error_msg.lower():
        message = "A record with this information already exists"
    elif "foreign key" in error_msg.lower():
        message = "Cannot perform this operation due to related records"
    else:
        message = "Database constraint violation"
    
    return JSONResponse(
        status_code=409,
        content={
            "success": False,
            "error": {
                "message": message,
                "type": "IntegrityError",
                "status_code": 409
            }
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Handle general database errors.
    
    This catches all SQLAlchemy errors not handled by more specific handlers.
    """
    logger.error(
        f"Database error: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "error_type": exc.__class__.__name__
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "message": "A database error occurred. Please try again later.",
                "type": "DatabaseError",
                "status_code": 500
            }
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Handle Pydantic request validation errors.
    
    These occur when request body, query params, or path params
    don't match the expected schema.
    """
    errors = exc.errors()
    logger.warning(
        f"Request validation error: {len(errors)} validation error(s)",
        extra={
            "path": request.url.path,
            "method": request.method,
            "errors": errors
        }
    )
    
    # Format errors for better readability
    formatted_errors = []
    for error in errors:
        formatted_errors.append({
            "field": ".".join(str(loc) for loc in error["loc"]),
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=422,
        content={
            "success": False,
            "error": {
                "message": "Request validation failed",
                "type": "ValidationError",
                "status_code": 422,
                "validation_errors": formatted_errors
            }
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """
    Handle all unhandled exceptions.
    
    This is the catch-all handler for any exceptions not handled
    by more specific handlers. Always logs full stack trace.
    """
    logger.critical(
        f"Unhandled exception: {exc.__class__.__name__}: {str(exc)}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method,
            "exception_type": exc.__class__.__name__
        }
    )
    
    # In production, don't expose internal error details
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": {
                "message": "An unexpected error occurred. Please try again later.",
                "type": "InternalServerError",
                "status_code": 500
            }
        }
    )

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
@limiter.limit("100/minute")  # Apply rate limiting to root endpoint
async def root(request: Request):
    return {"message": "Welcome to Coffee Shop API"}
