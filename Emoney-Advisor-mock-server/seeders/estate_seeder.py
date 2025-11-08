from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import json
from datetime import datetime, timezone, timedelta, date
from faker import Faker
import random
import uuid

from database import SessionLocal
from models.estate import Estate, Will, Trust, Beneficiary
from models.clients import Client
from models.users import User
from models.financial import FinancialPlan

# Initialize Faker
fake = Faker()

# Main function to seed all estate planning data
def seed_estate_planning(db: Session = None):
    """Main function to seed all estate planning data."""
    if db is None:
        db = SessionLocal()
    
    try:
        # Check if data already exists to avoid duplicates
        existing_estates = db.query(Estate).count()
        if existing_estates > 0:
            print("Estate planning data already seeded, skipping...")
            return
        
        # Get clients
        clients = db.query(Client).all()
        if not clients:
            print("No clients found. Please seed client data first.")
            return
        
        # Get users (for created_by, updated_by fields)
        users = db.query(User).all()
        if not users:
            print("No users found. Please seed user data first.")
            return
        
        # Get financial plans (to link estates to)
        financial_plans = db.query(FinancialPlan).all()
        
        print(f"Found {len(clients)} clients. Seeding estate planning data...")
        
        # Seed estates for about 60% of clients
        selected_clients = random.sample(clients, int(len(clients) * 0.6))
        estate_count = 0
        will_count = 0
        trust_count = 0
        beneficiary_count = 0
        
        workspace_id = "workspace-" + uuid.uuid4().hex[:8]
        
        for client in selected_clients:
            # Find if this client has a financial plan
            client_plan = next((plan for plan in financial_plans if plan.client_id == client.id), None)
            
            # Create estate
            estate = seed_estate_record(db, workspace_id, client, client_plan, users)
            estate_count += 1
            
            # Create wills (50-80% chance)
            if random.random() < 0.8:
                will = seed_will_record(db, workspace_id, estate, client, users)
                will_count += 1
                
                # Update estate's has_will status
                estate.has_will = True
                
                # Create beneficiaries for the will (2-5 per will)
                will_beneficiaries = seed_beneficiaries(db, workspace_id, estate, client, users, 
                                                      will_id=will.id, count=random.randint(2, 5))
                beneficiary_count += len(will_beneficiaries)
            
            # Create trusts (30-60% chance)
            if random.random() < 0.6:
                # Create 1-3 trusts
                num_trusts = random.randint(1, 3)
                for _ in range(num_trusts):
                    trust = seed_trust_record(db, workspace_id, estate, client, users)
                    trust_count += 1
                    
                    # Update estate's has_trust status
                    estate.has_trust = True
                    
                    # Create beneficiaries for the trust (1-4 per trust)
                    trust_beneficiaries = seed_beneficiaries(db, workspace_id, estate, client, users, 
                                                           trust_id=trust.id, count=random.randint(1, 4))
                    beneficiary_count += len(trust_beneficiaries)
            
            # Create estate-level beneficiaries (2-6 per estate)
            estate_beneficiaries = seed_beneficiaries(db, workspace_id, estate, client, users, count=random.randint(2, 6))
            beneficiary_count += len(estate_beneficiaries)
            
            # Update the estate to reflect beneficiary designations
            estate.has_beneficiary_designations = True
            db.commit()
        
        print(f"Estate planning seeding complete!")
        print(f"Created: {estate_count} estates, {will_count} wills, "
              f"{trust_count} trusts, {beneficiary_count} beneficiaries")
        
        return estate_count
        
    except Exception as e:
        print(f"Error seeding estate planning data: {e}")
        db.rollback()
        raise
    finally:
        if db is not None:
            db.close()

def generate_id(prefix: str) -> str:
    """Generate a unique ID with a prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def seed_estate_record(db: Session, workspace_id, client, financial_plan, users):
    """Create an estate record for a client."""
    # Select a random user as creator/updater
    user = random.choice(users)
    
    # Determine estate value (based on client's age and random factors)
    age = (date.today() - client.date_of_birth).days // 365 if client.date_of_birth else random.randint(30, 80)
    base_value = random.uniform(100000, 500000) + (age * random.uniform(5000, 20000))
    
    # Add additional value based on marital status
    if client.marital_status == "Married":
        base_value *= random.uniform(1.3, 1.8)
    
    total_estate_value = base_value
    
    # Calculate taxable estate (70-95% of total value)
    taxable_estate = total_estate_value * random.uniform(0.7, 0.95)
    
    # Calculate estimated tax (15-40% of taxable estate)
    estimated_tax = taxable_estate * random.uniform(0.15, 0.4)
    
    # Generate asset composition
    asset_composition = {
        "real_estate": round(random.uniform(0.2, 0.6), 2),
        "investments": round(random.uniform(0.1, 0.4), 2),
        "retirement_accounts": round(random.uniform(0.1, 0.3), 2),
        "business_interests": round(random.uniform(0, 0.2), 2),
        "personal_property": round(random.uniform(0.05, 0.15), 2),
        "cash_and_equivalents": round(random.uniform(0.02, 0.1), 2),
        "life_insurance": round(random.uniform(0, 0.15), 2),
    }
    
    # Normalize asset percentages to sum to 1.0
    total = sum(asset_composition.values())
    asset_composition = {k: round(v / total, 2) for k, v in asset_composition.items()}
    
    # Generate planning objectives
    planning_objectives = random.sample([
        "Minimize estate taxes",
        "Provide for spouse",
        "Provide for children",
        "Provide for grandchildren",
        "Support charitable causes",
        "Business succession planning",
        "Asset protection",
        "Special needs planning",
        "Legacy planning",
        "Education funding"
    ], k=random.randint(3, 6))
    
    # Generate planning strategies
    planning_strategies = random.sample([
        "Revocable living trust",
        "Irrevocable life insurance trust",
        "Credit shelter trust",
        "Qualified personal residence trust",
        "Charitable remainder trust",
        "Grantor retained annuity trust",
        "Family limited partnership",
        "Annual gifting strategy",
        "Donor-advised fund",
        "Dynasty trust",
        "Special needs trust"
    ], k=random.randint(2, 5))
    
    # Generate estate advisors
    advisors = [
        {
            "type": "Attorney",
            "name": fake.name(),
            "firm": f"{fake.last_name()}, {fake.last_name()} & Associates",
            "contact": fake.email()
        },
        {
            "type": "Accountant",
            "name": fake.name(),
            "firm": f"{fake.last_name()} {random.choice(['LLC', 'CPA', 'Group', 'Partners'])}",
            "contact": fake.email()
        }
    ]
    
    if random.random() < 0.7:
        advisors.append({
            "type": "Insurance Agent",
            "name": fake.name(),
            "firm": f"{fake.last_name()} Insurance",
            "contact": fake.email()
        })
    
    if random.random() < 0.5:
        advisors.append({
            "type": "Trust Officer",
            "name": fake.name(),
            "firm": f"{random.choice(['First', 'National', 'Premier', 'Capital', 'Union'])} {random.choice(['Trust', 'Bank', 'Financial'])}",
            "contact": fake.email()
        })
    
    # Generate dates
    last_review_date = fake.date_between(start_date='-2y', end_date='-3m')
    next_review_date = fake.date_between(start_date='+1m', end_date='+1y')
    
    # Create estate record
    estate = Estate(
        id=generate_id("estate"),
        workspace_id=workspace_id,
        client_id=client.id,
        financial_plan_id=financial_plan.id if financial_plan else None,
        created_by=user.id,
        updated_by=user.id,
        created_at=fake.date_time_between(start_date='-2y', end_date='-3m'),
        updated_at=fake.date_time_between(start_date='-3m', end_date='now'),
        status=random.choice(["Active", "Draft", "Review", "Complete"]),
        complexity=random.choice(["Simple", "Moderate", "Complex"]),
        marital_status=client.marital_status,
        total_estate_value=round(total_estate_value, 2),
        taxable_estate=round(taxable_estate, 2),
        estimated_tax=round(estimated_tax, 2),
        tax_status=random.choice(["Exempt", "Taxable", "Partially Taxable"]),
        asset_composition=asset_composition,
        state_of_residence=fake.state_abbr(),
        has_will=False,  # Will be updated later if will is created
        has_trust=False,  # Will be updated later if trust is created
        has_power_of_attorney=random.choice([True, False]),
        has_healthcare_directive=random.choice([True, False]),
        has_beneficiary_designations=False,  # Will be updated later if beneficiaries are created
        last_review_date=last_review_date,
        next_review_date=next_review_date,
        planning_objectives=planning_objectives,
        planning_strategies=planning_strategies,
        documents=[
            {
                "type": "Power of Attorney",
                "status": "Executed",
                "location": "Client Safe",
                "date": str(fake.date_between(start_date='-5y', end_date='-1y'))
            },
            {
                "type": "Healthcare Directive",
                "status": "Executed",
                "location": "Client Safe",
                "date": str(fake.date_between(start_date='-5y', end_date='-1y'))
            }
        ],
        advisors=advisors,
        notes=fake.paragraph() if random.random() < 0.7 else None
    )
    
    db.add(estate)
    db.flush()
    return estate

def seed_will_record(db: Session, workspace_id, estate, client, users):
    """Create a will record for an estate."""
    # Select a random user as creator/updater
    user = random.choice(users)
    
    # Generate dates
    execution_date = fake.date_between(start_date='-5y', end_date='-1y')
    last_updated = execution_date
    if random.random() < 0.3:  # 30% chance of being updated after execution
        last_updated = fake.date_between(start_date=execution_date, end_date='-1m')
    
    # Generate executor details
    is_spouse_executor = client.marital_status == "Married" and random.random() < 0.8
    
    if is_spouse_executor:
        executor = {
            "name": "Spouse",
            "relationship": "Spouse",
            "contact": fake.email()
        }
    else:
        executor = {
            "name": fake.name(),
            "relationship": random.choice(["Child", "Sibling", "Friend", "Attorney"]),
            "contact": fake.email()
        }
    
    # Generate alternate executor
    alternate_executor = {
        "name": fake.name(),
        "relationship": random.choice(["Child", "Sibling", "Friend", "Attorney"]),
        "contact": fake.email()
    }
    
    # Generate guardian for minors (if applicable)
    guardian_for_minors = None
    if random.random() < 0.5:  # 50% chance of having guardian designation
        guardian_for_minors = {
            "name": fake.name(),
            "relationship": random.choice(["Sibling", "Friend", "Relative"]),
            "contact": fake.email(),
            "alternate": {
                "name": fake.name(),
                "relationship": random.choice(["Sibling", "Friend", "Relative"]),
                "contact": fake.email()
            }
        }
    
    # Generate specific bequests
    specific_bequests = []
    if random.random() < 0.7:  # 70% chance of having specific bequests
        num_bequests = random.randint(1, 5)
        for _ in range(num_bequests):
            bequest = {
                "item": random.choice([
                    "Jewelry collection", "Antique furniture", "Art collection", 
                    "Family heirloom", "Coin collection", "Vintage car",
                    "Vacation property", "Firearms collection", "Book collection",
                    "Specific financial asset"
                ]),
                "description": fake.sentence(),
                "recipient": fake.name(),
                "relationship": random.choice(["Child", "Grandchild", "Sibling", "Friend", "Charity"]),
                "estimated_value": round(random.uniform(1000, 100000), 2)
            }
            specific_bequests.append(bequest)
    
    # Generate residuary estate distribution
    residuary_estate = []
    
    # If married, spouse often gets a large portion
    if client.marital_status == "Married" and random.random() < 0.9:
        residuary_estate.append({
            "recipient": "Spouse",
            "relationship": "Spouse",
            "percentage": random.randint(50, 100)
        })
    
    # Add children or other beneficiaries to reach 100%
    remaining_percentage = 100 - sum(item["percentage"] for item in residuary_estate)
    
    if remaining_percentage > 0:
        # Children
        if random.random() < 0.8:  # 80% chance of leaving to children
            num_children = random.randint(1, 4)
            child_percentage = remaining_percentage / num_children
            
            for i in range(num_children):
                residuary_estate.append({
                    "recipient": f"Child {i + 1}",
                    "relationship": "Child",
                    "percentage": round(child_percentage, 2)
                })
        else:
            # Other beneficiaries
            residuary_estate.append({
                "recipient": random.choice(["Charity", "Sibling", "Friend", "Other Relative"]),
                "relationship": random.choice(["Charity", "Sibling", "Friend", "Other Relative"]),
                "percentage": remaining_percentage
            })
    
    # Create will record
    will = Will(
        id=generate_id("will"),
        workspace_id=workspace_id,
        estate_id=estate.id,
        client_id=client.id,
        created_by=user.id,
        updated_by=user.id,
        created_at=fake.date_time_between(start_date='-2y', end_date='-3m'),
        updated_at=fake.date_time_between(start_date='-3m', end_date='now'),
        status=random.choice(["Draft", "Executed", "Under Review", "Updated Needed"]),
        type=random.choice(["Simple Will", "Pour-Over Will", "Living Will", "Holographic Will", "Joint Will"]),
        execution_date=execution_date,
        last_updated=last_updated,
        location=random.choice([
            "Attorney's office", "Home safe", "Safe deposit box", 
            "Court records", "Digital storage", "Trust company"
        ]),
        executor=executor,
        alternate_executor=alternate_executor,
        guardian_for_minors=guardian_for_minors,
        specific_bequests=specific_bequests,
        residuary_estate=residuary_estate,
        testamentary_trust=random.choice([True, False]),
        no_contest_clause=random.choice([True, False]),
        digital_assets=random.choice([True, False]),
        pet_provisions=random.choice([True, False]),
        charitable_provisions=random.choice([True, False]),
        special_instructions=fake.paragraph() if random.random() < 0.5 else None,
        attorney={
            "name": fake.name(),
            "firm": f"{fake.last_name()}, {fake.last_name()} & Associates",
            "contact": fake.email()
        },
        document_id=generate_id("doc"),
        notes=fake.paragraph() if random.random() < 0.5 else None
    )
    
    db.add(will)
    db.flush()
    return will

def seed_trust_record(db: Session, workspace_id, estate, client, users):
    """Create a trust record for an estate."""
    # Select a random user as creator/updater
    user = random.choice(users)
    
    # Choose trust type
    trust_types = [
        "Revocable Living Trust", "Irrevocable Trust", "Charitable Trust",
        "Special Needs Trust", "Spendthrift Trust", "Bypass Trust",
        "Generation-Skipping Trust", "Qualified Terminable Interest Property Trust",
        "Qualified Personal Residence Trust", "Grantor Retained Annuity Trust"
    ]
    trust_type = random.choice(trust_types)
    
    # Generate trust purpose based on type
    purpose_by_type = {
        "Revocable Living Trust": "Avoid probate and provide for smooth asset transition",
        "Irrevocable Trust": "Reduce estate tax liability and protect assets",
        "Charitable Trust": "Support charitable causes while providing income",
        "Special Needs Trust": "Provide for individual with disabilities while maintaining benefit eligibility",
        "Spendthrift Trust": "Protect assets from beneficiary's creditors and provide controlled distributions",
        "Bypass Trust": "Minimize estate taxes for married couples",
        "Generation-Skipping Trust": "Transfer wealth to grandchildren while minimizing generation-skipping tax",
        "Qualified Terminable Interest Property Trust": "Provide for spouse while controlling final disposition",
        "Qualified Personal Residence Trust": "Transfer residence with reduced gift tax",
        "Grantor Retained Annuity Trust": "Transfer appreciation of assets with minimal gift tax"
    }
    purpose = purpose_by_type.get(trust_type, "Estate planning and asset management")
    
    # Generate dates
    execution_date = fake.date_between(start_date='-10y', end_date='-1y')
    amendment_date = None
    if random.random() < 0.4:  # 40% chance of being amended
        amendment_date = fake.date_between(start_date=execution_date, end_date='-1m')
    
    # Generate grantor
    grantor = {
        "name": client.first_name + " " + client.last_name,
        "relationship": "Self",
        "contact": client.email
    }
    
    # Generate co-grantor (usually spouse if married)
    co_grantor = None
    if client.marital_status == "Married" and random.random() < 0.8:
        co_grantor = {
            "name": "Spouse",
            "relationship": "Spouse",
            "contact": fake.email()
        }
    
    # Generate trustee
    is_self_trustee = random.random() < 0.7  # 70% chance client is their own trustee
    
    if is_self_trustee:
        trustee = {
            "name": client.first_name + " " + client.last_name,
            "relationship": "Self",
            "contact": client.email
        }
    else:
        trustee = {
            "name": fake.name(),
            "relationship": random.choice(["Spouse", "Child", "Sibling", "Professional Trustee"]),
            "contact": fake.email()
        }
    
    # Generate successor trustee
    successor_trustee = {
        "name": fake.name(),
        "relationship": random.choice(["Spouse", "Child", "Sibling", "Friend", "Corporate Trustee"]),
        "contact": fake.email(),
        "institution": random.choice([None, "Trust Company", "Bank"]) if random.random() < 0.3 else None
    }
    
    # Generate trust value and funding source
    trust_value = estate.total_estate_value * random.uniform(0.3, 0.9)
    
    funding_source = []
    if random.random() < 0.8:
        funding_source.append({
            "type": "Real Estate",
            "description": "Primary residence and/or vacation property",
            "value": round(trust_value * random.uniform(0.3, 0.7), 2)
        })
    
    if random.random() < 0.7:
        funding_source.append({
            "type": "Investment Accounts",
            "description": "Brokerage accounts and/or retirement accounts",
            "value": round(trust_value * random.uniform(0.2, 0.6), 2)
        })
    
    if random.random() < 0.5:
        funding_source.append({
            "type": "Business Interests",
            "description": "Ownership stake in private business",
            "value": round(trust_value * random.uniform(0.1, 0.5), 2)
        })
    
    if random.random() < 0.6:
        funding_source.append({
            "type": "Life Insurance",
            "description": "Life insurance policies",
            "value": round(trust_value * random.uniform(0.1, 0.4), 2)
        })
    
    # Generate distribution provisions
    distribution_provisions = []
    
    # Spouse provision
    if client.marital_status == "Married" and random.random() < 0.9:
        distribution_provisions.append({
            "beneficiary": "Spouse",
            "relationship": "Spouse",
            "type": "Income",
            "terms": "All income for life, with discretionary principal distributions"
        })
    
    # Children provisions
    if random.random() < 0.8:
        num_children = random.randint(1, 4)
        for i in range(num_children):
            distribution_provisions.append({
                "beneficiary": f"Child {i + 1}",
                "relationship": "Child",
                "type": "Principal",
                "terms": random.choice([
                    "Equal share upon death of grantor",
                    "One-third at age 25, one-third at age 30, one-third at age 35",
                    "Half at age 30, half at age 40",
                    "Income until age 30, then principal",
                    "Discretionary distributions for health, education, and support"
                ])
            })
    
    # Charity provisions
    if random.random() < 0.4:
        distribution_provisions.append({
            "beneficiary": random.choice([
                "American Red Cross", "Habitat for Humanity", "St. Jude's Children's Hospital",
                "Local Community Foundation", "Alma Mater University", "Local Religious Organization"
            ]),
            "relationship": "Charity",
            "type": "Remainder",
            "terms": random.choice([
                "Remainder interest after all other beneficiaries",
                "10% of principal upon death of grantor",
                "Specific dollar amount annually"
            ])
        })
    
    # Generate tax filing requirements
    tax_id = None
    if trust_type in ["Irrevocable Trust", "Charitable Trust", "Special Needs Trust"]:
        tax_id = f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}"
    
    tax_filing_requirements = []
    if tax_id:
        tax_filing_requirements = [
            "Annual Form 1041 filing",
            "Schedule K-1 for beneficiaries",
            f"EIN: {tax_id}"
        ]
        
        if "Charitable" in trust_type:
            tax_filing_requirements.append("Form 5227 for split-interest trust")
    
    # Create trust record
    trust = Trust(
        id=generate_id("trust"),
        workspace_id=workspace_id,
        estate_id=estate.id,
        client_id=client.id,
        created_by=user.id,
        updated_by=user.id,
        created_at=fake.date_time_between(start_date='-2y', end_date='-3m'),
        updated_at=fake.date_time_between(start_date='-3m', end_date='now'),
        name=f"{client.last_name} {trust_type}",
        status=random.choice(["Active", "Pending Funding", "Under Review", "Inactive"]),
        trust_type=trust_type,
        purpose=purpose,
        execution_date=execution_date,
        amendment_date=amendment_date,
        location=random.choice([
            "Attorney's office", "Home safe", "Safe deposit box", 
            "Trust company", "Digital storage"
        ]),
        grantor=grantor,
        co_grantor=co_grantor,
        trustee=trustee,
        successor_trustee=successor_trustee,
        is_funded=random.choice([True, False]),
        trust_value=round(trust_value, 2),
        funding_source=funding_source,
        distribution_provisions=distribution_provisions,
        spendthrift_provision=random.choice([True, False]),
        generation_skipping=random.choice([True, False]),
        tax_id=tax_id,
        tax_filing_requirements=tax_filing_requirements if tax_id else None,
        attorney={
            "name": fake.name(),
            "firm": f"{fake.last_name()}, {fake.last_name()} & Associates",
            "contact": fake.email()
        },
        document_id=generate_id("doc"),
        notes=fake.paragraph() if random.random() < 0.5 else None
    )
    
    db.add(trust)
    db.flush()
    return trust

def seed_beneficiaries(db: Session, workspace_id, estate, client, users, will_id=None, trust_id=None, count=3):
    """Create beneficiary records for an estate, will, or trust."""
    # Select a random user as creator/updater
    user = random.choice(users)
    
    # Define common relationships for beneficiary types
    relationships = {
        "Individual": ["Spouse", "Child", "Grandchild", "Sibling", "Niece/Nephew", "Friend"],
        "Organization": ["Charity", "Educational Institution", "Religious Organization"],
        "Trust": ["Family Trust", "Charitable Trust", "Special Needs Trust"]
    }
    
    # Asset types that can be specified
    asset_types = [
        "Real Estate", "Financial Accounts", "Retirement Accounts", 
        "Life Insurance", "Personal Property", "Business Interests"
    ]
    
    beneficiaries = []
    
    # For wills and trusts, we need to distribute 100% among beneficiaries
    total_percentage = 0
    remaining_percentage = 100
    
    for i in range(count):
        # Determine if this is a primary or contingent beneficiary
        is_primary = i < count * 0.7  # First 70% are primary
        is_contingent = not is_primary
        
        # Determine type and relationship
        beneficiary_type = random.choices(
            ["Individual", "Organization", "Trust"],
            weights=[0.8, 0.15, 0.05],
            k=1
        )[0]
        
        relationship = random.choice(relationships[beneficiary_type])
        
        # If it's a spouse, set spouse-specific data
        if relationship == "Spouse" and client.marital_status != "Married":
            relationship = "Child"  # Fall back to child if not married
        
        # Determine percentage allocation
        if is_primary:
            # For primary beneficiaries, allocate a percentage that adds up to 100%
            min_percentage = 5
            max_percentage = min(95, remaining_percentage - (count - i - 1) * min_percentage)
            
            if i == count - 1 or is_contingent:  # Last beneficiary or moving to contingent
                percentage = remaining_percentage
            else:
                percentage = random.randint(min_percentage, max_percentage)
            
            remaining_percentage -= percentage
            total_percentage += percentage
        else:
            # Contingent beneficiaries often get equal splits
            percentage = 100 / (count - int(count * 0.7))
            percentage = round(percentage, 2)
        
        # Determine asset types and specific assets for this beneficiary
        num_asset_types = random.randint(1, 3)
        selected_asset_types = random.sample(asset_types, num_asset_types)
        
        specific_assets = []
        if random.random() < 0.4:  # 40% chance of specifying assets
            for asset_type in selected_asset_types:
                if asset_type == "Real Estate":
                    specific_assets.append({
                        "description": random.choice([
                            "Primary Residence", "Vacation Home", "Rental Property", 
                            "Commercial Property", "Land"
                        ]),
                        "value": round(random.uniform(100000, 1000000), 2)
                    })
                elif asset_type == "Financial Accounts":
                    specific_assets.append({
                        "description": random.choice([
                            "Brokerage Account", "Savings Account", "Checking Account",
                            "Certificate of Deposit", "Money Market Account"
                        ]),
                        "value": round(random.uniform(10000, 500000), 2)
                    })
                elif asset_type == "Retirement Accounts":
                    specific_assets.append({
                        "description": random.choice([
                            "IRA", "401(k)", "403(b)", "SEP IRA", "Roth IRA"
                        ]),
                        "value": round(random.uniform(50000, 1000000), 2)
                    })
                elif asset_type == "Life Insurance":
                    specific_assets.append({
                        "description": random.choice([
                            "Term Life Policy", "Whole Life Policy", 
                            "Universal Life Policy", "Group Life Policy"
                        ]),
                        "value": round(random.uniform(100000, 2000000), 2)
                    })
                elif asset_type == "Personal Property":
                    specific_assets.append({
                        "description": random.choice([
                            "Jewelry", "Art Collection", "Antiques", 
                            "Vehicles", "Collectibles"
                        ]),
                        "value": round(random.uniform(5000, 100000), 2)
                    })
                elif asset_type == "Business Interests":
                    specific_assets.append({
                        "description": random.choice([
                            "LLC Membership Interest", "Partnership Interest",
                            "Corporate Stock", "Sole Proprietorship"
                        ]),
                        "value": round(random.uniform(50000, 1000000), 2)
                    })
        
        # Generate conditions for the bequest
        conditions = None
        if random.random() < 0.3:  # 30% chance of conditions
            conditions = random.sample([
                "Must be at least 25 years old",
                "Must be married",
                "Must have completed college degree",
                "Must use for education expenses only",
                "Must purchase a home",
                "Cannot sell the property for 10 years",
                "Subject to drug testing",
                "Requires annual accounting",
                "Required to maintain property"
            ], k=random.randint(1, 3))
        
        # Create the beneficiary record
        beneficiary = Beneficiary(
            id=generate_id("benef"),
            workspace_id=workspace_id,
            estate_id=estate.id,
            will_id=will_id,
            trust_id=trust_id,
            client_id=client.id,
            created_by=user.id,
            updated_by=user.id,
            created_at=fake.date_time_between(start_date='-2y', end_date='-3m'),
            updated_at=fake.date_time_between(start_date='-3m', end_date='now'),
            name=relationship if relationship in ["Spouse"] else fake.name(),
            type=beneficiary_type,
            relationship=relationship,
            status="Active",
            primary=is_primary,
            contingent=is_contingent,
            percentage=round(percentage, 2),
            priority=i + 1,
            asset_types=selected_asset_types,
            specific_assets=specific_assets,
            details={
                "age": random.randint(18, 80) if beneficiary_type == "Individual" else None,
                "tax_id": f"{random.randint(10, 99)}-{random.randint(1000000, 9999999)}" if beneficiary_type != "Individual" else None,
                "contact": {
                    "email": fake.email(),
                    "phone": fake.phone_number(),
                    "address": fake.address() if random.random() < 0.5 else None
                } if beneficiary_type == "Individual" else {
                    "contact_person": fake.name(),
                    "email": fake.email(),
                    "phone": fake.phone_number()
                }
            },
            conditions=conditions,
            notes=fake.paragraph() if random.random() < 0.5 else None
        )
        
        db.add(beneficiary)
        beneficiaries.append(beneficiary)
    
    db.flush()
    return beneficiaries

if __name__ == "__main__":
    seed_estate_planning()