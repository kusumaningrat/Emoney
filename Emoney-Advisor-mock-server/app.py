from fastapi import FastAPI, Depends, HTTPException, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from sqlalchemy.orm import Session
from datetime import datetime, timezone

from database import get_db, Base, engine, SessionLocal
from auth.dependencies import verify_api_key
from services.entity_factory import get_entity_service

# Import all route modules
from routes.health import router as health_router
from routes.admin import router as admin_router
from routes.users import router as users_router
from routes.clients import router as clients_router
from routes.financial import router as financial_router
from routes.accounts import router as accounts_router
from routes.assets import router as assets_router
from routes.spending import router as spending_router
from routes.estate import router as estate_router
from routes.retirement import router as retirement_router
from routes.insurance import router as insurance_router
from routes.tax import router as tax_router
from routes.documents import router as documents_router

# Import all models for table creation
from models.users import User, Role, Permission, Firm, Logon, Workspace, Advisor
from models.clients import Client, Spouse, Household, HouseholdMember, Contact, Relationship
from models.financial import (
    FinancialPlan, Goal, MonteCarlo, Projection, CashFlow, Scenario, 
    PlanIncome
)
from models.accounts import Account, AccountTypeModel, Investment, Liability
from models.assets import Asset, AssetClass, Allocation, Security, Holding
from models.spending import Spending, Budget, Income, Expense, BudgetCategory
from models.estate import Estate, Will, Trust, Beneficiary
from models.retirement import RetirementPlan, Pension, SocialSecurity, RMD
from models.insurance import Insurance, InsurancePolicy, Coverage, Premium
from models.tax import TaxPlan, TaxBracket, Deduction, Credit, FinancialTaxDeduction, TaxCredit
from models.documents import FileType, VaultDocument, Attachment, Note, Task, Alert

# Create database tables
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

# Add startup event to ensure system user exists
@app.on_event("startup")
async def startup_event():
    """Create system user on application startup"""
    try:
        seed_system_user()
    except Exception as e:
        print(f"Warning: Could not create system user on startup: {e}")

# Include all routers with /v1 prefix
app.include_router(health_router, prefix="/v1/health", tags=["Health"])
app.include_router(admin_router, prefix="/v1/admin", tags=["Admin"])
app.include_router(users_router, prefix="/v1")
app.include_router(clients_router, prefix="/v1")
app.include_router(financial_router, prefix="/v1")
app.include_router(accounts_router, prefix="/v1")
app.include_router(assets_router, prefix="/v1")
app.include_router(spending_router, prefix="/v1")
app.include_router(estate_router, prefix="/v1")
app.include_router(retirement_router, prefix="/v1")
app.include_router(insurance_router, prefix="/v1")
app.include_router(tax_router, prefix="/v1")
app.include_router(documents_router, prefix="/v1")

# Main API route for generic entity queries
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
    """
    Generic entity endpoint for querying any entity type
    
    Examples:
    - GET /v1/entities?type=Client&q=status==active&limit=50
    - GET /v1/entities?type=Account&firm_id=firm-123
    """
    # Verify API key and secret
    verify_api_key(x_api_key, x_api_secret)
    
    # Get the appropriate service based on entity type
    # Convert type to title case for case-insensitivity
    service = get_entity_service(type.title(), db)
    if not service:
        raise HTTPException(status_code=400, detail=f"Unknown entity type: {type}")
    
    # Get entities using the service
    return service.get_entities(q=q, limit=limit, offset=offset, options=options, firm_id=firm_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=6820, reload=True)