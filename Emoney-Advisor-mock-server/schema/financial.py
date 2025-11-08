from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum
from .base import PaginatedResponse


class PlanType(str, Enum):
    BASE = "Base Facts"
    SCENARIO = "Advanced Planning Scenario"
    WHAT_IF = "What-If"


# Base schemas
class FinancialPlanBase(BaseModel):
    client_id: str = Field(..., description="ID of client plan belongs to")
    name: str = Field(..., description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    status: str = Field("active", description="Plan status")


class GoalBase(BaseModel):
    plan_id: str = Field(..., description="ID of plan goal belongs to")
    name: str = Field(..., description="Goal name")
    description: Optional[str] = Field(None, description="Goal description")
    target_amount: Optional[float] = Field(None, description="Target amount")
    current_amount: Optional[float] = Field(0.0, description="Current amount")
    target_date: Optional[date] = Field(None, description="Target date")
    priority: Optional[str] = Field(None, description="Goal priority")
    category: Optional[str] = Field(None, description="Goal category")


class MonteCarloBase(BaseModel):
    plan_id: str = Field(..., description="ID of plan simulation belongs to")
    success_rate: Optional[float] = Field(None, description="Success rate")
    iterations: Optional[int] = Field(None, description="Number of iterations")
    confidence_interval: Optional[float] = Field(None, description="Confidence interval")
    median_ending_value: Optional[float] = Field(None, description="Median ending value")
    lowest_percentile_value: Optional[float] = Field(None, description="Lowest percentile value")
    highest_percentile_value: Optional[float] = Field(None, description="Highest percentile value")
    results_detail: Optional[Dict[str, Any]] = Field(None, description="Detailed results")


class ProjectionBase(BaseModel):
    plan_id: str = Field(..., description="ID of plan projection belongs to")
    year: int = Field(..., description="Projection year")
    assets: Optional[float] = Field(None, description="Asset value")
    liabilities: Optional[float] = Field(None, description="Liability value")
    net_worth: Optional[float] = Field(None, description="Net worth")
    income: Optional[float] = Field(None, description="Income")
    expenses: Optional[float] = Field(None, description="Expenses")
    cash_flow: Optional[float] = Field(None, description="Cash flow")


class CashFlowBase(BaseModel):
    plan_id: str = Field(..., description="ID of plan cash flow belongs to")
    salary_income: float = Field(0.0, description="Salary income")
    business_income: float = Field(0.0, description="Business income")
    investment_income: float = Field(0.0, description="Investment income")
    rental_income: float = Field(0.0, description="Rental income")
    other_income: float = Field(0.0, description="Other income")
    total_income: float = Field(0.0, description="Total income")
    housing_expense: float = Field(0.0, description="Housing expense")
    utilities_expense: float = Field(0.0, description="Utilities expense")
    food_expense: float = Field(0.0, description="Food expense")
    transportation_expense: float = Field(0.0, description="Transportation expense")
    healthcare_expense: float = Field(0.0, description="Healthcare expense")
    insurance_expense: float = Field(0.0, description="Insurance expense")
    debt_payments: float = Field(0.0, description="Debt payments")
    entertainment_expense: float = Field(0.0, description="Entertainment expense")
    personal_expense: float = Field(0.0, description="Personal expense")
    other_expense: float = Field(0.0, description="Other expense")
    total_expenses: float = Field(0.0, description="Total expenses")
    net_cash_flow: float = Field(0.0, description="Net cash flow")
    period: Optional[str] = Field(None, description="Time period")
    year: Optional[int] = Field(None, description="Year")


# Response models with ID and timestamps
class FinancialPlanResponse(BaseModel):
    id: str = Field(..., description="Plan ID")
    clientId: str = Field(..., description="ID of client plan belongs to")
    name: str = Field(..., description="Plan name")
    description: Optional[str] = Field(None, description="Plan description")
    status: str = Field("active", description="Plan status")
    createdAt: datetime = Field(..., description="Timestamp when plan was created")
    updatedAt: datetime = Field(..., description="Timestamp when plan was last updated")
    
    model_config = {
        "from_attributes": True
    }


class GoalResponse(BaseModel):
    id: str = Field(..., description="Goal ID")
    planId: str = Field(..., description="ID of plan goal belongs to")
    name: str = Field(..., description="Goal name")
    description: Optional[str] = Field(None, description="Goal description")
    targetAmount: Optional[float] = Field(None, description="Target amount")
    currentAmount: Optional[float] = Field(0.0, description="Current amount")
    targetDate: Optional[date] = Field(None, description="Target date")
    priority: Optional[str] = Field(None, description="Goal priority")
    category: Optional[str] = Field(None, description="Goal category")
    createdAt: datetime = Field(..., description="Timestamp when goal was created")
    updatedAt: datetime = Field(..., description="Timestamp when goal was last updated")
    
    model_config = {
        "from_attributes": True
    }


class MonteCarloResponse(BaseModel):
    id: str = Field(..., description="Monte Carlo ID")
    planId: str = Field(..., description="ID of plan simulation belongs to")
    successRate: Optional[float] = Field(None, description="Success rate")
    iterations: Optional[int] = Field(None, description="Number of iterations")
    confidenceInterval: Optional[float] = Field(None, description="Confidence interval")
    medianEndingValue: Optional[float] = Field(None, description="Median ending value")
    lowestPercentileValue: Optional[float] = Field(None, description="Lowest percentile value")
    highestPercentileValue: Optional[float] = Field(None, description="Highest percentile value")
    resultsDetail: Optional[Dict[str, Any]] = Field(None, description="Detailed results")
    createdAt: datetime = Field(..., description="Timestamp when simulation was created")
    updatedAt: datetime = Field(..., description="Timestamp when simulation was last updated")
    
    model_config = {
        "from_attributes": True
    }


class ProjectionResponse(BaseModel):
    id: str = Field(..., description="Projection ID")
    planId: str = Field(..., description="ID of plan projection belongs to")
    year: int = Field(..., description="Projection year")
    assets: Optional[float] = Field(None, description="Asset value")
    liabilities: Optional[float] = Field(None, description="Liability value")
    netWorth: Optional[float] = Field(None, description="Net worth")
    income: Optional[float] = Field(None, description="Income")
    expenses: Optional[float] = Field(None, description="Expenses")
    cashFlow: Optional[float] = Field(None, description="Cash flow")
    createdAt: datetime = Field(..., description="Timestamp when projection was created")
    
    model_config = {
        "from_attributes": True
    }


class CashFlowResponse(BaseModel):
    id: str = Field(..., description="Cash flow ID")
    planId: str = Field(..., description="ID of plan cash flow belongs to")
    salaryIncome: float = Field(0.0, description="Salary income")
    businessIncome: float = Field(0.0, description="Business income")
    investmentIncome: float = Field(0.0, description="Investment income")
    rentalIncome: float = Field(0.0, description="Rental income")
    otherIncome: float = Field(0.0, description="Other income")
    totalIncome: float = Field(0.0, description="Total income")
    housingExpense: float = Field(0.0, description="Housing expense")
    utilitiesExpense: float = Field(0.0, description="Utilities expense")
    foodExpense: float = Field(0.0, description="Food expense")
    transportationExpense: float = Field(0.0, description="Transportation expense")
    healthcareExpense: float = Field(0.0, description="Healthcare expense")
    insuranceExpense: float = Field(0.0, description="Insurance expense")
    debtPayments: float = Field(0.0, description="Debt payments")
    entertainmentExpense: float = Field(0.0, description="Entertainment expense")
    personalExpense: float = Field(0.0, description="Personal expense")
    otherExpense: float = Field(0.0, description="Other expense")
    totalExpenses: float = Field(0.0, description="Total expenses")
    netCashFlow: float = Field(0.0, description="Net cash flow")
    period: Optional[str] = Field(None, description="Time period")
    year: Optional[int] = Field(None, description="Year")
    createdAt: datetime = Field(..., description="Timestamp when cash flow was created")
    updatedAt: datetime = Field(..., description="Timestamp when cash flow was last updated")
    
    model_config = {
        "from_attributes": True
    }


# Paginated list response classes
class FinancialPlanListResponse(BaseModel):
    plans: List[FinancialPlanResponse] = Field(..., description="List of plans")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class GoalListResponse(BaseModel):
    goals: List[GoalResponse] = Field(..., description="List of goals")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class MonteCarloListResponse(BaseModel):
    monteCarlos: List[MonteCarloResponse] = Field(..., description="List of Monte Carlo simulations")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class ProjectionListResponse(BaseModel):
    projections: List[ProjectionResponse] = Field(..., description="List of projections")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class CashFlowListResponse(BaseModel):
    cashFlows: List[CashFlowResponse] = Field(..., description="List of cash flows")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class FinancialPlanFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    status: Optional[str] = Field(None, description="Filter by plan status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("created_at", description="Sort field")
    count: bool = Field(False, description="Return count only")


class GoalFilterParams(BaseModel):
    plan_id: Optional[str] = Field(None, description="Filter by plan ID")
    category: Optional[str] = Field(None, description="Filter by goal category")
    priority: Optional[str] = Field(None, description="Filter by goal priority")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("priority", description="Sort field")
    count: bool = Field(False, description="Return count only")


class MonteCarloFilterParams(BaseModel):
    plan_id: Optional[str] = Field(None, description="Filter by plan ID")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("created_at", description="Sort field")
    count: bool = Field(False, description="Return count only")


class ProjectionFilterParams(BaseModel):
    plan_id: Optional[str] = Field(None, description="Filter by plan ID")
    year: Optional[int] = Field(None, description="Filter by year")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("year", description="Sort field")
    count: bool = Field(False, description="Return count only")


class CashFlowFilterParams(BaseModel):
    plan_id: Optional[str] = Field(None, description="Filter by plan ID")
    year: Optional[int] = Field(None, description="Filter by year")
    period: Optional[str] = Field(None, description="Filter by period")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("year", description="Sort field")
    count: bool = Field(False, description="Return count only")