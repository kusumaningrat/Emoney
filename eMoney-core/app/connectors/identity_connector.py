import logging
import json
from typing import Dict, Any, Optional, List
from app.connectors.api_connector import SimpleAPIConnector
from app.core.exceptions import ServiceConnectionError
from app.settings import get_settings
from app.service_config import STANDARD_ENDPOINTS, WEALTHBOX_SERVICES, DEFAULT_SCAN_CONFIG

logger = logging.getLogger(__name__)

class WealthboxIdentityConnector:
    """
    Connector for Wealthbox Identity Service data extraction operations.
    Handles identity entity scanning and data extraction for users, user profiles,
    workspaces, roles, and permissions.
    """
    
    # Supported specific entity types for this service
    SUPPORTED_ENTITY_TYPES = ["user", "user_profile", "workspace", "role", "permission"]
    
    def __init__(self, api_key: Optional[str] = None, timeout: float = 5.0):
        """
        Initialize the Identity connector with configuration from settings.
        
        Args:
            api_key: Optional API key override (defaults to settings)
            timeout: Request timeout in seconds
        """
        settings = get_settings()
        self.service_key = "identity"
        self.service_url = settings.get_service_url(self.service_key)
        
        if not self.service_url:
            logger.error(f"No URL configured for {self.service_key} service in {settings.ENVIRONMENT} environment")
        
        # Get the endpoints for this service
        self.service_config = WEALTHBOX_SERVICES.get(self.service_key, {})
        self.endpoints = self.service_config.get("endpoints", STANDARD_ENDPOINTS.copy())
        
        self.api_key = api_key or settings.API_KEY
        self.connector = SimpleAPIConnector(
            base_url=self.service_url,
            api_key=self.api_key,
            timeout=timeout
        )
        
        logger.info(f"Initialized WealthboxIdentityConnector for {self.service_url}")
    
    def _get_endpoint_path(self, endpoint_key: str, **path_params) -> str:
        """
        Get the path for a specific endpoint, substituting path parameters if needed.
        
        Args:
            endpoint_key: Key of the endpoint in STANDARD_ENDPOINTS
            **path_params: Path parameters to substitute
            
        Returns:
            str: Endpoint path
        """
        endpoint = self.endpoints.get(endpoint_key)
        if not endpoint:
            logger.error(f"Endpoint {endpoint_key} not found")
            return ""
            
        path = endpoint.get("path", "")
        
        # Substitute path parameters
        if path_params:
            for param_name, param_value in path_params.items():
                path = path.replace(f"{{{param_name}}}", str(param_value))
                
        return path.lstrip("/")
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Check if the Identity service is healthy.
        
        Returns:
            Dict[str, Any]: Health status response
        """
        try:
            path = self._get_endpoint_path("health")
            return await self.connector.get(path)
        except Exception as e:
            logger.error(f"Identity service health check failed: {str(e)}")
            raise ServiceConnectionError(f"Identity service unavailable: {str(e)}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """
        Get service statistics.
        
        Returns:
            Dict[str, Any]: Service statistics
        """
        try:
            path = self._get_endpoint_path("stats")
            return await self.connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get identity service stats: {str(e)}")
            raise ServiceConnectionError(f"Stats retrieval failed: {str(e)}")
    
    async def start_scan(self, scan_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a data extraction scan for identity entities with Wealthbox OAuth support.
        
        Expected input format (orchestrator):
        {
            "config": {
                "scanId": "wealthbox-identity-scan-2025-001",
                "organizationId": "org-12345",
                "type": ["user", "user_profile", "workspace", "role", "permission"],
                "auth": {
                    "client_id": "wealthbox-client-123456789",
                    "client_secret": "c1ient-s3cret-v4lue-example",
                    "grant_type": "client_credentials",
                    "scope": "read"
                },
                "filters": {
                    "dateRange": {
                        "startDate": "2025-01-01",
                        "endDate": "2025-12-31"
                    },
                    "batchSize": 100,
                    "includeArchived": false
                }
            }
        }
        
        For mock servers, we pass through the OAuth credentials as-is.
        The mock server will validate and handle them directly.
        
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
            
            # Ensure required fields exist
            config = scan_config["config"]
            if "organizationId" not in config:
                config["organizationId"] = ""
                
            # Handle type field - ensure it's a list
            if "type" not in config or not config["type"]:
                config["type"] = []
            
            # Convert string to list if needed
            if isinstance(config["type"], str):
                config["type"] = [config["type"]]
                    
            # Normalize and expand entity types
            # The generic "identity" type should be expanded to all specific types
            expanded_types = []
            for entity_type in config["type"]:
                entity_type_lower = entity_type.lower() if isinstance(entity_type, str) else entity_type
                
                # If the generic "identity" type is requested, expand to all specific types
                if entity_type_lower == "identity":
                    logger.info(f"Expanding generic 'identity' type to specific types: {self.SUPPORTED_ENTITY_TYPES}")
                    expanded_types.extend(self.SUPPORTED_ENTITY_TYPES)
                else:
                    # Keep specific types as-is
                    expanded_types.append(entity_type_lower)
            
            # Remove duplicates while preserving order
            config["type"] = list(dict.fromkeys(expanded_types))
            logger.debug(f"Final entity types after expansion: {config['type']}")
            
            # FIXED: Pass through OAuth credentials directly to mock server
            # The mock server expects and validates OAuth credentials, not access tokens
            if "auth" in config:
                auth_config = config["auth"]
                
                # Check if OAuth credentials are provided
                if all(k in auth_config for k in ["client_id", "client_secret"]):
                    logger.info("OAuth credentials detected, passing through to mock server for validation")
                    # Keep the original OAuth credentials - don't transform them
                    # The mock server will handle validation
                elif "accessToken" in auth_config:
                    # If somehow an access token is already present, that's fine too
                    logger.info("Access token already present in config")
                else:
                    logger.warning("Auth config present but missing required fields")
            else:
                logger.warning("No auth configuration provided in scan config")
                
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
                            # Swap the dates
                            config["filters"]["dateRange"]["startDate"] = end_date
                            config["filters"]["dateRange"]["endDate"] = start_date
                    except Exception as date_error:
                        logger.warning(f"Could not validate date range: {date_error}")
            
            # FIXED: Remove fields that the mock server doesn't recognize
            # Remove batchSize from filters
            batch_size = config["filters"].pop("batchSize", None)
            if batch_size:
                logger.debug(f"Removed batchSize ({batch_size}) from filters (not supported by mock server)")
            
            # Remove includeArchived from filters if present
            include_archived = config["filters"].pop("includeArchived", None)
            if include_archived is not None:
                logger.debug(f"Removed includeArchived ({include_archived}) from filters (not supported by mock server)")
                
            # Generate a scanId if not provided
            if "scanId" not in config:
                import uuid
                config["scanId"] = f"wealthbox-{self.service_key}-scan-{str(uuid.uuid4())[:8]}"
                
            logger.info(f"Starting {self.service_key} scan with ID {config.get('scanId')}")
            logger.debug(f"Scan config being sent: {json.dumps(scan_config, indent=2)}")
                
            # Get the endpoint path from standard endpoints
            path = self._get_endpoint_path("scan_start")
            
            # Make the API request with the config
            return await self.connector.post(path, json_data=scan_config)
            
        except Exception as e:
            # Enhanced error logging to capture response details
            error_details = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    # Try to get response text/json for more context
                    if hasattr(e.response, 'text'):
                        error_details = f"{error_details}\nResponse body: {e.response.text}"
                    elif hasattr(e.response, 'json'):
                        try:
                            response_json = e.response.json()
                            error_details = f"{error_details}\nResponse JSON: {response_json}"
                        except:
                            pass
                    
                    # Log the full request details for debugging
                    if hasattr(e.response, 'request'):
                        request = e.response.request
                        logger.error(f"Request URL: {request.url}")
                        logger.error(f"Request method: {request.method}")
                        if hasattr(request, 'content'):
                            logger.error(f"Request body: {request.content}")
                except Exception as log_error:
                    logger.warning(f"Could not extract response details: {log_error}")
            
            logger.error(f"Failed to start {self.service_key} scan: {error_details}")
            raise ServiceConnectionError(f"Scan initialization failed: {error_details}")
    
    async def get_scan_status(self, scan_id: str) -> Dict[str, Any]:
        """
        Get the status of a running scan.
        
        Args:
            scan_id: ID of the scan to check
            
        Returns:
            Dict[str, Any]: Scan status details
        """
        try:
            path = self._get_endpoint_path("scan_status", scan_id=scan_id)
            return await self.connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get scan status for {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Scan status retrieval failed: {str(e)}")
    
    async def cancel_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Cancel a running scan.
        
        Args:
            scan_id: ID of the scan to cancel
            
        Returns:
            Dict[str, Any]: Cancellation response
        """
        try:
            path = self._get_endpoint_path("scan_cancel", scan_id=scan_id)
            return await self.connector.post(path)
        except Exception as e:
            logger.error(f"Failed to cancel scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Scan cancellation failed: {str(e)}")
    
    async def list_scans(self, page: int = 1, limit: int = 20) -> Dict[str, Any]:
        """
        List all scans with pagination.
        
        Args:
            page: Page number
            limit: Items per page
            
        Returns:
            Dict[str, Any]: List of scans with pagination info
        """
        try:
            path = self._get_endpoint_path("scan_list")
            return await self.connector.get(
                path, 
                params={"page": page, "limit": limit}
            )
        except Exception as e:
            logger.error(f"Failed to list scans: {str(e)}")
            raise ServiceConnectionError(f"Scan listing failed: {str(e)}")
    
    async def get_scan_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about scans.
        
        Returns:
            Dict[str, Any]: Scan statistics
        """
        try:
            path = self._get_endpoint_path("scan_statistics")
            return await self.connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get scan statistics: {str(e)}")
            raise ServiceConnectionError(f"Scan statistics retrieval failed: {str(e)}")
    
    async def remove_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Remove a scan and its data.
        
        Args:
            scan_id: ID of the scan to remove
            
        Returns:
            Dict[str, Any]: Removal response
        """
        try:
            path = self._get_endpoint_path("scan_remove", scan_id=scan_id)
            return await self.connector.delete(path)
        except Exception as e:
            logger.error(f"Failed to remove scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Scan removal failed: {str(e)}")
    
    async def get_available_tables(self, scan_id: str) -> Dict[str, Any]:
        """
        Get available result tables for a scan.
        
        Args:
            scan_id: ID of the completed scan
            
        Returns:
            Dict[str, Any]: Available tables
        """
        try:
            path = self._get_endpoint_path("results_tables", scan_id=scan_id)
            return await self.connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get tables for scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Tables retrieval failed: {str(e)}")
    
    async def get_scan_results(self, scan_id: str) -> Dict[str, Any]:
        """
        Get the results of a completed scan.
        
        Args:
            scan_id: ID of the completed scan
            
        Returns:
            Dict[str, Any]: Scan results data
        """
        try:
            path = self._get_endpoint_path("results_data", scan_id=scan_id)
            return await self.connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get results for scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Results retrieval failed: {str(e)}")
    
    async def get_pipeline_info(self) -> Dict[str, Any]:
        """
        Get information about the DLT pipeline.
        
        Returns:
            Dict[str, Any]: Pipeline information
        """
        try:
            path = self._get_endpoint_path("pipeline_info")
            return await self.connector.get(path)
        except Exception as e:
            logger.error(f"Failed to get pipeline info: {str(e)}")
            raise ServiceConnectionError(f"Pipeline info retrieval failed: {str(e)}")
    
    async def cleanup_old_scans(self, days: int = 30) -> Dict[str, Any]:
        """
        Clean up old scans.
        
        Args:
            days: Age in days for cleanup threshold
            
        Returns:
            Dict[str, Any]: Cleanup response
        """
        try:
            path = self._get_endpoint_path("maintenance_cleanup")
            return await self.connector.post(
                path,
                json_data={"days": days}
            )
        except Exception as e:
            logger.error(f"Failed to clean up old scans: {str(e)}")
            raise ServiceConnectionError(f"Cleanup operation failed: {str(e)}")
    
    async def detect_crashed_jobs(self) -> Dict[str, Any]:
        """
        Detect crashed jobs.
        
        Returns:
            Dict[str, Any]: Crashed jobs detection response
        """
        try:
            path = self._get_endpoint_path("maintenance_detect_crashed")
            return await self.connector.post(path)
        except Exception as e:
            logger.error(f"Failed to detect crashed jobs: {str(e)}")
            raise ServiceConnectionError(f"Crashed jobs detection failed: {str(e)}")
        
    async def pause_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Pause a running scan.
        
        Args:
            scan_id: ID of the scan to pause
            
        Returns:
            Dict[str, Any]: Pause response
        """
        try:
            path = self._get_endpoint_path("scan_pause", scan_id=scan_id)
            return await self.connector.post(path)
        except Exception as e:
            logger.error(f"Failed to pause scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Scan pause failed: {str(e)}")

    async def resume_scan(self, scan_id: str) -> Dict[str, Any]:
        """
        Resume a paused scan.
        
        Args:
            scan_id: ID of the scan to resume
            
        Returns:
            Dict[str, Any]: Resume response
        """
        try:
            path = self._get_endpoint_path("scan_resume", scan_id=scan_id)
            return await self.connector.post(path)
        except Exception as e:
            logger.error(f"Failed to resume scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Scan resume failed: {str(e)}")
        
    async def stream_data(self, scan_id: str, offset: int = 0, limit: int = 100) -> Dict[str, Any]:
        """
        Stream data from a completed scan with pagination.
        
        Args:
            scan_id: ID of the completed scan
            offset: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            Dict[str, Any]: Streamed data response
        """
        try:
            path = self._get_endpoint_path("stream_data", scan_id=scan_id)
            return await self.connector.get(
                path,
                params={"offset": offset, "limit": limit}
            )
        except Exception as e:
            logger.error(f"Failed to stream data for scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Data streaming failed: {str(e)}")