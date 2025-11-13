"""
Integration tests for health check endpoints.
"""
import pytest
from fastapi.testclient import TestClient


def test_basic_health_check(client: TestClient):
    """Test basic health check endpoint."""
    response = client.get("/api/v1/health/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["service"] == "Coffee Shop API"
    assert "version" in data


def test_detailed_health_check(client: TestClient):
    """Test detailed health check endpoint."""
    response = client.get("/api/v1/health/detailed")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "timestamp" in data
    assert "service" in data
    assert "database" in data
    assert "system" in data
    
    # Check database health
    assert "status" in data["database"]
    
    # Check system info
    assert "python_version" in data["system"]
    assert "platform" in data["system"]


def test_readiness_check(client: TestClient):
    """Test Kubernetes readiness probe."""
    response = client.get("/api/v1/health/ready")
    
    assert response.status_code == 200
    data = response.json()
    
    assert "status" in data
    assert "timestamp" in data
    # Status should be "ready" if database is healthy
    assert data["status"] in ["ready", "not_ready"]


def test_liveness_check(client: TestClient):
    """Test Kubernetes liveness probe."""
    response = client.get("/api/v1/health/live")
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["status"] == "alive"
    assert "timestamp" in data
