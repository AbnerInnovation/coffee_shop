"""
Tests for centralized error handling.

These tests verify that custom exceptions are properly handled
and return consistent error responses.
"""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions import (
    AppException,
    ResourceNotFoundError,
    ValidationError,
    UnauthorizedError,
    ForbiddenError,
    ConflictError,
    DatabaseError,
    ExternalServiceError
)


# Create a test app with exception handlers
def create_test_app():
    """Create a minimal FastAPI app for testing exception handlers."""
    from fastapi import FastAPI
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    from sqlalchemy.exc import SQLAlchemyError, IntegrityError as SQLIntegrityError
    
    app = FastAPI()
    
    # Import exception handlers from main
    from app.main import (
        app_exception_handler,
        integrity_error_handler,
        sqlalchemy_exception_handler,
        validation_exception_handler,
        general_exception_handler
    )
    
    # Register exception handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(SQLIntegrityError, integrity_error_handler)
    app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)
    
    return app


# Test fixtures
@pytest.fixture
def app():
    """Create test app."""
    return create_test_app()


@pytest.fixture
def client(app):
    """Create test client."""
    return TestClient(app)


# Test exception classes
class TestExceptionClasses:
    """Test custom exception class behavior."""
    
    def test_app_exception_basic(self):
        """Test basic AppException."""
        exc = AppException("Test error", status_code=418)
        assert exc.message == "Test error"
        assert exc.status_code == 418
        assert exc.details == {}
    
    def test_app_exception_with_details(self):
        """Test AppException with details."""
        exc = AppException(
            "Test error",
            status_code=400,
            details={"field": "test", "value": 123}
        )
        assert exc.details["field"] == "test"
        assert exc.details["value"] == 123
    
    def test_resource_not_found_error(self):
        """Test ResourceNotFoundError."""
        exc = ResourceNotFoundError("Order", 123)
        assert exc.status_code == 404
        assert "Order" in exc.message
        assert "123" in exc.message
        assert exc.details["resource"] == "Order"
        assert exc.details["identifier"] == "123"
    
    def test_validation_error(self):
        """Test ValidationError."""
        exc = ValidationError("Invalid email", field="email")
        assert exc.status_code == 400
        assert exc.message == "Invalid email"
        assert exc.details["field"] == "email"
    
    def test_validation_error_no_field(self):
        """Test ValidationError without field."""
        exc = ValidationError("General validation error")
        assert exc.status_code == 400
        assert exc.details == {}
    
    def test_unauthorized_error(self):
        """Test UnauthorizedError."""
        exc = UnauthorizedError("Invalid token")
        assert exc.status_code == 401
        assert exc.message == "Invalid token"
        assert exc.details["auth_required"] is True
    
    def test_unauthorized_error_default(self):
        """Test UnauthorizedError with default message."""
        exc = UnauthorizedError()
        assert exc.status_code == 401
        assert exc.message == "Authentication required"
    
    def test_forbidden_error(self):
        """Test ForbiddenError."""
        exc = ForbiddenError("Admin only", required_permission="admin")
        assert exc.status_code == 403
        assert exc.message == "Admin only"
        assert exc.details["required_permission"] == "admin"
    
    def test_conflict_error(self):
        """Test ConflictError."""
        exc = ConflictError("Duplicate entry", resource="User")
        assert exc.status_code == 409
        assert exc.message == "Duplicate entry"
        assert exc.details["resource"] == "User"
    
    def test_database_error(self):
        """Test DatabaseError."""
        exc = DatabaseError("Insert failed", operation="insert")
        assert exc.status_code == 500
        assert exc.message == "Insert failed"
        assert exc.details["operation"] == "insert"
    
    def test_external_service_error(self):
        """Test ExternalServiceError."""
        exc = ExternalServiceError("payment_gateway", "Timeout")
        assert exc.status_code == 503
        assert exc.message == "Timeout"
        assert exc.details["service"] == "payment_gateway"
    
    def test_exception_repr(self):
        """Test exception __repr__ method."""
        exc = ValidationError("Test", field="test")
        repr_str = repr(exc)
        assert "ValidationError" in repr_str
        assert "Test" in repr_str
        assert "400" in repr_str


# Test exception handlers
class TestExceptionHandlers:
    """Test exception handler responses."""
    
    def test_resource_not_found_handler(self, app, client):
        """Test ResourceNotFoundError handler."""
        @app.get("/test-404")
        def test_endpoint():
            raise ResourceNotFoundError("TestResource", 999)
        
        response = client.get("/test-404")
        assert response.status_code == 404
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["type"] == "ResourceNotFoundError"
        assert data["error"]["status_code"] == 404
        assert "TestResource" in data["error"]["message"]
        assert "999" in data["error"]["message"]
    
    def test_validation_error_handler(self, app, client):
        """Test ValidationError handler."""
        @app.get("/test-validation")
        def test_endpoint():
            raise ValidationError("Invalid input", field="email")
        
        response = client.get("/test-validation")
        assert response.status_code == 400
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["type"] == "ValidationError"
        assert data["error"]["field"] == "email"
    
    def test_unauthorized_error_handler(self, app, client):
        """Test UnauthorizedError handler."""
        @app.get("/test-unauthorized")
        def test_endpoint():
            raise UnauthorizedError("Token expired")
        
        response = client.get("/test-unauthorized")
        assert response.status_code == 401
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["type"] == "UnauthorizedError"
        assert data["error"]["auth_required"] is True
    
    def test_forbidden_error_handler(self, app, client):
        """Test ForbiddenError handler."""
        @app.get("/test-forbidden")
        def test_endpoint():
            raise ForbiddenError("Admin required", required_permission="admin")
        
        response = client.get("/test-forbidden")
        assert response.status_code == 403
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["type"] == "ForbiddenError"
        assert data["error"]["required_permission"] == "admin"
    
    def test_conflict_error_handler(self, app, client):
        """Test ConflictError handler."""
        @app.get("/test-conflict")
        def test_endpoint():
            raise ConflictError("Already exists", resource="Order")
        
        response = client.get("/test-conflict")
        assert response.status_code == 409
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["type"] == "ConflictError"
        assert data["error"]["resource"] == "Order"
    
    def test_database_error_handler(self, app, client):
        """Test DatabaseError handler."""
        @app.get("/test-database")
        def test_endpoint():
            raise DatabaseError("Query failed", operation="select")
        
        response = client.get("/test-database")
        assert response.status_code == 500
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["type"] == "DatabaseError"
        assert data["error"]["operation"] == "select"
    
    def test_external_service_error_handler(self, app, client):
        """Test ExternalServiceError handler."""
        @app.get("/test-external")
        def test_endpoint():
            raise ExternalServiceError("api", "Connection timeout")
        
        response = client.get("/test-external")
        assert response.status_code == 503
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["type"] == "ExternalServiceError"
        assert data["error"]["service"] == "api"
    
    def test_general_exception_handler(self, app, client):
        """Test general exception handler for unhandled exceptions."""
        @app.get("/test-unhandled")
        def test_endpoint():
            raise ValueError("Unexpected error")
        
        response = client.get("/test-unhandled")
        assert response.status_code == 500
        
        data = response.json()
        assert data["success"] is False
        assert data["error"]["type"] == "InternalServerError"
        # Should not expose internal error details
        assert "ValueError" not in data["error"]["message"]


# Integration tests
class TestErrorHandlingIntegration:
    """Test error handling in realistic scenarios."""
    
    def test_multiple_validation_errors(self, app, client):
        """Test handling multiple validation errors."""
        from pydantic import BaseModel, Field
        
        class TestModel(BaseModel):
            email: str = Field(..., min_length=5)
            age: int = Field(..., gt=0, lt=150)
        
        @app.post("/test-validation-multiple")
        def test_endpoint(data: TestModel):
            return {"success": True}
        
        # Send invalid data
        response = client.post(
            "/test-validation-multiple",
            json={"email": "abc", "age": 200}
        )
        
        assert response.status_code == 422
        data = response.json()
        assert data["success"] is False
        assert "validation_errors" in data["error"]
        assert len(data["error"]["validation_errors"]) > 0
    
    def test_error_response_consistency(self, app, client):
        """Test that all error responses follow the same format."""
        error_endpoints = []
        
        @app.get("/test-404")
        def endpoint_404():
            raise ResourceNotFoundError("Item", 1)
        
        @app.get("/test-400")
        def endpoint_400():
            raise ValidationError("Bad request")
        
        @app.get("/test-401")
        def endpoint_401():
            raise UnauthorizedError()
        
        @app.get("/test-403")
        def endpoint_403():
            raise ForbiddenError()
        
        @app.get("/test-409")
        def endpoint_409():
            raise ConflictError("Conflict")
        
        @app.get("/test-500")
        def endpoint_500():
            raise DatabaseError()
        
        endpoints = [
            "/test-404", "/test-400", "/test-401",
            "/test-403", "/test-409", "/test-500"
        ]
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            data = response.json()
            
            # All errors should have consistent structure
            assert "success" in data
            assert data["success"] is False
            assert "error" in data
            assert "message" in data["error"]
            assert "type" in data["error"]
            assert "status_code" in data["error"]
    
    def test_error_logging_levels(self, app, client, caplog):
        """Test that errors are logged at appropriate levels."""
        import logging
        
        @app.get("/test-client-error")
        def client_error():
            raise ValidationError("Client error")
        
        @app.get("/test-server-error")
        def server_error():
            raise DatabaseError("Server error")
        
        # Client errors (4xx) should be warnings
        with caplog.at_level(logging.WARNING):
            client.get("/test-client-error")
            assert any("ValidationError" in record.message for record in caplog.records)
        
        # Server errors (5xx) should be errors
        caplog.clear()
        with caplog.at_level(logging.ERROR):
            client.get("/test-server-error")
            assert any("DatabaseError" in record.message for record in caplog.records)


# Performance tests
class TestErrorHandlingPerformance:
    """Test error handling performance."""
    
    def test_exception_creation_performance(self):
        """Test that exception creation is fast."""
        import time
        
        start = time.time()
        for i in range(1000):
            exc = ResourceNotFoundError("Resource", i)
        end = time.time()
        
        # Should create 1000 exceptions in less than 0.1 seconds
        assert (end - start) < 0.1
    
    def test_error_response_performance(self, app, client):
        """Test that error responses are fast."""
        import time
        
        @app.get("/test-perf")
        def test_endpoint():
            raise ResourceNotFoundError("Item", 1)
        
        # Warm up
        client.get("/test-perf")
        
        # Measure
        start = time.time()
        for _ in range(100):
            client.get("/test-perf")
        end = time.time()
        
        # Should handle 100 error responses in less than 1 second
        assert (end - start) < 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
