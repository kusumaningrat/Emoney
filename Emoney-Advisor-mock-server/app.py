from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db, Base, engine, SessionLocal
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service
from routes.health import router as health_router
from routes.admin import router as admin_router

# Core users & User Management
from models.users import User, Role, Permission, Firm, Logon, Workspace, Advisor

# Client & Relationship Management
from models.clients import Client, Spouse, Household, HouseholdMember, Contact, Relationship

# Financial Planning
from models.financial import (
    FinancialPlan, Goal, MonteCarlo, Projection, CashFlow, Scenario, 
    PlanIncome
)

# Account Management
from models.accounts import Account, AccountTypeModel, Investment, Liability

# Asset Management
from models.assets import Asset, AssetClass, Allocation, Security, Holding

# Spending & Budget Management
from models.spending import Spending, Budget, Income, Expense, BudgetCategory

# Estate Planning
from models.estate import Estate, Will, Trust, Beneficiary

# Retirement Planning
from models.retirement import RetirementPlan, Pension, SocialSecurity, RMD

# Insurance Planning
from models.insurance import Insurance, InsurancePolicy, Coverage, Premium

# Tax Planning
from models.tax import TaxPlan, TaxBracket, Deduction, Credit, FinancialTaxDeduction, TaxCredit

# Document Management
from models.documents import FileType, VaultDocument, Attachment, Note, Task, Alert

# Comment out database table creation to avoid the index creation error
Base.metadata.create_all(bind=engine, checkfirst=True)

app = FastAPI(
    title="eMoney Advisor Mock API",
    description="A FastAPI-based mock implementation of eMoney Advisor APIs",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def seed_system_user():
    """Create system user if it doesn't exist - MUST BE CALLED BEFORE ANY SEEDING"""
    db = SessionLocal()
    try:
        existing = db.query(User).filter_by(id='system').first()
        if existing:
            print("✓ System user already exists")
            return
        
        print("Creating system user...")
        
        # Create system user without workspace_id
        system_user = User(
            id='system',
            # Remove workspace_id=workspace.id,
            email='system@internal.app',
            username='System',
            first_name='System',
            last_name='User',
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(system_user)
        db.commit()
        print("✓ System user created successfully")
    except Exception as e:
        print(f"Error creating system user: {e}")
        db.rollback()
        raise
    finally:
        db.close()

# Include routers - this will include the /v1/admin/seed endpoint from admin router
app.include_router(health_router, prefix="/v1/health", tags=["Health"])
app.include_router(admin_router, prefix="/v1/admin", tags=["Admin"])

# Add startup event to ensure system user exists
@app.on_event("startup")
async def startup_event():
    """Create system user on application startup"""
    try:
        seed_system_user()
    except Exception as e:
        print(f"Warning: Could not create system user on startup: {e}")

# Main API routes for data extraction
@app.get("/v1/entities", tags=["Entities"])
def get_entities(
    type: str = Query(..., description="Entity type (e.g., Client, Account, Goal)"),
    q: Optional[str] = Query(None, description="Query filter (e.g., status==active)"),
    limit: int = Query(100, description="Number of results"),
    offset: int = Query(0, description="Pagination offset"),
    options: Optional[str] = Query(None, description="Response options (count for count only)"),
    firm_id: Optional[str] = Query(None, description="Filter by firm identifier"),
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    # Verify API key and secret
    verify_api_key(x_api_key, x_api_secret)
    
    # Get the appropriate service based on entity type
    # Convert type to title case for case-insensitivity
    service = get_entity_service(type.title(), db)
    if not service:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {type}")
    
    # Get entities using the service
    return service.get_entities(q=q, limit=limit, offset=offset, options=options, firm_id=firm_id)

#########################################
# User & Access Management endpoints
#########################################
@app.get("/users", tags=["User & Access Management"])
def get_users(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("User", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@app.get("/users/{user_id}", tags=["User & Access Management"])
def get_user(
    user_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("User", db)
    return service.get_entity_by_id(user_id)

@app.get("/roles", tags=["User & Access Management"])
def get_roles(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Role", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@app.get("/permissions", tags=["User & Access Management"])
def get_permissions(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Permission", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@app.get("/firms", tags=["User & Access Management"])
def get_firms(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Firm", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@app.get("/advisors", tags=["User & Access Management"])
def get_advisors(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Advisor", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

#########################################
# Client & Relationship Management endpoints
#########################################
@app.get("/clients", tags=["Client & Relationship Management"])
def get_clients(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Client", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@app.get("/clients/{client_id}", tags=["Client & Relationship Management"])
def get_client(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Client", db)
    return service.get_entity_by_id(client_id)

@app.get("/clients/{client_id}/spouse", tags=["Client & Relationship Management"])
def get_client_spouse(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Spouse", db)
    return service.get_spouse_by_client_id(client_id)

@app.get("/clients/{client_id}/household", tags=["Client & Relationship Management"])
def get_client_household(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Household", db)
    return service.get_household_by_client_id(client_id)

@app.get("/clients/{client_id}/contacts", tags=["Client & Relationship Management"])
def get_client_contacts(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Contact", db)
    return service.get_contacts_by_client_id(client_id)

@app.get("/clients/{client_id}/relationships", tags=["Client & Relationship Management"])
def get_client_relationships(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Relationship", db)
    return service.get_relationships_by_client_id(client_id)

#########################################
# Financial Planning endpoints
#########################################
@app.get("/clients/{client_id}/plans", tags=["Financial Planning"])
def get_client_plans(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("FinancialPlan", db)
    return service.get_plans_by_client_id(client_id)

@app.get("/clients/{client_id}/plans/{plan_id}", tags=["Financial Planning"])
def get_plan(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("FinancialPlan", db)
    return service.get_plan_by_id(client_id, plan_id)

@app.get("/clients/{client_id}/plans/{plan_id}/scenarios", tags=["Financial Planning"])
def get_plan_scenarios(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Scenario", db)
    return service.get_scenarios_by_plan_id(client_id, plan_id)

@app.get("/clients/{client_id}/plans/{plan_id}/cash-flows", tags=["Financial Planning"])
def get_plan_cashflows(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("CashFlow", db)
    return service.get_cashflows_by_plan_id(client_id, plan_id)

#########################################
# Account Management endpoints
#########################################
@app.get("/clients/{client_id}/accounts", tags=["Account Management"])
def get_client_accounts(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Account", db)
    return service.get_accounts_by_client_id(client_id)

@app.get("/clients/{client_id}/accounts/{account_id}", tags=["Account Management"])
def get_account(
    client_id: str,
    account_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Account", db)
    return service.get_account_by_id(client_id, account_id)

@app.get("/clients/{client_id}/accounts/{account_id}/investments", tags=["Account Management"])
def get_account_investments(
    client_id: str,
    account_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Investment", db)
    return service.get_investments_by_account_id(client_id, account_id)

@app.get("/clients/{client_id}/liabilities", tags=["Account Management"])
def get_client_liabilities(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Liability", db)
    return service.get_liabilities_by_client_id(client_id)

@app.get("/account-types", tags=["Account Management"])
def get_account_types(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("AccountType", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

#########################################
# Asset Management endpoints
#########################################
@app.get("/clients/{client_id}/assets", tags=["Asset Management"])
def get_client_assets(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Asset", db)
    return service.get_assets_by_client_id(client_id)

@app.get("/clients/{client_id}/plans/{plan_id}/assets", tags=["Asset Management"])
def get_plan_assets(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Asset", db)
    return service.get_assets_by_plan_id(client_id, plan_id)

@app.get("/asset-classes", tags=["Asset Management"])
def get_asset_classes(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("AssetClass", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@app.get("/securities", tags=["Asset Management"])
def get_securities(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Security", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

#########################################
# Spending & Budget Management endpoints
#########################################
@app.get("/clients/{client_id}/spending", tags=["Spending & Budget Management"])
def get_client_spending(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Spending", db)
    return service.get_spending_by_client_id(client_id)

@app.get("/clients/{client_id}/budgets", tags=["Spending & Budget Management"])
def get_client_budgets(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Budget", db)
    return service.get_budgets_by_client_id(client_id)

@app.get("/clients/{client_id}/income", tags=["Spending & Budget Management"])
def get_client_income(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Income", db)
    return service.get_income_by_client_id(client_id)

@app.get("/clients/{client_id}/plans/{plan_id}/income", tags=["Spending & Budget Management"])
def get_plan_income(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Income", db)
    return service.get_income_by_plan_id(client_id, plan_id)

@app.get("/clients/{client_id}/expenses", tags=["Spending & Budget Management"])
def get_client_expenses(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Expense", db)
    return service.get_expenses_by_client_id(client_id)

@app.get("/clients/{client_id}/plans/{plan_id}/expenses", tags=["Spending & Budget Management"])
def get_plan_expenses(
    client_id: str,
    plan_id: str,
    is_goal: Optional[bool] = Query(None, description="Filter expenses by goal flag"),
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Expense", db)
    return service.get_expenses_by_plan_id(client_id, plan_id, is_goal)

#########################################
# Estate Planning endpoints
#########################################
@app.get("/clients/{client_id}/estate", tags=["Estate Planning"])
def get_client_estate(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Estate", db)
    return service.get_estate_by_client_id(client_id)

@app.get("/clients/{client_id}/estate/will", tags=["Estate Planning"])
def get_client_will(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Will", db)
    return service.get_will_by_client_id(client_id)

@app.get("/clients/{client_id}/estate/trusts", tags=["Estate Planning"])
def get_client_trusts(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Trust", db)
    return service.get_trusts_by_client_id(client_id)

@app.get("/clients/{client_id}/estate/beneficiaries", tags=["Estate Planning"])
def get_client_beneficiaries(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Beneficiary", db)
    return service.get_beneficiaries_by_client_id(client_id)

#########################################
# Retirement Planning endpoints
#########################################
@app.get("/clients/{client_id}/retirement", tags=["Retirement Planning"])
def get_client_retirement_plan(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("RetirementPlan", db)
    return service.get_retirement_plan_by_client_id(client_id)

@app.get("/clients/{client_id}/retirement/pension", tags=["Retirement Planning"])
def get_client_pension(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Pension", db)
    return service.get_pension_by_client_id(client_id)

@app.get("/clients/{client_id}/retirement/social-security", tags=["Retirement Planning"])
def get_client_social_security(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("SocialSecurity", db)
    return service.get_social_security_by_client_id(client_id)

@app.get("/clients/{client_id}/retirement/rmds", tags=["Retirement Planning"])
def get_client_rmds(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("RMD", db)
    return service.get_rmds_by_client_id(client_id)

#########################################
# Insurance Planning endpoints
#########################################
@app.get("/clients/{client_id}/insurance", tags=["Insurance Planning"])
def get_client_insurance(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Insurance", db)
    return service.get_insurance_by_client_id(client_id)

@app.get("/clients/{client_id}/insurance/policies", tags=["Insurance Planning"])
def get_client_insurance_policies(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Policy", db)
    return service.get_policies_by_client_id(client_id)

@app.get("/clients/{client_id}/insurance/coverage", tags=["Insurance Planning"])
def get_client_insurance_coverage(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Coverage", db)
    return service.get_coverage_by_client_id(client_id)

@app.get("/clients/{client_id}/insurance/premiums", tags=["Insurance Planning"])
def get_client_insurance_premiums(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Premium", db)
    return service.get_premiums_by_client_id(client_id)

#########################################
# Tax Planning endpoints
#########################################
@app.get("/clients/{client_id}/tax", tags=["Tax Planning"])
def get_client_tax_plan(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("TaxPlan", db)
    return service.get_tax_plan_by_client_id(client_id)

@app.get("/clients/{client_id}/tax/brackets", tags=["Tax Planning"])
def get_client_tax_brackets(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("TaxBracket", db)
    return service.get_tax_brackets_by_client_id(client_id)

@app.get("/clients/{client_id}/tax/deductions", tags=["Tax Planning"])
def get_client_tax_deductions(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Deduction", db)
    return service.get_deductions_by_client_id(client_id)

@app.get("/clients/{client_id}/tax/credits", tags=["Tax Planning"])
def get_client_tax_credits(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Credit", db)
    return service.get_credits_by_client_id(client_id)

#########################################
# Goals & Projections endpoints
#########################################
@app.get("/clients/{client_id}/plans/{plan_id}/goals", tags=["Goals & Projections"])
def get_plan_goals(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Goal", db)
    return service.get_goals_by_plan_id(client_id, plan_id)

@app.get("/clients/{client_id}/plans/{plan_id}/monte-carlo", tags=["Goals & Projections"])
def get_plan_monte_carlo(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("MonteCarlo", db)
    return service.get_monte_carlo_by_plan_id(client_id, plan_id)

@app.get("/clients/{client_id}/plans/{plan_id}/net-worth", tags=["Goals & Projections"])
def get_client_net_worth(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("NetWorth", db)
    return service.get_net_worth_by_plan_id(client_id, plan_id)

@app.get("/clients/{client_id}/plans/{plan_id}/projection", tags=["Goals & Projections"])
def get_plan_projection(
    client_id: str,
    plan_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Projection", db)
    return service.get_projection_by_plan_id(client_id, plan_id)

#########################################
# Documents & Communication endpoints
#########################################
@app.get("/clients/{client_id}/vault", tags=["Documents & Communication"])
def get_client_vault_documents(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("VaultDocument", db)
    return service.get_documents_by_client_id(client_id)

@app.get("/clients/{client_id}/vault/{document_id}", tags=["Documents & Communication"])
def get_client_vault_document(
    client_id: str,
    document_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("VaultDocument", db)
    return service.get_document_by_id(client_id, document_id)

@app.get("/file-types", tags=["Documents & Communication"])
def get_file_types(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("FileType", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@app.get("/clients/{client_id}/notes", tags=["Documents & Communication"])
def get_client_notes(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Note", db)
    return service.get_notes_by_client_id(client_id)

@app.get("/clients/{client_id}/tasks", tags=["Documents & Communication"])
def get_client_tasks(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Task", db)
    return service.get_tasks_by_client_id(client_id)

@app.get("/alerts", tags=["Documents & Communication"])
def get_alerts(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Alert", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

#########################################
# Administration & Portal Access endpoints
#########################################
@app.get("/logons", tags=["Administration & Portal Access"])
def get_logons(
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Logon", db)
    return service.get_entities(q=None, limit=100, offset=0, options=None, firm_id=None)

@app.get("/logons/{logon_id}", tags=["Administration & Portal Access"])
def get_logon(
    logon_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Logon", db)
    return service.get_entity_by_id(logon_id)

@app.get("/clients/{client_id}/logons", tags=["Administration & Portal Access"])
def get_client_logon(
    client_id: str,
    x_api_key: str = Header(...),
    x_api_secret: str = Header(...),
    db: Session = Depends(get_db)
):
    verify_api_key(x_api_key, x_api_secret)
    service = get_entity_service("Logon", db)
    return service.get_logon_by_client_id(client_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=6820, reload=True)