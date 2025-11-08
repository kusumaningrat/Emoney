# seeders/insurance.py

from sqlalchemy.orm import Session
import json
from datetime import datetime, timezone, timedelta, date
from faker import Faker
import random
import uuid
from decimal import Decimal
import calendar

from database import SessionLocal
from models.insurance import Insurance, InsurancePolicy, Coverage, Premium
from models.clients import Client, Contact
from models.users import User, Workspace
from seeders.client_seeder import seed_clients

# Initialize Faker
fake = Faker()

# Main function to seed all insurance planning data
def seed_insurance_data():
    """Main function to seed all insurance planning data in correct order."""
    db = SessionLocal()
    try:
        # Check if data already exists to avoid duplicates
        existing_insurance = db.query(Insurance).count()
        if existing_insurance > 0:
            print("Insurance planning data already seeded, skipping...")
            return

        # Ensure clients exist
        clients = db.query(Client).all()
        if not clients:
            print("No clients found, seeding clients first...")
            seed_clients()
            clients = db.query(Client).all()
            
        # 1. Create insurance records first
        insurance_records = seed_insurance_records(db, clients)
        db.commit()
        
        # 2. Create policy records
        policies = seed_policies(db, insurance_records)
        db.commit()
        
        # 3. Create coverage details
        seed_coverages(db, policies)
        db.commit()
        
        # 4. Create premium records
        seed_premiums(db, policies)
        db.commit()
        
        print("Insurance planning seeding complete!")
        
    except Exception as e:
        print(f"Error seeding insurance planning data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def seed_insurance_records(db: Session, clients: list) -> list:
    """Seed insurance portfolio data for clients."""
    print("Seeding insurance portfolio data...")
    
    insurance_records_created = 0
    insurance_records = []
    insurance_id = 1
    
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
        
        # Create timestamps with timezone info
        created_at = datetime.now(timezone.utc)
        if hasattr(client, 'created_at') and client.created_at:
            if isinstance(client.created_at, datetime):
                created_at = client.created_at
                if created_at.tzinfo is None:
                    created_at = created_at.replace(tzinfo=timezone.utc)
            
        updated_at = datetime.now(timezone.utc)
        
        # Insurance needs and summary - use Decimal
        total_coverage = Decimal('0')
        annual_premiums = Decimal('0')
        
        # Determine coverage gaps
        coverage_gaps = []
        if random.random() > 0.7:
            gaps = random.sample([
                "Life insurance death benefit insufficient",
                "Disability coverage lacking",
                "Long-term care coverage needed",
                "Health insurance deductibles too high",
                "Auto liability limits too low",
                "Umbrella policy recommended",
                "Home insurance replacement cost insufficient"
            ], random.randint(1, 3))
            coverage_gaps.extend(gaps)
        
        # Create insurance portfolio data
        insurance_data = {
            "id": f"insurance_{str(insurance_id).zfill(3)}",
            "workspace_id": workspace_id,
            "client_id": client.id,
            "created_by": created_by,
            "updated_by": updated_by,
            "created_at": created_at,
            "updated_at": updated_at,
            "status": "Active",
            "last_review_date": fake.date_between(start_date='-1y', end_date='-30d') if random.random() > 0.5 else None,
            "next_review_date": fake.date_between(start_date='today', end_date='+180d'),
            "total_coverage": total_coverage,  # Will update after creating policies
            "annual_premiums": annual_premiums,  # Will update after creating policies
            "coverage_score": random.randint(50, 95),
            "coverage_gaps": json.dumps(coverage_gaps) if coverage_gaps else None,
            "recommendations": json.dumps([
                "Review life insurance death benefit",
                "Consider umbrella liability policy",
                "Evaluate long-term care options"
            ]) if random.random() > 0.5 else None,
            "notes": fake.paragraph() if random.random() > 0.7 else None
        }
        
        insurance = Insurance(**insurance_data)
        db.add(insurance)
        insurance_records.append(insurance)
        
        insurance_id += 1
        insurance_records_created += 1
    
    db.commit()
    print(f"Seeded {insurance_records_created} insurance portfolios successfully!")
    return insurance_records

def seed_policies(db: Session, insurance_records: list) -> list:
    """Create insurance policy records."""
    print("Creating insurance policy records...")
    
    policies_created = 0
    policies = []
    policy_id = 1
    
    # Policy templates
    policy_templates = [
        {
            "type": "Life",
            "subtype": "Term",
            "provider_options": ["Northwestern Mutual", "New York Life", "State Farm", "MassMutual", "Guardian"],
            "typical_coverage": (100000, 2000000),
            "typical_premium": (250, 2500),
            "duration_years": (10, 20, 30)
        },
        {
            "type": "Life",
            "subtype": "Whole",
            "provider_options": ["Northwestern Mutual", "New York Life", "MassMutual", "Guardian", "Prudential"],
            "typical_coverage": (50000, 1000000),
            "typical_premium": (1000, 10000),
            "duration_years": None  # Permanent
        },
        {
            "type": "Life",
            "subtype": "Universal",
            "provider_options": ["Prudential", "Lincoln Financial", "John Hancock", "AIG", "Nationwide"],
            "typical_coverage": (100000, 2000000),
            "typical_premium": (1000, 8000),
            "duration_years": None  # Permanent
        },
        {
            "type": "Health",
            "subtype": "Individual",
            "provider_options": ["Blue Cross Blue Shield", "UnitedHealthcare", "Aetna", "Cigna", "Humana"],
            "typical_coverage": (1000000, 5000000),  # Maximum out-of-pocket + coverage limit
            "typical_premium": (3000, 12000),
            "duration_years": (1, 1)
        },
        {
            "type": "Health",
            "subtype": "Group",
            "provider_options": ["Blue Cross Blue Shield", "UnitedHealthcare", "Aetna", "Cigna", "Kaiser Permanente"],
            "typical_coverage": (1000000, 5000000),  # Maximum out-of-pocket + coverage limit
            "typical_premium": (2000, 8000),  # Employee portion
            "duration_years": (1, 1)
        },
        {
            "type": "Disability",
            "subtype": "Long-term",
            "provider_options": ["Guardian", "Principal", "The Standard", "Mutual of Omaha", "Unum"],
            "typical_coverage": (2000, 10000),  # Monthly benefit
            "typical_premium": (500, 3000),
            "duration_years": (2, 5, 10, "To age 65")
        },
        {
            "type": "Disability",
            "subtype": "Short-term",
            "provider_options": ["Guardian", "Principal", "The Standard", "Mutual of Omaha", "Unum"],
            "typical_coverage": (1000, 5000),  # Monthly benefit
            "typical_premium": (200, 1500),
            "duration_years": (0.25, 0.5, 1)  # 3, 6, or 12 months
        },
        {
            "type": "Long-Term Care",
            "subtype": "Traditional",
            "provider_options": ["Genworth", "Mutual of Omaha", "New York Life", "Northwestern Mutual", "MassMutual"],
            "typical_coverage": (100, 500),  # Daily benefit
            "typical_premium": (1500, 8000),
            "duration_years": (3, 5, "Lifetime")
        },
        {
            "type": "Property",
            "subtype": "Homeowners",
            "provider_options": ["State Farm", "Allstate", "Liberty Mutual", "Farmers", "Travelers"],
            "typical_coverage": (200000, 1000000),
            "typical_premium": (800, 3000),
            "duration_years": (1, 1)
        },
        {
            "type": "Property",
            "subtype": "Auto",
            "provider_options": ["GEICO", "State Farm", "Progressive", "Allstate", "Liberty Mutual"],
            "typical_coverage": (100000, 500000),  # Liability limits
            "typical_premium": (600, 2500),
            "duration_years": (0.5, 1)  # 6 months or 1 year
        },
        {
            "type": "Property",
            "subtype": "Umbrella",
            "provider_options": ["State Farm", "Allstate", "GEICO", "Liberty Mutual", "Travelers"],
            "typical_coverage": (1000000, 5000000),
            "typical_premium": (300, 1000),
            "duration_years": (1, 1)
        }
    ]
    
    for insurance in insurance_records:
        # Get client
        client = db.query(Client).filter(Client.id == insurance.client_id).first()
        if not client:
            continue
            
        # Get contact info from client's contacts instead of contact_id
        primary_contact = None
        if hasattr(client, 'contacts') and client.contacts:
            primary_contact = next((c for c in client.contacts if hasattr(c, 'is_preferred') and c.is_preferred), None)
            if not primary_contact and len(client.contacts) > 0:
                primary_contact = client.contacts[0]
        
        if not primary_contact:
            continue
        
        # Determine number and types of policies for this client
        # Always include basic coverage: health, auto, home if homeowner
        essential_policies = ["Health", "Property"] if random.random() > 0.3 else ["Health"]
        
        # Add more advanced policies based on client sophistication
        if random.random() > 0.5:
            essential_policies.append("Life")
        if random.random() > 0.7:
            essential_policies.append("Disability")
        if random.random() > 0.85:
            essential_policies.append("Long-Term Care")
        
        # Create a list (not a set) of policy types to add
        selected_policy_types = []
        
        # Add essential policies
        for policy_type in essential_policies:
            templates = [t for t in policy_templates if t["type"] == policy_type]
            if templates:
                # Add at least one of each essential policy type
                selected_policy_types.append(random.choice(templates))
        
        # Add some additional policies randomly
        additional_count = random.randint(0, 3)
        for _ in range(additional_count):
            # Add random policy, check for duplicates by type and subtype
            candidate = random.choice(policy_templates)
            # Check if we already have this policy type/subtype
            if not any(p["type"] == candidate["type"] and p["subtype"] == candidate["subtype"] for p in selected_policy_types):
                selected_policy_types.append(candidate)
        
        total_coverage = Decimal('0')
        annual_premiums = Decimal('0')
        
        # Create each selected policy
        for policy_template in selected_policy_types:
            # Create timestamps with timezone info
            created_at = insurance.created_at
            updated_at = insurance.updated_at
            
            # Policy details
            policy_type = policy_template["type"]
            policy_subtype = policy_template["subtype"]
            
            # Choose provider
            provider = random.choice(policy_template["provider_options"])
            
            # Policy name
            policy_name = f"{provider} {policy_subtype} {policy_type}"
            
            # Coverage amount - use Decimal
            if isinstance(policy_template["typical_coverage"], tuple):
                min_coverage, max_coverage = policy_template["typical_coverage"]
                coverage_amount = Decimal(str(round(random.uniform(min_coverage, max_coverage), 2)))
            else:
                coverage_amount = Decimal(str(round(policy_template["typical_coverage"], 2)))
                
            # Premium amount - use Decimal
            if isinstance(policy_template["typical_premium"], tuple):
                min_premium, max_premium = policy_template["typical_premium"]
                premium_amount = Decimal(str(round(random.uniform(min_premium, max_premium), 2)))
            else:
                premium_amount = Decimal(str(round(policy_template["typical_premium"], 2)))
                
            # Policy status
            status = "Active" if random.random() > 0.1 else random.choice(["Pending", "Lapsed", "Cancelled"])
            
            # Policy term/duration
            if policy_template["duration_years"] is None:
                # Permanent policy
                term = "Lifetime"
                expiration_date = None
                effective_date = fake.date_between(start_date='-10y', end_date='-1y')
            elif isinstance(policy_template["duration_years"], tuple):
                # Choose from options
                term_options = policy_template["duration_years"]
                term = random.choice(term_options)
                if isinstance(term, (int, float)):
                    if policy_type == "Life" and policy_subtype == "Term":
                        # Term life typically has fixed term lengths (10, 20, 30 years)
                        effective_date = fake.date_between(start_date='-10y', end_date='-1y')
                        expiration_date = effective_date.replace(year=effective_date.year + int(term))
                    else:
                        # Short policies like auto typically renew annually
                        effective_date = fake.date_between(start_date='-1y', end_date='-30d')
                        expiration_date = effective_date + timedelta(days=int(term * 365))
                else:
                    # "To age 65" or "Lifetime" type terms
                    term = str(term)
                    effective_date = fake.date_between(start_date='-10y', end_date='-1y')
                    expiration_date = None
            else:
                # Single value
                term = str(policy_template["duration_years"])
                effective_date = fake.date_between(start_date='-1y', end_date='-30d')
                expiration_date = effective_date + timedelta(days=int(float(term) * 365))
            
            # Insured person(s)
            insured = ["Client"]
            has_spouse = hasattr(client, 'spouse') and client.spouse
            
            if policy_type in ["Health", "Life"] and has_spouse and random.random() > 0.5:
                insured.append("Spouse")
                
                # Family policies have higher premiums
                premium_amount = premium_amount * Decimal('1.8')
            
            has_household = hasattr(client, 'household_memberships') and client.household_memberships
            if policy_type == "Health" and has_household and random.random() > 0.7:
                insured.append("Dependents")
                
                # Family policies with kids have even higher premiums
                premium_amount = premium_amount * Decimal('1.3')
            
            # Policy number
            policy_number = f"{fake.lexify(text='??').upper()}-{fake.numerify(text='######')}"
            
            # Create policy data
            policy_data = {
                "id": f"policy_{str(policy_id).zfill(3)}",
                "workspace_id": insurance.workspace_id,
                "insurance_id": insurance.id,
                "client_id": insurance.client_id,
                "created_by": insurance.created_by,
                "updated_by": insurance.updated_by,
                "created_at": created_at,
                "updated_at": updated_at,
                "name": policy_name,
                "policy_type": policy_type,
                "policy_subtype": policy_subtype,
                "policy_number": policy_number,
                "provider": provider,
                "status": status,
                "effective_date": effective_date,
                "expiration_date": expiration_date,
                "term": term,
                "premium_amount": premium_amount,
                "premium_frequency": random.choice(["Monthly", "Quarterly", "Semi-Annual", "Annual"]),
                "coverage_amount": coverage_amount,
                "insured": json.dumps(insured),
                "owner": "Client" if random.random() > 0.2 else "Trust",
                "beneficiaries": json.dumps({
                    "primary": [{"name": "Spouse", "relationship": "Spouse", "percentage": 100}] if has_spouse else [{"name": "Estate", "relationship": "Estate", "percentage": 100}],
                    "contingent": [{"name": "Children", "relationship": "Children", "percentage": 100}] if random.random() > 0.5 else []
                }) if policy_type == "Life" else None,
                "renewal_type": random.choice(["Automatic", "Manual"]),
                "payment_method": random.choice(["Credit Card", "Bank Draft", "Check", "Payroll Deduction"]),
                "agent_name": fake.name(),
                "agent_contact": fake.phone_number() if random.random() > 0.5 else None,
                "underwriting_class": random.choice(["Preferred Plus", "Preferred", "Standard Plus", "Standard", "Substandard"]) if policy_type == "Life" else None,
                "policy_features": json.dumps([
                    f"Feature {i+1}: {fake.bs()}" for i in range(random.randint(1, 3))
                ]) if random.random() > 0.5 else None,
                "notes": fake.paragraph() if random.random() > 0.7 else None
            }
            
            policy = InsurancePolicy(**policy_data)
            db.add(policy)
            policies.append(policy)
            
            # Update total coverage and premiums
            if policy.status == "Active":
                total_coverage += coverage_amount
                
                # Calculate annual premium regardless of frequency
                annual_premium = Decimal('0')
                if policy.premium_frequency == "Monthly":
                    annual_premium = premium_amount * Decimal('12')
                elif policy.premium_frequency == "Quarterly":
                    annual_premium = premium_amount * Decimal('4')
                elif policy.premium_frequency == "Semi-Annual":
                    annual_premium = premium_amount * Decimal('2')
                else:  # Annual
                    annual_premium = premium_amount
                    
                annual_premiums += annual_premium
            
            policy_id += 1
            policies_created += 1
        
        # Update the insurance record with totals
        insurance.total_coverage = total_coverage
        insurance.annual_premiums = annual_premiums
    
    db.commit()
    print(f"Seeded {policies_created} insurance policies successfully!")
    return policies

def seed_coverages(db: Session, policies: list):
    """Create coverage details for insurance policies."""
    print("Creating coverage details...")
    
    coverages_created = 0
    coverage_id = 1
    
    for policy in policies:
        # Skip some policies for detailed coverage
        if random.random() > 0.8:
            continue
            
        # Number of coverages to create depends on policy type
        num_coverages = 1
        if policy.policy_type == "Health":
            num_coverages = random.randint(3, 6)
        elif policy.policy_type == "Property" and policy.policy_subtype in ["Homeowners", "Auto"]:
            num_coverages = random.randint(2, 5)
        
        # Create each coverage
        for i in range(num_coverages):
            # Create timestamps with timezone info
            created_at = policy.created_at
            updated_at = policy.updated_at
            
            # Coverage details based on policy type
            if policy.policy_type == "Life":
                coverage_type = "Death Benefit"
                name = "Death Benefit"
                description = "Pays beneficiary upon death of insured"
                coverage_amount = policy.coverage_amount
                deductible = Decimal('0')
                coinsurance_percentage = 0
                out_of_pocket_max = Decimal('0')
                annual_limit = Decimal('0')
                lifetime_limit = policy.coverage_amount
            elif policy.policy_type == "Health":
                # Health insurance has multiple coverage types
                coverage_options = [
                    {
                        "type": "Medical",
                        "name": "Medical Services",
                        "description": "Coverage for doctor visits, hospital stays, and medical procedures",
                        "deductible": (500, 3000),
                        "coinsurance": (10, 30),
                        "out_of_pocket_max": (3000, 10000)
                    },
                    {
                        "type": "Prescription",
                        "name": "Prescription Drugs",
                        "description": "Coverage for prescription medications",
                        "deductible": (0, 500),
                        "coinsurance": (10, 50),
                        "out_of_pocket_max": (1000, 5000)
                    },
                    {
                        "type": "Preventive",
                        "name": "Preventive Care",
                        "description": "Coverage for annual check-ups, vaccinations, and screenings",
                        "deductible": (0, 0),
                        "coinsurance": (0, 0),
                        "out_of_pocket_max": (0, 0)
                    },
                    {
                        "type": "Emergency",
                        "name": "Emergency Services",
                        "description": "Coverage for emergency room visits and ambulance services",
                        "deductible": (100, 1000),
                        "coinsurance": (10, 30),
                        "out_of_pocket_max": (2000, 8000)
                    },
                    {
                        "type": "Specialty",
                        "name": "Specialty Care",
                        "description": "Coverage for specialist visits and specialized treatments",
                        "deductible": (500, 2000),
                        "coinsurance": (20, 40),
                        "out_of_pocket_max": (3000, 9000)
                    },
                    {
                        "type": "Mental Health",
                        "name": "Mental Health Services",
                        "description": "Coverage for therapy, counseling, and psychiatric services",
                        "deductible": (200, 1000),
                        "coinsurance": (10, 30),
                        "out_of_pocket_max": (2000, 7000)
                    }
                ]
                
                # Select a coverage type that hasn't been used yet for this policy
                used_types = []
                if hasattr(policy, 'coverages'):
                    try:
                        used_types = [c.coverage_type for c in policy.coverages]
                    except:
                        used_types = []
                
                available_options = [c for c in coverage_options if c["type"] not in used_types]
                
                if not available_options:
                    # If all types are used, skip creating more
                    continue
                    
                selected_coverage = random.choice(available_options)
                
                coverage_type = selected_coverage["type"]
                name = selected_coverage["name"]
                description = selected_coverage["description"]
                coverage_amount = policy.coverage_amount if i == 0 else Decimal('0')  # Only first coverage shows full amount
                
                if isinstance(selected_coverage["deductible"], tuple):
                    min_deductible, max_deductible = selected_coverage["deductible"]
                    deductible = Decimal(str(round(random.uniform(min_deductible, max_deductible), 2)))
                else:
                    deductible = Decimal(str(selected_coverage["deductible"]))
                    
                if isinstance(selected_coverage["coinsurance"], tuple):
                    min_coinsurance, max_coinsurance = selected_coverage["coinsurance"]
                    coinsurance_percentage = random.randint(min_coinsurance, max_coinsurance)
                else:
                    coinsurance_percentage = selected_coverage["coinsurance"]
                    
                if isinstance(selected_coverage["out_of_pocket_max"], tuple):
                    min_oop, max_oop = selected_coverage["out_of_pocket_max"]
                    out_of_pocket_max = Decimal(str(round(random.uniform(min_oop, max_oop), 2)))
                else:
                    out_of_pocket_max = Decimal(str(selected_coverage["out_of_pocket_max"]))
                    
                annual_limit = Decimal('0')  # ACA eliminated annual limits
                lifetime_limit = Decimal('0')  # ACA eliminated lifetime limits
            elif policy.policy_type == "Property" and policy.policy_subtype == "Homeowners":
                # Homeowners has multiple coverage types
                coverage_options = [
                    {
                        "type": "Dwelling",
                        "name": "Dwelling Coverage",
                        "description": "Covers damage to the main structure of the home",
                        "percentage": (1.0, 1.0)  # 100% of policy coverage
                    },
                    {
                        "type": "Other Structures",
                        "name": "Other Structures Coverage",
                        "description": "Covers damage to detached structures like garages and sheds",
                        "percentage": (0.1, 0.2)  # 10-20% of policy coverage
                    },
                    {
                        "type": "Personal Property",
                        "name": "Personal Property Coverage",
                        "description": "Covers damage to or theft of personal belongings",
                        "percentage": (0.5, 0.7)  # 50-70% of policy coverage
                    },
                    {
                        "type": "Loss of Use",
                        "name": "Loss of Use Coverage",
                        "description": "Covers additional living expenses if home is uninhabitable",
                        "percentage": (0.2, 0.3)  # 20-30% of policy coverage
                    },
                    {
                        "type": "Liability",
                        "name": "Personal Liability",
                        "description": "Covers legal liability for injuries to others on your property",
                        "percentage": (0.3, 0.5)  # 30-50% of policy coverage, but separate limit
                    }
                ]
                
                # Select a coverage type that hasn't been used yet for this policy
                used_types = []
                if hasattr(policy, 'coverages'):
                    try:
                        used_types = [c.coverage_type for c in policy.coverages]
                    except:
                        used_types = []
                
                available_options = [c for c in coverage_options if c["type"] not in used_types]
                
                if not available_options:
                    # If all types are used, skip creating more
                    continue
                    
                selected_coverage = random.choice(available_options)
                
                coverage_type = selected_coverage["type"]
                name = selected_coverage["name"]
                description = selected_coverage["description"]
                
                if isinstance(selected_coverage["percentage"], tuple):
                    min_percentage, max_percentage = selected_coverage["percentage"]
                    coverage_percentage = random.uniform(min_percentage, max_percentage)
                else:
                    coverage_percentage = selected_coverage["percentage"]
                    
                coverage_amount = (policy.coverage_amount * Decimal(str(coverage_percentage))).quantize(Decimal('0.01'))
                deductible = Decimal(str(round(random.uniform(500, 2500), 2)))
                coinsurance_percentage = 0
                out_of_pocket_max = Decimal('0')
                annual_limit = Decimal('0')
                lifetime_limit = Decimal('0')
            elif policy.policy_type == "Property" and policy.policy_subtype == "Auto":
                # Auto insurance has multiple coverage types
                coverage_options = [
                    {
                        "type": "Liability",
                        "name": "Liability Coverage",
                        "description": "Covers damage you cause to others",
                        "percentage": (1.0, 1.0)  # Full policy limit
                    },
                    {
                        "type": "Collision",
                        "name": "Collision Coverage",
                        "description": "Covers damage to your car from an accident",
                        "percentage": (0.1, 1.0)  # Vehicle value
                    },
                    {
                        "type": "Comprehensive",
                        "name": "Comprehensive Coverage",
                        "description": "Covers non-accident damage like theft or weather",
                        "percentage": (0.1, 1.0)  # Vehicle value
                    },
                    {
                        "type": "Medical",
                        "name": "Medical Payments",
                        "description": "Covers medical expenses regardless of fault",
                        "percentage": (0.05, 0.2)  # 5-20% of policy limit
                    },
                    {
                        "type": "Uninsured",
                        "name": "Uninsured Motorist",
                        "description": "Covers damage caused by uninsured drivers",
                        "percentage": (0.5, 1.0)  # 50-100% of liability limit
                    }
                ]
                
                # Select a coverage type that hasn't been used yet for this policy
                used_types = []
                if hasattr(policy, 'coverages'):
                    try:
                        used_types = [c.coverage_type for c in policy.coverages]
                    except:
                        used_types = []
                
                available_options = [c for c in coverage_options if c["type"] not in used_types]
                
                if not available_options:
                    # If all types are used, skip creating more
                    continue
                    
                selected_coverage = random.choice(available_options)
                
                coverage_type = selected_coverage["type"]
                name = selected_coverage["name"]
                description = selected_coverage["description"]
                
                if isinstance(selected_coverage["percentage"], tuple):
                    min_percentage, max_percentage = selected_coverage["percentage"]
                    coverage_percentage = random.uniform(min_percentage, max_percentage)
                else:
                    coverage_percentage = selected_coverage["percentage"]
                    
                coverage_amount = (policy.coverage_amount * Decimal(str(coverage_percentage))).quantize(Decimal('0.01'))
                deductible = Decimal(str(round(random.uniform(250, 1000), 2))) if coverage_type in ["Collision", "Comprehensive"] else Decimal('0')
                coinsurance_percentage = 0
                out_of_pocket_max = Decimal('0')
                annual_limit = Decimal('0')
                lifetime_limit = Decimal('0')
            elif policy.policy_type == "Disability":
                coverage_type = "Income Replacement"
                name = "Disability Income"
                description = "Replaces a portion of income if unable to work due to disability"
                coverage_amount = policy.coverage_amount  # Monthly benefit
                deductible = Decimal('0')
                coinsurance_percentage = 0
                out_of_pocket_max = Decimal('0')
                annual_limit = coverage_amount * Decimal('12')  # Annual benefit
                lifetime_limit = Decimal('0')
            elif policy.policy_type == "Long-Term Care":
                coverage_type = "Care Expenses"
                name = "Long-Term Care Benefits"
                description = "Covers costs of long-term care services"
                coverage_amount = policy.coverage_amount  # Daily benefit
                deductible = Decimal('0')
                coinsurance_percentage = 0
                out_of_pocket_max = Decimal('0')
                annual_limit = coverage_amount * Decimal('365')  # Annual maximum
                lifetime_limit = annual_limit * Decimal(str(random.randint(2, 6)))  # 2-6 year benefit period
            else:
                # Generic coverage for other policy types
                coverage_type = "Primary"
                name = f"{policy.policy_type} Coverage"
                description = f"Standard coverage for {policy.policy_type} policy"
                coverage_amount = policy.coverage_amount
                deductible = Decimal(str(round(random.uniform(0, 1000), 2)))
                coinsurance_percentage = random.randint(0, 20)
                out_of_pocket_max = Decimal(str(round(random.uniform(1000, 10000), 2))) if coinsurance_percentage > 0 else Decimal('0')
                annual_limit = Decimal('0')
                lifetime_limit = Decimal('0')
            
            # Create exclusions, waiting periods, etc. based on policy type
            exclusions = None
            waiting_period = None
            elimination_period = None
            benefit_period = None
            covered_perils = None
            riders = None
            
            if policy.policy_type == "Life":
                exclusions = json.dumps(["Suicide within first two years", "Misrepresentation on application"])
                waiting_period = 0
                elimination_period = 0
                benefit_period = "Lifetime" if policy.policy_subtype in ["Whole", "Universal"] else policy.term
            elif policy.policy_type == "Health":
                exclusions = json.dumps(["Cosmetic procedures", "Experimental treatments"])
                waiting_period = 0 if coverage_type == "Preventive" else random.randint(0, 90)
                elimination_period = 0
                benefit_period = "Annual"
            elif policy.policy_type == "Disability":
                exclusions = json.dumps(["Pre-existing conditions", "Self-inflicted injuries"])
                waiting_period = 0
                elimination_period = random.choice([30, 60, 90, 180])
                benefit_period = policy.term if isinstance(policy.term, str) else f"{policy.term} years"
            elif policy.policy_type == "Long-Term Care":
                exclusions = json.dumps(["Pre-existing conditions", "Self-inflicted injuries"])
                waiting_period = 0
                elimination_period = random.choice([30, 60, 90, 180])
                benefit_period = policy.term if isinstance(policy.term, str) else f"{policy.term} years"
            elif policy.policy_type == "Property":
                if policy.policy_subtype == "Homeowners":
                    exclusions = json.dumps(["Flood damage", "Earthquake damage", "Normal wear and tear"])
                    covered_perils = json.dumps(["Fire", "Wind", "Hail", "Lightning", "Theft"])
                elif policy.policy_subtype == "Auto":
                    exclusions = json.dumps(["Racing or competitive driving", "Commercial use without endorsement"])
                    covered_perils = json.dumps(["Collision", "Theft", "Vandalism", "Natural disasters"]) if coverage_type in ["Collision", "Comprehensive"] else None
                waiting_period = 0
                elimination_period = 0
                benefit_period = policy.term if isinstance(policy.term, str) else f"{policy.term} years"
            
            # Optional riders for some policies
            if policy.policy_type == "Life" and random.random() > 0.7:
                possible_riders = [
                    "Waiver of Premium",
                    "Accelerated Death Benefit",
                    "Accidental Death Benefit",
                    "Child Rider",
                    "Term Conversion"
                ]
                riders = json.dumps(random.sample(possible_riders, random.randint(1, 2)))
            elif policy.policy_type == "Disability" and random.random() > 0.7:
                possible_riders = [
                    "Cost of Living Adjustment",
                    "Future Increase Option",
                    "Residual Disability",
                    "Own Occupation",
                    "Return of Premium"
                ]
                riders = json.dumps(random.sample(possible_riders, random.randint(1, 2)))
            
            # Create coverage data
            coverage_data = {
                "id": f"coverage_{str(coverage_id).zfill(3)}",
                "workspace_id": policy.workspace_id,
                "policy_id": policy.id,
                "client_id": policy.client_id,
                "created_by": policy.created_by,
                "updated_by": policy.updated_by,
                "created_at": created_at,
                "updated_at": updated_at,
                "coverage_type": coverage_type,
                "name": name,
                "description": description,
                "coverage_amount": coverage_amount,
                "deductible": deductible,
                "coinsurance_percentage": coinsurance_percentage,
                "out_of_pocket_max": out_of_pocket_max,
                "annual_limit": annual_limit,
                "lifetime_limit": lifetime_limit,
                "exclusions": exclusions,
                "waiting_period": waiting_period,
                "elimination_period": elimination_period,
                "benefit_period": benefit_period,
                "covered_perils": covered_perils,
                "riders": riders,
                "notes": fake.paragraph() if random.random() > 0.7 else None
            }
            
            coverage = Coverage(**coverage_data)
            db.add(coverage)
            
            coverage_id += 1
            coverages_created += 1
    
    db.commit()
    print(f"Seeded {coverages_created} coverage details successfully!")

def safe_date_calculation(base_date, months_to_add, days_to_subtract=0):
    """Safely calculate a new date by adding months and subtracting days."""
    # Calculate target year and month
    year = base_date.year
    month = base_date.month + months_to_add
    
    # Adjust for year overflow
    while month > 12:
        year += 1
        month -= 12
    
    # Determine max days in the target month
    max_days = calendar.monthrange(year, month)[1]
    
    # Use the original day if it fits, otherwise use the last day of month
    day = min(base_date.day, max_days)
    
    # Create new date
    new_date = date(year, month, day)
    
    # Subtract days if needed
    if days_to_subtract > 0:
        new_date = new_date - timedelta(days=days_to_subtract)
        
    return new_date

def seed_premiums(db: Session, policies: list):
    """Create premium records for insurance policies."""
    print("Creating premium records...")
    
    premiums_created = 0
    premium_id = 1
    
    for policy in policies:
        # Skip some policies
        if random.random() > 0.8:
            continue
            
        # Only create premium records for active policies
        if policy.status != "Active":
            continue
            
        # Create timestamps with timezone info
        created_at = policy.created_at
        updated_at = policy.updated_at
        
        # Create premium records based on frequency
        frequency = policy.premium_frequency
        
        # Determine how many records to create
        if frequency == "Monthly":
            num_records = random.randint(1, 12)
        elif frequency == "Quarterly":
            num_records = random.randint(1, 4)
        elif frequency == "Semi-Annual":
            num_records = random.randint(1, 2)
        else:  # Annual
            num_records = 1
        
        # Create premium records
        for i in range(num_records):
            # Determine due date based on effective date and frequency - safely
            if frequency == "Monthly":
                due_date = safe_date_calculation(policy.effective_date, i)
            elif frequency == "Quarterly":
                due_date = safe_date_calculation(policy.effective_date, i * 3)
            elif frequency == "Semi-Annual":
                due_date = safe_date_calculation(policy.effective_date, i * 6)
            else:  # Annual
                due_date = policy.effective_date
                
            # Determine if premium has been paid
            is_paid = due_date <= date.today()
            paid_date = fake.date_between(start_date=due_date - timedelta(days=10), end_date=due_date + timedelta(days=5)) if is_paid else None
            
            # Determine billing period - safely
            if frequency == "Monthly":
                billing_start = due_date
                billing_end = safe_date_calculation(due_date, 1, 1)
            elif frequency == "Quarterly":
                billing_start = due_date
                billing_end = safe_date_calculation(due_date, 3, 1)
            elif frequency == "Semi-Annual":
                billing_start = due_date
                billing_end = safe_date_calculation(due_date, 6, 1)
            else:  # Annual
                billing_start = due_date
                billing_end = date(due_date.year + 1, due_date.month, due_date.day) - timedelta(days=1)
            
            # Create premium data
            premium_data = {
                "id": f"premium_{str(premium_id).zfill(3)}",
                "workspace_id": policy.workspace_id,
                "policy_id": policy.id,
                "client_id": policy.client_id,
                "created_by": policy.created_by,
                "updated_by": policy.updated_by,
                "created_at": created_at,
                "updated_at": updated_at,
                "premium_type": "Regular",
                "amount": policy.premium_amount,
                "frequency": policy.premium_frequency,
                "due_date": due_date,
                "paid_date": paid_date,
                "payment_method": policy.payment_method,
                "is_paid": is_paid,
                "billing_period_start": billing_start,
                "billing_period_end": billing_end,
                "notes": f"Premium payment {i+1} of {num_records} for the current term" if random.random() > 0.7 else None
            }
            
            premium = Premium(**premium_data)
            db.add(premium)
            
            premium_id += 1
            premiums_created += 1
    
    db.commit()
    print(f"Seeded {premiums_created} premium records successfully!")

# Main function to call when executing the script directly
if __name__ == "__main__":
    seed_insurance_data()