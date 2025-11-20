# routes/entity.py - Main Entity Endpoints Router

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any, Union
from datetime import datetime

from database import get_db
from services.entity_factory import EntityServiceFactory

# Import all schemas
from schema.identity import (
    User, UserWithRelations, UserSearchParams, PaginatedUsersResponse,
    Office, OfficeWithRelations, Role, Permission, SharingRule, Logon
)
from schema.client import (
    Client, ClientWithRelations, ClientSearchParams, PaginatedClientsResponse,
    Household, HouseholdWithMembers, Spouse, Contact, Relationship
)
from schema.financial import (
    FinancialPlan, FinancialPlanWithRelations, Goal, Scenario, CashFlow, NetWorth,
    GoalSearchParams, CashFlowAnalysis
)
from schema.account import (
    Account, AccountWithRelations, Asset, AssetClass, Liability,
    AccountPerformance, AssetPerformance, LiabilitySchedule
)

router = APIRouter(tags=["Entities"])

# ============================================================================
# VERSION 1: IDENTITY & ACCESS MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/users", response_model=List[User], summary="List All Users")
async def get_users(
    skip: int = Query(default=0, ge=0, description="Number of records to skip"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum records to return"),
    status: Optional[str] = Query(default=None, description="Filter by user status"),
    role: Optional[str] = Query(default=None, description="Filter by role name"),
    office_id: Optional[str] = Query(default=None, description="Filter by office"),
    db: Session = Depends(get_db)
) -> List[User]:
    """
    Get all users with optional filtering and pagination.
    
    **Filters:**
    - `status`: User status (Active, Inactive, Locked)
    - `role`: Filter by role name
    - `office_id`: Filter by office ID
    
    **Example:**
    ```
    GET /users?status=Active&limit=50
    ```
    """
    service = EntityServiceFactory.get_service("user", db)
    return service.get_all(db, skip=skip, limit=limit, status=status)


@router.get("/users/{user_id}", response_model=UserWithRelations, summary="Get User by ID")
async def get_user(
    user_id: str,
    include: Optional[str] = Query(default=None, description="Comma-separated relations to include: roles,permissions,clients"),
    db: Session = Depends(get_db)
) -> UserWithRelations:
    """
    Get a specific user by ID with optional related data.
    
    **Include Options:**
    - `roles`: Include user's assigned roles
    - `permissions`: Include aggregated permissions
    - `clients`: Include accessible client IDs
    
    **Example:**
    ```
    GET /users/USR-001?include=roles,permissions
    ```
    """
    service = EntityServiceFactory.get_service("user", db)
    user = service.get_by_id(db, user_id)
    
    if not user:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    
    return user


@router.get("/users/{user_id}/profile", response_model=User, summary="Get User Profile")
async def get_user_profile(
    user_id: str,
    db: Session = Depends(get_db)
) -> User:
    """Get user profile with office details."""
    service = EntityServiceFactory.get_service("user", db)
    profile = service.get_user_profile(db, user_id)
    
    if not profile:
        raise HTTPException(status_code=404, detail=f"User profile {user_id} not found")
    
    return profile


@router.get("/users/{user_id}/permissions", response_model=List[Permission], summary="Get User Permissions")
async def get_user_permissions(
    user_id: str,
    db: Session = Depends(get_db)
) -> List[Permission]:
    """Get aggregated permissions for a user from all assigned roles."""
    service = EntityServiceFactory.get_service("user", db)
    return service.get_user_permissions(db, user_id)


@router.get("/users/{user_id}/roles", response_model=List[Role], summary="Get User Roles")
async def get_user_roles(
    user_id: str,
    db: Session = Depends(get_db)
) -> List[Role]:
    """Get all roles assigned to a user."""
    service = EntityServiceFactory.get_service("user", db)
    return service.get_user_roles(db, user_id)


@router.get("/users/{user_id}/clients", response_model=List[str], summary="Get User's Accessible Clients")
async def get_user_clients(
    user_id: str,
    db: Session = Depends(get_db)
) -> List[str]:
    """Get all client IDs accessible by a user through sharing rules."""
    service = EntityServiceFactory.get_service("user", db)
    return service.get_user_clients(db, user_id)


@router.get("/offices", response_model=List[Office], summary="List All Offices")
async def get_offices(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    status: Optional[str] = Query(default=None, description="Filter by office status"),
    db: Session = Depends(get_db)
) -> List[Office]:
    """Get all offices with optional filtering and pagination."""
    service = EntityServiceFactory.get_service("office", db)
    return service.get_all(db, skip=skip, limit=limit, status=status)


@router.get("/offices/{office_id}", response_model=OfficeWithRelations, summary="Get Office by ID")
async def get_office(
    office_id: str,
    db: Session = Depends(get_db)
) -> OfficeWithRelations:
    """Get a specific office by ID with hierarchical relationships."""
    service = EntityServiceFactory.get_service("office", db)
    office = service.get_by_id(db, office_id)
    
    if not office:
        raise HTTPException(status_code=404, detail=f"Office {office_id} not found")
    
    return office


@router.get("/offices/{office_id}/users", response_model=List[User], summary="Get Office Users")
async def get_office_users(
    office_id: str,
    status: Optional[str] = Query(default=None, description="Filter by user status"),
    db: Session = Depends(get_db)
) -> List[User]:
    """Get all users in an office."""
    service = EntityServiceFactory.get_service("office", db)
    return service.get_office_users(db, office_id, status=status)


@router.get("/offices/{office_id}/clients", response_model=List[str], summary="Get Office Clients")
async def get_office_clients(
    office_id: str,
    db: Session = Depends(get_db)
) -> List[str]:
    """Get all client IDs associated with users in an office."""
    service = EntityServiceFactory.get_service("office", db)
    return service.get_office_clients(db, office_id)


# ============================================================================
# VERSION 2: CLIENT & HOUSEHOLD MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/clients", response_model=List[Client], summary="List All Clients")
async def get_clients(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    status: Optional[str] = Query(default=None, description="Filter by client status"),
    advisor_id: Optional[str] = Query(default=None, description="Filter by advisor"),
    household_id: Optional[str] = Query(default=None, description="Filter by household"),
    db: Session = Depends(get_db)
) -> List[Client]:
    """
    Get all clients with optional filtering and pagination.
    
    **Filters:**
    - `status`: Client status (Active, Inactive, Prospect, Archived)
    - `advisor_id`: Filter by assigned advisor
    - `household_id`: Filter by household membership
    
    **Example:**
    ```
    GET /clients?status=Active&advisor_id=ADV-001&limit=50
    ```
    """
    service = EntityServiceFactory.get_service("client", db)
    return service.get_all(db, skip=skip, limit=limit, status=status, advisor_id=advisor_id)


@router.get("/clients/{client_id}", response_model=ClientWithRelations, summary="Get Client by ID")
async def get_client(
    client_id: str,
    includeHousehold: Optional[bool] = Query(default=False, description="Include household details"),
    db: Session = Depends(get_db)
) -> ClientWithRelations:
    """
    Get a specific client by ID with optional household details.
    
    **Query Parameters:**
    - `includeHousehold`: Include household, spouse, and contacts
    
    **Example:**
    ```
    GET /clients/C12345?includeHousehold=true
    ```
    """
    service = EntityServiceFactory.get_service("client", db)
    client = service.get_by_id(db, client_id, include_household=includeHousehold)
    
    if not client:
        raise HTTPException(status_code=404, detail=f"Client {client_id} not found")
    
    return client


@router.get("/clients/{client_id}/household", response_model=HouseholdWithMembers, summary="Get Client Household")
async def get_client_household(
    client_id: str,
    db: Session = Depends(get_db)
) -> HouseholdWithMembers:
    """Get client's household with all members."""
    service = EntityServiceFactory.get_service("client", db)
    household = service.get_client_household(db, client_id)
    
    if not household:
        raise HTTPException(status_code=404, detail=f"Household for client {client_id} not found")
    
    return household


@router.get("/clients/{client_id}/spouse", response_model=Spouse, summary="Get Client Spouse")
async def get_client_spouse(
    client_id: str,
    db: Session = Depends(get_db)
) -> Spouse:
    """Get client's spouse details."""
    service = EntityServiceFactory.get_service("client", db)
    spouse = service.get_client_spouse(db, client_id)
    
    if not spouse:
        raise HTTPException(status_code=404, detail=f"Spouse for client {client_id} not found")
    
    return spouse


@router.get("/clients/search", response_model=List[Client], summary="Search Clients")
async def search_clients(
    firstName: Optional[str] = Query(default=None, description="Search by first name"),
    lastName: Optional[str] = Query(default=None, description="Search by last name"),
    email: Optional[str] = Query(default=None, description="Search by email"),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    db: Session = Depends(get_db)
) -> List[Client]:
    """
    Search clients by various criteria.
    
    **Search Parameters:**
    - `firstName`: Partial match on first name
    - `lastName`: Partial match on last name  
    - `email`: Partial match on email address
    
    **Example:**
    ```
    GET /clients/search?firstName=John&lastName=Doe
    ```
    """
    service = EntityServiceFactory.get_service("client", db)
    return service.search_clients(
        db, first_name=firstName, last_name=lastName, email=email,
        skip=skip, limit=limit
    )


@router.get("/households/{household_id}", response_model=HouseholdWithMembers, summary="Get Household by ID")
async def get_household(
    household_id: str,
    db: Session = Depends(get_db)
) -> HouseholdWithMembers:
    """Get a specific household by ID with all members."""
    service = EntityServiceFactory.get_service("household", db)
    household = service.get_by_id(db, household_id)
    
    if not household:
        raise HTTPException(status_code=404, detail=f"Household {household_id} not found")
    
    return household


@router.get("/households/{household_id}/members", response_model=List[Client], summary="Get Household Members")
async def get_household_members(
    household_id: str,
    db: Session = Depends(get_db)
) -> List[Client]:
    """Get all members of a household."""
    service = EntityServiceFactory.get_service("household", db)
    return service.get_household_members(db, household_id)


@router.get("/households/{household_id}/networth", response_model=Household, summary="Get Household Net Worth")
async def get_household_networth(
    household_id: str,
    db: Session = Depends(get_db)
) -> Household:
    """Get household net worth information."""
    service = EntityServiceFactory.get_service("household", db)
    household = service.get_household_networth(db, household_id)
    
    if not household:
        raise HTTPException(status_code=404, detail=f"Household {household_id} not found")
    
    return household


# ============================================================================
# VERSION 3: FINANCIAL PLANNING ENDPOINTS
# ============================================================================

@router.get("/plans/{plan_id}", response_model=FinancialPlanWithRelations, summary="Get Financial Plan")
async def get_financial_plan(
    plan_id: str,
    includeGoals: Optional[bool] = Query(default=False, description="Include plan goals"),
    includeScenarios: Optional[bool] = Query(default=False, description="Include plan scenarios"),
    db: Session = Depends(get_db)
) -> FinancialPlanWithRelations:
    """
    Get a specific financial plan by ID with optional related data.
    
    **Query Parameters:**
    - `includeGoals`: Include all goals for this plan
    - `includeScenarios`: Include all scenarios for this plan
    
    **Example:**
    ```
    GET /plans/PLAN-67890?includeGoals=true&includeScenarios=true
    ```
    """
    service = EntityServiceFactory.get_service("financial_plan", db)
    plan = service.get_by_id(db, plan_id, include_goals=includeGoals, include_scenarios=includeScenarios)
    
    if not plan:
        raise HTTPException(status_code=404, detail=f"Financial plan {plan_id} not found")
    
    return plan


@router.get("/plans/{plan_id}/goals", response_model=List[Goal], summary="Get Plan Goals")
async def get_plan_goals(
    plan_id: str,
    status: Optional[str] = Query(default=None, description="Filter by goal status"),
    db: Session = Depends(get_db)
) -> List[Goal]:
    """Get all goals for a specific financial plan."""
    service = EntityServiceFactory.get_service("financial_plan", db)
    return service.get_plan_goals(db, plan_id, status=status)


@router.get("/plans/{plan_id}/scenarios", response_model=List[Scenario], summary="Get Plan Scenarios")
async def get_plan_scenarios(
    plan_id: str,
    scenario_type: Optional[str] = Query(default=None, description="Filter by scenario type"),
    db: Session = Depends(get_db)
) -> List[Scenario]:
    """Get all scenarios for a specific financial plan."""
    service = EntityServiceFactory.get_service("financial_plan", db)
    return service.get_plan_scenarios(db, plan_id, scenario_type=scenario_type)


@router.get("/plans/{plan_id}/cashflow", response_model=List[CashFlow], summary="Get Cash Flow Projections")
async def get_plan_cashflow(
    plan_id: str,
    startYear: Optional[int] = Query(default=None, description="Filter by start year"),
    endYear: Optional[int] = Query(default=None, description="Filter by end year"),
    db: Session = Depends(get_db)
) -> List[CashFlow]:
    """Get cash flow projections for a specific financial plan."""
    service = EntityServiceFactory.get_service("financial_plan", db)
    return service.get_plan_cashflow(db, plan_id, start_year=startYear, end_year=endYear)


@router.get("/plans/{plan_id}/networth", response_model=List[NetWorth], summary="Get Net Worth Analysis")
async def get_plan_networth(
    plan_id: str,
    startDate: Optional[str] = Query(default=None, description="Filter by start date (YYYY-MM-DD)"),
    endDate: Optional[str] = Query(default=None, description="Filter by end date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
) -> List[NetWorth]:
    """Get net worth analysis for a specific financial plan."""
    service = EntityServiceFactory.get_service("financial_plan", db)
    return service.get_plan_networth(db, plan_id, start_date=startDate, end_date=endDate)


@router.get("/goals", response_model=List[Goal], summary="List All Goals")
async def get_goals(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    client_id: Optional[str] = Query(default=None, description="Filter by client"),
    goal_type: Optional[str] = Query(default=None, description="Filter by goal type"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> List[Goal]:
    """Get all goals with optional filtering and pagination."""
    service = EntityServiceFactory.get_service("goal", db)
    return service.get_all(db, skip=skip, limit=limit, client_id=client_id, 
                          goal_type=goal_type, status=status)


@router.get("/goals/{goal_id}", response_model=Goal, summary="Get Goal by ID")
async def get_goal(
    goal_id: str,
    db: Session = Depends(get_db)
) -> Goal:
    """Get a specific goal by ID."""
    service = EntityServiceFactory.get_service("goal", db)
    goal = service.get_by_id(db, goal_id)
    
    if not goal:
        raise HTTPException(status_code=404, detail=f"Goal {goal_id} not found")
    
    return goal


@router.get("/scenarios/{scenario_id}", response_model=Scenario, summary="Get Scenario by ID")
async def get_scenario(
    scenario_id: str,
    db: Session = Depends(get_db)
) -> Scenario:
    """Get a specific scenario by ID."""
    service = EntityServiceFactory.get_service("scenario", db)
    scenario = service.get_by_id(db, scenario_id)
    
    if not scenario:
        raise HTTPException(status_code=404, detail=f"Scenario {scenario_id} not found")
    
    return scenario


@router.get("/cashflow/{plan_id}", response_model=List[CashFlow], summary="Get Cash Flow by Plan")
async def get_cashflow_by_plan(
    plan_id: str,
    start_year: Optional[int] = Query(default=None, description="Filter by start year"),
    end_year: Optional[int] = Query(default=None, description="Filter by end year"),
    db: Session = Depends(get_db)
) -> List[CashFlow]:
    """Get cash flow projections for a specific plan."""
    service = EntityServiceFactory.get_service("cash_flow", db)
    return service.get_by_plan_id(db, plan_id, start_year=start_year, end_year=end_year)


@router.get("/cashflow/{plan_id}/analysis", response_model=CashFlowAnalysis, summary="Get Cash Flow Analysis")
async def get_cashflow_analysis(
    plan_id: str,
    db: Session = Depends(get_db)
) -> CashFlowAnalysis:
    """Get cash flow analysis summary for a plan."""
    service = EntityServiceFactory.get_service("cash_flow", db)
    return service.get_cashflow_analysis(db, plan_id)


# ============================================================================
# VERSION 4: ACCOUNT & ASSET MANAGEMENT ENDPOINTS
# ============================================================================

@router.get("/accounts", response_model=List[Account], summary="List All Accounts")
async def get_accounts(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    client_id: Optional[str] = Query(default=None, description="Filter by client"),
    household_id: Optional[str] = Query(default=None, description="Filter by household"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> List[Account]:
    """Get all accounts with optional filtering and pagination."""
    service = EntityServiceFactory.get_service("account", db)
    return service.get_all(db, skip=skip, limit=limit, client_id=client_id, 
                          household_id=household_id, status=status)


@router.get("/accounts/{account_id}", response_model=AccountWithRelations, summary="Get Account by ID")
async def get_account(
    account_id: str,
    includeHoldings: Optional[bool] = Query(default=False, description="Include account holdings"),
    includePerformance: Optional[bool] = Query(default=False, description="Include performance metrics"),
    db: Session = Depends(get_db)
) -> AccountWithRelations:
    """Get a specific account by ID with optional holdings and performance."""
    service = EntityServiceFactory.get_service("account", db)
    account = service.get_by_id(db, account_id, include_holdings=includeHoldings, 
                              include_performance=includePerformance)
    
    if not account:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found")
    
    return account


@router.get("/accounts/{account_id}/holdings", response_model=List[Asset], summary="Get Account Holdings")
async def get_account_holdings(
    account_id: str,
    asOfDate: Optional[str] = Query(default=None, description="Holdings as of date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
) -> List[Asset]:
    """Get account holdings (assets)."""
    service = EntityServiceFactory.get_service("account", db)
    return service.get_account_holdings(db, account_id, as_of_date=asOfDate)


@router.get("/accounts/{account_id}/positions", response_model=List[Asset], summary="Get Account Positions")
async def get_account_positions(
    account_id: str,
    db: Session = Depends(get_db)
) -> List[Asset]:
    """Get account positions."""
    service = EntityServiceFactory.get_service("account", db)
    return service.get_account_positions(db, account_id)


@router.get("/accounts/{account_id}/performance", response_model=AccountPerformance, summary="Get Account Performance")
async def get_account_performance(
    account_id: str,
    startDate: Optional[str] = Query(default=None, description="Performance start date"),
    endDate: Optional[str] = Query(default=None, description="Performance end date"),
    db: Session = Depends(get_db)
) -> AccountPerformance:
    """Get account performance metrics."""
    service = EntityServiceFactory.get_service("account", db)
    return service.get_account_performance(db, account_id, start_date=startDate, end_date=endDate)


@router.get("/assets", response_model=List[Asset], summary="List All Assets")
async def get_assets(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    account_id: Optional[str] = Query(default=None, description="Filter by account"),
    symbol: Optional[str] = Query(default=None, description="Filter by symbol"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> List[Asset]:
    """Get all assets with optional filtering and pagination."""
    service = EntityServiceFactory.get_service("asset", db)
    return service.get_all(db, skip=skip, limit=limit, account_id=account_id, 
                          symbol=symbol, status=status)


@router.get("/assets/{asset_id}", response_model=Asset, summary="Get Asset by ID")
async def get_asset(
    asset_id: str,
    db: Session = Depends(get_db)
) -> Asset:
    """Get asset details by ID."""
    service = EntityServiceFactory.get_service("asset", db)
    asset = service.get_by_id(db, asset_id)
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {asset_id} not found")
    
    return asset


@router.get("/assets/{asset_id}/performance", response_model=AssetPerformance, summary="Get Asset Performance")
async def get_asset_performance(
    asset_id: str,
    startDate: Optional[str] = Query(default=None, description="Performance start date"),
    endDate: Optional[str] = Query(default=None, description="Performance end date"),
    db: Session = Depends(get_db)
) -> AssetPerformance:
    """Get asset performance metrics."""
    service = EntityServiceFactory.get_service("asset", db)
    return service.get_asset_performance(db, asset_id, start_date=startDate, end_date=endDate)


@router.get("/assetclasses", response_model=List[AssetClass], summary="List Asset Classes")
async def get_asset_classes(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    risk_level: Optional[str] = Query(default=None, description="Filter by risk level"),
    db: Session = Depends(get_db)
) -> List[AssetClass]:
    """Get all asset classes with optional filtering."""
    service = EntityServiceFactory.get_service("asset_class", db)
    return service.get_all(db, skip=skip, limit=limit, category=category, risk_level=risk_level)


@router.get("/assetclasses/{class_id}", response_model=AssetClass, summary="Get Asset Class by ID")
async def get_asset_class(
    class_id: str,
    db: Session = Depends(get_db)
) -> AssetClass:
    """Get specific asset class by ID."""
    service = EntityServiceFactory.get_service("asset_class", db)
    asset_class = service.get_by_id(db, class_id)
    
    if not asset_class:
        raise HTTPException(status_code=404, detail=f"Asset class {class_id} not found")
    
    return asset_class


@router.get("/liabilities", response_model=List[Liability], summary="List All Liabilities")
async def get_liabilities(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    client_id: Optional[str] = Query(default=None, description="Filter by client"),
    liability_type: Optional[str] = Query(default=None, description="Filter by liability type"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> List[Liability]:
    """Get all liabilities with optional filtering and pagination."""
    service = EntityServiceFactory.get_service("liability", db)
    return service.get_all(db, skip=skip, limit=limit, client_id=client_id, 
                          liability_type=liability_type, status=status)


@router.get("/liabilities/{liability_id}", response_model=Liability, summary="Get Liability by ID")
async def get_liability(
    liability_id: str,
    db: Session = Depends(get_db)
) -> Liability:
    """Get specific liability by ID."""
    service = EntityServiceFactory.get_service("liability", db)
    liability = service.get_by_id(db, liability_id)
    
    if not liability:
        raise HTTPException(status_code=404, detail=f"Liability {liability_id} not found")
    
    return liability


@router.get("/liabilities/{liability_id}/schedule", response_model=LiabilitySchedule, summary="Get Payment Schedule")
async def get_liability_schedule(
    liability_id: str,
    db: Session = Depends(get_db)
) -> LiabilitySchedule:
    """Get payment schedule for a liability."""
    service = EntityServiceFactory.get_service("liability", db)
    return service.get_liability_schedule(db, liability_id)


# ============================================================================
# ADDITIONAL ENDPOINTS
# ============================================================================

@router.get("/roles", response_model=List[Role], summary="List All Roles")
async def get_roles(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> List[Role]:
    """Get all roles with optional filtering."""
    service = EntityServiceFactory.get_service("role", db)
    return service.get_all(db, skip=skip, limit=limit, status=status)


@router.get("/roles/{role_id}", response_model=Role, summary="Get Role by ID")
async def get_role(
    role_id: str,
    db: Session = Depends(get_db)
) -> Role:
    """Get specific role by ID."""
    service = EntityServiceFactory.get_service("role", db)
    role = service.get_by_id(db, role_id)
    
    if not role:
        raise HTTPException(status_code=404, detail=f"Role {role_id} not found")
    
    return role


@router.get("/permissions", response_model=List[Permission], summary="List All Permissions")
async def get_permissions(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> List[Permission]:
    """Get all permissions with optional filtering."""
    service = EntityServiceFactory.get_service("permission", db)
    return service.get_all(db, skip=skip, limit=limit, category=category, status=status)


@router.get("/sharingrules", response_model=List[SharingRule], summary="List Sharing Rules")
async def get_sharing_rules(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    user_id: Optional[str] = Query(default=None, description="Filter by user"),
    client_id: Optional[str] = Query(default=None, description="Filter by client"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> List[SharingRule]:
    """Get client sharing rules with optional filtering."""
    service = EntityServiceFactory.get_service("sharing_rule", db)
    return service.get_all(db, skip=skip, limit=limit, user_id=user_id, 
                          client_id=client_id, status=status)


@router.get("/sharingrules/{rule_id}", response_model=SharingRule, summary="Get Sharing Rule by ID")
async def get_sharing_rule(
    rule_id: str,
    db: Session = Depends(get_db)
) -> SharingRule:
    """Get specific sharing rule by ID."""
    service = EntityServiceFactory.get_service("sharing_rule", db)
    rule = service.get_by_id(db, rule_id)
    
    if not rule:
        raise HTTPException(status_code=404, detail=f"Sharing rule {rule_id} not found")
    
    return rule


@router.get("/logons", response_model=List[Logon], summary="List All Logons")
async def get_logons(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1000),
    user_id: Optional[str] = Query(default=None, description="Filter by user"),
    logon_type: Optional[str] = Query(default=None, description="Filter by logon type"),
    status: Optional[str] = Query(default=None, description="Filter by status"),
    db: Session = Depends(get_db)
) -> List[Logon]:
    """Get all logons with optional filtering."""
    service = EntityServiceFactory.get_service("logon", db)
    return service.get_all(db, skip=skip, limit=limit, user_id=user_id, 
                          logon_type=logon_type, status=status)


@router.get("/logons/{logon_id}", response_model=Logon, summary="Get Logon by ID")
async def get_logon(
    logon_id: str,
    db: Session = Depends(get_db)
) -> Logon:
    """Get specific logon by ID."""
    service = EntityServiceFactory.get_service("logon", db)
    logon = service.get_by_id(db, logon_id)
    
    if not logon:
        raise HTTPException(status_code=404, detail=f"Logon {logon_id} not found")
    
    return logon


@router.get("/logons/{logon_id}/activity", response_model=Logon, summary="Get Logon Activity")
async def get_logon_activity(
    logon_id: str,
    db: Session = Depends(get_db)
) -> Logon:
    """Get logon activity history."""
    service = EntityServiceFactory.get_service("logon", db)
    return service.get_logon_activity(db, logon_id)