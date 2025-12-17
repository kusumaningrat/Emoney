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
    Handles data retrieval for account objects:
    Account, AccountType, Asset, AssetClass, Liability
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.config = get_config()
        self.access_token = None

        # eMoney Advisor API endpoints from config
        self.EMONEY_ACCOUNTS_ENDPOINT = self.config.EMONEY_ACCOUNTS_ENDPOINT
        self.EMONEY_ACCOUNT_TYPES_ENDPOINT = self.config.EMONEY_ACCOUNT_TYPES_ENDPOINT
        self.EMONEY_ASSETS_ENDPOINT = self.config.EMONEY_ASSETS_ENDPOINT
        self.EMONEY_ASSET_CLASSES_ENDPOINT = self.config.EMONEY_ASSET_CLASSES_ENDPOINT
        self.EMONEY_LIABILITIES_ENDPOINT = self.config.EMONEY_LIABILITIES_ENDPOINT

        # Default headers for eMoney Advisor API
        self.session.headers.update(
            {
                "Content-Type": "application/json",
                "Accept": "application/json",
                "User-Agent": "eMoney-Advisor/1.0",
            }
        )

    # ---------------------------
    # AUTHENTICATION
    # ---------------------------
    def authenticate(self, auth_config: Dict[str, Any] = None) -> str:
        """
        Authenticate with eMoney Advisor API

        Args:
            auth_config: Optional authentication config (not used for mock server)

        Returns:
            Access token (can be any string for mock server)
        """
        try:
            self.logger.info("Authenticating with eMoney Advisor API")

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