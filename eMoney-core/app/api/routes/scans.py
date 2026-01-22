# api/routes/scans.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
import logging
from datetime import datetime
from sqlalchemy import text

from app.db.database import get_db
from app.db.repositories.scan_repository import ScanRepository
from app.services.scan_service import ScanService
from app.schemas.scan import ScanRequest, ScanResponse, ScanStatusResponse, ScanListResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/scans",
    tags=["scans"],
    responses={404: {"description": "Not found"}}
)

@router.post("/start", response_model=ScanResponse)
async def start_scan(
    scan_request: ScanRequest,
    session: AsyncSession = Depends(get_db)
):
    """
    Start a new scan based on the request data.
    
    Args:
        scan_request: Scan configuration including scan_type and entity_types
        
    Returns:
        ScanResponse: Created scan details
    """
    try:
        scan_repository = ScanRepository(session)
        scan_service = ScanService(scan_repository)
        
        # Extract scan_type from the request
        scan_type = scan_request.scan_type
        
        # Pass the request data to the service
        result = await scan_service.start_scan(scan_request.dict(), scan_type)
        await session.commit()
        
        return result
    except ValueError as e:
        logger.error(f"Invalid scan request: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error starting {scan_request.scan_type} scan: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting scan: {str(e)}"
        )

@router.get("/{scan_id}/status", response_model=ScanStatusResponse)
async def get_scan_status(
    scan_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Get the status of a scan.
    
    Args:
        scan_id: ID of the scan to check
        
    Returns:
        ScanStatusResponse: Scan status details with entity results
    """
    try:
        scan_repository = ScanRepository(session)
        scan_service = ScanService(scan_repository)
        
        result = await scan_service.get_scan_status(scan_id)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error getting scan status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting scan status: {str(e)}"
        )

@router.get("/", response_model=ScanListResponse)
async def list_scans(
    scan_type: Optional[str] = None,
    scan_status: Optional[str] = None,
    organization_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db)
):
    """
    List scans with optional filtering and pagination.
    
    Args:
        scan_type: Filter by scan type (optional)
        scan_status: Filter by scan status (optional)
        organization_id: Filter by organization ID (optional)
        page: Page number for pagination
        limit: Items per page
        
    Returns:
        ScanListResponse: Paginated list of scans
    """
    try:
        scan_repository = ScanRepository(session)
        scan_service = ScanService(scan_repository)
        
        result = await scan_service.list_scans(
            scan_type=scan_type,
            scan_status=scan_status,
            organization_id=organization_id,
            page=page,
            limit=limit
        )
        
        return result
    except Exception as e:
        logger.error(f"Error listing scans: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing scans: {str(e)}"
        )

# New endpoint: Remove scan
@router.delete("/{scan_id}", response_model=dict)
async def remove_scan(
    scan_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Remove a scan and its associated data.
    
    Args:
        scan_id: ID of the scan to remove
        
    Returns:
        dict: Response with removal status
    """
    try:
        scan_repository = ScanRepository(session)
        scan_service = ScanService(scan_repository)
        
        result = await scan_service.remove_scan(scan_id)
        await session.commit()
        
        return {"success": True, "message": f"Scan {scan_id} removed successfully"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error removing scan {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error removing scan: {str(e)}"
        )

# New endpoint: Cancel scan
@router.post("/{scan_id}/cancel", response_model=ScanStatusResponse)
async def cancel_scan(
    scan_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Cancel a running or paused scan.
    
    Args:
        scan_id: ID of the scan to cancel
        
    Returns:
        ScanStatusResponse: Updated scan status
    """
    try:
        scan_repository = ScanRepository(session)
        scan_service = ScanService(scan_repository)
        
        result = await scan_service.cancel_scan(scan_id)
        await session.commit()
        
        return await scan_service.get_scan_status(scan_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error cancelling scan {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error cancelling scan: {str(e)}"
        )

# New endpoint: Pause scan
@router.post("/{scan_id}/pause", response_model=ScanStatusResponse)
async def pause_scan(
    scan_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Pause a running scan.
    
    Args:
        scan_id: ID of the scan to pause
        
    Returns:
        ScanStatusResponse: Updated scan status
    """
    try:
        scan_repository = ScanRepository(session)
        scan_service = ScanService(scan_repository)
        
        result = await scan_service.pause_scan(scan_id)
        await session.commit()
        
        return await scan_service.get_scan_status(scan_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error pausing scan {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error pausing scan: {str(e)}"
        )

# New endpoint: Resume scan
@router.post("/{scan_id}/resume", response_model=ScanStatusResponse)
async def resume_scan(
    scan_id: str,
    session: AsyncSession = Depends(get_db)
):
    """
    Resume a paused scan.
    
    Args:
        scan_id: ID of the scan to resume
        
    Returns:
        ScanStatusResponse: Updated scan status
    """
    try:
        scan_repository = ScanRepository(session)
        scan_service = ScanService(scan_repository)
        
        result = await scan_service.resume_scan(scan_id)
        await session.commit()
        
        return await scan_service.get_scan_status(scan_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        await session.rollback()
        logger.error(f"Error resuming scan {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error resuming scan: {str(e)}"
        )
    
@router.get("/{scan_id}/stream", response_model=Dict[str, Any])
async def stream_scan_data(
    scan_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    session: AsyncSession = Depends(get_db)
):
    """
    Stream data from a completed scan with pagination.
    
    Args:
        scan_id: ID of the scan to stream data from
        offset: Number of records to skip
        limit: Maximum number of records to return
        entity_type: Optional filter for specific entity type
        
    Returns:
        Dict[str, Any]: Stream response with data statistics
    """
    try:
        scan_repository = ScanRepository(session)
        scan_service = ScanService(scan_repository)
        
        result = await scan_service.stream_scan_data(
            scan_id=scan_id,
            offset=offset,
            limit=limit,
        )
        
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Error streaming data for scan {scan_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error streaming scan data: {str(e)}"
        )
    
@router.get("/health", response_model=Dict[str, Any])
async def check_service_health(session: AsyncSession = Depends(get_db)):
    """
    Check the health status of all connected services.
    
    Returns:
        Dict[str, Any]: Health status of all services with endpoint information and URLs
    """
    try:
        from sqlalchemy import text
        from app.settings import get_settings
        
        settings = get_settings()
        scan_repository = ScanRepository(session)
        scan_service = ScanService(scan_repository)
        
        # Initialize response structure
        health_response = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
            "services": {}
        }
        
        # Check database health
        try:
            # Properly use SQLAlchemy's text construct
            await session.execute(text("SELECT 1"))
            health_response["services"]["database"] = {
                "status": "up",
                "message": "Database connection successful",
                "endpoint": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL.split("///")[-1]  # Mask credentials
            }
        except Exception as e:
            health_response["services"]["database"] = {
                "status": "down",
                "error": str(e),
                "message": "Database connection failed",
                "endpoint": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL.split("///")[-1]  # Mask credentials
            }
            health_response["status"] = "degraded"
        
        # Add all service URLs from settings
        health_response["service_urls"] = settings.service_urls
        
        # Check all service connectors using master connector
        service_keys = ["account", "client", "financial_planning", "identity"]
        for service_key in service_keys:
            try:
                # Get service URL from settings
                service_url = settings.get_service_url(service_key)
                
                # Get the health check endpoint
                health_endpoint = "api/health"
                
                # Construct full endpoint URL
                full_endpoint = f"{service_url}/{health_endpoint}"
                
                # Use the master connector's health check method
                start_time = datetime.utcnow()
                result = await scan_service.connector.health_check(service_key)
                response_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Check if health check response indicates healthy status
                if result.get("status") == "up" or result.get("healthy") is True:
                    health_response["services"][service_key] = {
                        "status": "up",
                        "message": f"{service_key} service is healthy",
                        "url": service_url,
                        "endpoint": full_endpoint,
                        "response_time_ms": int(response_time)
                    }
                else:
                    # Service responded but indicates it's not healthy
                    health_response["services"][service_key] = {
                        "status": "degraded",
                        "message": result.get("message", f"{service_key} service reported unhealthy status"),
                        "url": service_url,
                        "endpoint": full_endpoint,
                        "response_time_ms": int(response_time),
                        "details": result
                    }
                    health_response["status"] = "degraded"
            except Exception as e:
                # Service health check request failed
                service_url = settings.get_service_url(service_key)
                health_response["services"][service_key] = {
                    "status": "down",
                    "error": str(e),
                    "message": f"{service_key} service health check failed",
                    "url": service_url,
                    "endpoint": f"{service_url}/api/health"
                }
                health_response["status"] = "degraded"
        
        # Add API endpoints information
        try:
            from app.service_config import STANDARD_ENDPOINTS, EMONEY_SERVICES
            
            health_response["endpoints"] = {
                "standard": {key: endpoint for key, endpoint in STANDARD_ENDPOINTS.items()},
                "service_specific": {
                    service_name: service_config.get("endpoints", {})
                    for service_name, service_config in EMONEY_SERVICES.items()
                    if "endpoints" in service_config
                }
            }
        except Exception as e:
            health_response["endpoints"] = {
                "error": f"Failed to retrieve endpoints: {str(e)}"
            }
        
        # Add application info
        health_response["application"] = {
            "name": settings.APP_NAME,
            "version": settings.API_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG
        }
        
        # If any service is down, mark overall status as degraded
        down_services = [s for s, info in health_response["services"].items() 
                         if info.get("status") == "down"]
        if down_services:
            health_response["status"] = "critical" if "database" in down_services else "degraded"
        
        # Add summary
        total_services = len(health_response["services"])
        healthy_services = len([s for s, info in health_response["services"].items() 
                               if info.get("status") == "up"])
        
        health_response["summary"] = {
            "total_services": total_services,
            "healthy_services": healthy_services,
            "degraded_services": total_services - healthy_services,
            "message": f"{healthy_services}/{total_services} services healthy"
        }
        
        # Set appropriate HTTP status code
        status_code = status.HTTP_200_OK
        if health_response["status"] == "critical":
            status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        elif health_response["status"] == "degraded":
            status_code = status.HTTP_207_MULTI_STATUS
        
        return health_response
    except Exception as e:
        logger.error(f"Error checking service health: {str(e)}", exc_info=True)
        return {
            "status": "critical",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "message": "Error checking service health"
        }