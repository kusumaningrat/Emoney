import logging
import json
from typing import Dict, Any, Optional, List
from app.connectors.api_connector import SimpleAPIConnector
from app.core.exceptions import ServiceConnectionError
from app.settings import get_settings
from app.service_config import STANDARD_ENDPOINTS, EMONEY_SERVICES, DEFAULT_SCAN_CONFIG

logger = logging.getLogger(__name__)

class EMoneyMasterConnector:
    """
    Master connector for EMoney Services data extraction operations.
    Handles routing and orchestration across Client, Account, Financial Planning,
    and Identity services.
    """
    
    # Map of service keys to their supported entity types
    SERVICE_ENTITY_MAP = {
        "client": ["client", "contact", "household", "relationship", "spouse"],
        "account": ["account", "account_type", "accounttype", "asset", "asset_class", "assetclass", "liability"],
        "financial_planning": ["plan", "goal", "net_worth", "networth", "scenario", "cashflow"],
        "identity": ["permission", "role", "office", "logon", "sharing_rule", "sharingrule", "user"]
    }
    
    # Reverse map: entity type -> service key
    ENTITY_TO_SERVICE_MAP = {}
    
    def __init__(self, api_key: Optional[str] = None, timeout: float = 5.0):
        """
        Initialize the Master connector with configuration from settings.
        
        Args:
            api_key: Optional API key override (defaults to settings)
            timeout: Request timeout in seconds
        """
        settings = get_settings()
        self.api_key = api_key or settings.API_KEY
        self.timeout = timeout
        
        # Initialize connectors for each service
        self.connectors = {}
        
        for service_key in self.SERVICE_ENTITY_MAP.keys():
            service_url = settings.get_service_url(service_key)
            
            if not service_url:
                logger.error(f"No URL configured for {service_key} service in {settings.ENVIRONMENT} environment")
                continue
            
            # Get service-specific endpoints
            service_config = EMONEY_SERVICES.get(service_key, {})
            endpoints = service_config.get("endpoints", STANDARD_ENDPOINTS.copy())
            
            # Create connector for this service
            self.connectors[service_key] = {
                "connector": SimpleAPIConnector(
                    base_url=service_url,
                    api_key=self.api_key,
                    timeout=self.timeout
                ),
                "endpoints": endpoints,
                "url": service_url
            }
            
            logger.info(f"Initialized connector for {service_key} service at {service_url}")
        
        # Build reverse map on initialization
        self._build_entity_to_service_map()
        
        logger.info(f"Initialized EMoneyMasterConnector with {len(self.connectors)} service connectors")
    
    def _build_entity_to_service_map(self):
        """Build a reverse map from entity types to service keys."""
        for service_key, entity_types in self.SERVICE_ENTITY_MAP.items():
            for entity_type in entity_types:
                self.ENTITY_TO_SERVICE_MAP[entity_type] = service_key
    
    def _get_service_for_entity(self, entity_type: str) -> Optional[str]:
        """
        Determine which service handles a given entity type.
        
        Args:
            entity_type: The entity type to look up
            
        Returns:
            str: Service key that handles this entity type, or None if not found
        """
        entity_type_lower = entity_type.lower() if isinstance(entity_type, str) else entity_type
        return self.ENTITY_TO_SERVICE_MAP.get(entity_type_lower)
    
    def _get_connector_info(self, service_key: str) -> Optional[Dict[str, Any]]:
        """
        Get the connector information for a service key.
        
        Args:
            service_key: The service key
            
        Returns:
            Dict with connector, endpoints, and url
        """
        return self.connectors.get(service_key)
    
    def _get_endpoint_path(self, service_key: str, endpoint_key: str, **path_params) -> str:
        """
        Get the path for a specific endpoint, substituting path parameters if needed.
        
        Args:
            service_key: The service key
            endpoint_key: Key of the endpoint in STANDARD_ENDPOINTS
            **path_params: Path parameters to substitute
            
        Returns:
            str: Endpoint path
        """
        connector_info = self._get_connector_info(service_key)
        if not connector_info:
            logger.error(f"Service {service_key} not found")
            return ""
        
        endpoints = connector_info.get("endpoints", {})
        endpoint = endpoints.get(endpoint_key)
        
        if not endpoint:
            logger.error(f"Endpoint {endpoint_key} not found for {service_key}")
            return ""
            
        path = endpoint.get("path", "")
        
        # Substitute path parameters
        if path_params:
            for param_name, param_value in path_params.items():
                path = path.replace(f"{{{param_name}}}", str(param_value))
                
        return path.lstrip("/")
    
    def _ensure_service_scan_id(self, scan_id: str, service_key: str) -> str:
        """
        Ensure the scan_id has the service suffix.
        
        Args:
            scan_id: The scan ID (with or without service suffix)
            service_key: The service key to append if missing
            
        Returns:
            str: Scan ID with service suffix
        """
        if not scan_id.endswith(f"-{service_key}"):
            service_scan_id = f"{scan_id}-{service_key}"
            logger.debug(f"Added service suffix to scan_id: {scan_id} -> {service_scan_id}")
            return service_scan_id
        return scan_id
    
    def _route_scan_by_entities(self, scan_config: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Route entity types to their appropriate service connectors.
        
        Args:
            scan_config: Scan configuration containing entity types
            
        Returns:
            Dict mapping service_key -> list of entity types for that service
        """
        config = scan_config.get("config", scan_config)
        entity_types = config.get("type", [])
        
        # Ensure entity_types is a list
        if isinstance(entity_types, str):
            entity_types = [entity_types]
        
        # Route entities to services
        service_routes = {}
        unrouted_entities = []
        
        for entity_type in entity_types:
            service_key = self._get_service_for_entity(entity_type)
            if service_key:
                if service_key not in service_routes:
                    service_routes[service_key] = []
                service_routes[service_key].append(entity_type)
            else:
                unrouted_entities.append(entity_type)
        
        if unrouted_entities:
            logger.warning(f"Could not route entity types to services: {unrouted_entities}")
        
        logger.info(f"Routed entities to services: {service_routes}")
        return service_routes
    
    async def health_check(self, service_key: str) -> Dict[str, Any]:
        """
        Check if a specific service is healthy.
        
        Args:
            service_key: The service to check
            
        Returns:
            Dict[str, Any]: Health status response
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            path = self._get_endpoint_path(service_key, "health")
            connector = connector_info["connector"]
            return await connector.get(path)
        except Exception as e:
            logger.error(f"{service_key} service health check failed: {str(e)}")
            raise ServiceConnectionError(f"{service_key} service unavailable: {str(e)}")
    
    async def get_stats(self, service_key: str) -> Dict[str, Any]:
        """
        Get service statistics.
        
        Args:
            service_key: The service to get stats from
            
        Returns:
            Dict[str, Any]: Service statistics
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            path = self._get_endpoint_path(service_key, "stats")
            connector = connector_info["connector"]
            return await connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get {service_key} service stats: {str(e)}")
            raise ServiceConnectionError(f"Stats retrieval failed: {str(e)}")
    
    async def start_scan(self, scan_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a data extraction scan with EMoney JWT authentication.
        
        Expected input format (orchestrator):
        {
            "config": {
                "scanId": "emoney-scan-2025-001321",
                "organizationId": "org-12345",
                "type": ["client", "contact", "account", "role"],
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
                    "batchSize": 100
                }
            }
        }
        
        For EMoney servers, we pass through the JWT authentication as-is.
        The EMoney server will validate and handle them directly.
        
        Args:
            scan_config: Scan configuration with structure shown above
            
        Returns:
            Dict[str, Any]: Scan initialization response with scan_id
        """
        try:
            # Validate scan config structure
            if not scan_config or not isinstance(scan_config, dict):
                scan_config = {"config": DEFAULT_SCAN_CONFIG.copy()}
            
            # Ensure the config is wrapped in a "config" object
            if "config" not in scan_config:
                scan_config = {"config": scan_config}
            
            # Route entities to appropriate services
            service_routes = self._route_scan_by_entities(scan_config)
            
            if not service_routes:
                raise ServiceConnectionError("No valid entity types found in scan configuration")
            
            # Get base config
            config = scan_config["config"]
            
            # Ensure required fields exist
            if "organizationId" not in config:
                config["organizationId"] = "org-12345"
            
            # Generate a scanId if not provided
            if "scanId" not in config:
                import uuid
                config["scanId"] = f"emoney-master-2025-{str(uuid.uuid4())[:6]}"
            
            base_scan_id = config["scanId"]
            
            # Handle EMoney JWT authentication
            if "auth" in config:
                auth_config = config["auth"]
                
                # Check if JWT credentials are provided
                if "jwt_token" in auth_config and "client_id" in auth_config:
                    logger.info("EMoney JWT credentials detected, passing through to server for validation")
                elif "accessToken" in auth_config:
                    logger.info("Access token already present in config")
                else:
                    logger.warning("Auth config present but missing required EMoney JWT fields")
                    config["auth"] = {
                        "api_key": "emoney-api-key-67890",
                        "client_id": "emoney-client-id-12345",
                        "firm_id": "firm-12345",
                        "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                        "scope": "API"
                    }
            else:
                logger.warning("No auth configuration provided in scan config")
                config["auth"] = {
                    "api_key": "emoney-api-key-67890",
                    "client_id": "emoney-client-id-12345",
                    "firm_id": "firm-12345",
                    "jwt_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                    "scope": "API"
                }
            
            # Ensure filters exist with proper structure
            if "filters" not in config:
                config["filters"] = {
                    "dateRange": {
                        "startDate": "2025-01-01",
                        "endDate": "2025-12-31"
                    }
                }
            elif "dateRange" not in config["filters"]:
                config["filters"]["dateRange"] = {
                    "startDate": "2025-01-01",
                    "endDate": "2025-12-31"
                }
            
            # Validate and fix date range if needed
            if "dateRange" in config["filters"]:
                date_range = config["filters"]["dateRange"]
                start_date = date_range.get("startDate")
                end_date = date_range.get("endDate")
                
                # Check if dates are in correct order
                if start_date and end_date:
                    try:
                        from datetime import datetime
                        start = datetime.fromisoformat(start_date)
                        end = datetime.fromisoformat(end_date)
                        
                        if start > end:
                            logger.warning(f"Start date {start_date} is after end date {end_date}, swapping them")
                            config["filters"]["dateRange"]["startDate"] = end_date
                            config["filters"]["dateRange"]["endDate"] = start_date
                    except Exception as date_error:
                        logger.warning(f"Could not validate date range: {date_error}")
            
            # Handle batchSize
            batch_size = config["filters"].get("batchSize", 100)
            config["filters"]["batchSize"] = batch_size
            
            # Remove includeInactive as most services don't support it
            if "includeInactive" in config["filters"]:
                del config["filters"]["includeInactive"]
                logger.debug(f"Removed unsupported 'includeInactive' filter")
            
            # Start scans for each service
            scan_results = {}
            errors = {}
            
            for service_key, entity_types in service_routes.items():
                try:
                    # Create service-specific scan config
                    service_scan_config = {
                        "config": {
                            "scanId": f"{base_scan_id}-{service_key}",
                            "organizationId": config["organizationId"],
                            "type": entity_types,
                            "auth": config["auth"].copy(),
                            "filters": config["filters"].copy()
                        }
                    }
                    
                    logger.info(f"Starting {service_key} scan with ID {service_scan_config['config']['scanId']}")
                    logger.debug(f"Scan config being sent: {json.dumps(service_scan_config, indent=2)}")
                    
                    # Get the endpoint path and connector
                    connector_info = self._get_connector_info(service_key)
                    if connector_info:
                        path = self._get_endpoint_path(service_key, "scan_start")
                        connector = connector_info["connector"]
                        result = await connector.post(path, json_data=service_scan_config)
                        scan_results[service_key] = result
                    else:
                        logger.error(f"No connector found for service: {service_key}")
                        errors[service_key] = f"Connector not found"
                        
                except Exception as e:
                    error_details = str(e)
                    if hasattr(e, 'response') and e.response is not None:
                        try:
                            if hasattr(e.response, 'text'):
                                error_details = f"{error_details}\nResponse body: {e.response.text}"
                            elif hasattr(e.response, 'json'):
                                try:
                                    response_json = e.response.json()
                                    error_details = f"{error_details}\nResponse JSON: {response_json}"
                                except:
                                    pass
                            
                            if hasattr(e.response, 'request'):
                                request = e.response.request
                                logger.error(f"Request URL: {request.url}")
                                logger.error(f"Request method: {request.method}")
                                if hasattr(request, 'content'):
                                    logger.error(f"Request body: {request.content}")
                        except Exception as log_error:
                            logger.warning(f"Could not extract response details: {log_error}")
                    
                    logger.error(f"Failed to start {service_key} scan: {error_details}")
                    errors[service_key] = error_details
            
            # Return aggregated response
            response = {
                "master_scan_id": base_scan_id,
                "services": scan_results,
                "status": "partial" if errors else "success",
                "total_services": len(service_routes),
                "successful_services": len(scan_results),
                "failed_services": len(errors)
            }
            
            if errors:
                response["errors"] = errors
            
            return response
            
        except Exception as e:
            error_details = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    if hasattr(e.response, 'text'):
                        error_details = f"{error_details}\nResponse body: {e.response.text}"
                    elif hasattr(e.response, 'json'):
                        try:
                            response_json = e.response.json()
                            error_details = f"{error_details}\nResponse JSON: {response_json}"
                        except:
                            pass
                    
                    if hasattr(e.response, 'request'):
                        request = e.response.request
                        logger.error(f"Request URL: {request.url}")
                        logger.error(f"Request method: {request.method}")
                        if hasattr(request, 'content'):
                            logger.error(f"Request body: {request.content}")
                except Exception as log_error:
                    logger.warning(f"Could not extract response details: {log_error}")
            
            logger.error(f"Failed to start master scan: {error_details}")
            raise ServiceConnectionError(f"Scan initialization failed: {error_details}")
    
    async def get_scan_status(self, scan_id: str, service_key: str) -> Dict[str, Any]:
        """
        Get the status of a running scan.
        
        Args:
            scan_id: ID of the scan to check (with or without service suffix)
            service_key: The service to check
            
        Returns:
            Dict[str, Any]: Scan status details
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            # Ensure the scan_id has the service suffix
            service_scan_id = self._ensure_service_scan_id(scan_id, service_key)
            
            path = self._get_endpoint_path(service_key, "scan_status", scan_id=service_scan_id)
            connector = connector_info["connector"]
            return await connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get scan status for {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Scan status retrieval failed: {str(e)}")
    
    async def cancel_scan(self, scan_id: str, service_key: str) -> Dict[str, Any]:
        """
        Cancel a running scan.
        
        Args:
            scan_id: ID of the scan to cancel (with or without service suffix)
            service_key: The service to cancel
            
        Returns:
            Dict[str, Any]: Cancellation response
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            # Ensure the scan_id has the service suffix
            service_scan_id = self._ensure_service_scan_id(scan_id, service_key)
            
            path = self._get_endpoint_path(service_key, "scan_cancel", scan_id=service_scan_id)
            connector = connector_info["connector"]
            return await connector.post(path)
        except Exception as e:
            logger.error(f"Failed to cancel scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Scan cancellation failed: {str(e)}")
    
    async def list_scans(self, service_key: str, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        List all scans with pagination.
        
        Args:
            service_key: The service to list scans from
            page: Page number
            limit: Items per page
            
        Returns:
            Dict[str, Any]: List of scans with pagination info
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            path = self._get_endpoint_path(service_key, "scan_list")
            connector = connector_info["connector"]
            return await connector.get(path, params={"page": page, "limit": limit})
        except Exception as e:
            logger.error(f"Failed to list scans: {str(e)}")
            raise ServiceConnectionError(f"Scan listing failed: {str(e)}")
    
    async def get_scan_statistics(self, service_key: str) -> Dict[str, Any]:
        """
        Get statistics about scans.
        
        Args:
            service_key: The service to get statistics from
            
        Returns:
            Dict[str, Any]: Scan statistics
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            path = self._get_endpoint_path(service_key, "scan_statistics")
            connector = connector_info["connector"]
            return await connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get scan statistics: {str(e)}")
            raise ServiceConnectionError(f"Scan statistics retrieval failed: {str(e)}")
    
    async def remove_scan(self, scan_id: str, service_key: str) -> Dict[str, Any]:
        """
        Remove a scan and its data.
        
        Args:
            scan_id: ID of the scan to remove (with or without service suffix)
            service_key: The service to remove from
            
        Returns:
            Dict[str, Any]: Removal response
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            # Ensure the scan_id has the service suffix
            service_scan_id = self._ensure_service_scan_id(scan_id, service_key)
            
            path = self._get_endpoint_path(service_key, "scan_remove", scan_id=service_scan_id)
            connector = connector_info["connector"]
            return await connector.delete(path)
        except Exception as e:
            logger.error(f"Failed to remove scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Scan removal failed: {str(e)}")
    
    async def get_available_tables(self, scan_id: str, service_key: str) -> Dict[str, Any]:
        """
        Get available result tables for a scan.
        
        Args:
            scan_id: ID of the completed scan (with or without service suffix)
            service_key: The service to get tables from
            
        Returns:
            Dict[str, Any]: Available tables
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            # Ensure the scan_id has the service suffix
            service_scan_id = self._ensure_service_scan_id(scan_id, service_key)
            
            path = self._get_endpoint_path(service_key, "results_tables", scan_id=service_scan_id)
            connector = connector_info["connector"]
            return await connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get tables for scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Tables retrieval failed: {str(e)}")
    
    async def get_scan_results(self, scan_id: str, service_key: str) -> Dict[str, Any]:
        """
        Get the results of a completed scan.
        
        Args:
            scan_id: ID of the completed scan (with or without service suffix)
            service_key: The service to get results from
            
        Returns:
            Dict[str, Any]: Scan results data
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            # Ensure the scan_id has the service suffix
            service_scan_id = self._ensure_service_scan_id(scan_id, service_key)
            
            path = self._get_endpoint_path(service_key, "results_data", scan_id=service_scan_id)
            connector = connector_info["connector"]
            return await connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get results for scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Results retrieval failed: {str(e)}")
    
    async def get_pipeline_info(self, service_key: str) -> Dict[str, Any]:
        """
        Get information about the DLT pipeline.
        
        Args:
            service_key: The service to get pipeline info from
            
        Returns:
            Dict[str, Any]: Pipeline information
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            path = self._get_endpoint_path(service_key, "pipeline_info")
            connector = connector_info["connector"]
            return await connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get pipeline info: {str(e)}")
            raise ServiceConnectionError(f"Pipeline info retrieval failed: {str(e)}")
    
    async def cleanup_old_scans(self, service_key: str, days: int = 30) -> Dict[str, Any]:
        """
        Clean up old scans.
        
        Args:
            service_key: The service to cleanup
            days: Age in days for cleanup threshold
            
        Returns:
            Dict[str, Any]: Cleanup response
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            path = self._get_endpoint_path(service_key, "maintenance_cleanup")
            connector = connector_info["connector"]
            return await connector.post(path, json_data={"days": days})
        except Exception as e:
            logger.error(f"Failed to clean up old scans: {str(e)}")
            raise ServiceConnectionError(f"Cleanup operation failed: {str(e)}")
    
    async def detect_crashed_jobs(self, service_key: str) -> Dict[str, Any]:
        """
        Detect crashed jobs.
        
        Args:
            service_key: The service to check
            
        Returns:
            Dict[str, Any]: Crashed jobs detection response
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            path = self._get_endpoint_path(service_key, "maintenance_detect_crashed")
            connector = connector_info["connector"]
            return await connector.post(path)
        except Exception as e:
            logger.error(f"Failed to detect crashed jobs: {str(e)}")
            raise ServiceConnectionError(f"Crashed jobs detection failed: {str(e)}")
    
    async def pause_scan(self, scan_id: str, service_key: str) -> Dict[str, Any]:
        """
        Pause a running scan.
        
        Args:
            scan_id: ID of the scan to pause (with or without service suffix)
            service_key: The service to pause
            
        Returns:
            Dict[str, Any]: Pause response
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            # Ensure the scan_id has the service suffix
            service_scan_id = self._ensure_service_scan_id(scan_id, service_key)
            
            path = self._get_endpoint_path(service_key, "scan_pause", scan_id=service_scan_id)
            connector = connector_info["connector"]
            return await connector.post(path)
        except Exception as e:
            logger.error(f"Failed to pause scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Scan pause failed: {str(e)}")

    async def resume_scan(self, scan_id: str, service_key: str) -> Dict[str, Any]:
        """
        Resume a paused scan.
        
        Args:
            scan_id: ID of the scan to resume (with or without service suffix)
            service_key: The service to resume
            
        Returns:
            Dict[str, Any]: Resume response
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            # Ensure the scan_id has the service suffix
            service_scan_id = self._ensure_service_scan_id(scan_id, service_key)
            
            path = self._get_endpoint_path(service_key, "scan_resume", scan_id=service_scan_id)
            connector = connector_info["connector"]
            return await connector.post(path)
        except Exception as e:
            logger.error(f"Failed to resume scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Scan resume failed: {str(e)}")
    
    async def stream_data(self, scan_id: str, service_key: str, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        Stream data from a completed scan with pagination.
        
        Args:
            scan_id: ID of the completed scan (with or without service suffix)
            service_key: The service to stream from
            offset: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dict[str, Any]: Streamed data response
        """
        try:
            connector_info = self._get_connector_info(service_key)
            if not connector_info:
                raise ServiceConnectionError(f"Unknown service: {service_key}")
            
            # Ensure the scan_id has the service suffix
            service_scan_id = self._ensure_service_scan_id(scan_id, service_key)
            
            path = self._get_endpoint_path(service_key, "stream_data", scan_id=service_scan_id)
            connector = connector_info["connector"]
            return await connector.get(path, params={"offset": offset, "limit": limit})
        except Exception as e:
            logger.error(f"Failed to stream data for scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Data streaming failed: {str(e)}")