# seeders/asset_seeder.py

from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta, date
from faker import Faker
import random
import uuid
import json

from database import SessionLocal
from models.assets import Asset, AssetClass, Allocation, Security, Holding
from models.clients import Client
from models.accounts import Account
from models.users import User
from models.financial import FinancialPlan

# Initialize Faker
fake = Faker()

# Main function to seed all asset data
def seed_asset_data(db: Session = None):
    """Main function to seed all asset management data in correct order."""
    if db is None:
        db = SessionLocal()
    
    try:
        # Check if data already exists to avoid duplicates
        existing_asset_classes = db.query(AssetClass).count()
        if existing_asset_classes > 0:
            print("Asset management data already seeded, skipping...")
            return
        
        # Ensure clients exist
        clients = db.query(Client).all()
        if not clients:
            print("No clients found, seeding clients first required.")
            return
            
        # Get accounts
        accounts = db.query(Account).all()
        if not accounts:
            print("No accounts found, seeding accounts first required.")
            return
            
        # Get users
        users = db.query(User).all()
        if not users:
            print("No users found, seeding users first required.")
            return
            
        # Get financial plans if available
        financial_plans = db.query(FinancialPlan).all()
        
        # 1. Create asset classes first
        asset_classes = seed_asset_classes(db, users)
        db.commit()
            
        # 2. Create securities
        securities = seed_securities(db, asset_classes, users)
        db.commit()
            
        # 3. Create assets with allocations and holdings
        assets = seed_assets(db, clients, accounts, financial_plans, asset_classes, securities, users)
        db.commit()
        
        print("Asset management seeding complete!")
        return True
        
    except Exception as e:
        print(f"Error seeding asset management data: {e}")
        db.rollback()
        raise
    finally:
        if db is not None:
            db.close()

def generate_id(prefix: str) -> str:
    """Generate a unique ID with a prefix."""
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def seed_asset_classes(db: Session, users: list):
    """Create asset class hierarchy."""
    print("Creating asset classes...")
    
    # Top level asset classes
    top_level_classes = [
        {"name": "Equity", "parent_id": None},
        {"name": "Fixed Income", "parent_id": None},
        {"name": "Cash & Equivalents", "parent_id": None},
        {"name": "Real Estate", "parent_id": None},
        {"name": "Alternative Investments", "parent_id": None}
    ]
    
    # Second level classes with parents
    sub_classes = [
        # Equity sub-classes
        {"name": "US Large Cap", "parent_name": "Equity"},
        {"name": "US Mid Cap", "parent_name": "Equity"},
        {"name": "US Small Cap", "parent_name": "Equity"},
        {"name": "International Developed", "parent_name": "Equity"},
        {"name": "Emerging Markets", "parent_name": "Equity"},
        
        # Fixed Income sub-classes
        {"name": "US Government Bonds", "parent_name": "Fixed Income"},
        {"name": "Corporate Bonds", "parent_name": "Fixed Income"},
        {"name": "Municipal Bonds", "parent_name": "Fixed Income"},
        {"name": "International Bonds", "parent_name": "Fixed Income"},
        {"name": "High Yield Bonds", "parent_name": "Fixed Income"},
        
        # Cash sub-classes
        {"name": "Money Market", "parent_name": "Cash & Equivalents"},
        {"name": "Certificates of Deposit", "parent_name": "Cash & Equivalents"},
        {"name": "Treasury Bills", "parent_name": "Cash & Equivalents"},
        
        # Real Estate sub-classes
        {"name": "Residential Real Estate", "parent_name": "Real Estate"},
        {"name": "Commercial Real Estate", "parent_name": "Real Estate"},
        {"name": "REITs", "parent_name": "Real Estate"},
        
        # Alternative Investments sub-classes
        {"name": "Private Equity", "parent_name": "Alternative Investments"},
        {"name": "Hedge Funds", "parent_name": "Alternative Investments"},
        {"name": "Commodities", "parent_name": "Alternative Investments"},
        {"name": "Collectibles", "parent_name": "Alternative Investments"},
        {"name": "Cryptocurrency", "parent_name": "Alternative Investments"}
    ]
    
    # Create top level classes first
    asset_class_map = {}  # To store id by name
    
    # Select random user for created_by/updated_by
    user = random.choice(users)
    
    for class_data in top_level_classes:
        asset_class = AssetClass(
            id=generate_id("assetclass"),
            name=class_data["name"],
            parent_id=None,
            created_by=user.id,
            updated_by=user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(asset_class)
        asset_class_map[class_data["name"]] = asset_class
    
    db.flush()
    
    # Create sub-classes
    for sub_class in sub_classes:
        parent_class = asset_class_map.get(sub_class["parent_name"])
        if parent_class:
            asset_class = AssetClass(
                id=generate_id("assetclass"),
                name=sub_class["name"],
                parent_id=parent_class.id,
                created_by=user.id,
                updated_by=user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(asset_class)
            asset_class_map[sub_class["name"]] = asset_class
    
    db.commit()
    print(f"Created {len(asset_class_map)} asset classes!")
    return list(asset_class_map.values())

def seed_securities(db: Session, asset_classes: list, users: list):
    """Create securities for investment accounts."""
    print("Creating securities...")
    
    # Map asset classes by name for easy lookup
    asset_class_map = {ac.name: ac for ac in asset_classes}
    
    # Map security types to appropriate asset classes
    security_type_mapping = {
        "US Large Cap": ["US Large Cap", "Equity"],
        "US Mid Cap": ["US Mid Cap", "Equity"],
        "US Small Cap": ["US Small Cap", "Equity"],
        "International Developed": ["International Developed", "Equity"],
        "Emerging Markets": ["Emerging Markets", "Equity"],
        "US Government Bonds": ["US Government Bonds", "Fixed Income"],
        "Corporate Bonds": ["Corporate Bonds", "Fixed Income"],
        "Municipal Bonds": ["Municipal Bonds", "Fixed Income"],
        "International Bonds": ["International Bonds", "Fixed Income"],
        "High Yield Bonds": ["High Yield Bonds", "Fixed Income"],
        "Money Market": ["Money Market", "Cash & Equivalents"],
        "REITs": ["REITs", "Real Estate"],
        "Commodities": ["Commodities", "Alternative Investments"],
        "Cryptocurrency": ["Cryptocurrency", "Alternative Investments"]
    }
    
    # Define securities
    securities_data = [
        # Large Cap Stocks
        {"symbol": "AAPL", "name": "Apple Inc.", "type": "Stock", "asset_class_type": "US Large Cap", "price": 174.23},
        {"symbol": "MSFT", "name": "Microsoft Corporation", "type": "Stock", "asset_class_type": "US Large Cap", "price": 323.87},
        {"symbol": "AMZN", "name": "Amazon.com Inc.", "type": "Stock", "asset_class_type": "US Large Cap", "price": 125.17},
        {"symbol": "GOOGL", "name": "Alphabet Inc. Class A", "type": "Stock", "asset_class_type": "US Large Cap", "price": 138.45},
        {"symbol": "META", "name": "Meta Platforms Inc.", "type": "Stock", "asset_class_type": "US Large Cap", "price": 287.71},
        
        # Mid Cap Stocks
        {"symbol": "ETSY", "name": "Etsy Inc.", "type": "Stock", "asset_class_type": "US Mid Cap", "price": 68.23},
        {"symbol": "DECK", "name": "Deckers Outdoor Corp", "type": "Stock", "asset_class_type": "US Mid Cap", "price": 654.89},
        {"symbol": "AXON", "name": "Axon Enterprise Inc.", "type": "Stock", "asset_class_type": "US Mid Cap", "price": 211.34},
        
        # Small Cap Stocks
        {"symbol": "CROX", "name": "Crocs Inc.", "type": "Stock", "asset_class_type": "US Small Cap", "price": 96.43},
        {"symbol": "WING", "name": "Wingstop Inc.", "type": "Stock", "asset_class_type": "US Small Cap", "price": 208.76},
        
        # International Developed
        {"symbol": "SONY", "name": "Sony Group Corp", "type": "Stock", "asset_class_type": "International Developed", "price": 89.32},
        {"symbol": "SAP", "name": "SAP SE", "type": "Stock", "asset_class_type": "International Developed", "price": 138.68},
        
        # Emerging Markets
        {"symbol": "BABA", "name": "Alibaba Group Holding Ltd", "type": "Stock", "asset_class_type": "Emerging Markets", "price": 84.57},
        {"symbol": "TSM", "name": "Taiwan Semiconductor Manufacturing Co Ltd", "type": "Stock", "asset_class_type": "Emerging Markets", "price": 105.23},
        
        # Government Bonds
        {"symbol": "TLT", "name": "iShares 20+ Year Treasury Bond ETF", "type": "ETF", "asset_class_type": "US Government Bonds", "price": 94.68},
        {"symbol": "IEF", "name": "iShares 7-10 Year Treasury Bond ETF", "type": "ETF", "asset_class_type": "US Government Bonds", "price": 98.12},
        
        # Corporate Bonds
        {"symbol": "LQD", "name": "iShares iBoxx $ Investment Grade Corporate Bond ETF", "type": "ETF", "asset_class_type": "Corporate Bonds", "price": 108.32},
        {"symbol": "VCLT", "name": "Vanguard Long-Term Corporate Bond ETF", "type": "ETF", "asset_class_type": "Corporate Bonds", "price": 76.84},
        
        # Municipal Bonds
        {"symbol": "MUB", "name": "iShares National Muni Bond ETF", "type": "ETF", "asset_class_type": "Municipal Bonds", "price": 107.89},
        {"symbol": "TFI", "name": "SPDR Nuveen Bloomberg Municipal Bond ETF", "type": "ETF", "asset_class_type": "Municipal Bonds", "price": 46.32},
        
        # International Bonds
        {"symbol": "BNDX", "name": "Vanguard Total International Bond ETF", "type": "ETF", "asset_class_type": "International Bonds", "price": 48.76},
        {"symbol": "IGOV", "name": "iShares International Treasury Bond ETF", "type": "ETF", "asset_class_type": "International Bonds", "price": 39.45},
        
        # High Yield Bonds
        {"symbol": "HYG", "name": "iShares iBoxx $ High Yield Corporate Bond ETF", "type": "ETF", "asset_class_type": "High Yield Bonds", "price": 74.32},
        {"symbol": "JNK", "name": "SPDR Bloomberg High Yield Bond ETF", "type": "ETF", "asset_class_type": "High Yield Bonds", "price": 91.27},
        
        # Money Market
        {"symbol": "SPAXX", "name": "Fidelity Government Money Market Fund", "type": "Mutual Fund", "asset_class_type": "Money Market", "price": 1.00},
        {"symbol": "VMMXX", "name": "Vanguard Federal Money Market Fund", "type": "Mutual Fund", "asset_class_type": "Money Market", "price": 1.00},
        
        # REITs
        {"symbol": "VNQ", "name": "Vanguard Real Estate ETF", "type": "ETF", "asset_class_type": "REITs", "price": 84.35},
        {"symbol": "IYR", "name": "iShares U.S. Real Estate ETF", "type": "ETF", "asset_class_type": "REITs", "price": 86.92},
        
        # Commodities
        {"symbol": "GLD", "name": "SPDR Gold Shares", "type": "ETF", "asset_class_type": "Commodities", "price": 184.78},
        {"symbol": "USO", "name": "United States Oil Fund", "type": "ETF", "asset_class_type": "Commodities", "price": 72.34},
        
        # Cryptocurrency
        {"symbol": "GBTC", "name": "Grayscale Bitcoin Trust", "type": "Trust", "asset_class_type": "Cryptocurrency", "price": 35.27},
        {"symbol": "ETHE", "name": "Grayscale Ethereum Trust", "type": "Trust", "asset_class_type": "Cryptocurrency", "price": 17.82}
    ]
    
    securities = []
    
    # Select random user for created_by/updated_by
    user = random.choice(users)
    
    for security_data in securities_data:
        # Find appropriate asset class
        asset_class_type = security_data["asset_class_type"]
        asset_class = None
        
        # Try to find exact match first, then fallback to parent
        if asset_class_type in asset_class_map:
            asset_class = asset_class_map[asset_class_type]
        elif asset_class_type in security_type_mapping:
            for class_name in security_type_mapping[asset_class_type]:
                if class_name in asset_class_map:
                    asset_class = asset_class_map[class_name]
                    break
        
        if not asset_class:
            # If no match found, use a default class
            asset_class = random.choice(asset_classes)
        
        security = Security(
            id=generate_id("security"),
            symbol=security_data["symbol"],
            name=security_data["name"],
            type=security_data["type"],
            price=security_data["price"],
            price_date=date.today(),
            asset_class_id=asset_class.id,
            created_by=user.id,
            updated_by=user.id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(security)
        securities.append(security)
    
    db.commit()
    print(f"Created {len(securities)} securities!")
    return securities

def seed_assets(db: Session, clients: list, accounts: list, financial_plans: list, asset_classes: list, securities: list, users: list):
    """Create assets with allocations and holdings."""
    print("Creating assets, allocations, and holdings...")
    
    assets_created = 0
    allocations_created = 0
    holdings_created = 0
    
    # Map asset classes by name
    asset_class_map = {ac.name: ac for ac in asset_classes}
    
    # Map securities by type
    security_map = {}
    for security in securities:
        if security.type not in security_map:
            security_map[security.type] = []
        security_map[security.type].append(security)
    
    for client in clients:
        # Skip some clients
        if random.random() > 0.8:
            continue
            
        # Try to find a financial plan for this client
        client_plan = next((plan for plan in financial_plans if plan.client_id == client.id), None)
        
        # Get client's accounts
        client_accounts = [a for a in accounts if a.client_id == client.id]
        
        # Define common asset types for this client
        asset_types = [
            "Real Estate",
            "Investment Portfolio",
            "Bank Account",
            "Retirement Account",
            "Business Interest",
            "Personal Property",
            "Life Insurance",
            "Collectible"
        ]
        
        # Create 1-5 assets for this client
        num_assets = random.randint(1, 5)
        selected_asset_types = random.sample(asset_types, min(num_assets, len(asset_types)))
        
        for asset_type in selected_asset_types:
            # Select random user for created_by/updated_by
            creator = random.choice(users)
            updater = random.choice(users)
            
            # Select a random account or None
            account = random.choice(client_accounts) if client_accounts and random.random() > 0.5 else None
            
            # Generate asset name and description
            if asset_type == "Real Estate":
                name = f"{client.last_name} {random.choice(['Primary Residence', 'Vacation Home', 'Rental Property'])}"
                description = f"Located in {fake.city()}, {fake.state_abbr()}"
                value = random.uniform(200000, 1500000)
                basis = value * random.uniform(0.5, 0.9)  # Purchase price
                growth_rate = random.uniform(0.02, 0.05)  # 2-5% annual appreciation
            elif asset_type == "Investment Portfolio":
                name = f"{client.last_name} Investment Portfolio"
                description = f"Managed at {random.choice(['Charles Schwab', 'Fidelity', 'Vanguard', 'Morgan Stanley', 'Merrill Lynch'])}"
                value = random.uniform(50000, 1000000)
                basis = value * random.uniform(0.7, 0.95)  # Cost basis
                growth_rate = random.uniform(0.04, 0.08)  # 4-8% expected return
            elif asset_type == "Bank Account":
                name = f"{client.last_name} {random.choice(['Checking', 'Savings', 'Money Market'])}"
                description = f"Account at {random.choice(['Chase', 'Bank of America', 'Wells Fargo', 'Citi', 'Capital One'])}"
                value = random.uniform(5000, 100000)
                basis = value  # Same as current value
                growth_rate = random.uniform(0.001, 0.03)  # 0.1-3% interest
            elif asset_type == "Retirement Account":
                name = f"{client.last_name} {random.choice(['401(k)', 'IRA', 'Roth IRA', '403(b)'])}"
                description = f"Retirement savings at {random.choice(['Fidelity', 'Vanguard', 'T. Rowe Price', 'TIAA'])}"
                value = random.uniform(100000, 1200000)
                basis = value * random.uniform(0.5, 0.9)  # Contributions
                growth_rate = random.uniform(0.05, 0.08)  # 5-8% expected return
            elif asset_type == "Business Interest":
                name = f"Ownership in {fake.company()}"
                description = f"{random.randint(10, 100)}% ownership stake"
                value = random.uniform(50000, 2000000)
                basis = value * random.uniform(0.2, 0.8)  # Initial investment
                growth_rate = random.uniform(0.05, 0.15)  # 5-15% growth
            elif asset_type == "Personal Property":
                name = f"{client.last_name} {random.choice(['Vehicles', 'Furniture', 'Jewelry', 'Electronics'])}"
                description = "Personal assets"
                value = random.uniform(10000, 100000)
                basis = value * random.uniform(1.1, 1.5)  # Usually depreciates
                growth_rate = random.uniform(-0.1, 0.0)  # -10% to 0% (depreciation)
            elif asset_type == "Life Insurance":
                name = f"{client.last_name} Life Insurance"
                description = f"{random.choice(['Term', 'Whole', 'Universal'])} policy"
                value = random.uniform(100000, 2000000)
                basis = value * random.uniform(0.05, 0.2)  # Premiums paid
                growth_rate = random.uniform(0.01, 0.04)  # 1-4% for cash value
            elif asset_type == "Collectible":
                collectible_type = random.choice(['Art', 'Wine', 'Coins', 'Stamps', 'Antiques', 'Classic Car'])
                name = f"{client.last_name} {collectible_type} Collection"
                description = f"Collection of {collectible_type.lower()}"
                value = random.uniform(10000, 500000)
                basis = value * random.uniform(0.3, 0.8)  # Purchase cost
                growth_rate = random.uniform(0.02, 0.1)  # 2-10% appreciation
            
            # Create asset
            asset_id = generate_id("asset")
            asset = Asset(
                id=asset_id,
                client_id=client.id,
                plan_id=client_plan.id if client_plan else None,
                name=name,
                description=description,
                type=asset_type,
                value=round(value, 2),
                basis=round(basis, 2) if random.random() > 0.3 else None,
                growth_rate=growth_rate,
                ownership=random.choice(["Individual", "Joint"]),
                account_id=account.id if account else None,
                created_by=creator.id,
                updated_by=updater.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(asset)
            assets_created += 1
            
            # Create allocations for investment-related assets
            if asset_type in ["Investment Portfolio", "Retirement Account"]:
                # Choose 2-5 asset classes
                selected_classes = random.sample(asset_classes, random.randint(2, 5))
                
                # Distribute percentages
                percentages = []
                for _ in range(len(selected_classes)):
                    percentages.append(random.randint(5, 30))
                
                # Normalize to 100%
                total = sum(percentages)
                percentages = [round((p / total) * 100, 2) for p in percentages]
                
                # Adjust for rounding errors
                if sum(percentages) < 100:
                    percentages[-1] += round(100 - sum(percentages), 2)
                elif sum(percentages) > 100:
                    percentages[-1] -= round(sum(percentages) - 100, 2)
                
                # Create allocations
                for i, asset_class in enumerate(selected_classes):
                    allocation_pct = percentages[i]
                    allocation_value = value * (allocation_pct / 100)
                    
                    allocation = Allocation(
                        id=generate_id("alloc"),
                        asset_id=asset_id,
                        asset_class_id=asset_class.id,
                        percentage=allocation_pct,
                        value=round(allocation_value, 2),
                        created_by=creator.id,
                        updated_by=updater.id,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.add(allocation)
                    allocations_created += 1
                    
                    # Create holdings for each allocation if securities available
                    if asset_class.name in asset_class_map and random.random() > 0.3:
                        # Try to find securities for this asset class
                        available_securities = []
                        for security_type in security_map:
                            for security in security_map[security_type]:
                                if security.asset_class_id == asset_class.id:
                                    available_securities.append(security)
                        
                        if available_securities:
                            # Choose 1-3 securities for this allocation
                            num_securities = min(random.randint(1, 3), len(available_securities))
                            selected_securities = random.sample(available_securities, num_securities)
                            
                            # Distribute the allocation value among securities
                            security_percentages = []
                            for _ in range(num_securities):
                                security_percentages.append(random.randint(1, 100))
                            
                            total = sum(security_percentages)
                            security_percentages = [p / total for p in security_percentages]
                            
                            for j, security in enumerate(selected_securities):
                                security_value = allocation_value * security_percentages[j]
                                
                                # Calculate shares based on price
                                shares = round(security_value / security.price, 4)
                                
                                holding = Holding(
                                    id=generate_id("holding"),
                                    asset_id=asset_id,
                                    security_id=security.id,
                                    shares=shares,
                                    price=security.price,
                                    value=round(security_value, 2),
                                    basis=round(security_value * random.uniform(0.8, 1.2), 2),
                                    created_by=creator.id,
                                    updated_by=updater.id,
                                    created_at=datetime.utcnow(),
                                    updated_at=datetime.utcnow()
                                )
                                
                                db.add(holding)
                                holdings_created += 1
    
    db.commit()
    print(f"Created {assets_created} assets, {allocations_created} allocations, and {holdings_created} holdings!")
    return assets_created

if __name__ == "__main__":
    seed_asset_data()