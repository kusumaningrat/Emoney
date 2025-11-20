# seeders/client_seeder.py - FIXED for PascalCase field names

from sqlalchemy.orm import Session
from datetime import datetime, timedelta, date
from typing import Dict, List, Any
from decimal import Decimal
import random
from faker import Faker

from models.client import (
    Client, Household, Spouse, Contact, Relationship,
    ClientStatus, MaritalStatus, Gender, ContactType, PreferredMethod, 
    RiskTolerance, RelationshipType
)

fake = Faker()

class ClientSeeder:
    def __init__(self, db: Session):
        self.db = db
        self.created_data = {
            "households": [],
            "clients": [],
            "spouses": [],
            "contacts": [],
            "relationships": []
        }
    
    def seed_all(self) -> Dict[str, List[Any]]:
        """Seed all V2 Client & Household Management entities"""
        print("Starting V2 Client & Household seeding...")
        
        # Seed in dependency order
        self.seed_households()
        self.seed_clients()
        self.seed_spouses()
        self.seed_contacts()
        self.seed_relationships()
        
        self.db.commit()
        print("V2 Client & Household seeding completed!")
        
        return self.created_data
    
    def seed_households(self):
        """Seed 150 households"""
        print("Seeding households...")
        
        family_names = [
            "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", 
            "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
            "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
            "Lee", "Perez", "Thompson", "White", "Harris", "Sanchez", "Clark",
            "Ramirez", "Lewis", "Robinson", "Walker", "Young", "Allen", "King",
            "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores", "Green",
            "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
            "Carter", "Roberts"
        ]
        
        for i in range(1, 151):
            family_name = random.choice(family_names)
            
            household = Household(
                HouseholdID=f"H{i:03d}",
                HouseholdName=f"{family_name} Family",
                PrimaryClientID=None,  # Will be set after creating clients
                NetWorth=Decimal(str(random.randint(-50000, 5000000))),
                Status=random.choice([ClientStatus.ACTIVE.value] * 9 + [ClientStatus.INACTIVE.value]),
                RiskTolerance=random.choice(list(RiskTolerance)).value,
                CreatedDate=datetime.utcnow() - timedelta(days=random.randint(30, 1825)),
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            self.db.add(household)
            self.created_data["households"].append(household)
        
        print(f"✓ Seeded {len(self.created_data['households'])} households")
    
    def seed_clients(self):
        """Seed 250 clients"""
        print("Seeding clients...")
        
        households = self.created_data["households"]
        
        # Get user and office IDs from V1 (assuming they exist)
        user_ids = [f"USR-{i:03d}" for i in range(1, 61)]
        office_ids = [f"OFF-{i:03d}" for i in range(1, 16)]
        
        for i in range(1, 251):
            # Assign household - some clients share households, others are solo
            if i <= 150:
                household = households[i-1]  # First 150 clients get their own household
            else:
                household = random.choice(households[:100])  # Remaining clients join existing households
            
            first_name = fake.first_name()
            last_name = household.HouseholdName.replace(" Family", "")
            
            # Generate realistic birthdate (18-85 years old)
            birth_date = fake.date_of_birth(minimum_age=18, maximum_age=85)
            
            client = Client(
                ClientID=f"C{i:05d}",
                FirstName=first_name,
                LastName=last_name,
                MiddleName=fake.first_name() if random.random() < 0.3 else None,
                Email=f"{first_name.lower()}.{last_name.lower()}{i}@example.com" if random.random() < 0.8 else None,
                Phone=fake.phone_number() if random.random() < 0.9 else None,
                DateOfBirth=birth_date,
                Gender=random.choice(list(Gender)).value,
                MaritalStatus=random.choice(list(MaritalStatus)).value,
                Status=random.choice([ClientStatus.ACTIVE.value] * 8 + 
                                   [ClientStatus.PROSPECT.value] * 2 + 
                                   [ClientStatus.INACTIVE.value]),
                HouseholdID=household.HouseholdID,
                SpouseID=None,  # Will be set when creating spouses
                AdvisorID=random.choice(user_ids),
                OwningUserID=random.choice(user_ids),
                OfficeID=random.choice(office_ids),
                FirmID="FIRM-001",
                CreatedDate=datetime.utcnow() - timedelta(days=random.randint(30, 1825)),
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            self.db.add(client)
            self.created_data["clients"].append(client)
        
        self.db.flush()
        
        # Set primary client for each household
        for household in households:
            household_clients = [c for c in self.created_data["clients"] if c.HouseholdID == household.HouseholdID]
            if household_clients:
                household.PrimaryClientID = household_clients[0].ClientID
        
        print(f"✓ Seeded {len(self.created_data['clients'])} clients")
    
    def seed_spouses(self):
        """Seed 180 spouses"""
        print("Seeding spouses...")
        
        # Get married clients to create spouses for
        married_clients = [c for c in self.created_data["clients"] if c.MaritalStatus == MaritalStatus.MARRIED.value]
        selected_clients = random.sample(married_clients, min(180, len(married_clients)))
        
        for i, client in enumerate(selected_clients, 1):
            # Generate spouse with complementary gender
            if client.Gender == Gender.MALE.value:
                spouse_gender = Gender.FEMALE.value
                spouse_first_name = fake.first_name_female()
            elif client.Gender == Gender.FEMALE.value:
                spouse_gender = Gender.MALE.value
                spouse_first_name = fake.first_name_male()
            else:
                spouse_gender = random.choice([Gender.MALE.value, Gender.FEMALE.value])
                spouse_first_name = fake.first_name()
            
            # Spouse typically has same last name and similar age
            age_diff = random.randint(-10, 10)
            spouse_birth_date = client.DateOfBirth + timedelta(days=age_diff * 365)
            
            spouse = Spouse(
                SpouseID=f"SP{i:03d}",
                ClientID=client.ClientID,
                FirstName=spouse_first_name,
                LastName=client.LastName,
                MiddleName=fake.first_name() if random.random() < 0.2 else None,
                Email=f"{spouse_first_name.lower()}.{client.LastName.lower()}@example.com" if random.random() < 0.7 else None,
                Phone=fake.phone_number() if random.random() < 0.8 else None,
                DateOfBirth=spouse_birth_date,
                Gender=spouse_gender,
                Status=ClientStatus.ACTIVE.value,
                CreatedDate=client.CreatedDate + timedelta(days=random.randint(0, 30)),
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            self.db.add(spouse)
            self.created_data["spouses"].append(spouse)
            
            # Link spouse back to client
            client.SpouseID = spouse.SpouseID
        
        print(f"✓ Seeded {len(self.created_data['spouses'])} spouses")
    
    def seed_contacts(self):
        """Seed 100 contacts"""
        print("Seeding contacts...")
        
        clients = self.created_data["clients"]
        contact_types = list(ContactType)
        
        # Select 100 random clients to have contacts
        selected_clients = random.sample(clients, min(100, len(clients)))
        
        for i, client in enumerate(selected_clients, 1):
            contact_type = random.choice(contact_types)
            
            # Generate contact based on type
            if contact_type == ContactType.ATTORNEY:
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = f"{first_name.lower()}.{last_name.lower()}@lawfirm.com"
            elif contact_type == ContactType.ACCOUNTANT:
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = f"{first_name.lower()}.{last_name.lower()}@cpa.com"
            elif contact_type == ContactType.EMERGENCY:
                first_name = fake.first_name()
                last_name = random.choice([client.LastName, fake.last_name()])
                email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            else:
                first_name = fake.first_name()
                last_name = fake.last_name()
                email = f"{first_name.lower()}.{last_name.lower()}@example.com"
            
            contact = Contact(
                ContactID=f"CON-{i:03d}",
                ClientID=client.ClientID,
                ContactType=contact_type.value,
                FirstName=first_name,
                LastName=last_name,
                Email=email if random.random() < 0.9 else None,
                Phone=fake.phone_number() if random.random() < 0.95 else None,
                Address=fake.street_address() if random.random() < 0.7 else None,
                City=fake.city() if random.random() < 0.7 else None,
                State=fake.state_abbr() if random.random() < 0.7 else None,
                ZipCode=fake.zipcode() if random.random() < 0.7 else None,
                Country="US",
                PreferredMethod=random.choice(list(PreferredMethod)).value,
                Status=ClientStatus.ACTIVE.value,
                CreatedDate=client.CreatedDate + timedelta(days=random.randint(0, 365)),
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            self.db.add(contact)
            self.created_data["contacts"].append(contact)
        
        print(f"✓ Seeded {len(self.created_data['contacts'])} contacts")
    
    def seed_relationships(self):
        """Seed 120 relationships"""
        print("Seeding relationships...")
        
        clients = self.created_data["clients"]
        relationship_types = list(RelationshipType)
        
        created_pairs = set()  # Track client pairs to avoid duplicates
        
        for i in range(1, 121):
            # Select two different clients
            while True:
                client1 = random.choice(clients)
                client2 = random.choice(clients)
                
                if client1.ClientID != client2.ClientID:
                    pair = tuple(sorted([client1.ClientID, client2.ClientID]))
                    if pair not in created_pairs:
                        created_pairs.add(pair)
                        break
            
            # Determine relationship type based on context
            if client1.HouseholdID == client2.HouseholdID:
                # Same household - likely family
                rel_type = random.choice([RelationshipType.SPOUSE, RelationshipType.CHILD, 
                                        RelationshipType.PARENT, RelationshipType.SIBLING])
            else:
                # Different households - could be referral or business
                rel_type = random.choice([RelationshipType.REFERRAL, RelationshipType.BUSINESS_PARTNER, 
                                        RelationshipType.OTHER])
            
            # Create bidirectional relationships
            relationship1 = Relationship(
                RelationshipID=f"REL-{i:03d}A",
                ClientID=client1.ClientID,
                RelatedClientID=client2.ClientID,
                RelationshipType=rel_type.value,
                Description=self._generate_relationship_description(rel_type, client1, client2),
                Status=ClientStatus.ACTIVE.value,
                CreatedDate=datetime.utcnow() - timedelta(days=random.randint(0, 730)),
                ModifiedDate=datetime.utcnow() - timedelta(days=random.randint(0, 30))
            )
            
            # Reciprocal relationship (if applicable)
            reciprocal_type = self._get_reciprocal_relationship(rel_type)
            relationship2 = Relationship(
                RelationshipID=f"REL-{i:03d}B",
                ClientID=client2.ClientID,
                RelatedClientID=client1.ClientID,
                RelationshipType=reciprocal_type.value,
                Description=self._generate_relationship_description(reciprocal_type, client2, client1),
                Status=ClientStatus.ACTIVE.value,
                CreatedDate=relationship1.CreatedDate,
                ModifiedDate=relationship1.ModifiedDate
            )
            
            self.db.add(relationship1)
            self.db.add(relationship2)
            self.created_data["relationships"].extend([relationship1, relationship2])
        
        print(f"✓ Seeded {len(self.created_data['relationships'])} relationships")
    
    def _generate_relationship_description(self, rel_type: RelationshipType, client1, client2) -> str:
        """Generate description for relationship"""
        descriptions = {
            RelationshipType.SPOUSE: f"Married to {client2.FirstName} {client2.LastName}",
            RelationshipType.CHILD: f"Child of {client2.FirstName} {client2.LastName}",
            RelationshipType.PARENT: f"Parent of {client2.FirstName} {client2.LastName}",
            RelationshipType.SIBLING: f"Sibling of {client2.FirstName} {client2.LastName}",
            RelationshipType.REFERRAL: f"Referred by {client2.FirstName} {client2.LastName}",
            RelationshipType.BUSINESS_PARTNER: f"Business partner with {client2.FirstName} {client2.LastName}",
            RelationshipType.OTHER: f"Related to {client2.FirstName} {client2.LastName}"
        }
        return descriptions.get(rel_type, f"Connected to {client2.FirstName} {client2.LastName}")
    
    def _get_reciprocal_relationship(self, rel_type: RelationshipType) -> RelationshipType:
        """Get reciprocal relationship type"""
        reciprocals = {
            RelationshipType.SPOUSE: RelationshipType.SPOUSE,
            RelationshipType.CHILD: RelationshipType.PARENT,
            RelationshipType.PARENT: RelationshipType.CHILD,
            RelationshipType.SIBLING: RelationshipType.SIBLING,
            RelationshipType.REFERRAL: RelationshipType.OTHER,  # Person who made referral
            RelationshipType.BUSINESS_PARTNER: RelationshipType.BUSINESS_PARTNER,
            RelationshipType.OTHER: RelationshipType.OTHER
        }
        return reciprocals.get(rel_type, RelationshipType.OTHER)