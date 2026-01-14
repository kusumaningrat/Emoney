import time
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from config import get_config


class APIService:
    """
    Service for interacting with eMoney Service API
    Handles data retrieval for eMoney Service objects:
    User, Role, Permission, Office, Logon, SharingRule, Plan, Goal, Scenario, CashFlow, NetWorth, Client, Contact, Household, Spouse, Relationship, Account, AccountType, Asset, AssetClass, Liability 
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.config = get_config()
        self.access_token = None

        # eMoney Service API endpoints from config
        self.EMONEY_USERS_ENDPOINT = self.config.EMONEY_USERS_ENDPOINT
        self.EMONEY_ROLES_ENDPOINT = self.config.EMONEY_ROLES_ENDPOINT
        self.EMONEY_PERMISSIONS_ENDPOINT = self.config.EMONEY_PERMISSIONS_ENDPOINT
        self.EMONEY_OFFICES_ENDPOINT = self.config.EMONEY_OFFICES_ENDPOINT
        self.EMONEY_LOGONS_ENDPOINT = self.config.EMONEY_LOGONS_ENDPOINT
        self.EMONEY_SHARINGRULES_ENDPOINT = self.config.EMONEY_SHARINGRULES_ENDPOINT
        self.EMONEY_PLANS_ENDPOINT = self.config.EMONEY_PLANS_ENDPOINT
        self.EMONEY_GOALS_ENDPOINT = self.config.EMONEY_GOALS_ENDPOINT
        self.EMONEY_SCENARIOS_ENDPOINT = self.config.EMONEY_SCENARIOS_ENDPOINT
        self.EMONEY_CASHFLOW_ENDPOINT = self.config.EMONEY_CASHFLOW_ENDPOINT
        self.EMONEY_NETWORTH_ENDPOINT = self.config.EMONEY_NETWORTH_ENDPOINT
        self.EMONEY_CLIENTS_ENDPOINT = self.config.EMONEY_CLIENTS_ENDPOINT
        self.EMONEY_CONTACTS_ENDPOINT = self.config.EMONEY_CONTACTS_ENDPOINT
        self.EMONEY_HOUSEHOLDS_ENDPOINT = self.config.EMONEY_HOUSEHOLDS_ENDPOINT
        self.EMONEY_SPOUSES_ENDPOINT = self.config.EMONEY_SPOUSES_ENDPOINT
        self.EMONEY_RELATIONSHIPS_ENDPOINT = self.config.EMONEY_RELATIONSHIPS_ENDPOINT
        self.EMONEY_ACCOUNTS_ENDPOINT = self.config.EMONEY_ACCOUNTS_ENDPOINT
        self.EMONEY_ACCOUNT_TYPES_ENDPOINT = self.config.EMONEY_ACCOUNT_TYPES_ENDPOINT
        self.EMONEY_ASSETS_ENDPOINT = self.config.EMONEY_ASSETS_ENDPOINT
        self.EMONEY_ASSET_CLASSES_ENDPOINT = self.config.EMONEY_ASSET_CLASSES_ENDPOINT
        self.EMONEY_LIABILITIES_ENDPOINT = self.config.EMONEY_LIABILITIES_ENDPOINT

        # Default headers for eMoney Service API
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "emoney-Service/1.0",
            }
        )

    # ---------------------------
    # AUTHENTICATION
    # ---------------------------
    def authenticate(self, auth_config: Dict[str, Any] = None) -> str:
        """
        Authenticate with emoney Service API

        Args:
            auth_config: Optional authentication config (not used for mock server)

        Returns:
            Access token (can be any string for mock server)
        """
        try:
            self.logger.info("Authenticating with emoney Service API")

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
        Get user records from emoney Service API
        
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
        Get role records from emoney Service API
        
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
        Get permission records from emoney Service API
        
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
        Get office records from emoney Service API
        
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
        Get logon history records from emoney Service API
        
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
        Get sharing rule records from eMoney Service API
        
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
    
    # ---------------------------
    # PLAN OBJECTS (eMoney API pagination uses page & pageSize)
    # ---------------------------
    def get_plans(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_scenarios: bool = False,
        include_goals: bool = False,
    ) -> Dict[str, Any]:
        """
        Get financial plan records from eMoney Planning API
        
        Endpoint: GET /plans
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply (client_id, status, etc.)
            include_scenarios: Include scenario data in response
            include_goals: Include goals data in response

        Returns:
            Dict with plan records
        """
        endpoint = self.EMONEY_PLANS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        # Build include parameter
        include_parts = []
        if include_scenarios:
            include_parts.append("scenarios")
        if include_goals:
            include_parts.append("goals")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_plan(
        self, 
        plan_id: str, 
        include_scenarios: bool = True,
        include_goals: bool = True,
        include_cashflow: bool = False,
        include_networth: bool = False,
    ) -> Dict[str, Any]:
        """
        Get specific financial plan by ID
        
        Endpoint: GET /plans/{planId}
        
        Args:
            plan_id: Plan ID
            include_scenarios: Include scenario data
            include_goals: Include goals data
            include_cashflow: Include cash flow projections
            include_networth: Include net worth projections

        Returns:
            Plan record with requested includes
        """
        endpoint = f"{self.EMONEY_PLANS_ENDPOINT}/{plan_id}"
        params = {}
        
        # Build include parameter
        include_parts = []
        if include_scenarios:
            include_parts.append("scenarios")
        if include_goals:
            include_parts.append("goals")
        if include_cashflow:
            include_parts.append("cashflow")
        if include_networth:
            include_parts.append("networth")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # GOAL ENDPOINTS
    # ---------------------------
    def get_goals(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get goal records from eMoney Planning API
        
        Endpoint: GET /goals
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters (goal_type, status, plan_id, etc.)

        Returns:
            Dict with goal records
        """
        endpoint = self.EMONEY_GOALS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_goal(self, goal_id: str) -> Dict[str, Any]:
        """
        Get specific goal by ID
        
        Endpoint: GET /goals/{goalId}
        
        Args:
            goal_id: Goal ID

        Returns:
            Goal record
        """
        endpoint = f"{self.EMONEY_GOALS_ENDPOINT}/{goal_id}"
        return self._make_request(endpoint)
    
    # ---------------------------
    # SCENARIOS ENDPOINTS
    # ---------------------------
    def get_scenarios(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get scenario records from eMoney Planning API
        
        Endpoint: GET /scenarios
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters (plan_id, scenario_type, etc.)

        Returns:
            Dict with scenario records
        """
        endpoint = self.EMONEY_SCENARIOS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_scenario(
        self, 
        scenario_id: str,
        include_cashflow: bool = False,
        include_networth: bool = False,
    ) -> Dict[str, Any]:
        """
        Get specific scenario by ID
        
        Endpoint: GET /scenarios/{scenarioId}
        
        Args:
            scenario_id: Scenario ID
            include_cashflow: Include cash flow projections
            include_networth: Include net worth projections

        Returns:
            Scenario record
        """
        endpoint = f"{self.EMONEY_SCENARIOS_ENDPOINT}/{scenario_id}"
        params = {}
        
        # Build include parameter
        include_parts = []
        if include_cashflow:
            include_parts.append("cashflow")
        if include_networth:
            include_parts.append("networth")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # CASHFLOW ENDPOINTS
    # ---------------------------
    def get_cashflows(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get all cash flow records from eMoney Planning API
        
        Endpoint: GET /cashflow
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters (plan_id, scenario_id, year, etc.)

        Returns:
            Dict with cash flow records
        """
        endpoint = self.EMONEY_CASHFLOW_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # NETWORTH ENDPOINTS
    # ---------------------------
    def get_networths(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get all net worth records from eMoney Planning API
        
        Endpoint: GET /networth
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters (plan_id, scenario_id, year, etc.)

        Returns:
            Dict with net worth records
        """
        endpoint = self.EMONEY_NETWORTH_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)
    
    # ---------------------------
    # CLIENT OBJECTS (eMoney API pagination uses page & pageSize)
    # ---------------------------
    def get_clients(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_household: bool = False,
    ) -> Dict[str, Any]:
        """
        Get client records from eMoney Client API
        
        Endpoint: GET /clients
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply (status, advisor, etc.)
            include_household: Include household data in response

        Returns:
            Dict with client records
        """
        endpoint = self.EMONEY_CLIENTS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if include_household:
            params["includeHousehold"] = "true"
            
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_client(self, client_id: str, include_household: bool = True) -> Dict[str, Any]:
        """
        Get specific client by ID
        
        Endpoint: GET /clients/{clientId}
        
        Args:
            client_id: Client ID
            include_household: Include household data

        Returns:
            Client record
        """
        endpoint = f"{self.EMONEY_CLIENTS_ENDPOINT}/{client_id}"
        params = {}
        
        if include_household:
            params["includeHousehold"] = "true"
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # CONTACTS ENDPOINTS
    # ---------------------------
    def get_contacts(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get contact records from eMoney Client API
        
        Endpoint: GET /contacts
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply

        Returns:
            Dict with contact records
        """
        endpoint = self.EMONEY_CONTACTS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_contact(self, contact_id: str) -> Dict[str, Any]:
        """
        Get specific contact by ID
        
        Endpoint: GET /contacts/{contactId}
        
        Args:
            contact_id: Contact ID

        Returns:
            Contact record
        """
        endpoint = f"{self.EMONEY_CONTACTS_ENDPOINT}/{contact_id}"
        return self._make_request(endpoint)

    # ---------------------------
    # HOUSEHOLDS ENDPOINTS
    # ---------------------------
    def get_households(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_members: bool = False,
        include_accounts: bool = False,
        include_networth: bool = False,
    ) -> Dict[str, Any]:
        """
        Get household records from eMoney Client API
        
        Endpoint: GET /households
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters (netWorth comparisons, etc.)
            include_members: Include household members
            include_accounts: Include household accounts
            include_networth: Include net worth data

        Returns:
            Dict with household records
        """
        endpoint = self.EMONEY_HOUSEHOLDS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        # Build include parameter
        include_parts = []
        if include_members:
            include_parts.append("members")
        if include_accounts:
            include_parts.append("accounts")
        if include_networth:
            include_parts.append("networth")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_household(
        self, 
        household_id: str,
        include_members: bool = True,
        include_accounts: bool = False,
        include_networth: bool = True,
    ) -> Dict[str, Any]:
        """
        Get specific household by ID
        
        Endpoint: GET /households/{householdId}
        
        Args:
            household_id: Household ID
            include_members: Include household members
            include_accounts: Include household accounts
            include_networth: Include net worth data

        Returns:
            Household record
        """
        endpoint = f"{self.EMONEY_HOUSEHOLDS_ENDPOINT}/{household_id}"
        params = {}
        
        # Build include parameter
        include_parts = []
        if include_members:
            include_parts.append("members")
        if include_accounts:
            include_parts.append("accounts")
        if include_networth:
            include_parts.append("networth")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # SPOUSES ENDPOINTS
    # ---------------------------
    def get_spouses(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get spouse records from eMoney Client API
        
        Endpoint: GET /spouses
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply

        Returns:
            Dict with spouse records
        """
        endpoint = self.EMONEY_SPOUSES_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_spouse(self, spouse_id: str) -> Dict[str, Any]:
        """
        Get spouse details by ID
        
        Endpoint: GET /spouses/{spouseId}
        
        Args:
            spouse_id: Spouse ID

        Returns:
            Spouse record
        """
        endpoint = f"{self.EMONEY_SPOUSES_ENDPOINT}/{spouse_id}"
        return self._make_request(endpoint)

    def get_client_spouse(self, client_id: str) -> Dict[str, Any]:
        """
        Get client's spouse
        
        Endpoint: GET /clients/{clientId}/spouse
        
        Args:
            client_id: Client ID

        Returns:
            Spouse record
        """
        endpoint = f"{self.EMONEY_CLIENTS_ENDPOINT}/{client_id}/spouse"
        return self._make_request(endpoint)

    # ---------------------------
    # RELATIONSHIPS ENDPOINTS
    # ---------------------------
    def get_relationships(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get relationship records from eMoney Client API
        
        Endpoint: GET /relationships
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 100)
            filters: Additional filters to apply

        Returns:
            Dict with relationship records
        """
        endpoint = self.EMONEY_RELATIONSHIPS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_relationship(self, relationship_id: str) -> Dict[str, Any]:
        """
        Get specific relationship by ID
        
        Endpoint: GET /relationships/{relationshipId}
        
        Args:
            relationship_id: Relationship ID

        Returns:
            Relationship record
        """
        endpoint = f"{self.EMONEY_RELATIONSHIPS_ENDPOINT}/{relationship_id}"
        return self._make_request(endpoint)
    
    # ---------------------------
    # ACCOUNT OBJECTS (eMoney API pagination uses page & pageSize)
    # ---------------------------
    def get_accounts(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Get account records from eMoney Advisor API
        
        Endpoint: GET /accounts
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page (max 500)
            filters: Additional filters to apply
            include_details: Include additional account details

        Returns:
            Dict with account records
        """
        endpoint = self.EMONEY_ACCOUNTS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 500)}
        
        if include_details:
            params["includeDetails"] = "true"
            
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_account(self, account_id: str) -> Dict[str, Any]:
        """
        Get specific account by ID
        
        Endpoint: GET /accounts/{accountId}
        
        Args:
            account_id: Account ID

        Returns:
            Account record
        """
        endpoint = f"{self.EMONEY_ACCOUNTS_ENDPOINT}/{account_id}"
        return self._make_request(endpoint)

    # ---------------------------
    # ACCOUNT_TYPES ENDPOINTS
    # ---------------------------
    def get_account_types(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get account type records from eMoney Advisor API
        
        Endpoint: GET /account-types
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page
            filters: Additional filters to apply

        Returns:
            Dict with account type records
        """
        endpoint = self.EMONEY_ACCOUNT_TYPES_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 500)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_account_type(self, account_type_id: str) -> Dict[str, Any]:
        """
        Get specific account type by ID
        
        Endpoint: GET /account-types/{accountTypeId}
        
        Args:
            account_type_id: Account Type ID

        Returns:
            Account type record
        """
        endpoint = f"{self.EMONEY_ACCOUNT_TYPES_ENDPOINT}/{account_type_id}"
        return self._make_request(endpoint)

    # ---------------------------
    # ASSETS ENDPOINTS
    # ---------------------------
    def get_assets(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Get asset records from eMoney Advisor API
        
        Endpoint: GET /assets
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page
            filters: Additional filters to apply
            include_details: Include additional asset details

        Returns:
            Dict with asset records
        """
        endpoint = self.EMONEY_ASSETS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 500)}
        
        if include_details:
            params["includeDetails"] = "true"
            
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """
        Get specific asset by ID
        
        Endpoint: GET /assets/{assetId}
        
        Args:
            asset_id: Asset ID

        Returns:
            Asset record
        """
        endpoint = f"{self.EMONEY_ASSETS_ENDPOINT}/{asset_id}"
        return self._make_request(endpoint)

    # ---------------------------
    # ASSET_CLASSES ENDPOINTS
    # ---------------------------
    def get_asset_classes(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Get asset class records from eMoney Advisor API
        
        Endpoint: GET /assetclasses
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page
            filters: Additional filters to apply
            include_details: Include additional details

        Returns:
            Dict with asset class records
        """
        endpoint = self.EMONEY_ASSET_CLASSES_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 500)}
        
        if include_details:
            params["includeDetails"] = "true"
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_asset_class(self, asset_class_id: str) -> Dict[str, Any]:
        """
        Get specific asset class by ID
        
        Endpoint: GET /assetclasses/{assetClassId}
        
        Args:
            asset_class_id: Asset Class ID

        Returns:
            Asset class record
        """
        endpoint = f"{self.EMONEY_ASSET_CLASSES_ENDPOINT}/{asset_class_id}"
        return self._make_request(endpoint)

    # ---------------------------
    # LIABILITIES ENDPOINTS
    # ---------------------------
    def get_liabilities(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Get liability records from eMoney Advisor API
        
        Endpoint: GET /liabilities
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page
            filters: Additional filters to apply
            include_details: Include additional liability details

        Returns:
            Dict with liability records
        """
        endpoint = self.EMONEY_LIABILITIES_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 500)}
        
        if include_details:
            params["includeDetails"] = "true"
            
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    def get_liability(self, liability_id: str) -> Dict[str, Any]:
        """
        Get specific liability by ID
        
        Endpoint: GET /liabilities/{liabilityId}
        
        Args:
            liability_id: Liability ID

        Returns:
            Liability record
        """
        endpoint = f"{self.EMONEY_LIABILITIES_ENDPOINT}/{liability_id}"
        return self._make_request(endpoint)