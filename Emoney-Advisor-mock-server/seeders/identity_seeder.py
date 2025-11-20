# seeders/identity_seeder.py - FIXED for PascalCase field names

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
            {"OfficeID": "OFF-001", "OfficeName": "Headquarters", "City": "New York", "State": "NY"},
            {"OfficeID": "OFF-002", "OfficeName": "West Coast Division", "City": "San Francisco", "State": "CA"},
            {"OfficeID": "OFF-003", "OfficeName": "Midwest Division", "City": "Chicago", "State": "IL"},
        ]
        
        for office_data in root_offices:
            office = Office(
                OfficeID=office_data["OfficeID"],
                OfficeName=office_data["OfficeName"],
                ParentOfficeID=None,
                OfficePath=f"/{office_data['OfficeName']}",
                Status=OfficeStatus.ACTIVE.value,
                Address=fake.street_address(),
                City=office_data["City"],
                State=office_data["State"],
                ZipCode=fake.zipcode(),
                Phone=fake.phone_number(),
                CreatedDate=datetime.utcnow(),
                ModifiedDate=datetime.utcnow()
            )
            self.db.add(office)
            self.created_data["offices"].append(office)
        
        self.db.flush()
        
        # Child offices
        child_offices = [
            {"OfficeID": "OFF-004", "OfficeName": "Manhattan Branch", "ParentOfficeID": "OFF-001", "City": "New York", "State": "NY"},
            {"OfficeID": "OFF-005", "OfficeName": "Brooklyn Branch", "ParentOfficeID": "OFF-001", "City": "Brooklyn", "State": "NY"},
            {"OfficeID": "OFF-006", "OfficeName": "San Jose Office", "ParentOfficeID": "OFF-002", "City": "San Jose", "State": "CA"},
            {"OfficeID": "OFF-007", "OfficeName": "Los Angeles Office", "ParentOfficeID": "OFF-002", "City": "Los Angeles", "State": "CA"},
            {"OfficeID": "OFF-008", "OfficeName": "Seattle Office", "ParentOfficeID": "OFF-002", "City": "Seattle", "State": "WA"},
            {"OfficeID": "OFF-009", "OfficeName": "Milwaukee Branch", "ParentOfficeID": "OFF-003", "City": "Milwaukee", "State": "WI"},
            {"OfficeID": "OFF-010", "OfficeName": "Detroit Branch", "ParentOfficeID": "OFF-003", "City": "Detroit", "State": "MI"},
            {"OfficeID": "OFF-011", "OfficeName": "South Region", "ParentOfficeID": None, "City": "Atlanta", "State": "GA"},
            {"OfficeID": "OFF-012", "OfficeName": "Miami Office", "ParentOfficeID": "OFF-011", "City": "Miami", "State": "FL"},
            {"OfficeID": "OFF-013", "OfficeName": "Dallas Office", "ParentOfficeID": "OFF-011", "City": "Dallas", "State": "TX"},
            {"OfficeID": "OFF-014", "OfficeName": "Houston Office", "ParentOfficeID": "OFF-011", "City": "Houston", "State": "TX"},
            {"OfficeID": "OFF-015", "OfficeName": "Boston Office", "ParentOfficeID": "OFF-001", "City": "Boston", "State": "MA"},
        ]
        
        for office_data in child_offices:
            parent = next((o for o in self.created_data["offices"] if o.OfficeID == office_data["ParentOfficeID"]), None) if office_data["ParentOfficeID"] else None
            office_path = f"{parent.OfficePath}/{office_data['OfficeName']}" if parent else f"/{office_data['OfficeName']}"
            
            office = Office(
                OfficeID=office_data["OfficeID"],
                OfficeName=office_data["OfficeName"],
                ParentOfficeID=office_data["ParentOfficeID"],
                OfficePath=office_path,
                Status=OfficeStatus.ACTIVE.value,
                Address=fake.street_address(),
                City=office_data["City"],
                State=office_data["State"],
                ZipCode=fake.zipcode(),
                Phone=fake.phone_number(),
                CreatedDate=datetime.utcnow(),
                ModifiedDate=datetime.utcnow()
            )
            self.db.add(office)
            self.created_data["offices"].append(office)
        
        print(f"✓ Seeded {len(self.created_data['offices'])} offices")
    
    def seed_roles(self):
        """Seed 10 roles"""
        print("Seeding roles...")
        
        roles_data = [
            {"RoleID": "ROLE-001", "RoleName": "Administrator", "RoleType": "System", "Description": "Full system access"},
            {"RoleID": "ROLE-002", "RoleName": "Senior Advisor", "RoleType": "Advisor", "Description": "Senior financial advisor"},
            {"RoleID": "ROLE-003", "RoleName": "Financial Advisor", "RoleType": "Advisor", "Description": "Standard financial advisor"},
            {"RoleID": "ROLE-004", "RoleName": "Junior Advisor", "RoleType": "Advisor", "Description": "Entry-level advisor"},
            {"RoleID": "ROLE-005", "RoleName": "Financial Planner", "RoleType": "Planner", "Description": "Financial planning specialist"},
            {"RoleID": "ROLE-006", "RoleName": "Compliance Officer", "RoleType": "Compliance", "Description": "Compliance and regulatory oversight"},
            {"RoleID": "ROLE-007", "RoleName": "Operations Manager", "RoleType": "Operations", "Description": "Operations management"},
            {"RoleID": "ROLE-008", "RoleName": "Client Service Rep", "RoleType": "Support", "Description": "Client support services"},
            {"RoleID": "ROLE-009", "RoleName": "Investment Specialist", "RoleType": "Investment", "Description": "Investment management"},
            {"RoleID": "ROLE-010", "RoleName": "Portfolio Manager", "RoleType": "Investment", "Description": "Portfolio management"},
        ]
        
        for role_data in roles_data:
            role = Role(
                RoleID=role_data["RoleID"],
                RoleName=role_data["RoleName"],
                Description=role_data["Description"],
                RoleType=role_data["RoleType"],
                Status=RoleStatus.ACTIVE.value,
                CreatedDate=datetime.utcnow(),
                ModifiedDate=datetime.utcnow()
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
                        PermissionID=f"PERM-{permission_id:03d}",
                        PermissionName=f"{action} {resource}",
                        PermissionCode=f"{category.upper()}_{resource.upper()}_{action.upper()}",
                        Category=category,
                        Description=f"Permission to {action.lower()} {resource.lower()}",
                        Status="Active",
                        CreatedDate=datetime.utcnow()
                    )
                    self.db.add(permission)
                    self.created_data["permissions"].append(permission)
                    permission_id += 1
        
        self.db.flush()
        
        # Assign permissions to roles (many-to-many)
        for role in self.created_data["roles"]:
            # Admins get all permissions
            if "Administrator" in role.RoleName:
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
                UserID=f"USR-{i:03d}",
                Username=username,
                Email=f"{username}@emoneyadvisor.com",
                FirstName=first_name,
                LastName=last_name,
                Status=random.choice([UserStatus.ACTIVE.value] * 9 + [UserStatus.INACTIVE.value]),
                OfficeID=random.choice(offices).OfficeID,
                CreatedDate=datetime.utcnow() - timedelta(days=random.randint(30, 730)),
                LastLoginDate=datetime.utcnow() - timedelta(days=random.randint(0, 30)) if random.random() > 0.2 else None,
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
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
                SharingRuleID=f"SR-{i:03d}",
                UserID=user.UserID,
                ClientID=client_id,
                AccessLevel=access_level,
                CanView=True,
                CanEdit=access_level in ["Full", "Limited"],
                CanDelete=access_level == "Full",
                StartDate=start_date,
                EndDate=end_date,
                Status=status,
                CreatedDate=start_date,
                CreatedBy=created_by.UserID,
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
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
                LogonID=f"LOG-{i:04d}",
                UserID=user.UserID,
                LogonType=random.choice([LogonType.USER.value] * 9 + [LogonType.PORTAL.value]),
                LogonDateTime=logon_datetime,
                LogoutDateTime=logout_datetime,
                IPAddress=fake.ipv4(),
                UserAgent=fake.user_agent(),
                SessionID=fake.uuid4(),
                Status=status,
                Duration=duration
            )
            self.db.add(logon)
            self.created_data["logons"].append(logon)
        
        print(f"✓ Seeded {len(self.created_data['logons'])} logon records")