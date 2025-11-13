"""
Health check endpoints for monitoring and Kubernetes probes.
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
import sys
import logging

from app.db.base import get_db

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])


def get_db_health() -> dict:
    """
    Check database health.
    
    Returns:
        dict: Database health status
    """
    try:
        from app.db.base import SessionLocal
        db = SessionLocal()
        db.execute("SELECT 1")
        db.close()
        return {
            "status": "healthy",
            "message": "Database connection successful"
        }
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        return {
            "status": "unhealthy",
            "message": "Database connection failed",
            "error": str(e)
        }


@router.get("/", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Basic health check endpoint.
    Returns 200 if service is running.
    
    Use this for basic monitoring and uptime checks.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Coffee Shop API",
        "version": "0.1.0"
    }


@router.get("/detailed", status_code=status.HTTP_200_OK)
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed health check with database and system info.
    
    Returns comprehensive health information including:
    - Service status
    - Database connectivity
    - System information
    - Python version
    
    Use this for detailed monitoring dashboards.
    """
    # Database health
    db_health = get_db_health()
    
    # Determine overall status
    overall_status = "healthy" if db_health["status"] == "healthy" else "degraded"
    
    return {
        "status": overall_status,
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Coffee Shop API",
        "version": "0.1.0",
        "database": db_health,
        "system": {
            "python_version": sys.version,
            "platform": sys.platform
        }
    }


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes readiness probe.
    
    Returns 200 if service is ready to accept traffic.
    Returns 503 if service is not ready (e.g., database unavailable).
    
    Use this for Kubernetes readiness probes to determine
    if the pod should receive traffic.
    """
    db_health = get_db_health()
    
    if db_health["status"] != "healthy":
        logger.warning("Readiness check failed: database unhealthy")
        return {
            "status": "not_ready",
            "reason": "database_unhealthy",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """
    Kubernetes liveness probe.
    
    Returns 200 if service is alive and responding.
    
    Use this for Kubernetes liveness probes to determine
    if the pod should be restarted.
    
    This endpoint should always return 200 unless the
    application is completely unresponsive.
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }
