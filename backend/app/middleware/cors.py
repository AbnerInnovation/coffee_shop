"""
CORS middleware configuration.

Configures Cross-Origin Resource Sharing for the application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def configure_cors(app: FastAPI) -> None:
    """
    Configure CORS middleware for the application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "https://www.shopacoffee.com",
        ],  # explicit safe origins (wildcards don't work here)
        allow_origin_regex=r"^https?://([a-z0-9-]+\.)?localhost(:\d+)?$|^https?://([a-z0-9-]+\.)?shopacoffee\.com$|^https?://([a-z0-9-]+\.)?shopacoffee\.local(:\d+)?$",
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,  # Cache preflight response for 10 minutes
    )
