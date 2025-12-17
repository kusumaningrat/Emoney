# app/service_config.py

"""
Service configuration for Wealthbox integration services.
This module defines service endpoints, entity types, and provides simple helper functions.
"""
import os
from typing import Dict, Any, Optional, List

# Get environment
ENVIRONMENT = os.getenv("APP_ENVIRONMENT", "dev").lower()

# List of all service keys
SERVICE_KEYS = [
    "client", 
    "opportunity", 
    "identity", 
    "activity",
    "auth"
]

# Standard endpoints that all extraction services share
# FIXED: Removed leading slashes and corrected paths to match actual service endpoints
STANDARD_ENDPOINTS = {
    "health": {"method": "GET", "path": "api/health", "description": "Health check endpoint"},
    "stats": {"method": "GET", "path": "api/stats", "description": "Service statistics"},
    "docs": {"method": "GET", "path": "docs/", "description": "Swagger UI documentation"},
    "scan_start": {"method": "POST", "path": "api/scan/start", "description": "Start a new data extraction scan"},
    "scan_status": {"method": "GET", "path": "api/scan/{scan_id}/status", "description": "Get scan status"},
    "scan_cancel": {"method": "POST", "path": "api/scan/{scan_id}/cancel", "description": "Cancel a running scan"},
    "scan_pause": {"method": "POST", "path": "api/scan/{scan_id}/pause", "description": "Pause a running scan"},
    "scan_resume": {"method": "POST", "path": "api/scan/{scan_id}/resume", "description": "Resume a paused scan"},
    "stream_data": {"method": "GET", "path": "api/stream/{scan_id}", "description": "Stream scan data in real-time"},
    "scan_list": {"method": "GET", "path": "api/scan/list", "description": "List all scans with pagination"},
    "scan_statistics": {"method": "GET", "path": "api/scan/statistics", "description": "Get scan statistics"},
    "scan_remove": {"method": "DELETE", "path": "api/scan/{scan_id}/remove", "description": "Remove scan and data"},
    "results_tables": {"method": "GET", "path": "api/results/{scan_id}/tables", "description": "Get available tables"},
    "results_data": {"method": "GET", "path": "api/results/{scan_id}/result", "description": "Get scan results"},
    "pipeline_info": {"method": "GET", "path": "api/pipeline/info", "description": "Get DLT pipeline info"},
    "maintenance_cleanup": {"method": "POST", "path": "api/maintenance/cleanup", "description": "Clean up old scans"},
    "maintenance_detect_crashed": {"method": "POST", "path": "api/maintenance/detect-crashed", "description": "Detect crashed jobs"}
}

# Wealthbox service metadata
WEALTHBOX_SERVICES = {
    "client": {
        "name": "Wealthbox Client Service",
        "domain": "Client Management",
        "description": "Extract client and contact data",
        "entity_types": ["contact", "client", "household", "applicant" ,"relationship"],
        "endpoints": STANDARD_ENDPOINTS.copy()
    },
    "opportunity": {
        "name": "Wealthbox Opportunity Service",
        "domain": "Opportunity Management",
        "description": "Extract opportunity and sales pipeline data",
        "entity_types": ["opportunity", "deal", "pipeline", "stage", "campaign"],
        "endpoints": STANDARD_ENDPOINTS.copy()
    },
    "identity": {
        "name": "Wealthbox Identity Service",
        "domain": "Identity & Authentication",
        "description": "Extract user and identity data",
        "entity_types": ["user", "user_profile", "workspace", "role", "permission"],
        "endpoints": STANDARD_ENDPOINTS.copy()
    },
    "activity": {
        "name": "Wealthbox Activity Service",
        "domain": "Activity & Interaction",
        "description": "Extract activity and interaction data",
        "entity_types": ["task", "event", "note", "project", "workflow"],
        "endpoints": STANDARD_ENDPOINTS.copy()
    },
    "auth": {
        "name": "Wealthbox Auth Service",
        "domain": "Authentication & Authorization",
        "description": "Extract authentication and authorization data",
        "entity_types": ["oauth", "token", "credential", "provider"],
        "endpoints": STANDARD_ENDPOINTS.copy()
    }
}

# Scan status enum values
SCAN_STATUS = {
    "PENDING": "pending",
    "RUNNING": "running",
    "PAUSED": "paused",
    "COMPLETED": "completed",
    "FAILED": "failed",
    "CANCELLED": "cancelled"
}

# Default scan configuration template
DEFAULT_SCAN_CONFIG = {
    "organizationId": "",
    "type": [],
    "auth": {
        "client_id": "",
        "client_secret": "",
        "grant_type": "client_credentials",
        "scope": "read"
    },
    "filters": {
        "dateRange": {
            "startDate": "2025-01-01",
            "endDate": "2025-12-31"
        },
        "batchSize": 100,
        "includeArchived": False
    }
}


def get_service_url(service_key: str) -> Optional[str]:
    """
    Get the URL for a specific service in the current environment from environment variables.
    
    Args:
        service_key (str): Key of the service (client, opportunity, identity, activity, auth)
        
    Returns:
        str: Service URL or None if not found
    """
    env_var_name = f"{service_key.upper()}_URL_{ENVIRONMENT.upper()}"
    url = os.getenv(env_var_name)
    
    return url


def get_endpoint_url(service_key: str, endpoint_key: str, **path_params) -> Optional[str]:
    """
    Get the full URL for a specific endpoint of a service.
    
    Args:
        service_key (str): Key of the service (client, opportunity, identity, activity, auth)
        endpoint_key (str): Key of the endpoint (e.g., scan_start, health)
        **path_params: Path parameters to substitute in the URL
        
    Returns:
        str: Full endpoint URL or None if service URL or endpoint not found
    """
    service_url = get_service_url(service_key)
    if not service_url:
        return None
    
    # Get the endpoint info from the service configuration
    service = WEALTHBOX_SERVICES.get(service_key, {})
    endpoints = service.get("endpoints", {})
    endpoint = endpoints.get(endpoint_key)
    
    if not endpoint:
        return None
    
    # Get the path and substitute path parameters
    path = endpoint.get("path", "")
    if path_params:
        for param_name, param_value in path_params.items():
            path = path.replace(f"{{{param_name}}}", str(param_value))
    
    return f"{service_url}{path}"


def get_scan_endpoint(service_key: str, api_version: str = "v1") -> Optional[str]:
    """
    Get the scan API endpoint for a service.
    
    Args:
        service_key (str): Key of the service
        api_version (str): API version
        
    Returns:
        str: Scan API endpoint URL or None if service URL is not found
    """
    return get_endpoint_url(service_key, "scan_start")


def get_service_by_entity(entity_type: str) -> Optional[Dict[str, Any]]:
    """
    Get service configuration that handles a specific entity type.
    
    Args:
        entity_type (str): Entity type name
        
    Returns:
        dict: Service configuration or None if not found
    """
    for key, service in WEALTHBOX_SERVICES.items():
        if entity_type in service["entity_types"]:
            return {
                **service,
                "service_key": key,
                "url": get_service_url(key)
            }
    return None


def generate_swagger_url(service_key: str) -> Optional[str]:
    """
    Generate the Swagger UI URL for a service.
    
    Args:
        service_key (str): Key of the service
        
    Returns:
        str: Swagger UI URL or None if service URL not found
    """
    return get_endpoint_url(service_key, "docs")


def get_service_endpoints(service_key: str) -> List[Dict[str, Any]]:
    """
    Get a list of all endpoints for a service.
    
    Args:
        service_key (str): Key of the service
        
    Returns:
        List[Dict[str, Any]]: List of endpoint configurations
    """
    service = WEALTHBOX_SERVICES.get(service_key, {})
    endpoints = service.get("endpoints", {})
    
    result = []
    for key, endpoint in endpoints.items():
        result.append({
            "key": key,
            "method": endpoint.get("method", "GET"),
            "path": endpoint.get("path", ""),
            "description": endpoint.get("description", ""),
            "url": get_endpoint_url(service_key, key)
        })
    
    return result