"""
Integration tests for authentication endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.user import User


def test_login_success(client: TestClient, test_admin_user: User):
    """Test successful login with valid credentials."""
    response = client.post("/api/v1/auth/token", data={
        "username": test_admin_user.email,
        "password": "testpassword123"
    })
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    # API doesn't return user in login response, only tokens


def test_login_invalid_email(client: TestClient):
    """Test login with non-existent email."""
    response = client.post("/api/v1/auth/token", data={
        "username": "nonexistent@test.com",
        "password": "testpassword123"
    })
    
    assert response.status_code == 401
    data = response.json()
    # API returns error object, not detail
    assert "error" in data or "detail" in data


def test_login_invalid_password(client: TestClient, test_admin_user: User):
    """Test login with incorrect password."""
    response = client.post("/api/v1/auth/token", data={
        "username": test_admin_user.email,
        "password": "wrongpassword"
    })
    
    assert response.status_code == 401
    data = response.json()
    # API returns error object, not detail
    assert "error" in data or "detail" in data


def test_get_current_user(client: TestClient, admin_token_headers: dict):
    """Test getting current user info."""
    response = client.get("/api/v1/auth/me", headers=admin_token_headers)
    
    assert response.status_code == 200
    data = response.json()
    
    assert "email" in data
    assert "role" in data


def test_get_current_user_unauthorized(client_no_auth: TestClient):
    """Test getting current user without authentication."""
    response = client_no_auth.get("/api/v1/auth/me")
    
    assert response.status_code == 401


def test_get_current_user_invalid_token(client_no_auth: TestClient):
    """Test getting current user with invalid token."""
    headers = {"Authorization": "Bearer invalid_token_here"}
    response = client_no_auth.get("/api/v1/auth/me", headers=headers)
    
    assert response.status_code == 401
