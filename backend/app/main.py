"""
Coffee Shop API - Main Application Entry Point.

This module creates and exports the FastAPI application instance.
All configuration, middleware, and routing is handled by the app factory.
"""
from .core.app_factory import create_app

# Create the FastAPI application instance
app = create_app()
