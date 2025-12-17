# app/service_config.py

"""
Service configuration for EMoney integration services.
This module defines service endpoints, entity types, and provides simple helper functions.
"""
import os
from typing import Dict, Any, Optional, List

# Get environment
ENVIRONMENT = os.getenv("APP_ENVIRONMENT", "dev").lower()

# List of all EMoney service keys
SERVICE_KEYS = [
    "account",
    "client", 
    "financial_planning", 
    "identity"
]

# Standard endpoints that all extraction services share
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

# EMoney service metadata
EMONEY_SERVICES = {
    "account": {
        "name": "EMoney Account Service",
        "domain": "Account & Asset Management",
        "description": "Extract account, asset, and liability data",
        "entity_types": ["account", "accounttype", "asset", "assetclass", "liability"],
        "endpoints": STANDARD_ENDPOINTS.copy(),
        "auth_type": "jwt",
        "default_scan_pattern": "emoney-account-scan-2025-{uuid}"
    },
    "client": {
        "name": "EMoney Client Service", 
        "domain": "Client Relationship Management",
        "description": "Extract client, household, and relationship data",
        "entity_types": ["client", "contact", "household", "relationship", "spouse"],
        "endpoints": STANDARD_ENDPOINTS.copy(),
        "auth_type": "jwt",
        "default_scan_pattern": "emoney-scan-2025-{uuid}"
    },
    "financial_planning": {
        "name": "EMoney Financial Planning Service",
        "domain": "Financial Planning & Analysis", 
        "description": "Extract financial plans, goals, and projections",
        "entity_types": ["plan", "goal", "net_worth", "scenario", "cashflow"],
        "endpoints": STANDARD_ENDPOINTS.copy(),
        "auth_type": "jwt",
        "default_scan_pattern": "emoney-plan-2025-{uuid}"
    },
    "identity": {
        "name": "EMoney Identity Service",
        "domain": "Identity & Access Management",
        "description": "Extract user, permission, and security data",
        "entity_types": ["user", "office", "role", "permission", "sharingrule", "logon"],
        "endpoints": STANDARD_ENDPOINTS.copy(),
        "auth_type": "jwt", 
        "default_scan_pattern": "emoney-identity-2025-{uuid}"
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

# Default scan configuration template for EMoney
DEFAULT_SCAN_CONFIG = {
    "organizationId": "org-12345",
    "type": [],
    "auth": {
        "api_key": "emoney-api-key-67890",
        "client_id": "emoney-client-id-12345",
        "firm_id": "firm-12345", 
        "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
        "scope": "API"
    },
    "filters": {
        "dateRange": {
            "startDate": "2025-01-01",
            "endDate": "2025-12-31"
        },
        "batchSize": 100,
        "includeInactive": False
    }
}


def get_service_url(service_key: str) -> Optional[str]:
    """
    Get the URL for a specific EMoney service in the current environment from environment variables.
    
    Args:
        service_key (str): Key of the service (account, client, financial_planning, identity)
        
    Returns:
        str: Service URL or None if not found
    """
    # EMoney service URL pattern
    env_var_name = f"EMONEY_{service_key.upper()}_URL_{ENVIRONMENT.upper()}"
    url = os.getenv(env_var_name)
    
    # Fallback to generic pattern
    if not url:
        env_var_name = f"{service_key.upper()}_URL_{ENVIRONMENT.upper()}"
        url = os.getenv(env_var_name)
    
    return url


def get_endpoint_url(service_key: str, endpoint_key: str, **path_params) -> Optional[str]:
    """
    Get the full URL for a specific endpoint of an EMoney service.
    
    Args:
        service_key (str): Key of the service (account, client, financial_planning, identity)
        endpoint_key (str): Key of the endpoint (e.g., scan_start, health)
        **path_params: Path parameters to substitute in the URL
        
    Returns:
        str: Full endpoint URL or None if service URL or endpoint not found
    """
    service_url = get_service_url(service_key)
    if not service_url:
        return None
    
    # Get the endpoint info from the service configuration
    service = EMONEY_SERVICES.get(service_key, {})
    endpoints = service.get("endpoints", {})
    endpoint = endpoints.get(endpoint_key)
    
    if not endpoint:
        return None
    
    # Get the path and substitute path parameters
    path = endpoint.get("path", "")
    if path_params:
        for param_name, param_value in path_params.items():
            path = path.replace(f"{{{param_name}}}", str(param_value))
    
    # Ensure proper URL formatting
    service_url = service_url.rstrip("/")
    path = path.lstrip("/")
    
    return f"{service_url}/{path}"


def get_scan_endpoint(service_key: str, api_version: str = "v1") -> Optional[str]:
    """
    Get the scan API endpoint for an EMoney service.
    
    Args:
        service_key (str): Key of the service
        api_version (str): API version (unused but kept for compatibility)
        
    Returns:
        str: Scan API endpoint URL or None if service URL is not found
    """
    return get_endpoint_url(service_key, "scan_start")


def get_service_by_entity(entity_type: str) -> Optional[Dict[str, Any]]:
    """
    Get EMoney service configuration that handles a specific entity type.
    
    Args:
        entity_type (str): Entity type name
        
    Returns:
        dict: Service configuration or None if not found
    """
    for key, service in EMONEY_SERVICES.items():
        if entity_type.lower() in [et.lower() for et in service["entity_types"]]:
            return {
                **service,
                "service_key": key,
                "url": get_service_url(key)
            }
    return None


def generate_swagger_url(service_key: str) -> Optional[str]:
    """
    Generate the Swagger UI URL for an EMoney service.
    
    Args:
        service_key (str): Key of the service
        
    Returns:
        str: Swagger UI URL or None if service URL not found
    """
    return get_endpoint_url(service_key, "docs")


def get_service_endpoints(service_key: str) -> List[Dict[str, Any]]:
    """
    Get a list of all endpoints for an EMoney service.
    
    Args:
        service_key (str): Key of the service
        
    Returns:
        List[Dict[str, Any]]: List of endpoint configurations
    """
    service = EMONEY_SERVICES.get(service_key, {})
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


def get_auth_config_template(service_key: str) -> Dict[str, Any]:
    """
    Get the authentication configuration template for a specific EMoney service.
    
    Args:
        service_key (str): Key of the service
        
    Returns:
        Dict[str, Any]: Auth configuration template
    """
    service = EMONEY_SERVICES.get(service_key, {})
    if service.get("auth_type") == "jwt":
        return {
            "api_key": "emoney-api-key-67890",
            "client_id": "emoney-client-id-12345", 
            "firm_id": "firm-12345",
            "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
            "scope": "API"
        }
    return {}


def get_scan_id_pattern(service_key: str) -> str:
    """
    Get the scan ID pattern for a specific EMoney service.
    
    Args:
        service_key (str): Key of the service
        
    Returns:
        str: Scan ID pattern
    """
    service = EMONEY_SERVICES.get(service_key, {})
    return service.get("default_scan_pattern", f"emoney-{service_key}-2025-{{uuid}}")


def validate_entity_types(service_key: str, entity_types: List[str]) -> List[str]:
    """
    Validate and filter entity types for a specific EMoney service.
    
    Args:
        service_key (str): Key of the service
        entity_types (List[str]): List of entity types to validate
        
    Returns:
        List[str]: Valid entity types for the service
    """
    service = EMONEY_SERVICES.get(service_key, {})
    supported_types = [et.lower() for et in service.get("entity_types", [])]
    
    valid_types = []
    for entity_type in entity_types:
        if entity_type.lower() in supported_types:
            valid_types.append(entity_type.lower())
    
    return valid_types


# EMoney-specific configuration
EMONEY_CONFIG = {
    "default_timeout": 30.0,
    "max_retries": 3,
    "rate_limit_retry_after": 60,
    "supported_auth_methods": ["jwt", "api_key"],
    "default_batch_size": 100,
    "max_batch_size": 1000
}