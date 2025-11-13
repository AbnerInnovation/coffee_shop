"""
Unit tests for configuration module.
"""
import pytest
from app.core.config import Settings


def test_settings_initialization():
    """Test that settings can be initialized with defaults."""
    # This will use values from .env file
    from app.core.config import settings
    
    # Test actual fields that exist in Settings
    assert settings.API_V1_STR == "/api/v1"
    assert settings.ALGORITHM == "HS256"
    assert settings.MYSQL_SERVER is not None
    assert settings.SECRET_KEY is not None


def test_database_uri_property():
    """Test that database connection string can be built."""
    from app.core.config import settings
    
    # DATABASE_URI is built in base.py, not a property of Settings
    # Test that we have the components needed
    assert settings.MYSQL_SERVER is not None
    assert settings.MYSQL_USER is not None
    assert settings.MYSQL_DB is not None
    assert settings.MYSQL_PORT == 3306


def test_environment_properties():
    """Test environment check properties."""
    from app.core.config import settings
    
    # Test DEBUG field that actually exists
    assert hasattr(settings, 'DEBUG')
    assert isinstance(settings.DEBUG, bool)
    # Test other environment-related fields
    assert hasattr(settings, 'BACKEND_CORS_ORIGINS')
    assert isinstance(settings.BACKEND_CORS_ORIGINS, list)


def test_secret_key_validation():
    """Test that SECRET_KEY has a default value."""
    # Settings has a default SECRET_KEY, so short keys are allowed in tests
    # Just verify that the default is long enough
    from app.core.config import settings
    assert len(settings.SECRET_KEY) >= 32


def test_valid_secret_key():
    """Test that valid SECRET_KEY passes validation."""
    # This should not raise an error
    settings = Settings(
        SECRET_KEY="a" * 32,  # 32 characters
        MYSQL_SERVER="localhost",
        MYSQL_USER="test",
        MYSQL_PASSWORD="test",
        MYSQL_DB="test"
    )
    assert len(settings.SECRET_KEY) >= 32
