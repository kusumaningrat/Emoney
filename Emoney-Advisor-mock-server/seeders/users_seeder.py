# seeders/users_seeder.py
# Complete replacement file with fix for unique constraint

from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from faker import Faker
import random
import uuid
import json
import hashlib

from database import SessionLocal
from models.users import (
    User, Role, Permission, Firm, Logon, 
    Workspace, Advisor, user_roles
)

# Initialize Faker
fake = Faker()

# Main function to seed all users data
def seed_users_data(db: Session = None):
    """Main function to seed all users management data in correct order."""
    if db is None:
        db = SessionLocal()
    
    try:
        # Check if data already exists to avoid duplicates
        existing_firms = db.query(Firm).count()
        if existing_firms > 0:
            print("Some user management data already exists, checking what needs to be seeded...")
            
        # 1. Create workspaces if they don't exist
        workspaces = db.query(Workspace).all()
        if not workspaces:
            workspaces = seed_workspaces(db)
            db.commit()
        else:
            print(f"Found {len(workspaces)} existing workspaces, skipping workspace creation.")
            
        # 2. Create firms if they don't exist
        firms = db.query(Firm).all()
        if not firms:
            firms = seed_firms(db)
            db.commit()
        else:
            print(f"Found {len(firms)} existing firms, skipping firm creation.")
            
        # 3. Create roles with permissions if they don't exist
        roles = db.query(Role).all()
        if not roles:
            roles = seed_roles_and_permissions(db)
            db.commit()
        else:
            print(f"Found {len(roles)} existing roles, skipping role creation.")
            
        # 4. Create users if they don't exist
        users = db.query(User).all()
        if not users:
            users = seed_users(db, firms, roles, workspaces)
            db.commit()
        else:
            print(f"Found {len(users)} existing users, skipping user creation.")
            
        # 5. Create advisors if they don't exist
        advisors = db.query(Advisor).all()
        if not advisors:
            advisors = seed_advisors(db, users, firms, workspaces)
            db.commit()
        else:
            print(f"Found {len(advisors)} existing advisors, skipping advisor creation.")
            
        # 6. Create logons if they don't exist
        logons = db.query(Logon).all()
        if not logons:
            logons = seed_logons(db, users)
            db.commit()
        else:
            print(f"Found {len(logons)} existing logons, skipping logon creation.")
        
        print("users management seeding complete!")
        return True
        
    except Exception as e:
        print(f"Error seeding users management data: {e}")
        db.rollback()
        raise
    finally:
        if db is not None:
            db.close()

def generate_id(prefix: str) -> str:
    """Generate a unique ID with a prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def seed_workspaces(db: Session):
    """Create workspaces."""
    print("Creating workspaces...")
    
    workspace_data = [
        {
            "id": generate_id("workspace"),
            "name": "eMoney Advisor",
            "plan": "Enterprise",
            "status": "Active",
            "users_limit": 100,
            "storage_limit": 1000 * 1024 * 1024,  # 1000 MB
            "storage_used": 250 * 1024 * 1024,  # 250 MB
            "custom_domain": "app.emoneyadvisor.com",
            "features": json.dumps({
                "whitelabel": True,
                "api_access": True,
                "advanced_analytics": True,
                "multi_factor_auth": True
            }),
            "branding": json.dumps({
                "logo_url": "https://assets.emoneyadvisor.com/logo.png",
                "primary_color": "#00529B",
                "secondary_color": "#A7C7E7",
                "theme": "light"
            }),
            "subscription": json.dumps({
                "plan": "Enterprise",
                "billing_cycle": "Annual",
                "next_billing_date": "2026-01-01",
                "payment_method": "Invoice"
            }),
            "settings": json.dumps({
                "time_zone": "America/New_York",
                "date_format": "MM/DD/YYYY",
                "language": "en-US",
                "currency": "USD"
            }),
            "api_keys": json.dumps({
                "production": "api_key_" + uuid.uuid4().hex,
                "sandbox": "api_key_sandbox_" + uuid.uuid4().hex
            }),
            "security": json.dumps({
                "password_policy": {
                    "min_length": 12,
                    "require_special_char": True,
                    "require_number": True,
                    "require_uppercase": True,
                    "max_age_days": 90
                },
                "session_timeout_minutes": 30,
                "ip_restrictions": False,
                "mfa_required": True
            })
        }
    ]
    
    workspaces = []
    
    for workspace in workspace_data:
        workspace_obj = Workspace(**workspace)
        db.add(workspace_obj)
        workspaces.append(workspace_obj)
    
    db.commit()
    print(f"Created {len(workspaces)} workspaces!")
    return workspaces

def seed_firms(db: Session):
    """Create firms."""
    print("Creating firms...")
    
    # Number of firms to create
    num_firms = 3
    
    firms = []
    
    for _ in range(num_firms):
        firm_name = fake.company()
        firm_id = generate_id("firm")
        
        firm = Firm(
            id=firm_id,
            name=firm_name,
            address=fake.street_address(),
            city=fake.city(),
            state=fake.state_abbr(),
            postal_code=fake.zipcode(),
            country="United States",
            phone=fake.phone_number(),
            email=f"info@{firm_name.lower().replace(' ', '')}.com",
            website=f"https://www.{firm_name.lower().replace(' ', '')}.com",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(firm)
        firms.append(firm)
    
    db.commit()
    print(f"Created {len(firms)} firms!")
    return firms

def seed_roles_and_permissions(db: Session):
    """Create roles and permissions."""
    print("Creating roles and permissions...")
    
    # Define roles with permissions
    roles_data = [
        {
            "name": "Administrator",
            "description": "Full system access with all permissions",
            "permissions": [
                {"resource": "client", "action": "create"},
                {"resource": "client", "action": "read"},
                {"resource": "client", "action": "update"},
                {"resource": "client", "action": "delete"},
                {"resource": "account", "action": "create"},
                {"resource": "account", "action": "read"},
                {"resource": "account", "action": "update"},
                {"resource": "account", "action": "delete"},
                {"resource": "financial_plan", "action": "create"},
                {"resource": "financial_plan", "action": "read"},
                {"resource": "financial_plan", "action": "update"},
                {"resource": "financial_plan", "action": "delete"},
                {"resource": "user", "action": "create"},
                {"resource": "user", "action": "read"},
                {"resource": "user", "action": "update"},
                {"resource": "user", "action": "delete"},
                {"resource": "firm", "action": "read"},
                {"resource": "firm", "action": "update"},
                {"resource": "reporting", "action": "read"},
                {"resource": "reporting", "action": "create"},
                {"resource": "system", "action": "configure"}
            ]
        },
        {
            "name": "Advisor",
            "description": "Standard advisor role with client management",
            "permissions": [
                {"resource": "client", "action": "create"},
                {"resource": "client", "action": "read"},
                {"resource": "client", "action": "update"},
                {"resource": "account", "action": "create"},
                {"resource": "account", "action": "read"},
                {"resource": "account", "action": "update"},
                {"resource": "financial_plan", "action": "create"},
                {"resource": "financial_plan", "action": "read"},
                {"resource": "financial_plan", "action": "update"},
                {"resource": "reporting", "action": "read"},
                {"resource": "reporting", "action": "create"}
            ]
        },
        {
            "name": "Associate",
            "description": "Support role for advisors with limited permissions",
            "permissions": [
                {"resource": "client", "action": "read"},
                {"resource": "client", "action": "update"},
                {"resource": "account", "action": "read"},
                {"resource": "account", "action": "update"},
                {"resource": "financial_plan", "action": "read"},
                {"resource": "reporting", "action": "read"}
            ]
        },
        {
            "name": "Analyst",
            "description": "Financial analysis role",
            "permissions": [
                {"resource": "client", "action": "read"},
                {"resource": "account", "action": "read"},
                {"resource": "financial_plan", "action": "read"},
                {"resource": "financial_plan", "action": "update"},
                {"resource": "reporting", "action": "read"},
                {"resource": "reporting", "action": "create"}
            ]
        },
        {
            "name": "Client",
            "description": "Client portal access",
            "permissions": [
                {"resource": "client", "action": "read_own"},
                {"resource": "account", "action": "read_own"},
                {"resource": "financial_plan", "action": "read_own"},
                {"resource": "reporting", "action": "read_own"}
            ]
        },
        {
            "name": "Auditor",
            "description": "Read-only access for compliance and auditing",
            "permissions": [
                {"resource": "client", "action": "read"},
                {"resource": "account", "action": "read"},
                {"resource": "financial_plan", "action": "read"},
                {"resource": "user", "action": "read"},
                {"resource": "firm", "action": "read"},
                {"resource": "reporting", "action": "read"},
                {"resource": "system", "action": "audit"}
            ]
        }
    ]
    
    roles = []
    permission_count = 0
    
    for role_data in roles_data:
        role_id = generate_id("role")
        
        role = Role(
            id=role_id,
            name=role_data["name"],
            description=role_data["description"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(role)
        roles.append(role)
        
        # Create permissions for this role
        for perm_data in role_data["permissions"]:
            permission = Permission(
                id=generate_id("perm"),
                role_id=role_id,
                resource=perm_data["resource"],
                action=perm_data["action"],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(permission)
            permission_count += 1
    
    db.commit()
    print(f"Created {len(roles)} roles with {permission_count} permissions!")
    return roles

# In users_seeder.py, replace your existing seed_users function with this version:

def seed_users(db: Session, firms=None, roles=None, workspaces=None):
    """Create users with roles."""
    print("Creating users...")
    
    # If parameters are not provided, get them from previous seed functions or database
    if firms is None:
        # Check if we already have firms in the database
        firms = db.query(Firm).all()
        if not firms:
            # If not, create them
            firms = seed_firms(db)
            db.commit()
    
    if roles is None:
        # Check if we already have roles in the database
        roles = db.query(Role).all()
        if not roles:
            # If not, create them
            roles = seed_roles_and_permissions(db)
            db.commit()
    
    if workspaces is None:
        # Check if we already have workspaces in the database
        workspaces = db.query(Workspace).all()
        if not workspaces:
            # If not, create them
            workspaces = seed_workspaces(db)
            db.commit()
    
    # Make sure we have the data we need
    if not firms:
        raise ValueError("No firms available for creating users")
    if not roles:
        raise ValueError("No roles available for creating users")
    
    # Rest of your existing seed_users function unchanged...
    users = []
    
    # Map roles by name for easy lookup
    roles_by_name = {role.name: role for role in roles}
    
    # User count per firm
    num_users_per_firm = {
        0: 5,  # First firm gets 5 users
        1: 3,  # Second firm gets 3 users
        2: 2   # Third firm gets 2 users
    }
    
    for idx, firm in enumerate(firms):
        num_users = num_users_per_firm.get(idx, 3)  # Default to 3 users per firm
        
        for i in range(num_users):
            # Determine role based on position
            if i == 0:
                # First user is Administrator
                assigned_role = roles_by_name.get("Administrator")
            elif i == 1:
                # Second user is Advisor
                assigned_role = roles_by_name.get("Advisor")
            else:
                # Others get random roles except Client
                available_roles = [r for r in roles if r.name != "Client"]
                assigned_role = random.choice(available_roles)
            
            # Create user
            first_name = fake.first_name()
            last_name = fake.last_name()
            email = f"{first_name.lower()}.{last_name.lower()}@{firm.name.lower().replace(' ', '')}.com"
            username = f"{first_name.lower()}.{last_name.lower()}"
            
            user = User(
                id=generate_id("user"),
                firm_id=firm.id,
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                title=fake.job() if random.random() < 0.8 else None,
                phone=fake.phone_number() if random.random() < 0.8 else None,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(user)
            db.flush()  # Flush to get the ID
            
            # Assign role
            if assigned_role:
                # Create user-role association
                stmt = user_roles.insert().values(
                    user_id=user.id,
                    role_id=assigned_role.id
                )
                db.execute(stmt)
            
            users.append(user)
    
    # Create a few client users
    client_role = roles_by_name.get("Client")
    
    for _ in range(20):  # Create 20 client users
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.email()
        username = f"{first_name.lower()}.{last_name.lower()}"
        
        # Randomly assign to a firm
        firm = random.choice(firms)
        
        user = User(
            id=generate_id("user"),
            firm_id=firm.id,
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            title=None,
            phone=fake.phone_number() if random.random() < 0.6 else None,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(user)
        db.flush()  # Flush to get the ID
        
        # Assign client role
        if client_role:
            stmt = user_roles.insert().values(
                user_id=user.id,
                role_id=client_role.id
            )
            db.execute(stmt)
        
        users.append(user)
    
    db.commit()
    print(f"Created {len(users)} users!")
    return users

# The rest of the users_seeder.py file remains unchanged

def seed_advisors(db: Session, users: list, firms: list, workspaces: list):
    """Create advisor profiles for advisor users."""
    print("Creating advisor profiles...")
    
    # Check if advisors already exist
    existing_advisors_count = db.query(Advisor).count()
    if existing_advisors_count > 0:
        print(f"Found {existing_advisors_count} existing advisors, skipping advisor creation.")
        return db.query(Advisor).all()
    
    advisors = []
    
    # Filter users with Advisor role
    advisor_users = []
    for user in users:
        for role in user.roles:
            if role.name in ["Administrator", "Advisor", "Analyst"]:
                advisor_users.append(user)
                break
    
    # Create advisor profiles
    for user in advisor_users:
        # Check if advisor already exists for this user
        existing_advisor = db.query(Advisor).filter(Advisor.user_id == user.id).first()
        if existing_advisor:
            print(f"Advisor already exists for user {user.username}, skipping.")
            advisors.append(existing_advisor)
            continue
            
        # Select workspace
        workspace = workspaces[0] if workspaces else None
        
        # Define specialties
        specialties_options = [
            "Retirement Planning", 
            "Investment Management", 
            "Estate Planning", 
            "Tax Planning", 
            "Insurance Planning",
            "College Planning",
            "Small Business Planning",
            "Wealth Management",
            "Financial Planning"
        ]
        
        selected_specialties = random.sample(
            specialties_options, 
            k=random.randint(1, min(4, len(specialties_options)))
        )
        
        # Define credentials
        credentials_options = [
            "CFP", "CFA", "ChFC", "CLU", "RICP", "CPA", "EA", "MBA", "JD"
        ]
        
        selected_credentials = random.sample(
            credentials_options,
            k=random.randint(1, min(3, len(credentials_options)))
        )
        
        # Create advisor profile
        advisor = Advisor(
            id=generate_id("advisor"),
            user_id=user.id,
            workspace_id=workspace.id if workspace else None,
            firm_id=user.firm_id,
            title=user.title or "Financial Advisor",
            specialties=json.dumps(selected_specialties),
            credentials=json.dumps(selected_credentials),
            experience_years=random.randint(1, 30),
            client_count=random.randint(5, 100),
            aum=random.randint(1000000, 100000000),  # $1M to $100M
            service_model=random.choice(["Comprehensive", "Investment-only", "Subscription", "Hourly"]),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(advisor)
        advisors.append(advisor)
    
    db.commit()
    print(f"Created {len(advisors)} advisor profiles!")
    return advisors

def seed_logons(db: Session, users: list):
    """Create logons for users."""
    print("Creating logons...")
    
    # Check if logons already exist
    existing_logons_count = db.query(Logon).count()
    if existing_logons_count > 0:
        print(f"Found {existing_logons_count} existing logons, skipping logon creation.")
        return db.query(Logon).all()
    
    logons = []
    
    for user in users:
        # Check if logon already exists for this user
        existing_logon = db.query(Logon).filter(Logon.user_id == user.id).first()
        if existing_logon:
            print(f"Logon already exists for user {user.username}, skipping.")
            logons.append(existing_logon)
            continue
            
        # Create logon for each user
        logon = Logon(
            id=generate_id("logon"),
            user_id=user.id,
            client_id=None,  # Could be linked to clients later
            username=user.username,
            status="Active" if user.is_active else "Inactive",
            last_login=fake.date_time_between(start_date="-30d", end_date="now") if random.random() < 0.8 else None,
            created_at=user.created_at,
            updated_at=datetime.utcnow()
        )
        
        db.add(logon)
        logons.append(logon)
    
    db.commit()
    print(f"Created {len(logons)} logons!")
    return logons

if __name__ == "__main__":
    seed_users_data()