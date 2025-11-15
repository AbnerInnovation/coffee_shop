"""
OpenAPI schema configuration.

Configures the OpenAPI documentation with authentication and scopes.
"""
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def configure_openapi(app: FastAPI) -> None:
    """
    Configure custom OpenAPI schema for the application.
    
    Args:
        app: FastAPI application instance
    """
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
    
    # Set the custom OpenAPI schema
    app.openapi = custom_openapi
