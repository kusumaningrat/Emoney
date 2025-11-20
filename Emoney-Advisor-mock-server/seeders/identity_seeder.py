# seeders/identity_seeder.py

from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random
from faker import Faker

from models.identity import (
    User, Office, Role, Permission, SharingRule, Logon,
    UserStatus, OfficeStatus, RoleStatus, SharingRuleStatus, LogonStatus, LogonType
)

fake = Faker()

class IdentitySeeder:
    def __init__(self, db: Session):
        self.db = db
        self.created_data = {
            "users": [],
            "offices": [],
            "roles": [],
            "permissions": [],
            "sharing_rules": [],
            "logons": []
        }
    
    def seed_all(self) -> Dict[str, List[Any]]:
        """Seed all V1 Identity & Access Management entities"""
        print("Starting V1 Identity seeding...")
        
        # Seed in dependency order
        self.seed_offices()
        self.seed_roles()
        self.seed_permissions()
        self.seed_users()
        self.seed_sharing_rules()
        self.seed_logons()
        
        self.db.commit()
        print("V1 Identity seeding completed!")
        
        return self.created_data
    
    def seed_offices(self):
        """Seed 15 offices with hierarchical structure"""
        print("Seeding offices...")
        
        # Root offices (no parent)
        root_offices = [
            {"office_id": "OFF-001", "office_name": "Headquarters", "city": "New York", "state": "NY"},
            {"office_id": "OFF-002", "office_name": "West Coast Division", "city": "San Francisco", "state": "CA"},
            {"office_id": "OFF-003", "office_name": "Midwest Division", "city": "Chicago", "state": "IL"},
        ]
        
        for office_data in root_offices:
            office = Office(
                office_id=office_data["office_id"],
                office_name=office_data["office_name"],
                parent_office_id=None,
                office_path=f"/{office_data['office_name']}",
                status=OfficeStatus.ACTIVE.value,
                address=fake.street_address(),
                city=office_data["city"],
                state=office_data["state"],
                zip_code=fake.zipcode(),
                phone=fake.phone_number(),
                created_date=datetime.utcnow(),
                modified_date=datetime.utcnow()
            )
            self.db.add(office)
            self.created_data["offices"].append(office)
        
        self.db.flush()
        
        # Child offices
        child_offices = [
            {"office_id": "OFF-004", "office_name": "Manhattan Branch", "parent_id": "OFF-001", "city": "New York", "state": "NY"},
            {"office_id": "OFF-005", "office_name": "Brooklyn Branch", "parent_id": "OFF-001", "city": "Brooklyn", "state": "NY"},
            {"office_id": "OFF-006", "office_name": "San Jose Office", "parent_id": "OFF-002", "city": "San Jose", "state": "CA"},
            {"office_id": "OFF-007", "office_name": "Los Angeles Office", "parent_id": "OFF-002", "city": "Los Angeles", "state": "CA"},
            {"office_id": "OFF-008", "office_name": "Seattle Office", "parent_id": "OFF-002", "city": "Seattle", "state": "WA"},
            {"office_id": "OFF-009", "office_name": "Milwaukee Branch", "parent_id": "OFF-003", "city": "Milwaukee", "state": "WI"},
            {"office_id": "OFF-010", "office_name": "Detroit Branch", "parent_id": "OFF-003", "city": "Detroit", "state": "MI"},
            {"office_id": "OFF-011", "office_name": "South Region", "parent_id": None, "city": "Atlanta", "state": "GA"},
            {"office_id": "OFF-012", "office_name": "Miami Office", "parent_id": "OFF-011", "city": "Miami", "state": "FL"},
            {"office_id": "OFF-013", "office_name": "Dallas Office", "parent_id": "OFF-011", "city": "Dallas", "state": "TX"},
            {"office_id": "OFF-014", "office_name": "Houston Office", "parent_id": "OFF-011", "city": "Houston", "state": "TX"},
            {"office_id": "OFF-015", "office_name": "Boston Office", "parent_id": "OFF-001", "city": "Boston", "state": "MA"},
        ]
        
        for office_data in child_offices:
            parent = next((o for o in self.created_data["offices"] if o.office_id == office_data["parent_id"]), None) if office_data["parent_id"] else None
            office_path = f"{parent.office_path}/{office_data['office_name']}" if parent else f"/{office_data['office_name']}"
            
            office = Office(
                office_id=office_data["office_id"],
                office_name=office_data["office_name"],
                parent_office_id=office_data["parent_id"],
                office_path=office_path,
                status=OfficeStatus.ACTIVE.value,
                address=fake.street_address(),
                city=office_data["city"],
                state=office_data["state"],
                zip_code=fake.zipcode(),
                phone=fake.phone_number(),
                created_date=datetime.utcnow(),
                modified_date=datetime.utcnow()
            )
            self.db.add(office)
            self.created_data["offices"].append(office)
        
        print(f"✓ Seeded {len(self.created_data['offices'])} offices")
    
    def seed_roles(self):
        """Seed 10 roles"""
        print("Seeding roles...")
        
        roles_data = [
            {"role_id": "ROLE-001", "role_name": "Administrator", "role_type": "System", "description": "Full system access"},
            {"role_id": "ROLE-002", "role_name": "Senior Advisor", "role_type": "Advisor", "description": "Senior financial advisor"},
            {"role_id": "ROLE-003", "role_name": "Financial Advisor", "role_type": "Advisor", "description": "Standard financial advisor"},
            {"role_id": "ROLE-004", "role_name": "Junior Advisor", "role_type": "Advisor", "description": "Entry-level advisor"},
            {"role_id": "ROLE-005", "role_name": "Financial Planner", "role_type": "Planner", "description": "Financial planning specialist"},
            {"role_id": "ROLE-006", "role_name": "Compliance Officer", "role_type": "Compliance", "description": "Compliance and regulatory oversight"},
            {"role_id": "ROLE-007", "role_name": "Operations Manager", "role_type": "Operations", "description": "Operations management"},
            {"role_id": "ROLE-008", "role_name": "Client Service Rep", "role_type": "Support", "description": "Client support services"},
            {"role_id": "ROLE-009", "role_name": "Investment Specialist", "role_type": "Investment", "description": "Investment management"},
            {"role_id": "ROLE-010", "role_name": "Portfolio Manager", "role_type": "Investment", "description": "Portfolio management"},
        ]
        
        for role_data in roles_data:
            role = Role(
                role_id=role_data["role_id"],
                role_name=role_data["role_name"],
                description=role_data["description"],
                role_type=role_data["role_type"],
                status=RoleStatus.ACTIVE.value,
                created_date=datetime.utcnow(),
                modified_date=datetime.utcnow()
            )
            self.db.add(role)
            self.created_data["roles"].append(role)
        
        print(f"✓ Seeded {len(self.created_data['roles'])} roles")
    
    def seed_permissions(self):
        """Seed 50 permissions"""
        print("Seeding permissions...")
        
        categories = ["Client", "Account", "Planning", "Reporting", "Admin", "Document"]
        actions = ["View", "Create", "Edit", "Delete", "Export"]
        resources = ["Client", "Account", "Plan", "Goal", "Portfolio", "Document", "User", "Report", "Transaction", "Task"]
        
        permission_id = 1
        for category in categories:
            for resource in resources[:5]:  # Limit combinations
                for action in actions[:3]:  # Limit actions
                    if permission_id > 50:
                        break
                    
                    permission = Permission(
                        permission_id=f"PERM-{permission_id:03d}",
                        permission_name=f"{action} {resource}",
                        permission_code=f"{category.upper()}_{resource.upper()}_{action.upper()}",
                        category=category,
                        description=f"Permission to {action.lower()} {resource.lower()}",
                        status="Active",
                        created_date=datetime.utcnow()
                    )
                    self.db.add(permission)
                    self.created_data["permissions"].append(permission)
                    permission_id += 1
        
        self.db.flush()
        
        # Assign permissions to roles (many-to-many)
        for role in self.created_data["roles"]:
            # Admins get all permissions
            if "Administrator" in role.role_name:
                role.permissions = self.created_data["permissions"]
            # Other roles get subset of permissions
            else:
                num_permissions = random.randint(10, 25)
                role.permissions = random.sample(self.created_data["permissions"], num_permissions)
        
        print(f"✓ Seeded {len(self.created_data['permissions'])} permissions")
    
    def seed_users(self):
        """Seed 60 users"""
        print("Seeding users...")
        
        offices = self.created_data["offices"]
        roles = self.created_data["roles"]
        
        for i in range(1, 61):
            first_name = fake.first_name()
            last_name = fake.last_name()
            username = f"{first_name.lower()}.{last_name.lower()}{i}"
            
            user = User(
                user_id=f"USR-{i:03d}",
                username=username,
                email=f"{username}@emoneyadvisor.com",
                first_name=first_name,
                last_name=last_name,
                status=random.choice([UserStatus.ACTIVE.value] * 9 + [UserStatus.INACTIVE.value]),
                office_id=random.choice(offices).office_id,
                created_date=datetime.utcnow() - timedelta(days=random.randint(30, 730)),
                last_login_date=datetime.utcnow() - timedelta(days=random.randint(0, 30)) if random.random() > 0.2 else None,
                modified_date=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            # Assign 1-3 roles to each user
            num_roles = random.randint(1, 3)
            user.roles = random.sample(roles, num_roles)
            
            self.db.add(user)
            self.created_data["users"].append(user)
        
        print(f"✓ Seeded {len(self.created_data['users'])} users")
    
    def seed_sharing_rules(self):
        """Seed 80 sharing rules"""
        print("Seeding sharing rules...")
        
        users = self.created_data["users"]
        
        for i in range(1, 81):
            user = random.choice(users)
            created_by = random.choice(users)
            
            # Generate random client IDs (these will be linked when V2 is implemented)
            client_id = f"C{random.randint(10000, 99999)}"
            
            start_date = datetime.utcnow() - timedelta(days=random.randint(0, 365))
            has_end_date = random.random() < 0.3
            end_date = start_date + timedelta(days=random.randint(30, 365)) if has_end_date else None
            
            # Determine status based on dates
            if end_date and end_date < datetime.utcnow():
                status = SharingRuleStatus.EXPIRED.value
            else:
                status = random.choice([SharingRuleStatus.ACTIVE.value] * 8 + [SharingRuleStatus.INACTIVE.value])
            
            access_levels = ["Full", "ReadOnly", "Limited", "Temporary"]
            access_level = random.choice(access_levels)
            
            sharing_rule = SharingRule(
                sharing_rule_id=f"SR-{i:03d}",
                user_id=user.user_id,
                client_id=client_id,
                access_level=access_level,
                can_view=True,
                can_edit=access_level in ["Full", "Limited"],
                can_delete=access_level == "Full",
                start_date=start_date,
                end_date=end_date,
                status=status,
                created_date=start_date,
                created_by=created_by.user_id,
                modified_date=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            self.db.add(sharing_rule)
            self.created_data["sharing_rules"].append(sharing_rule)
        
        print(f"✓ Seeded {len(self.created_data['sharing_rules'])} sharing rules")
    
    def seed_logons(self):
        """Seed 100 logon records"""
        print("Seeding logons...")
        
        users = self.created_data["users"]
        
        for i in range(1, 101):
            user = random.choice(users)
            
            logon_datetime = datetime.utcnow() - timedelta(
                days=random.randint(0, 90),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            
            # 70% of sessions are logged out
            is_logged_out = random.random() < 0.7
            logout_datetime = logon_datetime + timedelta(
                hours=random.randint(0, 8),
                minutes=random.randint(0, 59)
            ) if is_logged_out else None
            
            duration = int((logout_datetime - logon_datetime).total_seconds() / 60) if logout_datetime else None
            
            status = LogonStatus.LOGGED_OUT.value if is_logged_out else LogonStatus.ACTIVE.value
            
            logon = Logon(
                logon_id=f"LOG-{i:04d}",
                user_id=user.user_id,
                logon_type=random.choice([LogonType.USER.value] * 9 + [LogonType.PORTAL.value]),
                logon_date_time=logon_datetime,
                logout_date_time=logout_datetime,
                ip_address=fake.ipv4(),
                user_agent=fake.user_agent(),
                session_id=fake.uuid4(),
                status=status,
                duration=duration
            )
            self.db.add(logon)
            self.created_data["logons"].append(logon)
        
        print(f"✓ Seeded {len(self.created_data['logons'])} logon records")