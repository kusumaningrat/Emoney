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
    Handles data retrieval for financial planning objects:
    Plan, Goal, Scenario, CashFlow, NetWorth
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.config = get_config()
        self.access_token = None

        # eMoney API endpoints for financial planning
        self.EMONEY_PLANS_ENDPOINT = "/plans"
        self.EMONEY_GOALS_ENDPOINT = "/goals"
        self.EMONEY_SCENARIOS_ENDPOINT = "/scenarios"
        self.EMONEY_CASHFLOW_ENDPOINT = "/cashflow"
        self.EMONEY_NETWORTH_ENDPOINT = "/networth"

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
        Authenticate with eMoney API

        Args:
            auth_config: Optional authentication config (not used for mock server)

        Returns:
            Access token (can be any string for mock server)
        """
        try:
            self.logger.info("Authenticating with eMoney API")

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
        Get financial plan records from eMoney API
        
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

    def get_client_plans(
        self,
        client_id: str,
        page: int = 1,
        page_size: int = 100,
        include_scenarios: bool = False,
    ) -> Dict[str, Any]:
        """
        Get all plans for a specific client
        
        Endpoint: GET /clients/{clientId}/plans
        
        Args:
            client_id: Client ID
            page: Page number
            page_size: Results per page
            include_scenarios: Include scenario data

        Returns:
            Dict with client's plan records
        """
        endpoint = f"/clients/{client_id}/plans"
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if include_scenarios:
            params["include"] = "scenarios"
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # GOAL OBJECTS
    # ---------------------------
    def get_goals(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get goal records from eMoney API
        
        Endpoint: GET /goals
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page
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

    def get_plan_goals(
        self,
        plan_id: str,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get all goals for a specific plan
        
        Endpoint: GET /plans/{planId}/goals
        
        Args:
            plan_id: Plan ID
            page: Page number
            page_size: Results per page
            filters: Additional filters (goal_type, status, etc.)

        Returns:
            Dict with plan's goal records
        """
        endpoint = f"{self.EMONEY_PLANS_ENDPOINT}/{plan_id}/goals"
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        if filters:
            params.update(filters)
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # SCENARIO OBJECTS
    # ---------------------------
    def get_scenarios(
        self,
        page: int = 1,
        page_size: int = 100,
        filters: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Get scenario records from eMoney API
        
        Endpoint: GET /scenarios
        
        Args:
            page: Page number to retrieve (pagination)
            page_size: Maximum number of records per page
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

    def get_plan_scenarios(
        self,
        plan_id: str,
        page: int = 1,
        page_size: int = 100,
    ) -> Dict[str, Any]:
        """
        Get all scenarios for a specific plan
        
        Endpoint: GET /plans/{planId}/scenarios
        
        Args:
            plan_id: Plan ID
            page: Page number
            page_size: Results per page

        Returns:
            Dict with plan's scenario records
        """
        endpoint = f"{self.EMONEY_PLANS_ENDPOINT}/{plan_id}/scenarios"
        params = {"page": page, "pageSize": min(page_size, 100)}
        
        return self._make_request(endpoint, params)

    # ---------------------------
    # CASHFLOW OBJECTS
    # ---------------------------
    def get_cashflow(
        self,
        scenario_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        include_details: bool = False,
    ) -> Dict[str, Any]:
        """
        Get cash flow projections for a scenario
        
        Endpoint: GET /scenarios/{scenarioId}/cashflow
        
        Args:
            scenario_id: Scenario ID
            start_year: Starting year for projections
            end_year: Ending year for projections
            include_details: Include detailed cash flow breakdown

        Returns:
            Cash flow projection data
        """
        endpoint = f"{self.EMONEY_SCENARIOS_ENDPOINT}/{scenario_id}/cashflow"
        params = {}
        
        if start_year:
            params["startYear"] = start_year
        if end_year:
            params["endYear"] = end_year
        if include_details:
            params["includeDetails"] = "true"
            
        return self._make_request(endpoint, params)

    def get_plan_cashflow(
        self,
        plan_id: str,
        scenario_id: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get cash flow projections for a plan
        
        Endpoint: GET /plans/{planId}/cashflow
        
        Args:
            plan_id: Plan ID
            scenario_id: Optional specific scenario ID
            start_year: Starting year for projections
            end_year: Ending year for projections

        Returns:
            Cash flow projection data
        """
        endpoint = f"{self.EMONEY_PLANS_ENDPOINT}/{plan_id}/cashflow"
        params = {}
        
        if scenario_id:
            params["scenarioId"] = scenario_id
        if start_year:
            params["startYear"] = start_year
        if end_year:
            params["endYear"] = end_year
            
        return self._make_request(endpoint, params)

    # ---------------------------
    # NETWORTH OBJECTS
    # ---------------------------
    def get_networth(
        self,
        scenario_id: str,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        include_assets: bool = False,
        include_liabilities: bool = False,
    ) -> Dict[str, Any]:
        """
        Get net worth projections for a scenario
        
        Endpoint: GET /scenarios/{scenarioId}/networth
        
        Args:
            scenario_id: Scenario ID
            start_year: Starting year for projections
            end_year: Ending year for projections
            include_assets: Include detailed asset breakdown
            include_liabilities: Include detailed liability breakdown

        Returns:
            Net worth projection data
        """
        endpoint = f"{self.EMONEY_SCENARIOS_ENDPOINT}/{scenario_id}/networth"
        params = {}
        
        if start_year:
            params["startYear"] = start_year
        if end_year:
            params["endYear"] = end_year
            
        # Build include parameter
        include_parts = []
        if include_assets:
            include_parts.append("assets")
        if include_liabilities:
            include_parts.append("liabilities")
            
        if include_parts:
            params["include"] = ",".join(include_parts)
            
        return self._make_request(endpoint, params)

    def get_plan_networth(
        self,
        plan_id: str,
        scenario_id: Optional[str] = None,
        start_year: Optional[int] = None,
        end_year: Optional[int] = None,
        include_assets: bool = False,
    ) -> Dict[str, Any]:
        """
        Get net worth projections for a plan
        
        Endpoint: GET /plans/{planId}/networth
        
        Args:
            plan_id: Plan ID
            scenario_id: Optional specific scenario ID
            start_year: Starting year for projections
            end_year: Ending year for projections
            include_assets: Include detailed asset breakdown

        Returns:
            Net worth projection data
        """
        endpoint = f"{self.EMONEY_PLANS_ENDPOINT}/{plan_id}/networth"
        params = {}
        
        if scenario_id:
            params["scenarioId"] = scenario_id
        if start_year:
            params["startYear"] = start_year
        if end_year:
            params["endYear"] = end_year
        if include_assets:
            params["include"] = "assets"
            
        return self._make_request(endpoint, params)

    def get_current_networth(
        self,
        client_id: str,
        include_breakdown: bool = True,
    ) -> Dict[str, Any]:
        """
        Get current net worth for a client
        
        Endpoint: GET /clients/{clientId}/networth/current
        
        Args:
            client_id: Client ID
            include_breakdown: Include asset/liability breakdown

        Returns:
            Current net worth data
        """
        endpoint = f"/clients/{client_id}/networth/current"
        params = {}
        
        if include_breakdown:
            params["include"] = "breakdown"
            
        return self._make_request(endpoint, params)