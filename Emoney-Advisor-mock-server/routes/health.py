from fastapi import APIRouter, Depends, Header, Query
from typing import Dict, Any
import datetime
import platform
import os

router = APIRouter(
    tags=["Health"],
)

@router.get("/")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint that returns service status.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "emoney-advisor-mock-api",
        "version": "1.0.0"
    }

@router.get("/readiness")
async def readiness_check() -> Dict[str, Any]:
    """
    Readiness check endpoint that verifies if the service is ready to accept requests.
    """
    return {
        "status": "ready",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "emoney-advisor-mock-api",
        "version": "1.0.0"
    }

@router.get("/liveness")
async def liveness_check() -> Dict[str, Any]:
    """
    Liveness check endpoint that verifies if the service is running.
    """
    return {
        "status": "alive",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "emoney-advisor-mock-api",
        "version": "1.0.0"
    }

@router.get("/system-info")
async def system_info() -> Dict[str, Any]:
    """
    System information endpoint that provides details about the environment.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.datetime.now().isoformat(),
        "service": "emoney-advisor-mock-api",
        "version": "1.0.0",
        "system": {
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
            "processors": os.cpu_count(),
            "memory_info": "Not available in this environment"
        },
        "environment": {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "log_level": os.getenv("LOG_LEVEL", "info")
        }
    }