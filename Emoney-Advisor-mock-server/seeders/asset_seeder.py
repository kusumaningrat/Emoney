# seeders/asset_seeder.py - FIXED for PascalCase field names

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Dict, List, Any
from decimal import Decimal
import random
from faker import Faker

from models.asset import Asset, AssetClass, Liability
from models.asset import AssetStatus, RiskLevel, LiabilityType, LiabilityStatus

fake = Faker()

class AssetSeeder:
    def __init__(self, db: Session):
        self.db = db
        self.created_data = {
            "asset_classes": [],
            "assets": [],
            "liabilities": []
        }
    
    def seed_all(self) -> Dict[str, List[Any]]:
        """Seed all V4 Asset Management entities"""
        print("Starting V4 Asset Management seeding...")
        
        # Seed in dependency order
        self.seed_asset_classes()
        self.seed_assets()
        self.seed_liabilities()
        
        self.db.commit()
        print("V4 Asset Management seeding completed!")
        
        return self.created_data
    
    def seed_asset_classes(self):
        """Seed 12 asset classes"""
        print("Seeding asset classes...")
        
        asset_classes_data = [
            {
                "AssetClassID": "AC-001",
                "ClassName": "US Large Cap Equity",
                "Category": "Equity",
                "Description": "US Large Capitalization Stocks",
                "RiskLevel": RiskLevel.MODERATE.value
            },
            {
                "AssetClassID": "AC-002",
                "ClassName": "US Small Cap Equity",
                "Category": "Equity",
                "Description": "US Small Capitalization Stocks", 
                "RiskLevel": RiskLevel.HIGH.value
            },
            {
                "AssetClassID": "AC-003",
                "ClassName": "International Developed Equity",
                "Category": "Equity",
                "Description": "International Developed Market Stocks",
                "RiskLevel": RiskLevel.MODERATE.value
            },
            {
                "AssetClassID": "AC-004",
                "ClassName": "Emerging Markets Equity", 
                "Category": "Equity",
                "Description": "Emerging Market Stocks",
                "RiskLevel": RiskLevel.HIGH.value
            },
            {
                "AssetClassID": "AC-005",
                "ClassName": "US Government Bonds",
                "Category": "Fixed Income",
                "Description": "US Treasury and Government Bonds",
                "RiskLevel": RiskLevel.LOW.value
            },
            {
                "AssetClassID": "AC-006",
                "ClassName": "US Corporate Bonds",
                "Category": "Fixed Income",
                "Description": "US Corporate Investment Grade Bonds",
                "RiskLevel": RiskLevel.LOW.value
            },
            {
                "AssetClassID": "AC-007",
                "ClassName": "High Yield Bonds",
                "Category": "Fixed Income",
                "Description": "High Yield Corporate Bonds",
                "RiskLevel": RiskLevel.MODERATE.value
            },
            {
                "AssetClassID": "AC-008",
                "ClassName": "Real Estate (REITs)",
                "Category": "Alternative",
                "Description": "Real Estate Investment Trusts",
                "RiskLevel": RiskLevel.MODERATE.value
            },
            {
                "AssetClassID": "AC-009",
                "ClassName": "Commodities",
                "Category": "Alternative",
                "Description": "Commodity Investments",
                "RiskLevel": RiskLevel.HIGH.value
            },
            {
                "AssetClassID": "AC-010",
                "ClassName": "Cash & Cash Equivalents",
                "Category": "Cash",
                "Description": "Money Market and Cash Equivalents",
                "RiskLevel": RiskLevel.LOW.value
            },
            {
                "AssetClassID": "AC-011",
                "ClassName": "International Bonds",
                "Category": "Fixed Income", 
                "Description": "International Government and Corporate Bonds",
                "RiskLevel": RiskLevel.MODERATE.value
            },
            {
                "AssetClassID": "AC-012",
                "ClassName": "Private Equity",
                "Category": "Alternative",
                "Description": "Private Equity and Venture Capital",
                "RiskLevel": RiskLevel.VERY_HIGH.value
            }
        ]
        
        for class_data in asset_classes_data:
            asset_class = AssetClass(
                AssetClassID=class_data["AssetClassID"],
                ClassName=class_data["ClassName"],
                Category=class_data["Category"],
                Description=class_data["Description"],
                RiskLevel=class_data["RiskLevel"],
                Status="Active",
                CreatedDate=datetime.utcnow() - timedelta(days=random.randint(365, 1825))
            )
            
            self.db.add(asset_class)
            self.created_data["asset_classes"].append(asset_class)
        
        print(f"✓ Seeded {len(self.created_data['asset_classes'])} asset classes")
    
    def seed_assets(self):
        """Seed 800 assets"""
        print("Seeding assets...")
        
        # Get accounts from seeded data (assuming account seeder ran first)
        # For demo purposes, we'll use account IDs ACC-00001 through ACC-00500
        account_ids = [f"ACC-{i:05d}" for i in range(1, 501)]
        asset_classes = self.created_data["asset_classes"]
        
        # Common securities by asset class
        securities = {
            "US Large Cap Equity": [
                ("Vanguard Total Stock Market Index", "VTSAX", "922908769"),
                ("SPDR S&P 500 ETF", "SPY", "78462F103"),
                ("Vanguard S&P 500 Index", "VFINX", "922908728"),
                ("iShares Core S&P 500 ETF", "IVV", "464287200"),
                ("Apple Inc.", "AAPL", "037833100")
            ],
            "US Small Cap Equity": [
                ("Vanguard Small Cap Index", "VSMAX", "922908645"),
                ("iShares Russell 2000 ETF", "IWM", "464287812"),
                ("Vanguard Small Cap Value Index", "VSIAX", "922908694")
            ],
            "International Developed Equity": [
                ("Vanguard Total International Stock", "VTIAX", "92204A702"),
                ("iShares MSCI EAFE ETF", "EFA", "464287507"),
                ("Vanguard Developed Markets Index", "VTMGX", "922908371")
            ],
            "Emerging Markets Equity": [
                ("Vanguard Emerging Markets Stock", "VEMAX", "922908538"),
                ("iShares MSCI Emerging Markets", "EEM", "464287228")
            ],
            "US Government Bonds": [
                ("Vanguard Total Bond Market Index", "VBTLX", "922908769"),
                ("iShares Core US Aggregate Bond", "AGG", "464287366"),
                ("US Treasury 10-Year Note", "IEF", "464287812")
            ],
            "US Corporate Bonds": [
                ("Vanguard Intermediate-Term Corp", "VICSX", "922908645"),
                ("iShares iBoxx Investment Grade", "LQD", "464287200")
            ],
            "Real Estate (REITs)": [
                ("Vanguard Real Estate Index", "VGSLX", "922908538"),
                ("iShares US Real Estate ETF", "IYR", "464287366")
            ],
            "Cash & Cash Equivalents": [
                ("Vanguard Federal Money Market", "VMFXX", "922908371"),
                ("Fidelity Government Money Market", "FDRXX", "316390103")
            ]
        }
        
        for i in range(1, 801):
            account_id = random.choice(account_ids)
            asset_class = random.choice(asset_classes)
            
            # Get appropriate securities for this asset class
            class_securities = securities.get(asset_class.ClassName, [("Generic Security", "GENRC", "000000000")])
            security_name, symbol, cusip = random.choice(class_securities)
            
            # Add some variation to security names
            if i % 50 == 0:  # Create some individual stocks
                security_name = f"{fake.company()} Inc."
                symbol = f"{fake.lexify('????').upper()}"
                cusip = f"{random.randint(100000000, 999999999)}"
            
            # Generate realistic holding data
            shares, price, value, cost_basis = self._generate_holding_data(asset_class.ClassName)
            
            unrealized_gain = value - cost_basis
            unrealized_gain_percent = (unrealized_gain / cost_basis * 100) if cost_basis > 0 else Decimal('0.00')
            
            as_of_date = (datetime.utcnow() - timedelta(days=random.randint(0, 7))).date()
            
            asset = Asset(
                AssetID=f"AST-{i:05d}",
                AccountID=account_id,
                SecurityName=security_name,
                Symbol=symbol if symbol != "GENRC" else None,
                CUSIP=cusip if cusip != "000000000" else None,
                AssetClassID=asset_class.AssetClassID,
                Shares=shares,
                Price=price,
                Value=value,
                CostBasis=cost_basis,
                UnrealizedGain=unrealized_gain,
                UnrealizedGainPercent=unrealized_gain_percent,
                AsOfDate=as_of_date,
                Status=random.choice([AssetStatus.ACTIVE.value] * 9 + [AssetStatus.SOLD.value]),
                CreatedDate=datetime.utcnow() - timedelta(days=random.randint(30, 1825)),
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            self.db.add(asset)
            self.created_data["assets"].append(asset)
        
        print(f"✓ Seeded {len(self.created_data['assets'])} assets")
    
    def seed_liabilities(self):
        """Seed 300 liabilities"""
        print("Seeding liabilities...")
        
        # Assume clients C00001 through C00250 exist from V2
        client_ids = [f"C{i:05d}" for i in range(1, 251)]
        household_ids = [f"H{i:03d}" for i in range(1, 151)]
        
        liability_types = list(LiabilityType)
        
        # Common lenders by liability type
        lenders = {
            LiabilityType.MORTGAGE: [
                "Wells Fargo Home Mortgage", "Quicken Loans", "Bank of America",
                "JPMorgan Chase", "US Bank", "PNC Bank", "Citibank"
            ],
            LiabilityType.AUTO_LOAN: [
                "Toyota Financial", "Honda Finance", "Ford Credit", "GM Financial",
                "Wells Fargo Auto", "Chase Auto Finance", "Capital One Auto"
            ],
            LiabilityType.CREDIT_CARD: [
                "Chase Sapphire", "American Express", "Citi Platinum", "Capital One",
                "Discover Card", "Bank of America", "Wells Fargo"
            ],
            LiabilityType.STUDENT_LOAN: [
                "Federal Student Aid", "Sallie Mae", "Navient", "Great Lakes",
                "FedLoan Servicing", "MOHELA", "Nelnet"
            ],
            LiabilityType.PERSONAL_LOAN: [
                "SoFi", "LendingClub", "Prosper", "Marcus by Goldman Sachs",
                "Discover Personal Loans", "Wells Fargo", "Chase"
            ],
            LiabilityType.LINE_OF_CREDIT: [
                "Wells Fargo", "Bank of America", "Chase", "Citi",
                "PNC Bank", "US Bank", "TD Bank"
            ]
        }
        
        for i in range(1, 301):
            client_id = random.choice(client_ids)
            household_id = random.choice(household_ids)
            liability_type = random.choice(liability_types)
            
            # Generate liability details based on type
            liability_name, current_balance, original_amount, interest_rate, monthly_payment, maturity_date = \
                self._generate_liability_details(liability_type, i)
            
            # Select appropriate lender
            type_lenders = lenders.get(liability_type, ["Generic Lender"])
            lender = random.choice(type_lenders)
            
            liability = Liability(
                LiabilityID=f"LIA-{i:05d}",
                ClientID=client_id,
                HouseholdID=household_id if random.random() < 0.8 else None,
                LiabilityName=liability_name,
                LiabilityType=liability_type.value,
                CurrentBalance=current_balance,
                OriginalAmount=original_amount,
                InterestRate=interest_rate,
                MonthlyPayment=monthly_payment,
                MaturityDate=maturity_date.date() if maturity_date else None,
                Lender=lender,
                Status=LiabilityStatus.ACTIVE.value,
                CreatedDate=datetime.utcnow() - timedelta(days=random.randint(30, 2555)),
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            self.db.add(liability)
            self.created_data["liabilities"].append(liability)
        
        print(f"✓ Seeded {len(self.created_data['liabilities'])} liabilities")
    
    def _generate_holding_data(self, asset_class_name: str) -> tuple:
        """Generate realistic holding data based on asset class"""
        if "Equity" in asset_class_name or "Stock" in asset_class_name:
            shares = Decimal(str(random.randint(10, 1000)))
            price = Decimal(str(round(random.uniform(20.00, 500.00), 2)))
            value = shares * price
            # Cost basis is usually lower (gains) but sometimes higher (losses)
            cost_basis_per_share = price * Decimal(str(round(random.uniform(0.70, 1.30), 2)))
            cost_basis = shares * cost_basis_per_share
        elif "Bond" in asset_class_name:
            # Bonds often traded in larger denominations
            shares = Decimal(str(random.randint(5, 100)))
            price = Decimal(str(round(random.uniform(95.00, 105.00), 2)))
            value = shares * price * 10  # Bond prices are per $100 face value
            cost_basis_per_share = price * Decimal(str(round(random.uniform(0.95, 1.05), 2)))
            cost_basis = shares * cost_basis_per_share * 10
        elif "Cash" in asset_class_name:
            shares = Decimal('1.000000')
            price = Decimal('1.0000')
            value = Decimal(str(random.randint(1000, 50000)))
            cost_basis = value  # Cash equivalents have no gain/loss
        elif "REIT" in asset_class_name or "Real Estate" in asset_class_name:
            shares = Decimal(str(random.randint(50, 500)))
            price = Decimal(str(round(random.uniform(25.00, 200.00), 2)))
            value = shares * price
            cost_basis_per_share = price * Decimal(str(round(random.uniform(0.80, 1.20), 2)))
            cost_basis = shares * cost_basis_per_share
        else:  # Alternative investments, commodities, etc.
            shares = Decimal(str(random.randint(10, 200)))
            price = Decimal(str(round(random.uniform(50.00, 300.00), 2)))
            value = shares * price
            cost_basis_per_share = price * Decimal(str(round(random.uniform(0.75, 1.40), 2)))
            cost_basis = shares * cost_basis_per_share
        
        return shares, price, value, cost_basis
    
    def _generate_liability_details(self, liability_type: LiabilityType, index: int) -> tuple:
        """Generate liability details based on type"""
        if liability_type == LiabilityType.MORTGAGE:
            current_balance = Decimal(str(random.randint(150000, 800000)))
            original_amount = current_balance + Decimal(str(random.randint(50000, 200000)))
            interest_rate = Decimal(str(round(random.uniform(2.5, 6.5), 4)))
            monthly_payment = Decimal(str(random.randint(1200, 4500)))
            years_remaining = random.randint(5, 25)
            maturity_date = datetime.utcnow() + timedelta(days=years_remaining * 365)
            liability_name = f"Primary Residence Mortgage {index:03d}"
            
        elif liability_type == LiabilityType.AUTO_LOAN:
            current_balance = Decimal(str(random.randint(8000, 65000)))
            original_amount = current_balance + Decimal(str(random.randint(5000, 25000)))
            interest_rate = Decimal(str(round(random.uniform(1.9, 8.5), 4)))
            monthly_payment = Decimal(str(random.randint(250, 800)))
            years_remaining = random.randint(1, 6)
            maturity_date = datetime.utcnow() + timedelta(days=years_remaining * 365)
            liability_name = f"Auto Loan {index:03d}"
            
        elif liability_type == LiabilityType.CREDIT_CARD:
            current_balance = Decimal(str(random.randint(2000, 25000)))
            original_amount = Decimal(str(random.randint(30000, 50000)))  # Credit limit
            interest_rate = Decimal(str(round(random.uniform(12.0, 24.9), 4)))
            monthly_payment = Decimal(str(random.randint(100, 800)))
            maturity_date = None  # Revolving credit
            liability_name = f"Credit Card {index:03d}"
            
        elif liability_type == LiabilityType.STUDENT_LOAN:
            current_balance = Decimal(str(random.randint(15000, 150000)))
            original_amount = current_balance + Decimal(str(random.randint(10000, 50000)))
            interest_rate = Decimal(str(round(random.uniform(3.5, 6.8), 4)))
            monthly_payment = Decimal(str(random.randint(200, 1200)))
            years_remaining = random.randint(5, 20)
            maturity_date = datetime.utcnow() + timedelta(days=years_remaining * 365)
            liability_name = f"Student Loan {index:03d}"
            
        elif liability_type == LiabilityType.PERSONAL_LOAN:
            current_balance = Decimal(str(random.randint(5000, 50000)))
            original_amount = current_balance + Decimal(str(random.randint(2000, 15000)))
            interest_rate = Decimal(str(round(random.uniform(5.0, 15.0), 4)))
            monthly_payment = Decimal(str(random.randint(150, 700)))
            years_remaining = random.randint(2, 7)
            maturity_date = datetime.utcnow() + timedelta(days=years_remaining * 365)
            liability_name = f"Personal Loan {index:03d}"
            
        elif liability_type == LiabilityType.LINE_OF_CREDIT:
            current_balance = Decimal(str(random.randint(5000, 100000)))
            original_amount = Decimal(str(random.randint(50000, 200000)))  # Credit limit
            interest_rate = Decimal(str(round(random.uniform(4.0, 12.0), 4)))
            monthly_payment = Decimal(str(random.randint(200, 1000)))
            maturity_date = None  # Revolving credit
            liability_name = f"Home Equity Line of Credit {index:03d}"
            
        else:  # OTHER
            current_balance = Decimal(str(random.randint(1000, 30000)))
            original_amount = current_balance + Decimal(str(random.randint(500, 10000)))
            interest_rate = Decimal(str(round(random.uniform(3.0, 15.0), 4)))
            monthly_payment = Decimal(str(random.randint(100, 500)))
            years_remaining = random.randint(1, 5)
            maturity_date = datetime.utcnow() + timedelta(days=years_remaining * 365)
            liability_name = f"Other Debt {index:03d}"
        
        return liability_name, current_balance, original_amount, interest_rate, monthly_payment, maturity_date