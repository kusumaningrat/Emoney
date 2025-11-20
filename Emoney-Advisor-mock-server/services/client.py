# services/client.py - Version 2: Client & Household Services

from sqlalchemy.orm import Session, joinedload
from typing import Optional, List
from models.client import (
    Client, Household, Spouse, Contact, Relationship
)


class ClientService:
    """Service for Client operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, 
                status: Optional[str] = None, advisor_id: Optional[str] = None) -> List[Client]:
        """Get all clients with pagination and optional filters"""
        query = db.query(Client)
        if status:
            query = query.filter(Client.status == status)
        if advisor_id:
            query = query.filter(Client.advisor_id == advisor_id)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, client_id: str, include_household: bool = False) -> Optional[Client]:
        """Get client by ID with optional household details"""
        query = db.query(Client)
        if include_household:
            query = query.options(
                joinedload(Client.household),
                joinedload(Client.spouse),
                joinedload(Client.contacts)
            )
        return query.filter(Client.client_id == client_id).first()
    
    def get_client_household(self, db: Session, client_id: str) -> Optional[Household]:
        """Get client's household"""
        client = self.get_by_id(db, client_id)
        if client and client.household_id:
            return db.query(Household).options(
                joinedload(Household.members)
            ).filter(Household.household_id == client.household_id).first()
        return None
    
    def get_client_spouse(self, db: Session, client_id: str) -> Optional[Spouse]:
        """Get client's spouse"""
        client = self.get_by_id(db, client_id)
        if client and client.spouse_id:
            return db.query(Spouse).filter(Spouse.spouse_id == client.spouse_id).first()
        return None
    
    def search_clients(self, db: Session, first_name: Optional[str] = None, 
                      last_name: Optional[str] = None, email: Optional[str] = None,
                      skip: int = 0, limit: int = 100) -> List[Client]:
        """Search clients by various criteria"""
        query = db.query(Client)
        if first_name:
            query = query.filter(Client.first_name.ilike(f"%{first_name}%"))
        if last_name:
            query = query.filter(Client.last_name.ilike(f"%{last_name}%"))
        if email:
            query = query.filter(Client.email.ilike(f"%{email}%"))
        return query.offset(skip).limit(limit).all()


class HouseholdService:
    """Service for Household operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, 
                status: Optional[str] = None, min_net_worth: Optional[float] = None) -> List[Household]:
        """Get all households with pagination and optional filters"""
        query = db.query(Household)
        if status:
            query = query.filter(Household.status == status)
        if min_net_worth:
            query = query.filter(Household.net_worth >= min_net_worth)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, household_id: str) -> Optional[Household]:
        """Get household by ID with members"""
        return db.query(Household).options(
            joinedload(Household.members),
            joinedload(Household.primary_client)
        ).filter(Household.household_id == household_id).first()
    
    def get_household_members(self, db: Session, household_id: str) -> List[Client]:
        """Get all members of a household"""
        return db.query(Client).filter(
            Client.household_id == household_id,
            Client.status == "Active"
        ).all()
    
    def get_household_networth(self, db: Session, household_id: str) -> Optional[Household]:
        """Get household net worth (same as get_by_id for now)"""
        return self.get_by_id(db, household_id)


class SpouseService:
    """Service for Spouse operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100, 
                status: Optional[str] = None) -> List[Spouse]:
        """Get all spouses with pagination and optional status filter"""
        query = db.query(Spouse)
        if status:
            query = query.filter(Spouse.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, spouse_id: str) -> Optional[Spouse]:
        """Get spouse by ID with client details"""
        return db.query(Spouse).options(
            joinedload(Spouse.client)
        ).filter(Spouse.spouse_id == spouse_id).first()
    
    def get_by_client_id(self, db: Session, client_id: str) -> Optional[Spouse]:
        """Get spouse by client ID"""
        return db.query(Spouse).filter(Spouse.client_id == client_id).first()


class ContactService:
    """Service for Contact operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                client_id: Optional[str] = None, contact_type: Optional[str] = None,
                status: Optional[str] = None) -> List[Contact]:
        """Get all contacts with pagination and optional filters"""
        query = db.query(Contact)
        if client_id:
            query = query.filter(Contact.client_id == client_id)
        if contact_type:
            query = query.filter(Contact.contact_type == contact_type)
        if status:
            query = query.filter(Contact.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, contact_id: str) -> Optional[Contact]:
        """Get contact by ID with client details"""
        return db.query(Contact).options(
            joinedload(Contact.client)
        ).filter(Contact.contact_id == contact_id).first()
    
    def get_client_contacts(self, db: Session, client_id: str, 
                           contact_type: Optional[str] = None) -> List[Contact]:
        """Get all contacts for a specific client"""
        query = db.query(Contact).filter(Contact.client_id == client_id)
        if contact_type:
            query = query.filter(Contact.contact_type == contact_type)
        return query.all()


class RelationshipService:
    """Service for Relationship operations"""
    
    def get_all(self, db: Session, skip: int = 0, limit: int = 100,
                client_id: Optional[str] = None, relationship_type: Optional[str] = None,
                status: Optional[str] = None) -> List[Relationship]:
        """Get all relationships with pagination and optional filters"""
        query = db.query(Relationship)
        if client_id:
            query = query.filter(
                (Relationship.client_id == client_id) | 
                (Relationship.related_client_id == client_id)
            )
        if relationship_type:
            query = query.filter(Relationship.relationship_type == relationship_type)
        if status:
            query = query.filter(Relationship.status == status)
        return query.offset(skip).limit(limit).all()
    
    def get_by_id(self, db: Session, relationship_id: str) -> Optional[Relationship]:
        """Get relationship by ID with client details"""
        return db.query(Relationship).options(
            joinedload(Relationship.client),
            joinedload(Relationship.related_client)
        ).filter(Relationship.relationship_id == relationship_id).first()
    
    def get_client_relationships(self, db: Session, client_id: str,
                               relationship_type: Optional[str] = None) -> List[Relationship]:
        """Get all relationships for a specific client"""
        query = db.query(Relationship).filter(
            (Relationship.client_id == client_id) | 
            (Relationship.related_client_id == client_id)
        )
        if relationship_type:
            query = query.filter(Relationship.relationship_type == relationship_type)
        return query.all()