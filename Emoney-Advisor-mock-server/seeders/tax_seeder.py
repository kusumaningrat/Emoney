# seeders/tax.py

from sqlalchemy.orm import Session
import json
from datetime import datetime, timezone, timedelta, date
from faker import Faker
import random
import uuid
from decimal import Decimal

from database import SessionLocal
from models.tax import TaxPlan, TaxBracket, Deduction, Credit
from models.clients import Client, Contact
from models.users import User, Workspace
from seeders.client_seeder import seed_clients

# Initialize Faker
fake = Faker()

# Main function to seed all tax planning data
def seed_tax_data():
    """Main function to seed all tax planning data in correct order."""
    db = SessionLocal()
    try:
        # Check if data already exists to avoid duplicates
        existing_plans = db.query(TaxPlan).count()
        if existing_plans > 0:
            print("Tax planning data already seeded, skipping...")
            return

        # Ensure clients exist
        clients = db.query(Client).all()
        if not clients:
            print("No clients found, seeding clients first...")
            seed_clients()
            clients = db.query(Client).all()
            
        # 1. Create tax brackets first
        tax_brackets = seed_tax_brackets(db)
        db.commit()
        
        # 2. Create tax plans
        plans = seed_tax_plans(db, clients, tax_brackets)
        db.commit()
        
        # 3. Create deductions
        seed_deductions(db, plans)
        db.commit()
        
        # 4. Create credits
        seed_credits(db, plans)
        db.commit()
        
        print("Tax planning seeding complete!")
        
    except Exception as e:
        print(f"Error seeding tax planning data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def seed_tax_brackets(db: Session) -> list:
    """Create tax bracket data."""
    print("Creating tax bracket data...")
    
    brackets_created = 0
    brackets = []
    bracket_id = 1
    
    # Check if tax brackets already exist
    existing_brackets = db.query(TaxBracket).count()
    if existing_brackets > 0:
        print("Tax brackets already exist, fetching...")
        return db.query(TaxBracket).all()
    
    # Get default workspace
    workspaces = db.query(Workspace).all()
    default_workspace_id = workspaces[0].id if workspaces else "workspace_001"
    
    # Define tax bracket templates
    bracket_templates = [
        # Federal Income Tax Brackets - Single 2023
        {
            "bracket_type": "federal",
            "tax_year": 2023,
            "filing_status": "Single",
            "brackets": [
                {"income_min": 0, "income_max": 11000, "rate": 0.10, "base_tax": 0},
                {"income_min": 11001, "income_max": 44725, "rate": 0.12, "base_tax": 1100},
                {"income_min": 44726, "income_max": 95375, "rate": 0.22, "base_tax": 5147},
                {"income_min": 95376, "income_max": 182100, "rate": 0.24, "base_tax": 16290},
                {"income_min": 182101, "income_max": 231250, "rate": 0.32, "base_tax": 37104},
                {"income_min": 231251, "income_max": 578125, "rate": 0.35, "base_tax": 52832},
                {"income_min": 578126, "income_max": None, "rate": 0.37, "base_tax": 174238}
            ]
        },
        # Federal Income Tax Brackets - Married Filing Jointly 2023
        {
            "bracket_type": "federal",
            "tax_year": 2023,
            "filing_status": "Married Filing Jointly",
            "brackets": [
                {"income_min": 0, "income_max": 22000, "rate": 0.10, "base_tax": 0},
                {"income_min": 22001, "income_max": 89450, "rate": 0.12, "base_tax": 2200},
                {"income_min": 89451, "income_max": 190750, "rate": 0.22, "base_tax": 10294},
                {"income_min": 190751, "income_max": 364200, "rate": 0.24, "base_tax": 32580},
                {"income_min": 364201, "income_max": 462500, "rate": 0.32, "base_tax": 74208},
                {"income_min": 462501, "income_max": 693750, "rate": 0.35, "base_tax": 105664},
                {"income_min": 693751, "income_max": None, "rate": 0.37, "base_tax": 186601}
            ]
        },
        # State Income Tax Brackets (sample for California) - Single 2023
        {
            "bracket_type": "state",
            "tax_year": 2023,
            "filing_status": "Single",
            "state": "California",
            "brackets": [
                {"income_min": 0, "income_max": 10099, "rate": 0.01, "base_tax": 0},
                {"income_min": 10100, "income_max": 23942, "rate": 0.02, "base_tax": 101},
                {"income_min": 23943, "income_max": 37788, "rate": 0.04, "base_tax": 379},
                {"income_min": 37789, "income_max": 52455, "rate": 0.06, "base_tax": 934},
                {"income_min": 52456, "income_max": 66295, "rate": 0.08, "base_tax": 1814},
                {"income_min": 66296, "income_max": 338639, "rate": 0.093, "base_tax": 2982},
                {"income_min": 338640, "income_max": 406364, "rate": 0.103, "base_tax": 28257},
                {"income_min": 406365, "income_max": 677275, "rate": 0.113, "base_tax": 35316},
                {"income_min": 677276, "income_max": None, "rate": 0.123, "base_tax": 65979}
            ]
        }
    ]
    
    # Create brackets
    for template in bracket_templates:
        for bracket_data in template["brackets"]:
            # Get a client ID for association
            clients = db.query(Client).all()
            client_id = clients[0].id if clients else None
            
            # Create timestamps
            created_at = datetime.now(timezone.utc)
            updated_at = created_at
            
            # Create tax bracket entry
            tax_bracket_data = {
                "id": f"tax_bracket_{str(bracket_id).zfill(3)}",
                "workspace_id": default_workspace_id,
                "client_id": client_id,
                "created_by": "system",
                "updated_by": "system",
                "created_at": created_at,
                "updated_at": updated_at,
                "bracket_type": template["bracket_type"],
                "tax_year": template["tax_year"],
                "filing_status": template["filing_status"],
                "income_min": Decimal(str(bracket_data["income_min"])),
                "income_max": Decimal(str(bracket_data["income_max"])) if bracket_data["income_max"] is not None else None,
                "rate": Decimal(str(bracket_data["rate"])),
                "base_tax": Decimal(str(bracket_data["base_tax"])),
                "state": template.get("state")
            }
            
            tax_bracket = TaxBracket(**tax_bracket_data)
            db.add(tax_bracket)
            brackets.append(tax_bracket)
            
            bracket_id += 1
            brackets_created += 1
    
    db.commit()
    print(f"Seeded {brackets_created} tax brackets successfully!")
    return brackets

def seed_tax_plans(db: Session, clients: list, tax_brackets: list) -> list:
    """Create tax plans for clients."""
    print("Creating tax plans...")
    
    plans_created = 0
    plans = []
    plan_id = 1
    
    for client in clients:
        # Skip some clients
        if random.random() > 0.8:
            continue
            
        # Get primary contact for this client
        primary_contact = None
        if hasattr(client, 'contacts') and client.contacts:
            # Try to find preferred contact first
            primary_contact = next((c for c in client.contacts if hasattr(c, 'is_preferred') and c.is_preferred), None)
            # Fall back to first contact if no preferred contact
            if not primary_contact and len(client.contacts) > 0:
                primary_contact = client.contacts[0]
        
        # Skip if no valid contact
        if not primary_contact:
            continue
        
        # Determine workspace_id - simpler approach without assuming specific relationships
        workspace_id = None
        
        # First try to use client's workspace_id if it exists
        if hasattr(client, 'workspace_id') and client.workspace_id:
            workspace_id = client.workspace_id
        # Otherwise get a default workspace
        else:
            workspaces = db.query(Workspace).all()
            workspace_id = workspaces[0].id if workspaces else "workspace_001"
            
        # Get users for creator/updater
        created_by = client.created_by if hasattr(client, 'created_by') and client.created_by else None
        if not created_by:
            users = db.query(User).all()
            if users:
                created_by = users[0].id
            else:
                created_by = "system"
                
        updated_by = created_by  # Default to same user
        
        # Determine filing status
        has_spouse = hasattr(client, 'spouse') and client.spouse
        if has_spouse:
            filing_status = "Married Filing Jointly" if random.random() > 0.1 else "Married Filing Separately"
        else:
            filing_status = "Single" if random.random() > 0.2 else "Head of Household"
        
        # Create timestamps
        created_at = datetime.now(timezone.utc)
        if hasattr(client, 'created_at') and client.created_at:
            if isinstance(client.created_at, datetime):
                created_at = client.created_at
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
            
        updated_at = datetime.now(timezone.utc)
        
        # Create plan data
        tax_plan_data = {
            "id": f"tax_plan_{str(plan_id).zfill(3)}",
            "workspace_id": workspace_id,
            "client_id": client.id,
            "created_by": created_by,
            "updated_by": updated_by,
            "created_at": created_at,
            "updated_at": updated_at,
            "name": f"{client.first_name} {client.last_name} {datetime.now().year} Tax Plan",
            "description": f"Tax plan for {datetime.now().year} tax year",
            "tax_year": datetime.now().year,
            "filing_status": filing_status,
            "projected_income": Decimal(str(round(random.uniform(50000, 500000), 2))),
            "projected_deductions": Decimal(str(round(random.uniform(10000, 50000), 2))),
            "projected_credits": Decimal(str(round(random.uniform(0, 5000), 2))),
            "estimated_tax_liability": Decimal(str(round(random.uniform(5000, 100000), 2))),
            "effective_tax_rate": Decimal(str(round(random.uniform(0.15, 0.35), 2))),
            "marginal_tax_rate": Decimal(str(random.choice([0.10, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]))),
            "strategy_notes": fake.paragraph() if random.random() > 0.5 else None,
            "optimization_opportunities": json.dumps([
                "Maximize retirement contributions",
                "Harvest tax losses",
                "Charitable giving strategy",
                "Roth conversion analysis"
            ]) if random.random() > 0.5 else None,
            "risk_factors": json.dumps([
                "Potential audit risk due to high deductions",
                "State tax liability changes"
            ]) if random.random() > 0.7 else None,
            "assumptions": json.dumps({
                "inflation_rate": 0.03,
                "tax_law_changes": "None expected"
            }) if random.random() > 0.5 else None,
            "status": random.choice(["draft", "active", "approved", "implemented"])
        }
        
        plan = TaxPlan(**tax_plan_data)
        db.add(plan)
        plans.append(plan)
        
        plan_id += 1
        plans_created += 1
    
    db.commit()
    print(f"Seeded {plans_created} tax plans successfully!")
    return plans

def seed_deductions(db: Session, plans: list):
    """Create tax deductions for tax plans."""
    print("Creating tax deductions...")
    
    deductions_created = 0
    deduction_id = 1
    
    # Common deduction types
    deduction_templates = [
        {"name": "401(k) Contribution", "description": "Pre-tax retirement contributions", "category": "Retirement", "amount": (5000, 22500)},
        {"name": "IRA Contribution", "description": "Individual retirement account contributions", "category": "Retirement", "amount": (1000, 6500)},
        {"name": "HSA Contribution", "description": "Health savings account contributions", "category": "Health", "amount": (1000, 3850)},
        {"name": "Mortgage Interest", "description": "Mortgage interest paid on primary residence", "category": "Housing", "amount": (5000, 25000)},
        {"name": "Property Taxes", "description": "Property taxes paid on real estate", "category": "Taxes", "amount": (2000, 8000)},
        {"name": "Charitable Contributions", "description": "Donations to qualified charitable organizations", "category": "Charitable", "amount": (1000, 15000)},
        {"name": "Medical Expenses", "description": "Qualifying medical expenses", "category": "Health", "amount": (5000, 20000)},
        {"name": "Student Loan Interest", "description": "Interest paid on qualified student loans", "category": "Education", "amount": (500, 2500)}
    ]
    
    for plan in plans:
        # Skip some plans
        if random.random() > 0.9:
            continue
            
        # Determine number of deductions (2-5)
        num_deductions = random.randint(2, 5)
        
        # Randomly select deduction types
        selected_deductions = random.sample(deduction_templates, min(num_deductions, len(deduction_templates)))
        
        for deduction_template in selected_deductions:
            # Create timestamps
            created_at = plan.created_at
            updated_at = plan.updated_at
            
            # Determine amount
            min_amount, max_amount = deduction_template["amount"]
            amount = Decimal(str(round(random.uniform(min_amount, max_amount), 2)))
            
            # Create deduction
            deduction_data = {
                "id": f"deduction_{str(deduction_id).zfill(3)}",
                "workspace_id": plan.workspace_id,
                "tax_plan_id": plan.id,
                "client_id": plan.client_id,
                "created_by": plan.created_by,
                "updated_by": plan.updated_by,
                "created_at": created_at,
                "updated_at": updated_at,
                "name": deduction_template["name"],
                "description": deduction_template["description"],
                "deduction_type": "above_line" if deduction_template["category"] in ["Retirement", "Health"] else "itemized",
                "category": deduction_template["category"],
                "amount": amount,
                "is_recurring": True if deduction_template["category"] in ["Retirement", "Housing"] else False,
                "frequency": "annual",
                "documentation_required": True,
                "documentation_status": random.choice(["complete", "incomplete", "pending"]),
                "tax_year": plan.tax_year,
                "notes": fake.sentence() if random.random() > 0.7 else None
            }
            
            deduction = Deduction(**deduction_data)
            db.add(deduction)
            
            deduction_id += 1
            deductions_created += 1
    
    db.commit()
    print(f"Seeded {deductions_created} deductions successfully!")

def seed_credits(db: Session, plans: list):
    """Create tax credits for tax plans."""
    print("Creating tax credits...")
    
    credits_created = 0
    credit_id = 1
    
    # Common credit types
    credit_templates = [
        {"name": "Child Tax Credit", "description": "Credit for qualifying children", "category": "Family", "amount": (1000, 2000)},
        {"name": "Child and Dependent Care Credit", "description": "Credit for child care expenses", "category": "Family", "amount": (600, 2100)},
        {"name": "Earned Income Credit", "description": "Credit for low to moderate income workers", "category": "Income", "amount": (500, 6000)},
        {"name": "American Opportunity Credit", "description": "Credit for higher education expenses", "category": "Education", "amount": (1000, 2500)},
        {"name": "Lifetime Learning Credit", "description": "Credit for educational expenses", "category": "Education", "amount": (500, 2000)},
        {"name": "Residential Energy Credit", "description": "Credit for energy-efficient home improvements", "category": "Energy", "amount": (500, 3200)}
    ]
    
    for plan in plans:
        # Skip some plans
        if random.random() > 0.9:
            continue
            
        # Determine number of credits (0-3)
        num_credits = random.randint(0, 3)
        
        # Randomly select credit types
        selected_credits = random.sample(credit_templates, min(num_credits, len(credit_templates)))
        
        for credit_template in selected_credits:
            # Create timestamps
            created_at = plan.created_at
            updated_at = plan.updated_at
            
            # Determine amount
            min_amount, max_amount = credit_template["amount"]
            amount = Decimal(str(round(random.uniform(min_amount, max_amount), 2)))
            
            # Determine refundability
            is_refundable = credit_template["name"] in ["Child Tax Credit", "Earned Income Credit"]
            
            # Create credit
            credit_data = {
                "id": f"credit_{str(credit_id).zfill(3)}",
                "workspace_id": plan.workspace_id,
                "tax_plan_id": plan.id,
                "client_id": plan.client_id,
                "created_by": plan.created_by,
                "updated_by": plan.updated_by,
                "created_at": created_at,
                "updated_at": updated_at,
                "name": credit_template["name"],
                "description": credit_template["description"],
                "credit_type": "refundable" if is_refundable else "nonrefundable",
                "category": credit_template["category"],
                "amount": amount,
                "is_refundable": is_refundable,
                "documentation_required": True,
                "documentation_status": random.choice(["complete", "incomplete", "pending"]),
                "tax_year": plan.tax_year,
                "notes": fake.sentence() if random.random() > 0.7 else None
            }
            
            credit = Credit(**credit_data)
            db.add(credit)
            
            credit_id += 1
            credits_created += 1
    
    db.commit()
    print(f"Seeded {credits_created} credits successfully!")

# Main function to call when executing the script directly
if __name__ == "__main__":
    seed_tax_data()