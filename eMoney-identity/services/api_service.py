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

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.config = get_config()
        self.access_token = None

        # eMoney Identity API endpoints from config
        self.EMONEY_USERS_ENDPOINT = self.config.EMONEY_USERS_ENDPOINT
        self.EMONEY_OFFICES_ENDPOINT = self.config.EMONEY_OFFICES_ENDPOINT
        self.EMONEY_ROLES_ENDPOINT = self.config.EMONEY_ROLES_ENDPOINT
        self.EMONEY_PERMISSIONS_ENDPOINT = self.config.EMONEY_PERMISSIONS_ENDPOINT
        self.EMONEY_SHARINGRULES_ENDPOINT = self.config.EMONEY_SHARING_RULES_ENDPOINT
        self.EMONEY_LOGONS_ENDPOINT = self.config.EMONEY_LOGONS_ENDPOINT

        # Default headers for eMoney Identity API
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
        max_retries = 3

        # Ensure we have an authentication token
        if not self.access_token:
            self.authenticate()

        self.logger.info(f"Making {method} request to {url} with params: {params}")

        for attempt in range(max_retries):
            try:
                if method == "GET":
                    response = self.session.get(url, params=params, timeout=30)
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
                    wait_time = (2**attempt) * 2
                    self.logger.warning(
                        f"Request failed with status {response.status_code}, retrying in {wait_time}s... ({attempt + 1}/{max_retries})"
                    )
                    time.sleep(wait_time)

            except requests.exceptions.RequestException as e:
                self.logger.error(f"Request exception: {str(e)}")
                if attempt == max_retries - 1:
                    raise
                else:
                    wait_time = (2**attempt) * 2
                    time.sleep(wait_time)

        raise Exception(f"Failed to complete request after {max_retries} attempts")

    # ---------------------------
    # IDENTITY OBJECTS (eMoney API pagination uses page & pageSize)
    # ---------------------------
    def get_users(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get user records from eMoney Identity API
        
        Endpoint: GET /users
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by (e.g. 'last_name')

        Returns:
            Dict with user records
        """
        endpoint = self.EMONEY_USERS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_user(self, user_id: str) -> Dict[str, Any]:
        """
        Get specific user by ID
        
        Endpoint: GET /users/{userId}
        
        Args:
            user_id: User ID

        Returns:
            User record
        """
        endpoint = f"{self.EMONEY_USERS_ENDPOINT}/{user_id}"
        return self._make_request(endpoint)

    def get_offices(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get office records from eMoney Identity API
        
        Endpoint: GET /offices
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by

        Returns:
            Dict with office records
        """
        endpoint = self.EMONEY_OFFICES_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_office(self, office_id: str) -> Dict[str, Any]:
        """
        Get specific office by ID
        
        Endpoint: GET /offices/{officeId}
        
        Args:
            office_id: Office ID

        Returns:
            Office record
        """
        endpoint = f"{self.EMONEY_OFFICES_ENDPOINT}/{office_id}"
        return self._make_request(endpoint)

    def get_roles(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get role records from eMoney Identity API
        
        Endpoint: GET /roles
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by

        Returns:
            Dict with role records
        """
        endpoint = self.EMONEY_ROLES_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_role(self, role_id: str) -> Dict[str, Any]:
        """
        Get specific role by ID
        
        Endpoint: GET /roles/{roleId}
        
        Args:
            role_id: Role ID

        Returns:
            Role record
        """
        endpoint = f"{self.EMONEY_ROLES_ENDPOINT}/{role_id}"
        return self._make_request(endpoint)

    def get_permissions(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get permission records from eMoney Identity API
        
        Endpoint: GET /permissions
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by

        Returns:
            Dict with permission records
        """
        endpoint = self.EMONEY_PERMISSIONS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_permission(self, permission_id: str) -> Dict[str, Any]:
        """
        Get specific permission by ID
        
        Endpoint: GET /permissions/{permissionId}
        
        Args:
            permission_id: Permission ID

        Returns:
            Permission record
        """
        endpoint = f"{self.EMONEY_PERMISSIONS_ENDPOINT}/{permission_id}"
        return self._make_request(endpoint)

    def get_sharingrules(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get sharingrule records from eMoney Identity API
        
        Endpoint: GET /sharingrules
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by

        Returns:
            Dict with sharingrule records
        """
        endpoint = self.EMONEY_SHARINGRULES_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_sharingrule(self, sharingrule_id: str) -> Dict[str, Any]:
        """
        Get specific sharingrule by ID
        
        Endpoint: GET /sharingrules/{sharingruleId}
        
        Args:
            sharingrule_id: Sharingrule ID

        Returns:
            Sharingrule record
        """
        endpoint = f"{self.EMONEY_SHARINGRULES_ENDPOINT}/{sharingrule_id}"
        return self._make_request(endpoint)

    def get_logons(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        sort: str = None,
    ) -> Dict[str, Any]:
        """
        Get logon records from eMoney Identity API
        
        Endpoint: GET /logons
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply (field-value pairs)
            sort: Field to sort by

        Returns:
            Dict with logon records
        """
        endpoint = self.EMONEY_LOGONS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if sort:
            params["sort"] = sort
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_logon(self, logon_id: str) -> Dict[str, Any]:
        """
        Get specific logon by ID
        
        Endpoint: GET /logons/{logonId}
        
        Args:
            logon_id: Logon ID

        Returns:
            Logon record
        """
        endpoint = f"{self.EMONEY_LOGONS_ENDPOINT}/{logon_id}"
        return self._make_request(endpoint)