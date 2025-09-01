from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.utils import get_openapi
from sqlalchemy.orm import Session
import logging

from .core.config import settings
from .db.base import Base, engine, get_db
from .core.security import oauth2_scheme

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
from .models.user import User
from .models.menu import MenuItem, MenuItemVariant
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

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to Coffee Shop API"}
