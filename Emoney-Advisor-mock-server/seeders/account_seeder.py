# seeders/account_seeder.py - FIXED for PascalCase field names

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Dict, List, Any
from decimal import Decimal
import random
from faker import Faker

from models.account import Account, AccountType
from models.account import AccountStatus, AccountCategory, OwnerType

fake = Faker()

class AccountSeeder:
    def __init__(self, db: Session):
        self.db = db
        self.created_data = {
            "account_types": [],
            "accounts": []
        }
    
    def seed_all(self) -> Dict[str, List[Any]]:
        """Seed all V4 Account Management entities"""
        print("Starting V4 Account Management seeding...")
        
        # Seed in dependency order
        self.seed_account_types()
        self.seed_accounts()
        
        self.db.commit()
        print("V4 Account Management seeding completed!")
        
        return self.created_data
    
    def seed_account_types(self):
        """Seed 15 account types"""
        print("Seeding account types...")
        
        account_types_data = [
            {
                "AccountTypeID": "AT-001",
                "TypeName": "401(k)",
                "Category": AccountCategory.RETIREMENT.value,
                "Description": "Employer-sponsored retirement plan",
                "IsTaxDeferred": True,
                "IsTaxable": False
            },
            {
                "AccountTypeID": "AT-002", 
                "TypeName": "Traditional IRA",
                "Category": AccountCategory.RETIREMENT.value,
                "Description": "Traditional Individual Retirement Account",
                "IsTaxDeferred": True,
                "IsTaxable": False
            },
            {
                "AccountTypeID": "AT-003",
                "TypeName": "Roth IRA", 
                "Category": AccountCategory.RETIREMENT.value,
                "Description": "Roth Individual Retirement Account",
                "IsTaxDeferred": False,
                "IsTaxable": False
            },
            {
                "AccountTypeID": "AT-004",
                "TypeName": "Taxable Brokerage",
                "Category": AccountCategory.INVESTMENT.value,
                "Description": "Taxable investment account",
                "IsTaxDeferred": False,
                "IsTaxable": True
            },
            {
                "AccountTypeID": "AT-005",
                "TypeName": "529 Education",
                "Category": AccountCategory.OTHER.value,
                "Description": "529 Education Savings Plan",
                "IsTaxDeferred": False,
                "IsTaxable": False
            },
            {
                "AccountTypeID": "AT-006",
                "TypeName": "HSA",
                "Category": AccountCategory.OTHER.value,
                "Description": "Health Savings Account",
                "IsTaxDeferred": True,
                "IsTaxable": False
            },
            {
                "AccountTypeID": "AT-007",
                "TypeName": "SEP-IRA",
                "Category": AccountCategory.RETIREMENT.value,
                "Description": "Simplified Employee Pension IRA",
                "IsTaxDeferred": True,
                "IsTaxable": False
            },
            {
                "AccountTypeID": "AT-008",
                "TypeName": "Simple IRA",
                "Category": AccountCategory.RETIREMENT.value,
                "Description": "Simple Individual Retirement Account",
                "IsTaxDeferred": True,
                "IsTaxable": False
            },
            {
                "AccountTypeID": "AT-009",
                "TypeName": "403(b)",
                "Category": AccountCategory.RETIREMENT.value,
                "Description": "Tax-sheltered annuity plan",
                "IsTaxDeferred": True,
                "IsTaxable": False
            },
            {
                "AccountTypeID": "AT-010",
                "TypeName": "Pension",
                "Category": AccountCategory.RETIREMENT.value,
                "Description": "Defined benefit pension plan",
                "IsTaxDeferred": True,
                "IsTaxable": False
            },
            {
                "AccountTypeID": "AT-011",
                "TypeName": "Trust Account",
                "Category": AccountCategory.TRUST.value,
                "Description": "Trust investment account",
                "IsTaxDeferred": False,
                "IsTaxable": True
            },
            {
                "AccountTypeID": "AT-012",
                "TypeName": "Joint Taxable",
                "Category": AccountCategory.INVESTMENT.value,
                "Description": "Joint taxable investment account",
                "IsTaxDeferred": False,
                "IsTaxable": True
            },
            {
                "AccountTypeID": "AT-013",
                "TypeName": "Savings Account",
                "Category": AccountCategory.CASH.value,
                "Description": "Bank savings account",
                "IsTaxDeferred": False,
                "IsTaxable": True
            },
            {
                "AccountTypeID": "AT-014",
                "TypeName": "Checking Account",
                "Category": AccountCategory.CASH.value,
                "Description": "Bank checking account",
                "IsTaxDeferred": False,
                "IsTaxable": True
            },
            {
                "AccountTypeID": "AT-015",
                "TypeName": "Money Market",
                "Category": AccountCategory.CASH.value,
                "Description": "Money market account",
                "IsTaxDeferred": False,
                "IsTaxable": True
            }
        ]
        
        for type_data in account_types_data:
            account_type = AccountType(
                AccountTypeID=type_data["AccountTypeID"],
                TypeName=type_data["TypeName"],
                Category=type_data["Category"],
                Description=type_data["Description"],
                IsTaxDeferred=type_data["IsTaxDeferred"],
                IsTaxable=type_data["IsTaxable"],
                CreatedDate=datetime.utcnow() - timedelta(days=random.randint(365, 1825))
            )
            
            self.db.add(account_type)
            self.created_data["account_types"].append(account_type)
        
        print(f"✓ Seeded {len(self.created_data['account_types'])} account types")
    
    def seed_accounts(self):
        """Seed 500 accounts"""
        print("Seeding accounts...")
        
        # Assume clients C00001 through C00250 exist from V2
        client_ids = [f"C{i:05d}" for i in range(1, 251)]
        household_ids = [f"H{i:03d}" for i in range(1, 151)]
        account_types = self.created_data["account_types"]
        
        # Common custodians
        custodians = [
            "Fidelity Investments", "Charles Schwab", "Vanguard", "TD Ameritrade",
            "E*TRADE", "Merrill Lynch", "Morgan Stanley", "UBS", "Wells Fargo",
            "Bank of America", "JPMorgan Chase", "Raymond James", "LPL Financial",
            "Edward Jones", "Ameriprise Financial"
        ]
        
        for i in range(1, 501):
            client_id = random.choice(client_ids)
            household_id = random.choice(household_ids)
            account_type = random.choice(account_types)
            
            # Generate account number (masked for privacy)
            account_number = f"****{random.randint(1000, 9999)}"
            
            # Generate account name based on type and owner
            account_name = self._generate_account_name(account_type.TypeName, i)
            
            # Generate realistic balance based on account type
            balance = self._generate_account_balance(account_type.TypeName)
            
            # Determine if account is managed
            is_managed = random.random() < 0.3  # 30% are managed
            
            # Set owner type
            owner_type = self._determine_owner_type(account_type.Category)
            
            # Set as_of_date (recent) - using date type
            as_of_date = (datetime.utcnow() - timedelta(days=random.randint(0, 30))).date()
            
            account = Account(
                AccountID=f"ACC-{i:05d}",
                ClientID=client_id,
                HouseholdID=household_id if random.random() < 0.8 else None,
                AccountNumber=account_number,
                AccountName=account_name,
                AccountTypeID=account_type.AccountTypeID,
                Balance=balance,
                AsOfDate=as_of_date,
                CustodianName=random.choice(custodians),
                Status=random.choice([AccountStatus.ACTIVE.value] * 9 + [AccountStatus.CLOSED.value]),
                IsManaged=is_managed,
                IsTaxable=account_type.IsTaxable,
                OwnerType=owner_type.value,
                CreatedDate=datetime.utcnow() - timedelta(days=random.randint(30, 1825)),
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            self.db.add(account)
            self.created_data["accounts"].append(account)
        
        print(f"✓ Seeded {len(self.created_data['accounts'])} accounts")
    
    def _generate_account_name(self, type_name: str, index: int) -> str:
        """Generate account name based on type"""
        if "401(k)" in type_name:
            return f"Company 401(k) Plan - {index:03d}"
        elif "IRA" in type_name:
            return f"{type_name} Account - {index:03d}"
        elif "529" in type_name:
            return f"Education Savings - {index:03d}"
        elif "HSA" in type_name:
            return f"Health Savings - {index:03d}"
        elif "Brokerage" in type_name:
            return f"Investment Account - {index:03d}"
        elif "Trust" in type_name:
            return f"Family Trust - {index:03d}"
        elif "Savings" in type_name:
            return f"Savings Account - {index:03d}"
        elif "Checking" in type_name:
            return f"Checking Account - {index:03d}"
        elif "Money Market" in type_name:
            return f"Money Market - {index:03d}"
        else:
            return f"{type_name} - {index:03d}"
    
    def _generate_account_balance(self, type_name: str) -> Decimal:
        """Generate realistic balance based on account type"""
        if "401(k)" in type_name or "403(b)" in type_name:
            return Decimal(str(random.randint(25000, 500000)))
        elif "IRA" in type_name:
            return Decimal(str(random.randint(10000, 300000)))
        elif "529" in type_name:
            return Decimal(str(random.randint(5000, 100000)))
        elif "HSA" in type_name:
            return Decimal(str(random.randint(1000, 15000)))
        elif "Brokerage" in type_name or "Joint" in type_name:
            return Decimal(str(random.randint(50000, 1000000)))
        elif "Trust" in type_name:
            return Decimal(str(random.randint(100000, 2000000)))
        elif "Pension" in type_name:
            return Decimal(str(random.randint(200000, 800000)))
        elif "Savings" in type_name:
            return Decimal(str(random.randint(5000, 100000)))
        elif "Checking" in type_name:
            return Decimal(str(random.randint(1000, 25000)))
        elif "Money Market" in type_name:
            return Decimal(str(random.randint(10000, 200000)))
        else:
            return Decimal(str(random.randint(10000, 100000)))
    
    def _determine_owner_type(self, category: str) -> OwnerType:
        """Determine owner type based on account category"""
        if category == AccountCategory.TRUST.value:
            return OwnerType.TRUST
        elif "Joint" in category:
            return OwnerType.JOINT
        else:
            # Most accounts are individual, some are joint
            return random.choice([OwnerType.INDIVIDUAL] * 7 + [OwnerType.JOINT] * 2 + [OwnerType.ENTITY])