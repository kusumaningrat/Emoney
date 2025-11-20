# schema/financial.py - Version 3: Financial Planning Schemas

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal

# ============================================================================
# BASE SCHEMAS
# ============================================================================

class TimestampMixin(BaseModel):
    """Mixin for created/modified timestamps"""
    created_date: datetime
    modified_date: datetime

# ============================================================================
# FINANCIAL PLAN SCHEMAS
# ============================================================================

class FinancialPlanBase(BaseModel):
    """Base Financial Plan schema"""
    plan_name: str = Field(..., description="Financial plan name")
    plan_type: str = Field(default="Comprehensive", description="Type of financial plan")
    status: str = Field(default="Active", description="Plan status")
    start_date: Optional[datetime] = Field(None, description="Plan start date")
    end_date: Optional[datetime] = Field(None, description="Plan end date")
    last_reviewed: Optional[datetime] = Field(None, description="Last review date")
    retirement_readiness: Optional[str] = Field(default="Unknown", description="Retirement readiness status")

class FinancialPlanCreate(FinancialPlanBase):
    """Schema for creating a new financial plan"""
    client_id: str = Field(..., description="Associated client ID")
    household_id: Optional[str] = Field(None, description="Associated household ID")
    created_by: Optional[str] = Field(None, description="User who created the plan")

class FinancialPlanUpdate(BaseModel):
    """Schema for updating a financial plan"""
    plan_name: Optional[str] = None
    plan_type: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    last_reviewed: Optional[datetime] = None
    retirement_readiness: Optional[str] = None

class FinancialPlan(FinancialPlanBase, TimestampMixin):
    """Complete Financial Plan schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    plan_id: str = Field(..., description="Unique plan identifier")
    client_id: str = Field(..., description="Associated client ID")
    household_id: Optional[str] = Field(None, description="Associated household ID")
    created_by: Optional[str] = Field(None, description="User who created the plan")

class FinancialPlanWithRelations(FinancialPlan):
    """Financial Plan with related entities"""
    goals: List['Goal'] = []
    scenarios: List['Scenario'] = []
    cash_flows: List['CashFlow'] = []
    net_worths: List['NetWorth'] = []

# ============================================================================
# GOAL SCHEMAS
# ============================================================================

class GoalBase(BaseModel):
    """Base Goal schema"""
    goal_type: str = Field(default="Other", description="Type of goal")
    goal_name: str = Field(..., description="Goal name")
    description: Optional[str] = Field(None, description="Goal description")
    target_date: Optional[datetime] = Field(None, description="Target achievement date")
    target_amount: Optional[Decimal] = Field(None, description="Target amount needed")
    current_value: Optional[Decimal] = Field(default=Decimal('0.00'), description="Current value toward goal")
    monthly_contribution: Optional[Decimal] = Field(default=Decimal('0.00'), description="Monthly contribution")
    projected_value: Optional[Decimal] = Field(default=Decimal('0.00'), description="Projected final value")
    funding_percentage: Optional[Decimal] = Field(default=Decimal('0.00'), description="Percentage funded")
    priority: Optional[int] = Field(default=1, description="Goal priority (1=highest)")
    status: str = Field(default="OnTrack", description="Goal status")

class GoalCreate(GoalBase):
    """Schema for creating a new goal"""
    plan_id: str = Field(..., description="Associated financial plan ID")
    client_id: str = Field(..., description="Associated client ID")

class GoalUpdate(BaseModel):
    """Schema for updating a goal"""
    goal_type: Optional[str] = None
    goal_name: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    target_amount: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    monthly_contribution: Optional[Decimal] = None
    projected_value: Optional[Decimal] = None
    funding_percentage: Optional[Decimal] = None
    priority: Optional[int] = None
    status: Optional[str] = None

class Goal(GoalBase, TimestampMixin):
    """Complete Goal schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    goal_id: str = Field(..., description="Unique goal identifier")
    plan_id: str = Field(..., description="Associated financial plan ID")
    client_id: str = Field(..., description="Associated client ID")

class GoalWithPlan(Goal):
    """Goal with associated financial plan"""
    financial_plan: Optional[FinancialPlan] = None

# ============================================================================
# SCENARIO SCHEMAS
# ============================================================================

class ScenarioBase(BaseModel):
    """Base Scenario schema"""
    scenario_name: str = Field(..., description="Scenario name")
    scenario_type: str = Field(default="BaseCase", description="Type of scenario")
    description: Optional[str] = Field(None, description="Scenario description")
    assumptions: Optional[Dict[str, Any]] = Field(None, description="Scenario assumptions (JSON)")
    results: Optional[Dict[str, Any]] = Field(None, description="Scenario results (JSON)")
    status: str = Field(default="Active", description="Scenario status")

class ScenarioCreate(ScenarioBase):
    """Schema for creating a new scenario"""
    plan_id: str = Field(..., description="Associated financial plan ID")

class ScenarioUpdate(BaseModel):
    """Schema for updating a scenario"""
    scenario_name: Optional[str] = None
    scenario_type: Optional[str] = None
    description: Optional[str] = None
    assumptions: Optional[Dict[str, Any]] = None
    results: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class Scenario(ScenarioBase, TimestampMixin):
    """Complete Scenario schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    scenario_id: str = Field(..., description="Unique scenario identifier")
    plan_id: str = Field(..., description="Associated financial plan ID")

class ScenarioWithPlan(Scenario):
    """Scenario with associated financial plan"""
    financial_plan: Optional[FinancialPlan] = None

# ============================================================================
# CASH FLOW SCHEMAS
# ============================================================================

class CashFlowBase(BaseModel):
    """Base Cash Flow schema"""
    year: int = Field(..., description="Projection year")
    month: Optional[int] = Field(None, description="Projection month (optional)")
    total_income: Optional[Decimal] = Field(default=Decimal('0.00'), description="Total income")
    total_expenses: Optional[Decimal] = Field(default=Decimal('0.00'), description="Total expenses")
    net_cash_flow: Optional[Decimal] = Field(default=Decimal('0.00'), description="Net cash flow")
    cumulative_cash_flow: Optional[Decimal] = Field(default=Decimal('0.00'), description="Cumulative cash flow")
    inflation_rate: Optional[Decimal] = Field(default=Decimal('0.0300'), description="Assumed inflation rate")
    status: str = Field(default="Active", description="Cash flow status")

class CashFlowCreate(CashFlowBase):
    """Schema for creating a new cash flow projection"""
    plan_id: str = Field(..., description="Associated financial plan ID")

class CashFlowUpdate(BaseModel):
    """Schema for updating a cash flow projection"""
    year: Optional[int] = None
    month: Optional[int] = None
    total_income: Optional[Decimal] = None
    total_expenses: Optional[Decimal] = None
    net_cash_flow: Optional[Decimal] = None
    cumulative_cash_flow: Optional[Decimal] = None
    inflation_rate: Optional[Decimal] = None
    status: Optional[str] = None

class CashFlow(CashFlowBase, TimestampMixin):
    """Complete Cash Flow schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    cash_flow_id: str = Field(..., description="Unique cash flow identifier")
    plan_id: str = Field(..., description="Associated financial plan ID")

class CashFlowWithPlan(CashFlow):
    """Cash Flow with associated financial plan"""
    financial_plan: Optional[FinancialPlan] = None

class CashFlowAnalysis(BaseModel):
    """Cash Flow analysis summary"""
    plan_id: str
    total_income: Decimal
    total_expenses: Decimal
    net_cash_flow: Decimal
    projection_years: int
    final_cumulative_cash_flow: Decimal

# ============================================================================
# NET WORTH SCHEMAS
# ============================================================================

class NetWorthBase(BaseModel):
    """Base Net Worth schema"""
    as_of_date: datetime = Field(..., description="Net worth calculation date")
    total_assets: Optional[Decimal] = Field(default=Decimal('0.00'), description="Total assets")
    total_liabilities: Optional[Decimal] = Field(default=Decimal('0.00'), description="Total liabilities")
    net_worth: Optional[Decimal] = Field(default=Decimal('0.00'), description="Net worth (assets - liabilities)")
    liquid_assets: Optional[Decimal] = Field(default=Decimal('0.00'), description="Liquid assets")
    invested_assets: Optional[Decimal] = Field(default=Decimal('0.00'), description="Invested assets")
    use_assets: Optional[Decimal] = Field(default=Decimal('0.00'), description="Use assets (home, etc.)")
    status: str = Field(default="Active", description="Net worth status")

class NetWorthCreate(NetWorthBase):
    """Schema for creating a new net worth record"""
    plan_id: str = Field(..., description="Associated financial plan ID")
    household_id: Optional[str] = Field(None, description="Associated household ID")

class NetWorthUpdate(BaseModel):
    """Schema for updating a net worth record"""
    as_of_date: Optional[datetime] = None
    total_assets: Optional[Decimal] = None
    total_liabilities: Optional[Decimal] = None
    net_worth: Optional[Decimal] = None
    liquid_assets: Optional[Decimal] = None
    invested_assets: Optional[Decimal] = None
    use_assets: Optional[Decimal] = None
    status: Optional[str] = None

class NetWorth(NetWorthBase, TimestampMixin):
    """Complete Net Worth schema for responses"""
    model_config = ConfigDict(from_attributes=True)
    
    net_worth_id: str = Field(..., description="Unique net worth identifier")
    plan_id: str = Field(..., description="Associated financial plan ID")
    household_id: Optional[str] = Field(None, description="Associated household ID")

class NetWorthWithRelations(NetWorth):
    """Net Worth with associated entities"""
    financial_plan: Optional[FinancialPlan] = None

# ============================================================================
# SEARCH & FILTER SCHEMAS
# ============================================================================

class FinancialPlanSearchParams(BaseModel):
    """Parameters for financial plan search"""
    client_id: Optional[str] = Field(None, description="Filter by client")
    household_id: Optional[str] = Field(None, description="Filter by household")
    status: Optional[str] = Field(None, description="Filter by status")
    plan_type: Optional[str] = Field(None, description="Filter by plan type")
    retirement_readiness: Optional[str] = Field(None, description="Filter by retirement readiness")

class GoalSearchParams(BaseModel):
    """Parameters for goal search"""
    client_id: Optional[str] = Field(None, description="Filter by client")
    plan_id: Optional[str] = Field(None, description="Filter by plan")
    goal_type: Optional[str] = Field(None, description="Filter by goal type")
    status: Optional[str] = Field(None, description="Filter by status")
    priority: Optional[int] = Field(None, description="Filter by priority")

class ScenarioSearchParams(BaseModel):
    """Parameters for scenario search"""
    plan_id: Optional[str] = Field(None, description="Filter by plan")
    scenario_type: Optional[str] = Field(None, description="Filter by scenario type")
    status: Optional[str] = Field(None, description="Filter by status")

class CashFlowSearchParams(BaseModel):
    """Parameters for cash flow search"""
    plan_id: Optional[str] = Field(None, description="Filter by plan")
    year: Optional[int] = Field(None, description="Filter by year")
    start_year: Optional[int] = Field(None, description="Filter by start year")
    end_year: Optional[int] = Field(None, description="Filter by end year")
    status: Optional[str] = Field(None, description="Filter by status")

class NetWorthSearchParams(BaseModel):
    """Parameters for net worth search"""
    plan_id: Optional[str] = Field(None, description="Filter by plan")
    household_id: Optional[str] = Field(None, description="Filter by household")
    start_date: Optional[datetime] = Field(None, description="Filter by start date")
    end_date: Optional[datetime] = Field(None, description="Filter by end date")
    status: Optional[str] = Field(None, description="Filter by status")

# ============================================================================
# PAGINATION SCHEMAS
# ============================================================================

class PaginationParams(BaseModel):
    """Pagination parameters"""
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of records to return")

class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    total: int = Field(..., description="Total number of records")
    skip: int = Field(..., description="Number of records skipped")
    limit: int = Field(..., description="Maximum records returned")
    has_more: bool = Field(..., description="Whether more records are available")

class PaginatedFinancialPlansResponse(PaginatedResponse):
    """Paginated financial plans response"""
    items: List[FinancialPlan] = []

class PaginatedGoalsResponse(PaginatedResponse):
    """Paginated goals response"""
    items: List[Goal] = []

class PaginatedScenariosResponse(PaginatedResponse):
    """Paginated scenarios response"""
    items: List[Scenario] = []

class PaginatedCashFlowsResponse(PaginatedResponse):
    """Paginated cash flows response"""
    items: List[CashFlow] = []

class PaginatedNetWorthsResponse(PaginatedResponse):
    """Paginated net worths response"""
    items: List[NetWorth] = []

# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class FinancialPlanResponse(BaseModel):
    """Standard financial plan response"""
    status: str = "success"
    data: FinancialPlan

class GoalResponse(BaseModel):
    """Standard goal response"""
    status: str = "success"
    data: Goal

class ScenarioResponse(BaseModel):
    """Standard scenario response"""
    status: str = "success"
    data: Scenario

class CashFlowResponse(BaseModel):
    """Standard cash flow response"""
    status: str = "success"
    data: CashFlow

class NetWorthResponse(BaseModel):
    """Standard net worth response"""
    status: str = "success"
    data: NetWorth

class CashFlowAnalysisResponse(BaseModel):
    """Cash flow analysis response"""
    status: str = "success"
    data: CashFlowAnalysis

# ============================================================================
# SUMMARY SCHEMAS
# ============================================================================

class PlanSummary(BaseModel):
    """Financial plan summary"""
    plan_id: str
    plan_name: str
    client_name: str
    total_goals: int
    goals_on_track: int
    goals_off_track: int
    net_worth: Optional[Decimal] = None
    retirement_readiness: str
    last_reviewed: Optional[datetime] = None

class GoalSummary(BaseModel):
    """Goal summary"""
    goal_id: str
    goal_name: str
    goal_type: str
    target_amount: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    funding_percentage: Optional[Decimal] = None
    status: str
    target_date: Optional[datetime] = None

class ClientFinancialSummary(BaseModel):
    """Client financial summary"""
    client_id: str
    client_name: str
    total_plans: int
    active_goals: int
    total_net_worth: Optional[Decimal] = None
    retirement_readiness: Optional[str] = None
    last_plan_review: Optional[datetime] = None

# Forward references for relationships
FinancialPlanWithRelations.model_rebuild()
GoalWithPlan.model_rebuild()
ScenarioWithPlan.model_rebuild()
CashFlowWithPlan.model_rebuild()
NetWorthWithRelations.model_rebuild()