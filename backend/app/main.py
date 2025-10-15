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
from .core.exceptions import AppException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError

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

app = FastAPI(
    title="Coffee Shop API",
    description="API for managing a coffee shop's menu and orders",
    version="0.1.0"
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
    """Handle custom application exceptions."""
    logger.error(
        f"AppException: {exc.message}",
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
            "detail": exc.message,
            "type": "application_error",
            **exc.details
        }
    )

@app.exception_handler(SQLAlchemyError)
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    """Handle database errors."""
    logger.error(
        f"Database error: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Database error occurred",
            "type": "database_error"
        }
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors."""
    logger.warning(
        f"Validation error: {exc.errors()}",
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "type": "validation_error"
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all unhandled exceptions."""
    logger.error(
        f"Unhandled exception: {str(exc)}",
        exc_info=True,
        extra={"path": request.url.path, "method": request.method}
    )
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "server_error"
        }
    )

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
@limiter.limit("100/minute")  # Apply rate limiting to root endpoint
async def root(request: Request):
    return {"message": "Welcome to Coffee Shop API"}
