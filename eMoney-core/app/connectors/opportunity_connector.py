import logging
import json
from typing import Dict, Any, Optional, List
from app.connectors.api_connector import SimpleAPIConnector
from app.core.exceptions import ServiceConnectionError
from app.settings import get_settings
from app.service_config import (
    STANDARD_ENDPOINTS,
    WEALTHBOX_SERVICES,
    DEFAULT_SCAN_CONFIG,
)

logger = logging.getLogger(__name__)


class WealthboxOpportunityConnector:
    """
    Connector for Wealthbox Opportunity Service data extraction operations.
    Handles opportunity entity scanning and data extraction for deals, opportunities,
    opportunity stages, pipelines, and campaigns.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: float = 5.0):
        """
        Initialize the Opportunity connector with configuration from settings.

        Args:
            api_key: Optional API key override (defaults to settings)
            timeout: Request timeout in seconds
        """
        settings = get_settings()
        self.service_key = "opportunity"
        self.service_url = settings.get_service_url(self.service_key)

        if not self.service_url:
            logger.error(
                f"No URL configured for {self.service_key} service in {settings.ENVIRONMENT} environment"
            )

        # Get the endpoints for this service
        self.service_config = WEALTHBOX_SERVICES.get(self.service_key, {})
        self.endpoints = self.service_config.get("endpoints", STANDARD_ENDPOINTS.copy())

        self.api_key = api_key or settings.API_KEY
        self.connector = SimpleAPIConnector(
            base_url=self.service_url, api_key=self.api_key, timeout=timeout
        )

        logger.info(f"Initialized WealthboxOpportunityConnector for {self.service_url}")

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
        Check if the Opportunity service is healthy.

        Returns:
            Dict[str, Any]: Health status response
        """
        try:
            path = self._get_endpoint_path("health")
            return await self.connector.get(path)
        except Exception as e:
            logger.error(f"Opportunity service health check failed: {str(e)}")
            raise ServiceConnectionError(f"Opportunity service unavailable: {str(e)}")

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
            logger.error(f"Failed to get opportunity service stats: {str(e)}")
            raise ServiceConnectionError(f"Stats retrieval failed: {str(e)}")

    async def _get_access_token(self, auth_config: Dict[str, Any]) -> Optional[str]:
        """
        Generate a mock access token for development/testing with mock servers.

        For mock servers, we don't need real OAuth - just create a token-like string
        that satisfies API validation requirements.

        Args:
            auth_config: OAuth2 configuration with client_id, client_secret, etc.

        Returns:
            str: Mock access token
        """
        try:
            logger.info("Generating mock access token for development/testing")

            # Create a simple mock token that includes the client_id for traceability
            client_id = auth_config.get("client_id", "mock-client")

            # Generate a simple mock token format: mock_<client_id>_<timestamp>
            import time

            timestamp = int(time.time())
            mock_token = f"mock_token_{client_id}_{timestamp}"

            logger.info(f"Generated mock access token: {mock_token[:50]}...")
            return mock_token

        except Exception as e:
            logger.error(f"Failed to generate mock token: {str(e)}")
            # Return a fallback token
            return "mock_token_fallback"

    async def start_scan(self, scan_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Start a data extraction scan for auth entities.

        Expected format:
        {
          "config": {
            "scanId": "scan-id-string",
            "organizationId": "org-12345",
            "type": ["entity_type1" ],
            "auth": {
              "apiKey": "your-api-key",
              "username": "optional-username",
              "password": "optional-password"
            },
            "filters": {
              "dateRange": {
                "startDate": "YYYY-MM-DD",
                "endDate": "YYYY-MM-DD"
              },
              "additionalFilters": {}
            }
          }
        }

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
            if "type" not in config or not config["type"]:
                config["type"] = []
            if "auth" not in config:
                config["auth"] = {
                    "client_id": "wealthbox-client-123456789",
                    "client_secret": "c1ient-s3cret-v4lue-example",
                    "grant_type": "client_credentials",
                    "scope": "read",
                }
            if "filters" not in config:
                config["filters"] = {}

            # Generate a scanId if not provided
            if "scanId" not in config:
                import uuid
                config["scanId"] = f"scan-{str(uuid.uuid4())[:8]}-{self.service_key}"

            logger.info(
                f"Starting {self.service_key} scan with ID {config.get('scanId')}"
            )

            # Get the endpoint path from standard endpoints
            path = self._get_endpoint_path("scan_start")

            # Make the API request
            return await self.connector.post(path, json_data=scan_config)
        except Exception as e:
            logger.error(f"Failed to start {self.service_key} scan: {str(e)}")
            raise ServiceConnectionError(f"Scan initialization failed: {str(e)}")

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
            return await self.connector.get(path, params={"page": page, "limit": limit})
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
            return await self.connector.post(path, json_data={"days": days})
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

    async def stream_data(
        self, scan_id: str, offset: int = 0, limit: int = 100
    ) -> Dict[str, Any]:
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
                path, params={"offset": offset, "limit": limit}
            )
        except Exception as e:
            logger.error(f"Failed to stream data for scan {scan_id}: {str(e)}")
            raise ServiceConnectionError(f"Data streaming failed: {str(e)}")
