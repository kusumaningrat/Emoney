import time
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import json
from config import get_config


class APIService:
    """
    Service for interacting with eMoney Advisor API
    Handles data retrieval for client objects:
    Client, Contact, Household, Spouse, Relationship
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.config = get_config()
        self.access_token = None

        # eMoney API endpoints
        self.EMONEY_CLIENTS_ENDPOINT = "/clients"
        self.EMONEY_CONTACTS_ENDPOINT = "/contacts"
        self.EMONEY_HOUSEHOLDS_ENDPOINT = "/households"
        self.EMONEY_SPOUSES_ENDPOINT = "/spouse"
        self.EMONEY_RELATIONSHIPS_ENDPOINT = "/relationships"

        # Default headers for eMoney API
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "eMoney-Client/1.0",
            }
        )

    # ---------------------------
    # AUTHENTICATION
    # ---------------------------
    def authenticate(self, auth_config: Dict[str, Any] = None) -> str:
        """
        Authenticate with Wealthbox Client API

        Args:
            auth_config: Optional authentication config (not used for mock server)

        Returns:
            Access token (can be any string for mock server)
        """
        try:
            self.logger.info("Authenticating with Wealthbox Client API")

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
        Get client records from eMoney API
        
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

    def get_contacts(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get contact records from eMoney API
        
        Note: eMoney API documentation doesn't show a direct /contacts endpoint.
        Contacts are typically accessed via /clients/{clientId} or as part of household data.
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page
            filters: Additional filters to apply

        Returns:
            Dict with contact records
        """
        endpoint = self.EMONEY_CONTACTS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

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
        Get household records from eMoney API
        
        Endpoint: GET /households/{householdId}
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page
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

    def get_spouse(self, spouse_id: str) -> Dict[str, Any]:
        """
        Get spouse details by ID
        
        Endpoint: GET /spouse/{spouseId}
        
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

    def get_relationships(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get relationship records from eMoney API
        
        Note: eMoney API documentation doesn't explicitly show a /relationships endpoint.
        Relationships are typically accessed via household members or client data.
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page
            filters: Additional filters to apply

        Returns:
            Dict with relationship records
        """
        endpoint = self.EMONEY_RELATIONSHIPS_ENDPOINT
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)