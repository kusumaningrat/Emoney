from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from enum import Enum
from .base import PaginatedResponse


class IncomeType(str, Enum):
    SALARY = "Salary"
    BONUS = "Bonus"
    SELF_EMPLOYMENT = "Self-Employment"
    RENTAL = "Rental"
    INVESTMENT = "Investment"
    PENSION = "Pension"
    SOCIAL_SECURITY = "Social Security"
    OTHER = "Other"


class ExpenseCategory(str, Enum):
    HOUSING = "Housing"
    TRANSPORTATION = "Transportation"
    FOOD = "Food"
    HEALTHCARE = "Healthcare"
    ENTERTAINMENT = "Entertainment"
    DEBT = "Debt"
    EDUCATION = "Education"
    TRAVEL = "Travel"
    INSURANCE = "Insurance"
    PERSONAL = "Personal"
    UTILITIES = "Utilities"
    GIFTS = "Gifts & Donations"
    OTHER = "Other"


class FrequencyType(str, Enum):
    ANNUAL = "Annual"
    MONTHLY = "Monthly"
    BI_WEEKLY = "Bi-weekly"
    WEEKLY = "Weekly"
    ONE_TIME = "One-time"


# Base schemas
class SpendingBase(BaseModel):
    client_id: str = Field(..., description="ID of client spending record belongs to")
    workspace_id: str = Field(..., description="Workspace ID")
    status: str = Field(..., description="Spending status")
    annual_income: Optional[float] = Field(None, description="Annual income")
    annual_expenses: Optional[float] = Field(None, description="Annual expenses")
    annual_savings: Optional[float] = Field(None, description="Annual savings")
    monthly_income: Optional[float] = Field(None, description="Monthly income")
    monthly_expenses: Optional[float] = Field(None, description="Monthly expenses")
    monthly_savings: Optional[float] = Field(None, description="Monthly savings")
    savings_rate: Optional[float] = Field(None, description="Savings rate")
    expense_to_income_ratio: Optional[float] = Field(None, description="Expense to income ratio")
    cash_flow_status: Optional[str] = Field(None, description="Cash flow status")
    last_update: Optional[date] = Field(None, description="Last update date")
    sync_status: Optional[str] = Field(None, description="Sync status")
    expense_categories: Optional[Dict[str, Any]] = Field(None, description="Expense categories")
    linked_accounts: Optional[Dict[str, Any]] = Field(None, description="Linked accounts")
    analysis: Optional[Dict[str, Any]] = Field(None, description="Analysis")
    notes: Optional[str] = Field(None, description="Notes")
    created_by: str = Field(..., description="ID of user who created the spending record")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the spending record")


class BudgetBase(BaseModel):
    spending_id: str = Field(..., description="ID of spending record budget belongs to")
    client_id: str = Field(..., description="ID of client budget belongs to")
    workspace_id: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Budget name")
    status: str = Field(..., description="Budget status")
    period_type: Optional[str] = Field(None, description="Period type")
    start_date: date = Field(..., description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    total_income: Optional[float] = Field(None, description="Total income")
    total_expenses: Optional[float] = Field(None, description="Total expenses")
    total_savings: Optional[float] = Field(None, description="Total savings")
    allocations: Optional[Dict[str, Any]] = Field(None, description="Allocations")
    category_limits: Optional[Dict[str, Any]] = Field(None, description="Category limits")
    progress: Optional[Dict[str, Any]] = Field(None, description="Progress")
    auto_categorization: bool = Field(False, description="Whether auto categorization is enabled")
    notifications: Optional[Dict[str, Any]] = Field(None, description="Notifications")
    notes: Optional[str] = Field(None, description="Notes")
    created_by: str = Field(..., description="ID of user who created the budget")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the budget")


class IncomeBase(BaseModel):
    spending_id: str = Field(..., description="ID of spending record income belongs to")
    client_id: str = Field(..., description="ID of client income belongs to")
    plan_id: Optional[str] = Field(None, description="ID of plan income belongs to")
    workspace_id: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Income name")
    income_type: str = Field(..., description="Income type")
    status: str = Field(..., description="Income status")
    frequency: str = Field(..., description="Income frequency")
    annual_amount: Optional[float] = Field(None, description="Annual amount")
    monthly_amount: Optional[float] = Field(None, description="Monthly amount")
    amount_per_payment: Optional[float] = Field(None, description="Amount per payment")
    payment_day: Optional[int] = Field(None, description="Payment day")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    growth_rate: Optional[float] = Field(None, description="Growth rate")
    income_source: Optional[Dict[str, Any]] = Field(None, description="Income source")
    taxable: bool = Field(True, description="Whether income is taxable")
    tax_rate: Optional[float] = Field(None, description="Tax rate")
    notes: Optional[str] = Field(None, description="Notes")
    created_by: str = Field(..., description="ID of user who created the income")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the income")


class ExpenseBase(BaseModel):
    spending_id: str = Field(..., description="ID of spending record expense belongs to")
    client_id: str = Field(..., description="ID of client expense belongs to")
    plan_id: Optional[str] = Field(None, description="ID of plan expense belongs to")
    goal_id: Optional[str] = Field(None, description="ID of goal expense belongs to")
    workspace_id: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Expense name")
    category: str = Field(..., description="Expense category")
    status: str = Field(..., description="Expense status")
    frequency: str = Field(..., description="Expense frequency")
    annual_amount: Optional[float] = Field(None, description="Annual amount")
    monthly_amount: Optional[float] = Field(None, description="Monthly amount")
    amount_per_payment: Optional[float] = Field(None, description="Amount per payment")
    payment_day: Optional[int] = Field(None, description="Payment day")
    start_date: Optional[date] = Field(None, description="Start date")
    end_date: Optional[date] = Field(None, description="End date")
    growth_rate: Optional[float] = Field(None, description="Growth rate")
    auto_payment: bool = Field(False, description="Whether expense has auto payment")
    payment_method: Optional[str] = Field(None, description="Payment method")
    is_tax_deductible: bool = Field(False, description="Whether expense is tax deductible")
    expense_source: Optional[Dict[str, Any]] = Field(None, description="Expense source")
    is_discretionary: bool = Field(False, description="Whether expense is discretionary")
    is_goal: bool = Field(False, description="Whether expense is a goal")
    notes: Optional[str] = Field(None, description="Notes")
    created_by: str = Field(..., description="ID of user who created the expense")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the expense")


class BudgetCategoryBase(BaseModel):
    budget_id: str = Field(..., description="ID of budget category belongs to")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    amount: float = Field(..., description="Category amount")
    created_by: str = Field(..., description="ID of user who created the budget category")
    updated_by: Optional[str] = Field(None, description="ID of user who last updated the budget category")


# Response models with ID and timestamps
class SpendingResponse(BaseModel):
    id: str = Field(..., description="Spending ID")
    clientId: str = Field(..., description="ID of client spending record belongs to")
    workspaceId: str = Field(..., description="Workspace ID")
    status: str = Field(..., description="Spending status")
    annualIncome: Optional[float] = Field(None, description="Annual income")
    annualExpenses: Optional[float] = Field(None, description="Annual expenses")
    annualSavings: Optional[float] = Field(None, description="Annual savings")
    monthlyIncome: Optional[float] = Field(None, description="Monthly income")
    monthlyExpenses: Optional[float] = Field(None, description="Monthly expenses")
    monthlySavings: Optional[float] = Field(None, description="Monthly savings")
    savingsRate: Optional[float] = Field(None, description="Savings rate")
    expenseToIncomeRatio: Optional[float] = Field(None, description="Expense to income ratio")
    cashFlowStatus: Optional[str] = Field(None, description="Cash flow status")
    lastUpdate: Optional[date] = Field(None, description="Last update date")
    syncStatus: Optional[str] = Field(None, description="Sync status")
    expenseCategories: Optional[Dict[str, Any]] = Field(None, description="Expense categories")
    linkedAccounts: Optional[Dict[str, Any]] = Field(None, description="Linked accounts")
    analysis: Optional[Dict[str, Any]] = Field(None, description="Analysis")
    notes: Optional[str] = Field(None, description="Notes")
    createdBy: str = Field(..., description="ID of user who created the spending record")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the spending record")
    createdAt: datetime = Field(..., description="Timestamp when spending record was created")
    updatedAt: datetime = Field(..., description="Timestamp when spending record was last updated")
    
    model_config = {
        "from_attributes": True
    }


class BudgetResponse(BaseModel):
    id: str = Field(..., description="Budget ID")
    spendingId: str = Field(..., description="ID of spending record budget belongs to")
    clientId: str = Field(..., description="ID of client budget belongs to")
    workspaceId: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Budget name")
    status: str = Field(..., description="Budget status")
    periodType: Optional[str] = Field(None, description="Period type")
    startDate: date = Field(..., description="Start date")
    endDate: Optional[date] = Field(None, description="End date")
    totalIncome: Optional[float] = Field(None, description="Total income")
    totalExpenses: Optional[float] = Field(None, description="Total expenses")
    totalSavings: Optional[float] = Field(None, description="Total savings")
    allocations: Optional[Dict[str, Any]] = Field(None, description="Allocations")
    categoryLimits: Optional[Dict[str, Any]] = Field(None, description="Category limits")
    progress: Optional[Dict[str, Any]] = Field(None, description="Progress")
    autoCategorization: bool = Field(False, description="Whether auto categorization is enabled")
    notifications: Optional[Dict[str, Any]] = Field(None, description="Notifications")
    notes: Optional[str] = Field(None, description="Notes")
    createdBy: str = Field(..., description="ID of user who created the budget")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the budget")
    createdAt: datetime = Field(..., description="Timestamp when budget was created")
    updatedAt: datetime = Field(..., description="Timestamp when budget was last updated")
    
    model_config = {
        "from_attributes": True
    }


class IncomeResponse(BaseModel):
    id: str = Field(..., description="Income ID")
    spendingId: str = Field(..., description="ID of spending record income belongs to")
    clientId: str = Field(..., description="ID of client income belongs to")
    planId: Optional[str] = Field(None, description="ID of plan income belongs to")
    workspaceId: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Income name")
    incomeType: str = Field(..., description="Income type")
    status: str = Field(..., description="Income status")
    frequency: str = Field(..., description="Income frequency")
    annualAmount: Optional[float] = Field(None, description="Annual amount")
    monthlyAmount: Optional[float] = Field(None, description="Monthly amount")
    amountPerPayment: Optional[float] = Field(None, description="Amount per payment")
    paymentDay: Optional[int] = Field(None, description="Payment day")
    startDate: Optional[date] = Field(None, description="Start date")
    endDate: Optional[date] = Field(None, description="End date")
    growthRate: Optional[float] = Field(None, description="Growth rate")
    incomeSource: Optional[Dict[str, Any]] = Field(None, description="Income source")
    taxable: bool = Field(True, description="Whether income is taxable")
    taxRate: Optional[float] = Field(None, description="Tax rate")
    notes: Optional[str] = Field(None, description="Notes")
    createdBy: str = Field(..., description="ID of user who created the income")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the income")
    createdAt: datetime = Field(..., description="Timestamp when income was created")
    updatedAt: datetime = Field(..., description="Timestamp when income was last updated")
    
    model_config = {
        "from_attributes": True
    }


class ExpenseResponse(BaseModel):
    id: str = Field(..., description="Expense ID")
    spendingId: str = Field(..., description="ID of spending record expense belongs to")
    clientId: str = Field(..., description="ID of client expense belongs to")
    planId: Optional[str] = Field(None, description="ID of plan expense belongs to")
    goalId: Optional[str] = Field(None, description="ID of goal expense belongs to")
    workspaceId: str = Field(..., description="Workspace ID")
    name: str = Field(..., description="Expense name")
    category: str = Field(..., description="Expense category")
    status: str = Field(..., description="Expense status")
    frequency: str = Field(..., description="Expense frequency")
    annualAmount: Optional[float] = Field(None, description="Annual amount")
    monthlyAmount: Optional[float] = Field(None, description="Monthly amount")
    amountPerPayment: Optional[float] = Field(None, description="Amount per payment")
    paymentDay: Optional[int] = Field(None, description="Payment day")
    startDate: Optional[date] = Field(None, description="Start date")
    endDate: Optional[date] = Field(None, description="End date")
    growthRate: Optional[float] = Field(None, description="Growth rate")
    autoPayment: bool = Field(False, description="Whether expense has auto payment")
    paymentMethod: Optional[str] = Field(None, description="Payment method")
    isTaxDeductible: bool = Field(False, description="Whether expense is tax deductible")
    expenseSource: Optional[Dict[str, Any]] = Field(None, description="Expense source")
    isDiscretionary: bool = Field(False, description="Whether expense is discretionary")
    isGoal: bool = Field(False, description="Whether expense is a goal")
    notes: Optional[str] = Field(None, description="Notes")
    createdBy: str = Field(..., description="ID of user who created the expense")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the expense")
    createdAt: datetime = Field(..., description="Timestamp when expense was created")
    updatedAt: datetime = Field(..., description="Timestamp when expense was last updated")
    
    model_config = {
        "from_attributes": True
    }


class BudgetCategoryResponse(BaseModel):
    id: str = Field(..., description="Budget category ID")
    budgetId: str = Field(..., description="ID of budget category belongs to")
    name: str = Field(..., description="Category name")
    description: Optional[str] = Field(None, description="Category description")
    amount: float = Field(..., description="Category amount")
    createdBy: str = Field(..., description="ID of user who created the budget category")
    updatedBy: Optional[str] = Field(None, description="ID of user who last updated the budget category")
    createdAt: datetime = Field(..., description="Timestamp when budget category was created")
    updatedAt: datetime = Field(..., description="Timestamp when budget category was last updated")
    
    model_config = {
        "from_attributes": True
    }


# Paginated list response classes
class SpendingListResponse(BaseModel):
    spending: List[SpendingResponse] = Field(..., description="List of spending records")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class BudgetListResponse(BaseModel):
    budgets: List[BudgetResponse] = Field(..., description="List of budgets")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class IncomeListResponse(BaseModel):
    income: List[IncomeResponse] = Field(..., description="List of income records")
    totalAnnualIncome: float = Field(0.0, description="Total annual income")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class ExpenseListResponse(BaseModel):
    expenses: List[ExpenseResponse] = Field(..., description="List of expenses")
    totalAnnualExpenses: float = Field(0.0, description="Total annual expenses")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


class BudgetCategoryListResponse(BaseModel):
    categories: List[BudgetCategoryResponse] = Field(..., description="List of budget categories")
    totalAmount: float = Field(0.0, description="Total category amount")
    pagination: Optional[PaginatedResponse] = Field(None, description="Pagination information")

    model_config = {
        "from_attributes": True
    }


# Filter parameters
class SpendingFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    status: Optional[str] = Field(None, description="Filter by spending status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("created_at", description="Sort field")
    count: bool = Field(False, description="Return count only")


class BudgetFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    spending_id: Optional[str] = Field(None, description="Filter by spending ID")
    status: Optional[str] = Field(None, description="Filter by budget status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("name", description="Sort field")
    count: bool = Field(False, description="Return count only")


class IncomeFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    spending_id: Optional[str] = Field(None, description="Filter by spending ID")
    plan_id: Optional[str] = Field(None, description="Filter by plan ID")
    income_type: Optional[str] = Field(None, description="Filter by income type")
    status: Optional[str] = Field(None, description="Filter by income status")
    taxable: Optional[bool] = Field(None, description="Filter by taxable status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("annual_amount", description="Sort field")
    count: bool = Field(False, description="Return count only")


class ExpenseFilterParams(BaseModel):
    client_id: Optional[str] = Field(None, description="Filter by client ID")
    spending_id: Optional[str] = Field(None, description="Filter by spending ID")
    plan_id: Optional[str] = Field(None, description="Filter by plan ID")
    category: Optional[str] = Field(None, description="Filter by expense category")
    status: Optional[str] = Field(None, description="Filter by expense status")
    is_discretionary: Optional[bool] = Field(None, description="Filter by discretionary status")
    is_tax_deductible: Optional[bool] = Field(None, description="Filter by tax deductible status")
    is_goal: Optional[bool] = Field(None, description="Filter by goal status")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("annual_amount", description="Sort field")
    count: bool = Field(False, description="Return count only")


class BudgetCategoryFilterParams(BaseModel):
    budget_id: Optional[str] = Field(None, description="Filter by budget ID")
    name: Optional[str] = Field(None, description="Filter by category name")
    page: int = Field(1, description="Page number")
    limit: int = Field(10, description="Records per page")
    sort: str = Field("amount", description="Sort field")
    count: bool = Field(False, description="Return count only")