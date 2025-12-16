import time
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from config import get_config


class APIService:
    """
    Service for interacting with eMoney Identity API
    Handles data retrieval for identity objects:
    User, Office, Role, Permission, SharingRule, Logon
    """

    def __init__(self, base_url: str = None):
        self.config = get_config()
        self.base_url = (base_url or self.config.EMONEY_API_BASE_URL).rstrip("/")
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.access_token = None

        # Load endpoint configurations from config
        self.EMONEY_USERS_ENDPOINT = self.config.EMONEY_USERS_ENDPOINT
        self.EMONEY_OFFICES_ENDPOINT = self.config.EMONEY_OFFICES_ENDPOINT
        self.EMONEY_ROLES_ENDPOINT = self.config.EMONEY_ROLES_ENDPOINT
        self.EMONEY_PERMISSIONS_ENDPOINT = self.config.EMONEY_PERMISSIONS_ENDPOINT
        self.EMONEY_SHARINGRULES_ENDPOINT = self.config.EMONEY_SHARING_RULES_ENDPOINT
        self.EMONEY_LOGONS_ENDPOINT = self.config.EMONEY_LOGONS_ENDPOINT

        # Load retry and timeout settings from config
        self.api_timeout = self.config.EMONEY_API_TIMEOUT
        self.retry_attempts = self.config.EMONEY_RETRY_ATTEMPTS
        self.retry_delay = self.config.EMONEY_RETRY_DELAY

        # Default headers
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "eMoney-Identity/1.0",
            }
        )

    # ---------------------------
    # AUTHENTICATION
    # ---------------------------
    def authenticate(self, auth_config: Dict[str, Any] = None) -> str:
        """
        Authenticate with eMoney Identity API

        Args:
            auth_config: Optional authentication config (not used for mock server)

        Returns:
            Access token (can be any string for mock server)
        """
        try:
            self.logger.info("Authenticating with eMoney Identity API")

            # For the mock server, the token can be anything
            self.access_token = "anything"

            # Update session headers with the token
            self.session.headers.update(
                {"Authorization": f"Bearer {self.access_token}"}
            )

            self.logger.info("Authentication successful")
            return self.access_token

        except Exception as e:
            self.logger.error(f"Authentication failed: {str(e)}")
            raise

    # ---------------------------
    # REQUEST HANDLER
    # ---------------------------
    def _make_request(
        self, endpoint: str, params: Dict = None, method: str = "GET", data: Dict = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        max_retries = self.retry_attempts

        # Ensure we have an authentication token
        if not self.access_token:
            self.authenticate()

        self.logger.info(f"Making {method} request to {url} with params: {params}")

        for attempt in range(max_retries):
            try:
                if method == "GET":
                    response = self.session.get(url, params=params, timeout=self.api_timeout)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                self.logger.info(f"Response status code: {response.status_code}")

                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    self.logger.warning(
                        f"Rate limited. Waiting {retry_after} seconds..."
                    )
                    time.sleep(retry_after)
                    continue

                # If token expired (401), try to refresh it once
                if response.status_code == 401:
                    self.logger.warning("Token expired. Re-authenticating...")
                    self.authenticate()
                    continue

                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                self.logger.error(f"HTTP error: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                else:
                    wait_time = (2**attempt) * self.retry_delay
                    self.logger.warning(
                        f"Request failed with status {response.status_code}, retrying in {wait_time}s... ({attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request exception: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                else:
                    wait_time = (2**attempt) * self.retry_delay
                    time.sleep(wait_time)

        raise Exception(f"Failed to complete request after {max_retries} attempts")


    # ---------------------------
    # IDENTITY OBJECTS (Updated with pagination)
    # ---------------------------
    def get_users(
        self,
        page: int = 1,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get user records

        Args:
            page: Page number to retrieve (pagination)
            limit: Maximum number of records per page
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by (e.g. 'last_name')

        Returns:
            Dict with 'users' key containing list of records
        """
        endpoint = self.EMONEY_USERS_ENDPOINT
        params = {"page": page, "limit": min(limit, 1000)}
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
        return self._make_request(endpoint, params)

    def get_offices(
        self,
        page: int = 1,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get office records

        Args:
            page: Page number to retrieve (pagination)
            limit: Maximum number of records per page
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by

        Returns:
            Dict with 'offices' key containing list of records
        """
        endpoint = self.EMONEY_OFFICES_ENDPOINT
        params = {"page": page, "limit": min(limit, 1000)}
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
        return self._make_request(endpoint, params)

    def get_roles(
        self,
        page: int = 1,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get role records

        Args:
            page: Page number to retrieve (pagination)
            limit: Maximum number of records per page
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by

        Returns:
            Dict with 'roles' key containing list of records
        """
        endpoint = self.EMONEY_ROLES_ENDPOINT
        params = {"page": page, "limit": min(limit, 1000)}
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
        return self._make_request(endpoint, params)

    def get_permissions(
        self,
        page: int = 1,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get permission records

        Args:
            page: Page number to retrieve (pagination)
            limit: Maximum number of records per page
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by

        Returns:
            Dict with 'permissions' key containing list of records
        """
        endpoint = self.EMONEY_PERMISSIONS_ENDPOINT
        params = {"page": page, "limit": min(limit, 1000)}
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
        return self._make_request(endpoint, params)

    def get_sharingrules(
        self,
        page: int = 1,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get sharingrule records

        Args:
            page: Page number to retrieve (pagination)
            limit: Maximum number of records per page
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by

        Returns:
            Dict with 'sharingrules' key containing list of records
        """
        endpoint = self.EMONEY_SHARINGRULES_ENDPOINT
        params = {"page": page, "limit": min(limit, 1000)}
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
        return self._make_request(endpoint, params)

    def get_logons(
        self,
        page: int = 1,
        limit: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get logon records

        Args:
            page: Page number to retrieve (pagination)
            limit: Maximum number of records per page
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by

        Returns:
            Dict with 'logons' key containing list of records
        """
        endpoint = self.EMONEY_LOGONS_ENDPOINT
        params = {"page": page, "limit": min(limit, 1000)}
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
        return self._make_request(endpoint, params)