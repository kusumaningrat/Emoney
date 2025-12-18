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
    User, Role, Permission, Office, Logon, SharingRule
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.config = get_config()
        self.access_token = None

        # eMoney Identity API endpoints from config
        self.EMONEY_USERS_ENDPOINT = self.config.EMONEY_USERS_ENDPOINT
        self.EMONEY_ROLES_ENDPOINT = self.config.EMONEY_ROLES_ENDPOINT
        self.EMONEY_PERMISSIONS_ENDPOINT = self.config.EMONEY_PERMISSIONS_ENDPOINT
        self.EMONEY_OFFICES_ENDPOINT = self.config.EMONEY_OFFICES_ENDPOINT
        self.EMONEY_LOGONS_ENDPOINT = self.config.EMONEY_LOGONS_ENDPOINT
        self.EMONEY_SHARINGRULES_ENDPOINT = self.config.EMONEY_SHARINGRULES_ENDPOINT

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
            self.logger.info("No access token found, authenticating...")
            self.authenticate()

        self.logger.info(f"Making {method} request to: {url}")
        self.logger.info(f"Request params: {params}")
        self.logger.info(f"Authorization header present: {'Authorization' in self.session.headers}")

        for attempt in range(max_retries):
            try:
                if method == "GET":
                    response = self.session.get(url, params=params, timeout=30)
                else:
                    raise ValueError(f"Unsupported HTTP method: {method}")

                self.logger.info(f"Response status code: {response.status_code}")
                self.logger.debug(f"Response headers: {dict(response.headers)}")
                self.logger.debug(f"Response content length: {len(response.content)}")
                self.logger.debug(f"Response text preview: {response.text[:200] if response.text else 'EMPTY'}")

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
                
                # Check if response has content before parsing JSON
                if not response.content:
                    self.logger.warning("Empty response received from API")
                    return {}
                    
                try:
                    return response.json()
                except ValueError as json_err:
                    self.logger.error(f"Failed to parse JSON response: {json_err}")
                    self.logger.error(f"Response content: {response.text[:500]}")
                    raise

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
    # USER OBJECTS (eMoney API pagination uses page & pageSize)
    # ---------------------------
    def get_users(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_roles: bool = False,
        include_permissions: bool = False,
        include_office: bool = False,
    ) -> Dict[str, Any]:
        """
        Get user records from eMoney Identity API
        
        Endpoint: GET /users
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply (email, status, office_id, etc.)
            include_roles: Include role data in response
            include_permissions: Include permissions data in response
            include_office: Include office data in response

        Returns:
            Dict with user records
        """
        endpoint = self.EMONEY_USERS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        # Build include parameter
        include_parts = []
        if include_roles:
            include_parts.append("roles")
        if include_permissions:
            include_parts.append("permissions")
        if include_office:
            include_parts.append("office")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_user(
        self, 
        user_id: str, 
        include_roles: bool = True,
        include_permissions: bool = True,
        include_office: bool = True,
        include_logon_history: bool = False,
        include_sharingrules: bool = False,
    ) -> Dict[str, Any]:
        """
        Get specific user by ID
        
        Endpoint: GET /users/{userId}
        
        Args:
            user_id: User ID
            include_roles: Include role data
            include_permissions: Include permissions data
            include_office: Include office data
            include_logon_history: Include recent logon history
            include_sharingrules: Include sharing rules

        Returns:
            User record with requested includes
        """
        endpoint = f"{self.EMONEY_USERS_ENDPOINT}/{user_id}"
        params = {}
        
        # Build include parameter
        include_parts = []
        if include_roles:
            include_parts.append("roles")
        if include_permissions:
            include_parts.append("permissions")
        if include_office:
            include_parts.append("office")
        if include_logon_history:
            include_parts.append("logonHistory")
        if include_sharingrules:
            include_parts.append("sharingRules")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # ROLE OBJECTS
    # ---------------------------
    def get_roles(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_permissions: bool = False,
        include_users: bool = False,
    ) -> Dict[str, Any]:
        """
        Get role records from eMoney Identity API
        
        Endpoint: GET /roles
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters (role_type, is_active, etc.)
            include_permissions: Include associated permissions
            include_users: Include users with this role

        Returns:
            Dict with role records
        """
        endpoint = self.EMONEY_ROLES_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        # Build include parameter
        include_parts = []
        if include_permissions:
            include_parts.append("permissions")
        if include_users:
            include_parts.append("users")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_role(
        self, 
        role_id: str,
        include_permissions: bool = True,
        include_users: bool = False,
    ) -> Dict[str, Any]:
        """
        Get specific role by ID
        
        Endpoint: GET /roles/{roleId}
        
        Args:
            role_id: Role ID
            include_permissions: Include associated permissions
            include_users: Include users with this role

        Returns:
            Role record
        """
        endpoint = f"{self.EMONEY_ROLES_ENDPOINT}/{role_id}"
        params = {}
        
        # Build include parameter
        include_parts = []
        if include_permissions:
            include_parts.append("permissions")
        if include_users:
            include_parts.append("users")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # PERMISSION OBJECTS
    # ---------------------------
    def get_permissions(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get permission records from eMoney Identity API
        
        Endpoint: GET /permissions
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters (role_id, user_id, resource, action, etc.)

        Returns:
            Dict with permission records
        """
        endpoint = self.EMONEY_PERMISSIONS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
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

    # ---------------------------
    # OFFICE OBJECTS
    # ---------------------------
    def get_offices(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_users: bool = False,
        include_suboffices: bool = False,
    ) -> Dict[str, Any]:
        """
        Get office records from eMoney Identity API
        
        Endpoint: GET /offices
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters (parent_office_id, status, etc.)
            include_users: Include users in this office
            include_suboffices: Include sub-offices

        Returns:
            Dict with office records
        """
        endpoint = self.EMONEY_OFFICES_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        # Build include parameter
        include_parts = []
        if include_users:
            include_parts.append("users")
        if include_suboffices:
            include_parts.append("suboffices")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_office(
        self, 
        office_id: str,
        include_users: bool = True,
        include_suboffices: bool = True,
        include_parent: bool = False,
    ) -> Dict[str, Any]:
        """
        Get specific office by ID
        
        Endpoint: GET /offices/{officeId}
        
        Args:
            office_id: Office ID
            include_users: Include users in this office
            include_suboffices: Include sub-offices
            include_parent: Include parent office details

        Returns:
            Office record
        """
        endpoint = f"{self.EMONEY_OFFICES_ENDPOINT}/{office_id}"
        params = {}
        
        # Build include parameter
        include_parts = []
        if include_users:
            include_parts.append("users")
        if include_suboffices:
            include_parts.append("suboffices")
        if include_parent:
            include_parts.append("parent")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # LOGON OBJECTS
    # ---------------------------
    def get_logons(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_user: bool = False,
    ) -> Dict[str, Any]:
        """
        Get logon history records from eMoney Identity API
        
        Endpoint: GET /logons
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters (user_id, date_range, status, ip_address, etc.)
            include_user: Include user details in response

        Returns:
            Dict with logon records
        """
        endpoint = self.EMONEY_LOGONS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if include_user:
            params["include"] = "user"
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_logon(
        self, 
        logon_id: str,
        include_user: bool = True,
    ) -> Dict[str, Any]:
        """
        Get specific logon record by ID
        
        Endpoint: GET /logons/{logonId}
        
        Args:
            logon_id: Logon ID
            include_user: Include user details

        Returns:
            Logon record
        """
        endpoint = f"{self.EMONEY_LOGONS_ENDPOINT}/{logon_id}"
        params = {}
        
        if include_user:
            params["include"] = "user"
            
        return self._make_request(endpoint, params)

    def get_user_logon_history(
        self,
        user_id: str,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Get logon history for a specific user
        
        Endpoint: GET /users/{userId}/logons
        
        Args:
            user_id: User ID
            start_date: Start date for history (YYYY-MM-DD)
            end_date: End date for history (YYYY-MM-DD)
            status: Filter by logon status (success, failed, locked)
            page: Page number
            page_size: Records per page

        Returns:
            Logon history for the user
        """
        endpoint = f"{self.EMONEY_USERS_ENDPOINT}/{user_id}/logons"
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if start_date:
            params["startDate"] = start_date
        if end_date:
            params["endDate"] = end_date
        if status:
            params["status"] = status
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # SHARING RULE OBJECTS
    # ---------------------------
    def get_sharingrules(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_user: bool = False,
        include_shared_with_user: bool = False,
    ) -> Dict[str, Any]:
        """
        Get sharing rule records from eMoney Identity API
        
        Endpoint: GET /sharingrules
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters (user_id, resource_type, access_level, etc.)
            include_user: Include owner user details
            include_shared_with_user: Include shared with user details

        Returns:
            Dict with sharing rule records
        """
        endpoint = self.EMONEY_SHARINGRULES_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        # Build include parameter
        include_parts = []
        if include_user:
            include_parts.append("user")
        if include_shared_with_user:
            include_parts.append("sharedWithUser")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_sharingrule(
        self, 
        sharingrule_id: str,
        include_user: bool = True,
        include_shared_with_user: bool = True,
    ) -> Dict[str, Any]:
        """
        Get specific sharing rule by ID
        
        Endpoint: GET /sharingrules/{sharingRuleId}
        
        Args:
            sharingrule_id: Sharing Rule ID
            include_user: Include owner user details
            include_shared_with_user: Include shared with user details

        Returns:
            Sharing rule record
        """
        endpoint = f"{self.EMONEY_SHARINGRULES_ENDPOINT}/{sharingrule_id}"
        params = {}
        
        # Build include parameter
        include_parts = []
        if include_user:
            include_parts.append("user")
        if include_shared_with_user:
            include_parts.append("sharedWithUser")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        return self._make_request(endpoint, params)

    def get_user_sharingrules(
        self,
        user_id: str,
        resource_type: Optional[str] = None,
        access_level: Optional[str] = None,
        page: int = 1,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Get sharing rules owned by a specific user
        
        Endpoint: GET /users/{userId}/sharingrules
        
        Args:
            user_id: User ID
            resource_type: Filter by resource type
            access_level: Filter by access level (view, edit, full)
            page: Page number
            page_size: Records per page

        Returns:
            Sharing rules owned by the user
        """
        endpoint = f"{self.EMONEY_USERS_ENDPOINT}/{user_id}/sharingrules"
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if resource_type:
            params["resourceType"] = resource_type
        if access_level:
            params["accessLevel"] = access_level
            
        return self._make_request(endpoint, params)