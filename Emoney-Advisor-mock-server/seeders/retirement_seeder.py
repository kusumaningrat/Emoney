# seeders/retirement.py

from sqlalchemy.orm import Session
import json
from datetime import datetime, timezone, timedelta, date
from faker import Faker
import random
import uuid
from decimal import Decimal

from database import SessionLocal
from models.retirement import RetirementPlan, Pension, SocialSecurity, RMD
from models.clients import Client, Contact
from models.users import User, Workspace
from seeders.client_seeder import seed_clients

# Initialize Faker
fake = Faker()

# Main function to seed all retirement planning data
def seed_retirement_data():
    """Main function to seed all retirement planning data in correct order."""
    db = SessionLocal()
    try:
        # Check if data already exists to avoid duplicates
        existing_plans = db.query(RetirementPlan).count()
        if existing_plans > 0:
            print("Retirement planning data already seeded, skipping...")
            return

        # Ensure clients exist
        clients = db.query(Client).all()
        if not clients:
            print("No clients found, seeding clients first...")
            seed_clients()
            clients = db.query(Client).all()
            
        # 1. Create retirement plans first
        plans = seed_retirement_plans(db, clients)
        db.commit()
        
        # 2. Create pension records
        seed_pensions(db, plans)
        db.commit()
        
        # 3. Create social security benefits
        seed_social_security(db, plans)
        db.commit()
        
        # 4. Create RMD calculations
        seed_rmds(db, plans)
        db.commit()
        
        print("Retirement planning seeding complete!")
        
    except Exception as e:
        print(f"Error seeding retirement planning data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def seed_retirement_plans(db: Session, clients: list) -> list:
    """Seed retirement plan data for clients."""
    print("Seeding retirement plan data...")
    
    plans_created = 0
    plans = []
    plan_id = 1
    
    # Get all workspaces first to avoid repeated queries
    workspaces = db.query(Workspace).all()
    # Get default workspace ID if any exist
    default_workspace_id = workspaces[0].id if workspaces else None
    
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
        # Otherwise use default workspace from our list
        elif default_workspace_id:
            workspace_id = default_workspace_id
        # Last resort: use firm_id directly
        elif hasattr(client, 'firm_id') and client.firm_id:
            workspace_id = client.firm_id
        else:
            # Skip if no workspace reference is available
            continue
            
        # Get users for creator/updater
        created_by = client.created_by if hasattr(client, 'created_by') and client.created_by else None
        if not created_by:
            users = db.query(User).filter(User.firm_id == client.firm_id).all() if hasattr(client, 'firm_id') else []
            if users:
                created_by = users[0].id
            else:
                continue
                
        updated_by = created_by  # Default to same user
        
        # Current age calculation
        current_age = None
        if hasattr(client, 'date_of_birth') and client.date_of_birth:
            today = date.today()
            born = client.date_of_birth
            current_age = today.year - born.year - ((today.month, today.day) < (born.month, born.day))
        else:
            # Default to middle-aged if no birth date
            current_age = random.randint(35, 65)
        
        # Determine spouse age if applicable
        spouse_age = None
        if hasattr(client, 'spouse') and client.spouse:
            if hasattr(client.spouse, 'date_of_birth') and client.spouse.date_of_birth:
                today = date.today()
                spouse_born = client.spouse.date_of_birth
                spouse_age = today.year - spouse_born.year - ((today.month, today.day) < (spouse_born.month, spouse_born.day))
            else:
                # Estimate spouse age
                spouse_age = current_age + random.randint(-5, 5)
        
        # Retirement ages
        retirement_age = random.randint(62, 70)
        spouse_retirement_age = random.randint(62, 70) if spouse_age else None
        
        # Financial metrics
        retirement_assets = Decimal(str(round(random.uniform(100000, 3000000), 2)))
        annual_contributions = Decimal(str(round(random.uniform(5000, 50000), 2)))
        target_income = Decimal(str(round(random.uniform(50000, 200000), 2)))
        
        # Retirement income sources
        social_security = random.random() > 0.1  # Most people expect Social Security
        pension = random.random() > 0.7  # Fewer people have pensions
        
        # Create timestamps with timezone info
        created_at = datetime.now(timezone.utc)
        if hasattr(client, 'created_at') and client.created_at:
            if isinstance(client.created_at, datetime):
                created_at = client.created_at
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
            
        updated_at = datetime.now(timezone.utc)
        
        # Create retirement plan data
        plan_data = {
            "id": f"retirement_plan_{str(plan_id).zfill(3)}",
            "workspace_id": workspace_id,
            "client_id": client.id,
            "created_by": created_by,
            "updated_by": updated_by,
            "created_at": created_at,
            "updated_at": updated_at,
            "status": "Active",
            "current_age": current_age,
            "spouse_age": spouse_age,
            "retirement_age": retirement_age,
            "spouse_retirement_age": spouse_retirement_age,
            "life_expectancy": random.randint(85, 95),
            "spouse_life_expectancy": random.randint(85, 95) if spouse_age else None,
            "retirement_assets": retirement_assets,
            "annual_contributions": annual_contributions,
            "contribution_increase_rate": Decimal(str(round(random.uniform(0.01, 0.03), 4))),
            "pre_retirement_return": Decimal(str(round(random.uniform(0.05, 0.08), 4))),
            "post_retirement_return": Decimal(str(round(random.uniform(0.03, 0.05), 4))),
            "inflation_rate": Decimal(str(round(random.uniform(0.02, 0.04), 4))),
            "target_income": target_income,
            "income_replacement_ratio": Decimal(str(round(random.uniform(0.6, 0.85), 4))),
            "success_probability": random.randint(60, 95),
            "income_sources": json.dumps({
                "socialSecurity": {
                    "included": social_security,
                    "clientAge": random.randint(62, 70),
                    "spouseAge": random.randint(62, 70) if spouse_age else None
                },
                "pension": {
                    "included": pension
                },
                "retirementAccounts": {
                    "included": True
                },
                "otherIncome": {
                    "included": random.random() > 0.7,
                    "amount": str(round(random.uniform(10000, 50000), 2)) if random.random() > 0.7 else "0",
                    "description": "Rental income" if random.random() > 0.5 else "Part-time work"
                }
            }),
            "retirement_accounts": json.dumps([f"account_{random.randint(1, 100)}" for _ in range(random.randint(1, 5))]),
            "retirement_shortfall": Decimal(str(round(max(0, float(target_income) * 25 - float(retirement_assets)), 2))) if random.random() > 0.3 else None,
            "years_to_retirement": retirement_age - current_age,
            "required_savings_rate": Decimal(str(round(random.uniform(0.05, 0.2), 4))),
            "risk_capacity": random.choice(["Low", "Medium", "High"]),
            "strategies": json.dumps([
                "Maximize retirement contributions",
                "Consider delaying Social Security" if social_security else "Apply for Social Security at optimal age",
                "Review asset allocation",
                "Consider Roth conversion strategy" if random.random() > 0.5 else None,
                "Plan for healthcare costs" if random.random() > 0.5 else None
            ]),
            "notes": fake.paragraph() if random.random() > 0.7 else None
        }
        
        plan = RetirementPlan(**plan_data)
        db.add(plan)
        plans.append(plan)
        
        plan_id += 1
        plans_created += 1
    
    db.commit()
    print(f"Seeded {plans_created} retirement plans successfully!")
    return plans

def seed_pensions(db: Session, plans: list):
    """Create pension records for retirement plans."""
    print("Creating pension records...")
    
    pensions_created = 0
    pension_id = 1
    
    for plan in plans:
        # Check if plan includes pension
        income_sources = json.loads(plan.income_sources)
        if not income_sources.get("pension", {}).get("included", False) or random.random() > 0.8:
            continue
            
        # Get client
        client = db.query(Client).filter(Client.id == plan.client_id).first()
        if not client:
            continue
            
        # Create timestamps with timezone info
        created_at = plan.created_at
        updated_at = plan.updated_at
        
        # Determine if the pension is for the client or spouse
        for pension_recipient in ["Client", "Spouse"]:
            # Skip spouse if no spouse
            if pension_recipient == "Spouse" and not plan.spouse_age:
                continue
                
            # Skip randomly - not everyone has both
            if pension_recipient == "Spouse" and random.random() > 0.4:
                continue
            
            # Pension details
            pension_name = f"{fake.company()} Pension Plan"
            
            # Calculate monthly benefit
            if pension_recipient == "Client":
                monthly_benefit = Decimal(str(round(random.uniform(1000, 5000), 2)))
                retirement_age = plan.retirement_age
            else:
                monthly_benefit = Decimal(str(round(random.uniform(800, 4000), 2)))
                retirement_age = plan.spouse_retirement_age
            
            annual_benefit = monthly_benefit * Decimal('12')
            
            # Create pension data
            pension_data = {
                "id": f"pension_{str(pension_id).zfill(3)}",
                "workspace_id": plan.workspace_id,
                "client_id": plan.client_id,
                "retirement_plan_id": plan.id,
                "created_by": plan.created_by,
                "updated_by": plan.updated_by,
                "created_at": created_at,
                "updated_at": updated_at,
                "name": pension_name,
                "status": "Active",
                "type": "Defined Benefit",
                "recipient": pension_recipient,
                "provider": pension_name.split(" ")[0],
                "monthly_benefit": monthly_benefit,
                "annual_benefit": annual_benefit,
                "start_age": retirement_age,
                "benefit_period": random.choice(["Life", "Life with Period Certain", "Joint and Survivor"]),
                "cola_adjustment": random.random() > 0.7,
                "cola_rate": Decimal(str(round(random.uniform(0.01, 0.03), 4))) if random.random() > 0.7 else None,
                "payment_frequency": "Monthly",
                "survivor_benefit_percentage": random.choice([50, 75, 100]) if random.random() > 0.5 else None,
                "lump_sum_option": random.random() > 0.8,
                "lump_sum_amount": annual_benefit * Decimal(str(round(random.uniform(15, 20), 2))) if random.random() > 0.8 else None,
                "early_retirement_option": random.random() > 0.7,
                "early_retirement_age": random.randint(55, 60) if random.random() > 0.7 else None,
                "early_retirement_reduction": Decimal(str(round(random.uniform(0.03, 0.06), 4))) if random.random() > 0.7 else None,
                "vesting_percentage": 100,  # Assume fully vested
                "years_of_service": random.randint(15, 35),
                "pension_max": annual_benefit * Decimal(str(round(random.uniform(1.1, 1.5), 2))) if random.random() > 0.5 else None,
                "notes": fake.paragraph() if random.random() > 0.7 else None
            }
            
            pension = Pension(**pension_data)
            db.add(pension)
            
            pension_id += 1
            pensions_created += 1
    
    db.commit()
    print(f"Seeded {pensions_created} pension records successfully!")

def seed_social_security(db: Session, plans: list):
    """Create social security benefit records for retirement plans."""
    print("Creating social security records...")
    
    ss_records_created = 0
    ss_id = 1
    
    for plan in plans:
        # Check if plan includes Social Security
        income_sources = json.loads(plan.income_sources)
        if not income_sources.get("socialSecurity", {}).get("included", False):
            continue
            
        # Get client
        client = db.query(Client).filter(Client.id == plan.client_id).first()
        if not client:
            continue
            
        # Create timestamps with timezone info
        created_at = plan.created_at
        updated_at = plan.updated_at
        
        # Determine if SS records are for client, spouse, or both
        recipients = ["Client"]
        if plan.spouse_age:
            recipients.append("Spouse")
        
        # Create Social Security records
        for recipient in recipients:
            # Benefit details
            if recipient == "Client":
                current_age = plan.current_age
                claim_age = income_sources.get("socialSecurity", {}).get("clientAge", random.randint(62, 70))
                # Generate realistic benefit based on income
                # Convert to Decimal for all calculations
                target_income_decimal = plan.target_income if isinstance(plan.target_income, Decimal) else Decimal(str(plan.target_income))
                pia = min(Decimal('3000'), (target_income_decimal * Decimal('0.3') / Decimal('12')).quantize(Decimal('0.01')))
            else:  # Spouse
                current_age = plan.spouse_age
                claim_age = income_sources.get("socialSecurity", {}).get("spouseAge", random.randint(62, 70))
                # Spousal benefit might be lower
                target_income_decimal = plan.target_income if isinstance(plan.target_income, Decimal) else Decimal(str(plan.target_income))
                pia = min(Decimal('3000'), (target_income_decimal * Decimal('0.25') / Decimal('12')).quantize(Decimal('0.01')))
            
            # Adjust benefit based on claim age using Decimal math
            if claim_age < 67:  # Before Full Retirement Age (FRA)
                reduction_factor = Decimal(str(67 - claim_age)) * Decimal('0.0625')
                monthly_benefit = (pia * (Decimal('1') - reduction_factor)).quantize(Decimal('0.01'))
            elif claim_age > 67:  # After FRA
                increase_factor = Decimal(str(claim_age - 67)) * Decimal('0.08')
                monthly_benefit = (pia * (Decimal('1') + increase_factor)).quantize(Decimal('0.01'))
            else:
                monthly_benefit = pia
                
            # Annual benefit
            annual_benefit = monthly_benefit * Decimal('12')
            
            # Create Social Security data
            ss_data = {
                "id": f"social_security_{str(ss_id).zfill(3)}",
                "workspace_id": plan.workspace_id,
                "client_id": plan.client_id,
                "retirement_plan_id": plan.id,
                "created_by": plan.created_by,
                "updated_by": plan.updated_by,
                "created_at": created_at,
                "updated_at": updated_at,
                "recipient": recipient,
                "status": "Estimated" if current_age < 62 else "Eligible" if current_age >= 62 and current_age < claim_age else "Claiming",
                "current_age": current_age,
                "pia": pia,
                "early_retirement_age": 62,
                "full_retirement_age": 67,
                "maximum_retirement_age": 70,
                "claim_age": claim_age,
                "monthly_benefit_at_er": (pia * Decimal('0.7')).quantize(Decimal('0.01')),  # 30% reduction at 62
                "monthly_benefit_at_fra": pia,
                "monthly_benefit_at_max": (pia * Decimal('1.24')).quantize(Decimal('0.01')),  # 24% increase at 70
                "monthly_benefit": monthly_benefit,
                "annual_benefit": annual_benefit,
                "lifetime_benefit": (annual_benefit * Decimal(str(85 - claim_age))).quantize(Decimal('0.01')),  # Simple estimation to age 85
                "cola_assumption": Decimal(str(round(random.uniform(0.015, 0.03), 4))),
                "earnings_test_applicable": current_age >= 62 and current_age < 67 and random.random() > 0.7,
                "earnings_test_income": Decimal(str(round(random.uniform(10000, 30000), 2))) if current_age >= 62 and current_age < 67 and random.random() > 0.7 else None,
                "taxable_percentage": random.choice([0, 50, 85]),
                "spousal_benefit_eligible": recipient == "Spouse" and random.random() > 0.5,
                "spousal_benefit_amount": (monthly_benefit * Decimal(str(round(random.uniform(0.3, 0.5), 2)))).quantize(Decimal('0.01')) if recipient == "Spouse" and random.random() > 0.5 else None,
                "survivor_benefit_eligible": random.random() > 0.7,
                "survivor_benefit_amount": (monthly_benefit * Decimal(str(round(random.uniform(0.8, 1.0), 2)))).quantize(Decimal('0.01')) if random.random() > 0.7 else None,
                "optimization_strategy": random.choice([
                    "Claim at FRA",
                    "Delay until age 70",
                    "Claim early at 62",
                    "Spousal benefit strategy",
                    "File and suspend strategy"
                ]),
                "notes": fake.paragraph() if random.random() > 0.7 else None
            }
            
            social_security = SocialSecurity(**ss_data)
            db.add(social_security)
            
            ss_id += 1
            ss_records_created += 1
    
    db.commit()
    print(f"Seeded {ss_records_created} Social Security records successfully!")

def seed_rmds(db: Session, plans: list):
    """Create RMD (Required Minimum Distribution) calculations for retirement plans."""
    print("Creating RMD calculations...")
    
    rmds_created = 0
    rmd_id = 1
    
    for plan in plans:
        # Only create RMDs for clients who are near or in RMD age (72+)
        if plan.current_age is None or plan.current_age < 65:
            continue
            
        # Get client
        client = db.query(Client).filter(Client.id == plan.client_id).first()
        if not client:
            continue
            
        # Create timestamps with timezone info
        created_at = plan.created_at
        updated_at = plan.updated_at
        
        # RMD details - convert to Decimal
        if isinstance(plan.retirement_assets, Decimal):
            retirement_assets_decimal = plan.retirement_assets
        else:
            retirement_assets_decimal = Decimal(str(plan.retirement_assets))
            
        total_ira_balance = (retirement_assets_decimal * Decimal(str(round(random.uniform(0.5, 0.8), 2)))).quantize(Decimal('0.01'))
        
        # Current status
        if plan.current_age < 72:
            status = "Future"
            current_rmd = Decimal('0')
        else:
            status = "Current"
            # Calculate RMD based on IRS life expectancy tables
            life_expectancy = max(1, 100 - plan.current_age)
            current_rmd = (total_ira_balance / Decimal(str(life_expectancy))).quantize(Decimal('0.01'))
        
        # Create projection for next 10 years or until age 100
        projection_years = min(10, 100 - plan.current_age)
        rmd_projection = []
        
        for year in range(projection_years):
            age = plan.current_age + year
            if age < 72:
                rmd_amount = Decimal('0')
                balance = total_ira_balance * (Decimal('1') + Decimal(str(plan.post_retirement_return))) ** Decimal(str(year))
                rmd_projection.append({
                    "year": datetime.now().year + year,
                    "age": age,
                    "balance": str(balance.quantize(Decimal('0.01'))),
                    "lifeExpectancy": max(1, 100 - age),
                    "rmdAmount": "0.00",
                    "rmdPercentage": "0.00"
                })
            else:
                # Simple model of IRA growth and RMD calculation
                life_expectancy = max(1, 100 - age)
                
                if year == 0:
                    balance = total_ira_balance
                else:
                    # Previous year's balance plus growth minus RMD
                    previous_balance = Decimal(rmd_projection[year-1]["balance"])
                    previous_rmd = Decimal(rmd_projection[year-1]["rmdAmount"])
                    growth_rate = Decimal(str(plan.post_retirement_return))
                    balance = (previous_balance - previous_rmd) * (Decimal('1') + growth_rate)
                    
                rmd_amount = (balance / Decimal(str(life_expectancy))).quantize(Decimal('0.01'))
                rmd_percentage = Decimal('0') if balance == Decimal('0') else (rmd_amount / balance * Decimal('100')).quantize(Decimal('0.01'))
                
                rmd_projection.append({
                    "year": datetime.now().year + year,
                    "age": age,
                    "balance": str(balance.quantize(Decimal('0.01'))),
                    "lifeExpectancy": life_expectancy,
                    "rmdAmount": str(rmd_amount),
                    "rmdPercentage": str(rmd_percentage)
                })
        
        # Create RMD data
        rmd_data = {
            "id": f"rmd_{str(rmd_id).zfill(3)}",
            "workspace_id": plan.workspace_id,
            "client_id": plan.client_id,
            "retirement_plan_id": plan.id,
            "created_by": plan.created_by,
            "updated_by": plan.updated_by,
            "created_at": created_at,
            "updated_at": updated_at,
            "status": status,
            "current_age": plan.current_age,
            "rmd_start_age": 72,
            "total_ira_balance": total_ira_balance,
            "current_rmd": current_rmd,
            "rmd_accounts": json.dumps([f"account_{random.randint(1, 100)}" for _ in range(random.randint(1, 3))]),
            "rmd_projection": json.dumps(rmd_projection) if rmd_projection else None,
            "distribution_strategy": random.choice([
                "Take RMDs as cash",
                "Reinvest in taxable account",
                "Qualified charitable distribution",
                "Roth conversion strategy"
            ]),
            "tax_impact": json.dumps({
                "federalTaxRate": random.randint(15, 35),
                "stateTaxRate": random.randint(0, 10),
                "estimatedTax": str((current_rmd * Decimal(str(round(random.uniform(0.15, 0.35), 2)))).quantize(Decimal('0.01'))) if current_rmd > 0 else "0.00"
            }) if random.random() > 0.5 else None,
            "compliance_status": "Compliant" if status == "Current" and random.random() > 0.9 else "Not Required" if status == "Future" else "Pending",
            "previous_distributions": json.dumps([{
                "year": datetime.now().year - i,
                "amount": str((total_ira_balance / Decimal(str(max(1, 100 - (plan.current_age - i)))) * Decimal(str(round(random.uniform(0.9, 1.1), 2)))).quantize(Decimal('0.01'))),
                "date": fake.date_between(start_date=f'-{i}y-12-01', end_date=f'-{i}y-12-31').strftime('%Y-%m-%d'),
                "method": random.choice(["Cash", "In-kind", "Charitable"])
            } for i in range(1, 4)]) if status == "Current" and random.random() > 0.5 else None,
            "notes": fake.paragraph() if random.random() > 0.7 else None
        }
        
        rmd = RMD(**rmd_data)
        db.add(rmd)
        
        rmd_id += 1
        rmds_created += 1
    
    db.commit()
    print(f"Seeded {rmds_created} RMD calculations successfully!")

# Main function to call when executing the script directly
if __name__ == "__main__":
    seed_retirement_data()