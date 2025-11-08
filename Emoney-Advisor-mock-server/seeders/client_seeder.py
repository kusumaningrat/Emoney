from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import json
from datetime import datetime, timezone, timedelta, date
from faker import Faker
import random
import uuid

from database import SessionLocal
from models.clients import Client, Spouse, Household, HouseholdMember, Contact, Relationship
from models.users import User, Firm
from seeders.users_seeder import seed_firms, seed_users

# Initialize Faker
fake = Faker()

# Main function to seed all client data
def seed_clients():
    """Main function to seed all client data in correct order."""
    db = SessionLocal()
    try:
        # Check if data already exists to avoid duplicates
        existing_clients = db.query(Client).count()
        if existing_clients > 0:
            print("Client data already seeded, skipping...")
            return

        # Ensure firms and users exist
        firms = db.query(Firm).all()
        if not firms:
            print("No firms found, seeding firms first...")
            seed_firms(db)
            firms = db.query(Firm).all()
            
        users = db.query(User).all()
        if not users:
            print("No users found, seeding users first...")
            seed_users(db)
            users = db.query(User).all()
            
        # 1. Create clients first
        clients_data = seed_client_records(db, firms, users)
        db.commit()
        
        # 2. Create spouses for married clients
        spouse_data = seed_spouse_records(db, clients_data['clients'])
        db.commit()
        
        # 3. Create households for some clients
        household_data = seed_household_records(db, clients_data['clients'], users)
        db.commit()
        
        # 4. Create household members
        members_data = seed_household_members(db, household_data['households'], clients_data['clients'])
        db.commit()
        
        # 5. Create contact information for clients
        contact_data = seed_contact_records(db, clients_data['clients'])
        db.commit()
        
        # 6. Create relationship records between clients
        relationship_data = seed_relationship_records(db, clients_data['clients'])
        db.commit()
        
        print(f"Client management seeding complete!")
        print(f"Created: {len(clients_data['clients'])} clients, {len(spouse_data['spouses'])} spouses, "
              f"{len(household_data['households'])} households, {len(members_data['members'])} household members, "
              f"{len(contact_data['contacts'])} contacts, {len(relationship_data['relationships'])} relationships")
        
    except Exception as e:
        print(f"Error seeding client data: {e}")
        db.rollback()
        raise
    finally:
        db.close()

def generate_id(prefix: str) -> str:
    """Generate a unique ID with a prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def seed_client_records(db: Session, firms: list, users: list) -> dict:
    """Seed client data."""
    print("Seeding client data...")
    
    clients = []
    num_clients = random.randint(30, 50)  # Adjust as needed
    
    for i in range(num_clients):
        # Select a random firm and advisor
        firm = random.choice(firms)
        firm_users = [user for user in users if user.firm_id == firm.id]
        advisor = random.choice(firm_users) if firm_users else random.choice(users)
        
        # Generate client data
        marital_status = random.choice(["Single", "Married", "Divorced", "Widowed", "Separated"])
        previous_marriages = random.choice([True, False]) if marital_status in ["Divorced", "Widowed", "Married"] else False
        
        birth_year = random.randint(1950, 2000)
        birth_month = random.randint(1, 12)
        birth_day = random.randint(1, 28)  # Avoiding edge cases with month lengths
        dob = date(birth_year, birth_month, birth_day)
        
        # Create timestamps
        created_at = fake.date_time_between(start_date="-2y", end_date="-3m")
        updated_at = fake.date_time_between(start_date="-3m", end_date="now")
        
        client = Client(
            id=generate_id("client"),
            firm_id=firm.id,
            first_name=fake.first_name(),
            last_name=fake.last_name(),
            email=fake.email(),
            phone=fake.phone_number(),
            marital_status=marital_status,
            previous_marriages=previous_marriages,
            date_of_birth=dob,
            owning_advisor=advisor.id,
            external_id=f"CRM-{fake.random_number(digits=6)}",
            created_by=advisor.id,
            updated_by=advisor.id,
            created_at=created_at,
            updated_at=updated_at
        )
        
        clients.append(client)
        db.add(client)
    
    return {"clients": clients}

def seed_spouse_records(db: Session, clients: list) -> dict:
    """Create spouses for married clients."""
    print("Creating spouses for married clients...")
    
    spouses = []
    
    for client in clients:
        if client.marital_status == "Married":
            # Generate spouse data
            spouse_dob = fake.date_of_birth(minimum_age=25, maximum_age=80)
            
            spouse = Spouse(
                id=generate_id("spouse"),
                client_id=client.id,
                first_name=fake.first_name(),
                last_name=client.last_name,  # Assuming same last name
                email=fake.email(),
                phone=fake.phone_number(),
                date_of_birth=spouse_dob,
                previous_marriages=random.choice([True, False]),
                created_by=client.created_by,
                updated_by=client.updated_by,
                created_at=client.created_at,
                updated_at=client.updated_at
            )
            
            spouses.append(spouse)
            db.add(spouse)
    
    return {"spouses": spouses}

def seed_household_records(db: Session, clients: list, users: list) -> dict:
    """Create households for clients."""
    print("Creating household records...")
    
    households = []
    
    # Create households for about 80% of clients
    selected_clients = random.sample(clients, int(len(clients) * 0.8))
    
    for client in selected_clients:
        # Get an advisor (either the client's advisor or another one)
        advisor = db.query(User).filter(User.id == client.owning_advisor).first()
        if not advisor:
            advisor = random.choice(users)
        
        # Create household
        household = Household(
            id=generate_id("household"),
            name=f"{client.last_name} Household",
            primary_client_id=client.id,
            created_by=client.created_by,
            updated_by=client.updated_by,
            assigned_to=advisor.id,
            status="Active",
            address={
                "street": fake.street_address(),
                "city": fake.city(),
                "state": fake.state_abbr(),
                "zip": fake.zipcode(),
                "country": "United States"
            },
            total_aum=random.uniform(100000, 5000000),
            annual_revenue=random.uniform(1000, 50000),
            client_since=fake.date_between(start_date="-10y", end_date="-1y"),
            servicing_model=random.choice(["Comprehensive", "Investment-only", "Planning-only"]),
            review_frequency=random.choice(["Annual", "Semi-annual", "Quarterly"]),
            next_review_date=fake.date_between(start_date="now", end_date="+1y"),
            primary_advisor=advisor.id,
            secondary_advisor=random.choice(users).id if random.random() < 0.5 else None,
            service_team=[random.choice(users).id for _ in range(random.randint(0, 2))],
            accounts=[generate_id("account") for _ in range(random.randint(1, 5))],
            goals=[generate_id("goal") for _ in range(random.randint(1, 3))],
            financial_plan=generate_id("plan") if random.random() < 0.7 else None,
            notes=fake.paragraph() if random.random() < 0.5 else None,
            tags=random.sample(["VIP", "High Net Worth", "Retiree", "Business Owner", "Professional", "Family"], 
                             random.randint(0, 3)),
            created_at=client.created_at,
            updated_at=client.updated_at
        )
        
        households.append(household)
        db.add(household)
    
    return {"households": households}

def seed_household_members(db: Session, households: list, clients: list) -> dict:
    """Create household members for households."""
    print("Creating household members...")
    
    members = []
    
    for household in households:
        # Get primary client
        primary_client = db.query(Client).filter(Client.id == household.primary_client_id).first()
        if not primary_client:
            continue
        
        # Add 1-4 additional members (children, parents, etc.)
        num_members = random.randint(1, 4)
        
        for i in range(num_members):
            relationship = random.choice(["Child", "Parent", "Other"])
            
            # Generate age-appropriate DOB based on relationship
            if relationship == "Child":
                dob = fake.date_between(start_date="-30y", end_date="-1y")
            elif relationship == "Parent":
                dob = fake.date_between(start_date="-90y", end_date="-50y")
            else:
                dob = fake.date_of_birth(minimum_age=18, maximum_age=90)
            
            # Sometimes use an existing client as a member (20% chance)
            client_id = None
            first_name = fake.first_name()
            last_name = primary_client.last_name if relationship == "Child" else fake.last_name()
            
            if random.random() < 0.2 and clients:
                other_client = random.choice(clients)
                if other_client.id != primary_client.id:
                    client_id = other_client.id
                    first_name = other_client.first_name
                    last_name = other_client.last_name
            
            member = HouseholdMember(
                id=generate_id("member"),
                household_id=household.id,
                client_id=client_id,
                first_name=first_name,
                last_name=last_name,
                relationship=relationship,
                date_of_birth=dob,
                created_by=household.created_by,
                updated_by=household.updated_by,
                created_at=household.created_at,
                updated_at=household.updated_at
            )
            
            members.append(member)
            db.add(member)
    
    return {"members": members}

def seed_contact_records(db: Session, clients: list) -> dict:
    """Create contact records for clients."""
    print("Creating contact information for clients...")
    
    contacts = []
    
    for client in clients:
        # Create primary contact
        primary_contact = Contact(
            id=generate_id("contact"),
            client_id=client.id,
            type="Primary",
            address_line1=fake.street_address(),
            address_line2=fake.secondary_address() if random.random() < 0.3 else None,
            city=fake.city(),
            state=fake.state_abbr(),
            postal_code=fake.zipcode(),
            country="United States",
            email=client.email,
            phone=client.phone,
            is_preferred=True,
            created_by=client.created_by,
            updated_by=client.updated_by,
            created_at=client.created_at,
            updated_at=client.updated_at
        )
        
        contacts.append(primary_contact)
        db.add(primary_contact)
        
        # Create work contact (50% chance)
        if random.random() < 0.5:
            work_contact = Contact(
                id=generate_id("contact"),
                client_id=client.id,
                type="Work",
                address_line1=fake.street_address(),
                address_line2=fake.secondary_address() if random.random() < 0.5 else None,
                city=fake.city(),
                state=fake.state_abbr(),
                postal_code=fake.zipcode(),
                country="United States",
                email=fake.company_email(),
                phone=fake.phone_number(),
                is_preferred=False,
                created_by=client.created_by,
                updated_by=client.updated_by,
                created_at=client.created_at,
                updated_at=client.updated_at
            )
            
            contacts.append(work_contact)
            db.add(work_contact)
    
    return {"contacts": contacts}

def seed_relationship_records(db: Session, clients: list) -> dict:
    """Create relationship records between clients."""
    print("Creating client relationships...")
    
    relationships = []
    
    # Create relationships for about 30% of clients
    selected_clients = random.sample(clients, int(len(clients) * 0.3))
    
    for client in selected_clients:
        # Find 1-3 other clients to create relationships with
        other_clients = [c for c in clients if c.id != client.id]
        num_relationships = min(len(other_clients), random.randint(1, 3))
        related_clients = random.sample(other_clients, num_relationships)
        
        for related_client in related_clients:
            relationship_type = random.choice(["Family", "Professional", "Business"])
            
            # Generate relationship data
            start_date = fake.date_between(start_date="-5y", end_date="now")
            end_date = None
            if random.random() < 0.2:  # 20% chance of inactive relationship
                end_date = fake.date_between(start_date=start_date, end_date="now")
                is_active = False
            else:
                is_active = True
            
            relationship = Relationship(
                id=generate_id("rel"),
                client_id=client.id,
                related_client_id=related_client.id,
                relationship_type=relationship_type,
                description=fake.sentence() if random.random() < 0.7 else None,
                notes=fake.paragraph() if random.random() < 0.5 else None,
                start_date=start_date,
                end_date=end_date,
                is_active=is_active,
                created_by=client.created_by,
                updated_by=client.updated_by,
                created_at=client.created_at,
                updated_at=client.updated_at
            )
            
            relationships.append(relationship)
            db.add(relationship)
    
    return {"relationships": relationships}

# Main function to call when executing the script directly
if __name__ == "__main__":
    seed_clients()