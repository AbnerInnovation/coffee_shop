"""
Global exception handlers for the application.

Provides consistent error responses and logging for all exception types.
"""
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from .exceptions import AppException

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all exception handlers with the FastAPI application.
    
    Args:
        app: FastAPI application instance
    """
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(IntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)


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
