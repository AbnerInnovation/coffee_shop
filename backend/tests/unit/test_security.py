"""
Unit tests for security module.
"""
import pytest
from datetime import timedelta
from jose import jwt

from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token
)
from app.core.config import settings


def test_password_hashing():
    """Test password hashing and verification."""
    password = "testpassword123"
    hashed = get_password_hash(password)
    
    # Hash should be different from original
    assert hashed != password
    
    # Verification should succeed
    assert verify_password(password, hashed) is True
    
    # Wrong password should fail
    assert verify_password("wrongpassword", hashed) is False


def test_password_hash_uniqueness():
    """Test that same password generates different hashes."""
    password = "testpassword123"
    hash1 = get_password_hash(password)
    hash2 = get_password_hash(password)
    
    # Hashes should be different (due to salt)
    assert hash1 != hash2
    
    # But both should verify correctly
    assert verify_password(password, hash1) is True
    assert verify_password(password, hash2) is True


def test_create_access_token():
    """Test access token creation."""
    # create_access_token expects subject (user_id), not a dict
    user_id = "1"
    scopes = ["read:items", "write:items", "admin"]
    token = create_access_token(subject=user_id, scopes=scopes)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode and verify
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == user_id
    assert decoded["scopes"] == scopes
    assert decoded["type"] == "access"
    assert "exp" in decoded


def test_create_access_token_with_expiration():
    """Test access token creation with custom expiration."""
    user_id = "1"
    expires_delta = timedelta(minutes=15)
    token = create_access_token(subject=user_id, expires_delta=expires_delta)
    
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert "exp" in decoded
    assert decoded["sub"] == user_id


def test_create_refresh_token():
    """Test refresh token creation."""
    user_id = "1"
    token = create_refresh_token(subject=user_id)
    
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode and verify
    decoded = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert decoded["sub"] == user_id
    assert decoded["type"] == "refresh"
    assert "exp" in decoded


def test_decode_token_valid():
    """Test decoding a valid token."""
    user_id = "1"
    scopes = ["read:items", "admin"]
    token = create_access_token(subject=user_id, scopes=scopes)
    
    decoded = decode_token(token)
    assert decoded is not None
    assert decoded["sub"] == user_id
    assert decoded["scopes"] == scopes
    assert decoded["type"] == "access"


def test_decode_token_invalid():
    """Test decoding an invalid token."""
    from jose.exceptions import JWTError
    
    invalid_token = "invalid.token.here"
    
    # decode_token raises JWTError for invalid tokens
    with pytest.raises(JWTError):
        decode_token(invalid_token)


def test_decode_token_expired():
    """Test decoding an expired token."""
    from jose.exceptions import ExpiredSignatureError
    
    user_id = "1"
    # Create token that expires immediately
    token = create_access_token(subject=user_id, expires_delta=timedelta(seconds=-1))
    
    # decode_token raises ExpiredSignatureError for expired tokens
    with pytest.raises(ExpiredSignatureError):
        decode_token(token)
